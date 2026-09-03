"""logic_change.md 的 CHG 协调、生命周期与语义检查。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from datetime import date
from .constants import (
    CHANGE_HEADING_RE,
    CHANGE_STATUSES,
    CONFLICT_RESOLUTIONS,
    DECISION_GATES,
    DECISION_RECORD_POLICIES,
    DECISION_STATES,
    DEPENDENCY_REFERENCE_RE,
    GOVERNANCE_VERIFICATION_STATES,
    HISTORY_RETENTION_POLICIES,
    INTENT_ID_RE,
    PERSONAL_OPTIONAL_CHANGE_FIELDS,
    POSITIVE_INTEGER_RE,
    RECALL_ROUTES,
    REVIEW_DUE_RE,
    REVIEW_INTERVAL_RE,
    RULE_ID_RE,
    RUNTIME_STATES,
    SEMANTIC_REVIEW_STATES,
    TRACE_TEST_RE,
    VERSION_ID_TOKEN_RE,
)
from .textutil import (
    control_values,
    control_values_raw,
    has_meaningful_value,
    is_iso_date,
    is_none_like,
    markdown_table_rows,
    normalize_change_id,
    normalize_topic_id,
    relationship_items,
)

def change_field_tier(values: dict[str, list[str]], ledger_mode: str = "") -> str:
    """RULE-023：决定 CHG 块的字段要求档位。

    块自身的 ``governance_mode`` 优先，其次是账本（logic_change 文档控制）的模式；
    两者都缺时按 ``full`` 处理——保守地保持拆档前的完整字段要求，而不是替
    未声明模式的项目降低门槛。返回 ``"personal"`` 或 ``"full"``。
    """
    block_mode = (values.get("governance_mode") or [""])[0]
    mode = (block_mode or ledger_mode or "").strip().casefold()
    return "personal" if mode == "personal" else "full"


def governance_evidence_issues(
    values: dict[str, list[str]], *, label: str, collaborative_required: bool = False
) -> list[str]:
    """Check auditable governance evidence without claiming platform enforcement."""
    issues: list[str] = []
    mode = (values.get("governance_mode") or [""])[0].casefold()
    verification = (values.get("governance_verification") or [""])[0].casefold()
    evidence = (values.get("governance_evidence") or [""])[0]
    verified_at = (values.get("governance_verified_at") or [""])[0]
    if mode == "collaborative" or collaborative_required:
        if verification != "verified":
            issues.append(f"{label}:collaborative-governance-evidence-must-be-verified")
        if not has_meaningful_value(values, "governance_evidence"):
            issues.append(f"{label}:collaborative-governance-needs-evidence")
        if not is_iso_date(verified_at):
            issues.append(f"{label}:governance-verified-at-must-be-date")
        if evidence and not any(
            token.casefold().startswith(prefix)
            for token in re.split(r"[;,]", evidence)
            for prefix in (
                "pr:",
                "ci:",
                "branch-protection:",
                "codeowners:",
                "approval:",
            )
        ):
            issues.append(f"{label}:governance-evidence-needs-typed-reference")
    elif verification and verification not in GOVERNANCE_VERIFICATION_STATES:
        issues.append(f"{label}:invalid-governance-verification")
    elif verified_at and not is_iso_date(verified_at):
        issues.append(f"{label}:governance-verified-at-must-be-date")
    return issues


def traceability_issues(value: str, *, label: str) -> list[str]:
    """Validate INT -> RULE -> test -> VER chains used for durable recall."""
    if is_none_like(value):
        return [f"{label}:intent-traceability-required"]
    issues: list[str] = []
    chains = [item.strip() for item in re.split(r";", value) if item.strip()]
    for index, chain in enumerate(chains, start=1):
        parts = [item.strip() for item in re.split(r"\s*->\s*", chain)]
        if len(parts) != 4:
            issues.append(f"{label}:intent-traceability-chain-{index}-needs-four-parts")
            continue
        intent_id, rule_id, test_ref, version_id = parts
        if not INTENT_ID_RE.fullmatch(intent_id):
            issues.append(f"{label}:invalid-intent-id:{intent_id or 'empty'}")
        if not RULE_ID_RE.fullmatch(rule_id):
            issues.append(f"{label}:invalid-trace-rule-id:{rule_id or 'empty'}")
        if not TRACE_TEST_RE.fullmatch(test_ref):
            issues.append(f"{label}:invalid-trace-test-ref:{test_ref or 'empty'}")
        if not VERSION_ID_TOKEN_RE.fullmatch(version_id):
            issues.append(f"{label}:invalid-trace-version-id:{version_id or 'empty'}")
    if not chains:
        issues.append(f"{label}:intent-traceability-needs-chain")
    return issues


def review_freshness_issues(
    last_verified: str, trigger: str, *, label: str, today: date | None = None
) -> list[str]:
    """Make review_trigger enforceable while retaining event-based triggers."""
    today = today or date.today()
    issues: list[str] = []
    if not is_iso_date(last_verified):
        return issues
    match = REVIEW_INTERVAL_RE.search(trigger or "")
    due_match = REVIEW_DUE_RE.search(trigger or "")
    if not match and not due_match:
        issues.append(f"{label}:review-trigger-needs-interval-or-due")
        return issues
    verified = date.fromisoformat(last_verified)
    if due_match:
        due = date.fromisoformat(due_match.group(1))
        if due < today:
            issues.append(f"{label}:review-due-expired:{due.isoformat()}")
    if match:
        amount = int(match.group(1))
        unit = match.group(2).casefold()
        days = amount * {"d": 1, "w": 7, "m": 30, "y": 365}[unit]
        due = verified.fromordinal(verified.toordinal() + days)
        if due < today:
            issues.append(f"{label}:review-interval-expired:{due.isoformat()}")
    return issues


_WAITING_STATUSES = {"awaiting-decision", "blocked"}
_IMPLEMENTATION_STATUSES = {"implementing", "verifying", "promoting"}


def _coordination_entries(
    blocks: dict[str, str], ledger_mode: str, issues: list[str]
) -> dict[str, dict[str, object]]:
    """逐块解析协调字段（authority_surfaces/depends_on/conflicts_with…）。

    块自身的字段问题追加到 ``issues``；返回的 entries 供跨块关系检查使用。
    """
    entries: dict[str, dict[str, object]] = {}
    required_fields = (
        "authority_surfaces",
        "based_on",
        "depends_on",
        "conflicts_with",
        "conflict_resolution",
        "history_retention",
        "runtime_state",
        "runtime_environments",
        "feature_flag",
    )
    waiting_statuses = _WAITING_STATUSES
    implementation_statuses = _IMPLEMENTATION_STATUSES

    for change_id, block in blocks.items():
        raw_values = control_values_raw(block)
        values = control_values(block)
        strict = change_field_tier(values, ledger_mode) != "personal"

        def present(key: str) -> bool:
            # RULE-023：personal 层对可选字段"缺则不查、写则照查"
            return strict or key in raw_values

        def one_value(key: str) -> str:
            field_values = raw_values.get(key, [])
            if not field_values and not present(key) and key in PERSONAL_OPTIONAL_CHANGE_FIELDS:
                return ""
            if len(field_values) != 1:
                issues.append(
                    f"{change_id}:{key}-must-appear-once:{len(field_values)}"
                )
                return ""
            return field_values[0].strip()

        field_values = {key: one_value(key) for key in required_fields}
        status = (values.get("status") or [""])[0]
        proposal_revision = (values.get("proposal_revision") or [""])[0]
        decision_record = (values.get("decision_record") or [""])[0]

        authority_items = relationship_items(raw_values, "authority_surfaces")
        authority_non_none = [
            item for item in authority_items if not is_none_like(item)
        ]
        if present("authority_surfaces") and not authority_non_none:
            issues.append(f"{change_id}:missing-authority-surfaces")
        if any(is_none_like(item) for item in authority_items) and authority_non_none:
            issues.append(f"{change_id}:authority-surfaces-cannot-mix-none")
        authority_surfaces: set[str] = set()
        for item in authority_non_none:
            normalized = item.casefold()
            if normalized in {".", "*", "all", "all-project", "project-root"}:
                issues.append(f"{change_id}:authority-surface-too-broad:{item}")
            if normalized in authority_surfaces:
                issues.append(f"{change_id}:duplicate-authority-surface:{item}")
            authority_surfaces.add(normalized)

        based_on = field_values["based_on"]
        based_on_folded = based_on.casefold()
        if not has_meaningful_value(values, "based_on"):
            if present("based_on"):
                issues.append(f"{change_id}:missing-based-on")
        else:
            if "policy:" not in based_on_folded:
                issues.append(f"{change_id}:based-on-needs-policy-reference")
            if not any(
                marker in based_on_folded
                for marker in ("code:", "commit:", "snapshot:", "release:", "tree:")
            ):
                issues.append(f"{change_id}:based-on-needs-code-or-snapshot-reference")
            if "surfaces:" not in based_on_folded:
                issues.append(f"{change_id}:based-on-needs-authority-surfaces")
            for authority_surface in sorted(authority_surfaces):
                if authority_surface not in based_on_folded:
                    issues.append(
                        f"{change_id}:based-on-missing-authority-surface:"
                        f"{authority_surface}"
                    )

        history_retention = field_values["history_retention"].casefold()
        check_history = present("history_retention")
        if check_history and history_retention not in HISTORY_RETENTION_POLICIES:
            issues.append(
                f"{change_id}:invalid-history-retention:{history_retention}"
            )
        if (
            check_history
            and (values.get("recall_route") or [""])[0] == "high"
            and history_retention != "full"
        ):
            issues.append(f"{change_id}:high-route-needs-full-history-retention")
        if history_retention == "full" and decision_record != "required":
            issues.append(f"{change_id}:full-history-needs-required-decision-record")
        if history_retention in {"compact", "full"} and status in implementation_statuses:
            reserved_version = (values.get("reserved_version_id") or [""])[0]
            version_slug = (values.get("version_slug") or [""])[0]
            if is_none_like(reserved_version) or is_none_like(version_slug):
                issues.append(
                    f"{change_id}:retained-history-needs-reserved-version-record"
                )

        runtime_state = field_values["runtime_state"].casefold()
        runtime_items = relationship_items(raw_values, "runtime_environments")
        runtime_non_none = [item for item in runtime_items if not is_none_like(item)]
        feature_flag = field_values["feature_flag"]
        if present("runtime_state") and runtime_state not in RUNTIME_STATES:
            issues.append(f"{change_id}:invalid-runtime-state:{runtime_state}")
        if any(is_none_like(item) for item in runtime_items) and runtime_non_none:
            issues.append(f"{change_id}:runtime-environments-cannot-mix-none")
        if runtime_state in {
            "not-implemented",
            "implemented-unmerged",
            "merged-not-deployed",
        }:
            if runtime_non_none:
                issues.append(
                    f"{change_id}:{runtime_state}-must-not-name-runtime-environment"
                )
            if not is_none_like(feature_flag):
                issues.append(f"{change_id}:{runtime_state}-needs-feature-flag-none")
        elif runtime_state == "deployed-guarded":
            if not runtime_non_none:
                issues.append(f"{change_id}:{runtime_state}-needs-runtime-environment")
            if is_none_like(feature_flag):
                issues.append(f"{change_id}:deployed-guarded-needs-feature-flag")
        elif runtime_state == "deployed-active":
            if not runtime_non_none:
                issues.append(f"{change_id}:deployed-active-needs-runtime-environment")
            issues.append(
                f"{change_id}:deployed-active-must-be-promoted-and-closed"
            )

        dependency_items = relationship_items(raw_values, "depends_on")
        dependencies: list[tuple[str, str]] = []
        if any(is_none_like(item) for item in dependency_items) and any(
            not is_none_like(item) for item in dependency_items
        ):
            issues.append(f"{change_id}:depends-on-cannot-mix-none")
        for item in dependency_items:
            if is_none_like(item):
                continue
            match = DEPENDENCY_REFERENCE_RE.fullmatch(item)
            if not match:
                issues.append(f"{change_id}:invalid-dependency-reference:{item}")
                continue
            target = normalize_change_id(match.group(1))
            revision = match.group(2)
            if target == change_id:
                issues.append(f"{change_id}:self-dependency")
                continue
            dependencies.append((target, revision))
        if len(dependencies) != len(set(dependencies)):
            issues.append(f"{change_id}:duplicate-dependency-reference")

        conflict_items = relationship_items(raw_values, "conflicts_with")
        conflict_ids: set[str] = set()
        conflict_surfaces: set[str] = set()
        if any(is_none_like(item) for item in conflict_items) and any(
            not is_none_like(item) for item in conflict_items
        ):
            issues.append(f"{change_id}:conflicts-with-cannot-mix-none")
        for item in conflict_items:
            if is_none_like(item):
                continue
            normalized_change = normalize_change_id(item)
            if normalized_change:
                if normalized_change == change_id:
                    issues.append(f"{change_id}:self-conflict")
                else:
                    conflict_ids.add(normalized_change)
            elif item.casefold().startswith("chg-"):
                issues.append(f"{change_id}:invalid-conflict-reference:{item}")
            else:
                conflict_surfaces.add(item.casefold())

        conflict_resolution = field_values["conflict_resolution"].casefold()
        has_conflict = bool(conflict_ids or conflict_surfaces)
        if present("conflict_resolution") and conflict_resolution not in CONFLICT_RESOLUTIONS:
            issues.append(
                f"{change_id}:invalid-conflict-resolution:{conflict_resolution}"
            )
        elif has_conflict and conflict_resolution in {"none", ""}:
            # personal 块可以不写 conflict_resolution，但一旦声明了冲突就必须给出裁定
            issues.append(f"{change_id}:conflicts-need-resolution")
        elif not has_conflict and conflict_resolution not in {"none", ""}:
            issues.append(f"{change_id}:conflict-resolution-without-conflict")
        if conflict_resolution == "unresolved" and status not in waiting_statuses:
            issues.append(f"{change_id}:unresolved-conflict-needs-block-or-redecision")

        entries[change_id] = {
            "status": status,
            "proposal_revision": proposal_revision,
            "dependencies": dependencies,
            "dependency_targets": {target for target, _ in dependencies},
            "conflict_ids": conflict_ids,
            "conflict_resolution": conflict_resolution,
            "authority_surfaces": authority_surfaces,
            "blocked_by": relationship_items(raw_values, "blocked_by"),
            "unblock_condition": " ".join(
                raw_values.get("unblock_condition", [])
            ).strip(),
        }

    return entries


def change_coordination_issues(
    blocks: dict[str, str],
    *,
    ledger_mode: str = "",
    other_ledgers: dict[str, dict[str, str]] | None = None,
) -> list[str]:
    """Validate declared relationships between the active CHGs of one ledger.

    This intentionally validates only declared coordination.  It cannot prove
    that two code paths really are independent, so a missing declaration still
    requires human/code-semantic review.

    ``ledger_mode`` 是账本的 ``governance_mode``（RULE-023）：personal 块缺少
    collaborative/compliance 层字段时不报缺失，写了的字段照常校验。

    ``other_ledgers`` 是同一项目其余账本（根 + 各领域）的 CHG 块（RULE-018）：
    ``depends_on`` / ``conflicts_with`` / ``blocked_by`` 的目标可以落在别的账本，
    根议案与领域议案互写 ``conflicts_with`` 正是一法多议案的规定解法，不得被账本
    边界打成 ``conflict-target-not-active``。其他账本块自身的字段问题由它们各自的
    调用报告，这里只借用其关系字段；同账本影响面重叠仍只在本账本内比对
    （跨账本重叠由 :func:`cross_ledger_rule_conflicts` 报告）。
    """
    issues: list[str] = []
    waiting_statuses = _WAITING_STATUSES
    implementation_statuses = _IMPLEMENTATION_STATUSES
    entries = _coordination_entries(blocks, ledger_mode, issues)
    all_entries: dict[str, dict[str, object]] = dict(entries)
    for other_blocks in (other_ledgers or {}).values():
        if other_blocks is blocks:
            continue
        for other_id, other_entry in _coordination_entries(other_blocks, "", []).items():
            all_entries.setdefault(other_id, other_entry)

    dependency_graph: dict[str, set[str]] = {change_id: set() for change_id in all_entries}
    for change_id, entry in all_entries.items():
        for target, _revision in entry["dependencies"]:  # type: ignore[index]
            if target in all_entries:
                dependency_graph[change_id].add(target)
    for change_id, entry in entries.items():
        status = str(entry["status"])
        for target, revision in entry["dependencies"]:  # type: ignore[index]
            target_entry = all_entries.get(target)
            if target_entry is None:
                issues.append(f"{change_id}:dependency-target-not-active:{target}")
                continue
            target_revision = str(target_entry["proposal_revision"])
            if target_revision != revision and status not in waiting_statuses:
                issues.append(
                    f"{change_id}:dependency-revision-drift-needs-block-or-redecision:"
                    f"{target}@revision-{revision}!={target_revision}"
                )
            if str(target_entry["status"]) == "blocked" and status not in waiting_statuses:
                issues.append(
                    f"{change_id}:blocked-dependency-needs-block-or-redecision:{target}"
                )
            if status in implementation_statuses:
                # verifying + explicit unblock_condition = implementation landed and
                # only joint acceptance / rebind-after-upstream-close remains; the
                # re-verification commitment is carried by depends_on + unblock_condition.
                # blocked stays reserved for "cannot implement".
                acceptance_hold = status == "verifying" and bool(
                    str(entry.get("unblock_condition", "")).strip()
                )
                if not acceptance_hold:
                    issues.append(
                        f"{change_id}:active-dependency-needs-block-or-redecision:{target}"
                    )

    visiting: list[str] = []
    visited: set[str] = set()
    cycles: set[tuple[str, ...]] = set()

    def visit(change_id: str) -> None:
        if change_id in visiting:
            cycle_start = visiting.index(change_id)
            cycles.add(tuple(sorted(set(visiting[cycle_start:]))))
            return
        if change_id in visited:
            return
        visiting.append(change_id)
        for target in sorted(dependency_graph[change_id]):
            visit(target)
        visiting.pop()
        visited.add(change_id)

    for change_id in sorted(dependency_graph):
        visit(change_id)
    for cycle in sorted(cycles):
        # 跨账本环只由持有最小 CHG-ID 的账本报告一次
        if cycle[0] in entries:
            issues.append("dependency-cycle:" + ",".join(cycle))

    checked_conflict_pairs: set[tuple[str, str]] = set()
    for change_id, entry in entries.items():
        for target in sorted(entry["conflict_ids"]):  # type: ignore[index]
            target_entry = all_entries.get(target)
            if target_entry is None:
                issues.append(f"{change_id}:conflict-target-not-active:{target}")
                continue
            if change_id not in target_entry["conflict_ids"]:  # type: ignore[operator]
                issues.append(f"{change_id}:conflict-not-reciprocal:{target}")
                continue
            pair = tuple(sorted((change_id, target)))
            if pair in checked_conflict_pairs:
                continue
            checked_conflict_pairs.add(pair)
            target_resolution = str(target_entry["conflict_resolution"])
            resolution = str(entry["conflict_resolution"])
            if resolution != target_resolution:
                issues.append(
                    f"conflict-resolution-mismatch:{pair[0]}:{resolution}!="
                    f"{pair[1]}:{target_resolution}"
                )
                continue
            if resolution in {"unresolved", "merge", "supersede"}:
                if (
                    str(entry["status"]) not in waiting_statuses
                    or str(target_entry["status"]) not in waiting_statuses
                ):
                    issues.append(
                        "active-conflict-needs-block-or-redecision:"
                        + ":".join(pair)
                    )
            elif resolution == "sequence-and-revalidate":
                first_depends_on_second = target in entry["dependency_targets"]  # type: ignore[operator]
                second_depends_on_first = change_id in target_entry["dependency_targets"]  # type: ignore[operator]
                if first_depends_on_second == second_depends_on_first:
                    issues.append(
                        "sequence-conflict-needs-one-way-dependency:"
                        + ":".join(pair)
                    )

    change_ids = sorted(entries)
    for index, change_id in enumerate(change_ids):
        for target in change_ids[index + 1 :]:
            shared_surfaces = entries[change_id]["authority_surfaces"].intersection(  # type: ignore[union-attr]
                entries[target]["authority_surfaces"]  # type: ignore[union-attr]
            )
            if shared_surfaces and (
                target not in entries[change_id]["conflict_ids"]  # type: ignore[operator]
                or change_id not in entries[target]["conflict_ids"]  # type: ignore[operator]
            ):
                issues.append(
                    f"{change_id}:unmarked-authority-surface-overlap:{target}:"
                    + ",".join(sorted(shared_surfaces))
                )

    for change_id, entry in entries.items():
        if str(entry["status"]) != "blocked":
            continue
        for item in entry["blocked_by"]:  # type: ignore[index]
            target = normalize_change_id(item.split("@", 1)[0])
            if target and target not in all_entries:
                issues.append(f"{change_id}:blocked-by-target-not-active:{target}")

    return sorted(set(issues))


def change_lifecycle_issues(
    change_id: str,
    values: dict[str, list[str]],
    raw_values: dict[str, list[str]],
    *,
    tier: str = "full",
) -> list[str]:
    """Validate version-bound decision confirmation and semantic review metadata.

    ``tier`` 来自 :func:`change_field_tier`（RULE-023）。personal 档不要求
    ``decision_gate`` 状态机与语义审查字段，但进入实施状态前仍必须有
    ``decision_confirmed_by`` + ``decision_confirmed_at``：用户确认是核心原则 1/5，
    不随治理模式降级。
    """
    issues: list[str] = []

    def one_value(key: str) -> str:
        entries = raw_values.get(key, [])
        if not entries and tier == "personal" and key in PERSONAL_OPTIONAL_CHANGE_FIELDS:
            return ""
        if len(entries) != 1:
            issues.append(f"{change_id}:{key}-must-appear-once:{len(entries)}")
            return ""
        return (values.get(key) or [""])[0]

    proposal_revision = one_value("proposal_revision")
    recall_route = one_value("recall_route")
    decision_gate = one_value("decision_gate")
    decision_state = one_value("decision_state")
    confirmed_revision = one_value("confirmed_proposal_revision")
    confirmed_by = one_value("decision_confirmed_by")
    decision_ref = one_value("decision_ref")
    confirmed_at = one_value("decision_confirmed_at")
    decision_record = one_value("decision_record")
    review_state = one_value("semantic_review_state")
    reviewed_by = one_value("semantic_reviewed_by")
    review_ref = one_value("semantic_review_ref")
    reviewed_at = one_value("semantic_reviewed_at")

    if proposal_revision and not POSITIVE_INTEGER_RE.fullmatch(proposal_revision):
        issues.append(f"{change_id}:invalid-proposal-revision:{proposal_revision}")
    if recall_route not in RECALL_ROUTES:
        issues.append(f"{change_id}:invalid-recall-route:{recall_route}")
    if decision_gate and decision_gate not in DECISION_GATES:
        issues.append(f"{change_id}:invalid-decision-gate:{decision_gate}")
    if decision_state and decision_state not in DECISION_STATES:
        issues.append(f"{change_id}:invalid-decision-state:{decision_state}")
    if decision_record and decision_record not in DECISION_RECORD_POLICIES:
        issues.append(f"{change_id}:invalid-decision-record-policy:{decision_record}")
    if review_state and review_state not in SEMANTIC_REVIEW_STATES:
        issues.append(f"{change_id}:invalid-semantic-review-state:{review_state}")

    confirmation_fields = {
        "confirmed_proposal_revision": confirmed_revision,
        "decision_confirmed_by": confirmed_by,
        "decision_ref": decision_ref,
        "decision_confirmed_at": confirmed_at,
    }

    def confirmation_must_be_empty() -> None:
        for key, value in confirmation_fields.items():
            if value and not is_none_like(value):
                issues.append(f"{change_id}:{key}-must-be-none-without-confirmation")

    def confirmation_must_match_revision() -> None:
        if not POSITIVE_INTEGER_RE.fullmatch(confirmed_revision):
            issues.append(f"{change_id}:invalid-confirmed-proposal-revision")
        elif proposal_revision and confirmed_revision != proposal_revision:
            issues.append(
                f"{change_id}:confirmed-proposal-revision-mismatch:"
                f"{confirmed_revision}!={proposal_revision}"
            )
        for key, value in (
            ("decision_confirmed_by", confirmed_by),
            ("decision_ref", decision_ref),
        ):
            if is_none_like(value):
                issues.append(f"{change_id}:{key}-required-for-confirmed-decision")
        if not is_iso_date(confirmed_at):
            issues.append(f"{change_id}:decision_confirmed_at-must-be-date")

    status = (values.get("status") or [""])[0]
    personal_without_gate = tier == "personal" and not decision_gate
    if recall_route == "high" and decision_gate != "required" and not personal_without_gate:
        issues.append(f"{change_id}:high-route-needs-required-decision")
    if decision_gate == "required" and recall_route != "high":
        issues.append(f"{change_id}:required-decision-needs-high-route")
    if decision_gate == "required":
        if decision_record != "required":
            issues.append(f"{change_id}:required-decision-needs-immutable-record")
        if status in {"draft", "awaiting-decision"} and decision_state != "pending":
            issues.append(f"{change_id}:{status}-needs-pending-decision")
        if status in {"implementing", "verifying"} and decision_state != "confirmed":
            issues.append(f"{change_id}:{status}-needs-confirmed-current-decision")
        if status == "blocked" and decision_state not in {"pending", "confirmed"}:
            issues.append(f"{change_id}:blocked-needs-pending-or-confirmed-decision")
        if decision_state == "confirmed":
            confirmation_must_match_revision()
            if status in {"draft", "awaiting-decision"}:
                issues.append(f"{change_id}:confirmed-decision-must-enter-implementation")
        elif decision_state == "pending":
            confirmation_must_be_empty()
        elif decision_state:
            issues.append(f"{change_id}:required-decision-cannot-be-{decision_state}")

        if status in {"implementing", "verifying"}:
            reserved_version = (values.get("reserved_version_id") or [""])[0]
            version_slug = (values.get("version_slug") or [""])[0]
            if is_none_like(reserved_version) or is_none_like(version_slug):
                issues.append(
                    f"{change_id}:implementation-needs-reserved-immutable-record"
                )
    elif decision_gate == "not-required":
        if decision_state != "not-required":
            issues.append(f"{change_id}:not-required-decision-needs-not-required-state")
        confirmation_must_be_empty()
        if status == "awaiting-decision":
            issues.append(f"{change_id}:awaiting-decision-needs-required-gate")
    elif not decision_gate and tier == "personal":
        # RULE-023：personal 档没有 decision_gate 状态机，但实施必须有确认来源
        if status in {"implementing", "verifying", "promoting"}:
            if is_none_like(confirmed_by):
                issues.append(f"{change_id}:implementation-needs-decision-confirmation")
            if not is_iso_date(confirmed_at):
                issues.append(f"{change_id}:decision_confirmed_at-must-be-date")

    if review_state in {"passed", "failed"}:
        for key, value in (
            ("semantic_reviewed_by", reviewed_by),
            ("semantic_review_ref", review_ref),
        ):
            if is_none_like(value):
                issues.append(f"{change_id}:{key}-required-for-semantic-review")
        if not is_iso_date(reviewed_at):
            issues.append(f"{change_id}:semantic_reviewed_at-must-be-date")
    elif review_state in {"pending", "not-applicable"}:
        for key, value in (
            ("semantic_reviewed_by", reviewed_by),
            ("semantic_review_ref", review_ref),
            ("semantic_reviewed_at", reviewed_at),
        ):
            if value and not is_none_like(value):
                issues.append(f"{change_id}:{key}-requires-passed-or-failed-review")

    for legacy_field in ("reviewed_by", "review_ref", "approved_by"):
        if legacy_field in raw_values:
            issues.append(f"{change_id}:legacy-{legacy_field}-must-be-migrated")

    return sorted(set(issues))


def change_heading_ids(text: str) -> list[str]:
    return [
        normalize_change_id(match.group(1))
        for line in text.splitlines()
        for match in [CHANGE_HEADING_RE.match(line)]
        if match
    ]


def change_index_ids(text: str) -> set[str]:
    """Return CHG-IDs listed in the preamble/index of a change file."""
    rows = markdown_table_rows(text, "活跃议案索引")
    if rows or "## 活跃议案索引" in text:
        result = {
            change_id
            for row in rows
            for change_id in [normalize_change_id(row.get("change_id", ""))]
            if change_id
        }
        return result
    lines = text.splitlines()
    first_body = next(
        (index for index, line in enumerate(lines) if CHANGE_HEADING_RE.match(line)),
        len(lines),
    )
    index_text = chr(10).join(lines[:first_body]).replace("|", " ")
    return {
        normalize_change_id(token)
        for token in index_text.split()
        if normalize_change_id(token)
    }


def change_block_semantic_issues(text: str, *, root_index: bool = False) -> list[str]:
    """Validate proposal blocks and their local index.

    A module change file is a self-contained ledger, so every indexed CHG-ID
    must have a body in that file.  The root change file is also the project
    directory, and intentionally indexes module proposals without copying
    their bodies; in that case local bodies must be indexed, while external
    IDs are checked later by ``audit_proposal_integrity``.
    """
    lines = text.splitlines()
    starts = [
        index for index, line in enumerate(lines) if CHANGE_HEADING_RE.match(line)
    ]
    proposal_index_rows = markdown_table_rows(text, "活跃议案索引")
    ledger_mode = (control_values(text).get("governance_mode") or [""])[0]
    heading_ids: list[str] = []
    issues: list[str] = []
    for position, start in enumerate(starts):
        match = CHANGE_HEADING_RE.match(lines[start])
        change_id = normalize_change_id(match.group(1)) if match else ""
        heading_ids.append(change_id)
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block = chr(10).join(lines[start:end])
        values = control_values(block)
        raw_values = control_values_raw(block)
        tier = change_field_tier(values, ledger_mode)
        statuses = values.get("status", [])
        if not statuses:
            issues.append(f"{change_id}:missing-status")
        elif any(status not in CHANGE_STATUSES for status in statuses):
            issues.append(
                f"{change_id}:invalid-status:"
                + ",".join(sorted(set(statuses) - CHANGE_STATUSES))
            )
        effective = values.get("effective", [])
        if not effective or any(value != "false" for value in effective):
            issues.append(f"{change_id}:effective-must-be-false")
        topic_values = raw_values.get("topic_id", [])
        if not topic_values and tier == "personal":
            pass  # RULE-023：personal 档 topic_id 可省
        elif len(topic_values) != 1:
            issues.append(
                f"{change_id}:topic-id-must-appear-once:{len(topic_values)}"
            )
        elif not is_none_like(topic_values[0]) and not normalize_topic_id(
            topic_values[0]
        ):
            issues.append(f"{change_id}:invalid-topic-id:{topic_values[0]}")
        if not has_meaningful_value(values, "changed_by"):
            issues.append(f"{change_id}:missing-changed-by")
        recall_route = (values.get("recall_route") or [""])[0]
        history_retention = (values.get("history_retention") or [""])[0]
        if recall_route in {"medium", "high"} and history_retention in {"compact", "full"}:
            trace = (values.get("intent_traceability") or [""])[0]
            issues.extend(traceability_issues(trace, label=change_id))
        if (
            values.get("governance_mode") == ["collaborative"]
            and (values.get("decision_gate") or [""])[0] == "required"
            and (values.get("status") or [""])[0] == "verifying"
        ):
            execution_ref = (values.get("governance_execution_ref") or [""])[0]
            if not has_meaningful_value(values, "governance_execution_ref"):
                issues.append(f"{change_id}:collaborative-high-risk-needs-governance-execution-ref")
            elif not any(
                token.casefold().startswith(prefix)
                for token in re.split(r"[;,]", execution_ref)
                for prefix in ("pr:", "ci:", "approval:")
            ):
                issues.append(f"{change_id}:governance-execution-ref-needs-pr-ci-or-approval")
        issues.extend(change_lifecycle_issues(change_id, values, raw_values, tier=tier))
        if "blocked" in statuses:
            if "开放问题" not in block:
                issues.append(f"{change_id}:blocked-needs-open-question")
            for field in (
                "blocked_by",
                "next_action",
                "unblock_condition",
                "owner",
                "review_due",
            ):
                if not has_meaningful_value(values, field):
                    issues.append(f"{change_id}:blocked-needs-{field}")
            review_due = (values.get("review_due") or [""])[0]
            try:
                if date.fromisoformat(review_due) < date.today():
                    issues.append(f"{change_id}:blocked-review-due-expired")
            except ValueError:
                issues.append(f"{change_id}:blocked-review-due-must-be-date")

        matching_index_rows = [
            row
            for row in proposal_index_rows
            if normalize_change_id(row.get("change_id", "")) == change_id
        ]
        if not matching_index_rows:
            issues.append(f"{change_id}:missing-from-index")
        else:
            if len(matching_index_rows) != 1:
                issues.append(f"{change_id}:duplicate-index-rows")
            index_row = matching_index_rows[0]
            index_status = index_row.get("status", "").strip().casefold()
            if statuses and index_status and statuses[0] != index_status:
                issues.append(
                    f"{change_id}:index-status-mismatch:{index_status}!={statuses[0]}"
                )
            for key in ("scope", "owner"):
                value = (values.get(key) or [""])[0]
                indexed_value = index_row.get(key, "").strip().casefold()
                if has_meaningful_value(values, key) and value != indexed_value:
                    issues.append(f"{change_id}:index-{key}-mismatch")

    duplicates = sorted(
        change_id for change_id in set(heading_ids) if heading_ids.count(change_id) > 1
    )
    if duplicates:
        issues.append("duplicate-change-ids:" + ",".join(duplicates))

    indexed_ids = change_index_ids(text)

    values = control_values(text)

    def validate_count(field: str, expected_count: int) -> None:
        declared = (values.get(field) or [""])[0]
        if declared == "none":
            if expected_count:
                issues.append(f"{field}-none-but-changes-present")
        elif declared.isdigit():
            if int(declared) != expected_count:
                issues.append(f"{field}-mismatch:{declared}!={expected_count}")
        elif declared:
            issues.append(f"invalid-{field}:" + declared)

    validate_count("active_changes", len(heading_ids))
    if root_index:
        validate_count("active_changes_total", len(indexed_ids))
        validate_count("local_changes", len(heading_ids))

    if root_index:
        # Root may contain index-only module IDs; local proposal bodies still
        # must be represented in the root index.
        missing = sorted(set(heading_ids) - indexed_ids)
        if missing:
            issues.append("ids-missing-from-index:" + ",".join(missing))
    elif set(heading_ids) != indexed_ids:
        missing = sorted(set(heading_ids) - indexed_ids)
        extra = sorted(indexed_ids - set(heading_ids))
        if missing:
            issues.append("ids-missing-from-index:" + ",".join(missing))
        if extra:
            issues.append("index-ids-without-body:" + ",".join(extra))

    return sorted(set(issues))


# ---------------------------------------------------------------------------
# RULE-018/023：一法多议案——跨账本目标规则冲突与旧议案基线失效（VER-20260904-001）
# ---------------------------------------------------------------------------

_RULE_TOKEN_RE = re.compile(r"\bRULE-[A-Z0-9][A-Z0-9-]*\b", re.IGNORECASE)
_PROPOSED_SECTION_RE = re.compile(r"^###\s+拟议制度\s*$(.*?)(?=^###\s|\Z)", re.MULTILINE | re.DOTALL)


def _block_rule_targets(raw_values: dict[str, list[str]]) -> set[str]:
    """CHG 明确声明要改的规则：只认 authority_surfaces 里的 RULE-ID（方案 A，避免顺带引用误报）。"""
    targets: set[str] = set()
    for item in relationship_items(raw_values, "authority_surfaces"):
        for match in _RULE_TOKEN_RE.findall(item):
            targets.add(match.upper())
    return targets


def _block_date(values: dict[str, list[str]]) -> str:
    """议案立案/最近变动日期：取 created 与 last_status_change 中较晚且合法的一个。"""
    dates = [
        value
        for key in ("created", "last_status_change")
        for value in values.get(key, [])
        if is_iso_date(value)
    ]
    return max(dates) if dates else ""


def cross_ledger_rule_conflicts(
    blocks_by_ledger: dict[str, dict[str, str]], rule_dates: dict[str, str]
) -> list[str]:
    """一法多议案：跨全部账本比对目标规则，并检查旧议案的基线是否已被新法推翻。

    - ``shared-rule-target-needs-explicit-conflict``：两个活跃 CHG（不同账本）的
      authority_surfaces 指向同一 RULE 却未互写 conflicts_with。同账本重叠由
      ``change_coordination_issues`` 的 unmarked-authority-surface-overlap 报告。
    - ``rule-changed-after-proposal``：目标规则的 last_reviewed 晚于 CHG 的
      created/last_status_change——规则在议案之后被改过，须重核 based_on
      （references/change-lifecycle.md 第 3 步），否则旧议案会带着失效基线生效。
    - ``mentions-rule-without-authority-surfaces``：拟议制度提到 RULE 却没有声明
      authority_surfaces，冲突检测对它不可见。
    不按治理模式分档：personal 只需多写一行 ``authority_surfaces: RULE-xxx``。
    """
    issues: list[str] = []
    entries: list[tuple[str, str, set[str], set[str], str]] = []
    for ledger, blocks in blocks_by_ledger.items():
        for change_id, block in blocks.items():
            values = control_values(block)
            raw_values = control_values_raw(block)
            targets = _block_rule_targets(raw_values)
            conflict_ids = {
                normalize_change_id(item)
                for item in relationship_items(raw_values, "conflicts_with")
                if normalize_change_id(item)
            }
            if not targets:
                proposed = _PROPOSED_SECTION_RE.search(block)
                mentioned = sorted(
                    {match.upper() for match in _RULE_TOKEN_RE.findall(proposed.group(1))}
                ) if proposed else []
                if mentioned:
                    issues.append(
                        f"{change_id}:mentions-rule-without-authority-surfaces:" + ",".join(mentioned)
                    )
            change_date = _block_date(values)
            if change_date:
                for rule_id in sorted(targets):
                    rule_date = rule_dates.get(rule_id, "")
                    if is_iso_date(rule_date) and rule_date > change_date:
                        issues.append(
                            f"{change_id}:rule-changed-after-proposal:{rule_id}:{rule_date}>{change_date}"
                        )
            entries.append((ledger, change_id, targets, conflict_ids, change_date))

    for index, (ledger_a, id_a, targets_a, conflicts_a, _) in enumerate(entries):
        for ledger_b, id_b, targets_b, conflicts_b, _ in entries[index + 1:]:
            if ledger_a == ledger_b:
                continue
            shared = sorted(targets_a & targets_b)
            if shared and (id_b not in conflicts_a or id_a not in conflicts_b):
                issues.append(
                    f"{id_a}:shared-rule-target-needs-explicit-conflict:{id_b}:" + ",".join(shared)
                )
    return sorted(set(issues))
