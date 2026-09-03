"""单份 logic 文档的语义检查与 ModuleAudit 聚合。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from datetime import date
from dataclasses import asdict, dataclass
from pathlib import Path
from .constants import (
    ADR_STATUSES,
    CHANGE_STATUSES,
    CONTROL_RE,
    COORDINATION_ROLES,
    CURRENT_HISTORY_ROOT,
    DECISION_RECORD_POLICIES,
    FINAL_DECISION_STATES,
    FINAL_SEMANTIC_REVIEW_STATES,
    GOVERNANCE_MODES,
    HEADING_RE,
    INTENT_STATUSES,
    LAYERS,
    MEMBERSHIP_STATUSES,
    MODULE_DOC_POLICIES,
    POSITIVE_INTEGER_RE,
    README_STATUSES,
    REQUIRED_CHANGE_FIELDS,
    REQUIRED_CHANGE_FIELDS_V2,
    REQUIRED_CHANGE_FIELDS_V2_ROOT,
    REQUIRED_CHANGE_SECTIONS,
    REQUIRED_CHANGE_SECTIONS_V2,
    REQUIRED_README_FIELDS,
    REQUIRED_README_FIELDS_V2,
    REQUIRED_README_FIELDS_V2_ROOT,
    REQUIRED_README_SECTIONS,
    REQUIRED_README_SECTIONS_V2,
    REQUIRED_README_SECTIONS_V2_ROOT,
    SCOPE_TYPES,
    TEMP_STATES,
    TEST_LEVELS,
    VERSION_ID_RE,
    VERSION_SLUG_RE,
    VERSION_STATUSES,
)
from .textutil import (
    contains_angle_placeholder,
    control_values,
    control_values_raw,
    has_lifecycle_trigger,
    has_meaningful_value,
    inspect_markdown,
    is_iso_date,
    is_none_like,
    is_within,
    markdown_section_text,
    markdown_table_rows,
    normalize_scope_path,
    read_text,
)
from .fsclassify import (
    is_generated_file,
    is_runtime_data_file,
    is_source_file,
    is_test_file,
    looks_like_runtime_data_directory,
)
from .changes import (
    change_block_semantic_issues,
    governance_evidence_issues,
    review_freshness_issues,
    traceability_issues,
)

@dataclass
class ModuleAudit:
    path: str
    has_source_files: bool
    has_runtime_data: bool
    has_test_files: bool
    has_generated_files: bool
    logic_readme: bool
    logic_change: bool
    change_without_readme: bool
    missing_readme_sections: list[str]
    missing_readme_fields: list[str]
    missing_change_sections: list[str]
    missing_change_fields: list[str]
    semantic_issues: list[str]
    broken_links: list[str]
    v2_issues: list[str]
    module_binding_issues: list[str]


def semantic_issues(path: Path, kind: str, *, root: Path | None = None) -> list[str]:
    text, error = read_text(path)
    if error:
        return [f"unreadable:{error}"]

    values = control_values(text)
    issues: list[str] = []

    if kind == "readme":
        invalid = sorted(set(values.get("status", [])) - README_STATUSES)
        if invalid:
            issues.append("invalid-readme-status:" + ",".join(invalid))
        governance_modes = values.get("governance_mode", [])
        invalid_governance_modes = sorted(
            set(governance_modes) - GOVERNANCE_MODES
        )
        if invalid_governance_modes:
            issues.append(
                "invalid-governance-mode:" + ",".join(invalid_governance_modes)
            )
        if governance_modes == ["collaborative"] and not has_meaningful_value(
            values, "governance_ref"
        ):
            issues.append("collaborative-governance-needs-control-ref")
        issues.extend(
            governance_evidence_issues(values, label="logic_readme")
        )
        last_verified = (values.get("last_verified") or [""])[0]
        review_trigger = (values.get("review_trigger") or [""])[0]
        issues.extend(
            review_freshness_issues(
                last_verified, review_trigger, label="logic_readme"
            )
        )
        if "transitional" in values.get("status", []) and (
            "结束条件" not in text and "end_condition" not in text
        ):
            issues.append("transitional-needs-end-condition")
        if "transitional" in values.get("status", []):
            end_lines = [
                line
                for line in text.splitlines()
                if "结束条件" in line or "end_condition" in line
            ]
            if not end_lines or any("<" in line or "..." in line for line in end_lines):
                issues.append("transitional-end-condition-is-placeholder")
        for key, allowed in (
            ("membership", MEMBERSHIP_STATUSES),
            ("scope_type", SCOPE_TYPES),
            ("layer", LAYERS),
            ("module_doc_policy", MODULE_DOC_POLICIES),
        ):
            invalid_values = sorted(set(values.get(key, [])) - allowed)
            if invalid_values:
                issues.append(f"invalid-{key}:" + ",".join(invalid_values))
        for index, row in enumerate(markdown_table_rows(text, "测试与验证"), start=1):
            test_level = row.get("test_level", "").strip().casefold()
            if test_level not in TEST_LEVELS:
                issues.append(
                    f"test-row-{index}-invalid-test-level:{test_level or 'empty'}"
                )
    elif kind == "change":
        roles = {
            role.strip()
            for value in values.get("coordination_roles", [])
            for role in value.split(",")
            if role.strip()
        }
        invalid_roles = sorted(roles - COORDINATION_ROLES)
        if invalid_roles:
            issues.append("invalid-coordination-roles:" + ",".join(invalid_roles))
        invalid = sorted(set(values.get("status", [])) - CHANGE_STATUSES)
        if invalid:
            issues.append("invalid-change-status:" + ",".join(invalid))
        governance_modes = values.get("governance_mode", [])
        invalid_governance_modes = sorted(
            set(governance_modes) - GOVERNANCE_MODES
        )
        if invalid_governance_modes:
            issues.append(
                "invalid-governance-mode:" + ",".join(invalid_governance_modes)
            )
        if governance_modes == ["collaborative"] and not has_meaningful_value(
            values, "governance_ref"
        ):
            issues.append("collaborative-governance-needs-control-ref")
        issues.extend(
            governance_evidence_issues(values, label="logic_change")
        )
        invalid_intent_statuses = sorted(
            set(values.get("intent_status", [])) - INTENT_STATUSES
        )
        if invalid_intent_statuses:
            issues.append(
                "invalid-intent-status:" + ",".join(invalid_intent_statuses)
            )
        for value in values.get("intent_distilled_at", []):
            if not is_iso_date(value):
                issues.append("intent-distilled-at-must-be-date")
        effective_values = values.get("effective", [])
        if any(value != "false" for value in effective_values):
            issues.append("change-must-mark-effective-false")
        active_count = values.get("active_changes", [])
        is_root_index = root is not None and path == root / "logic_change.md"
        # A root change file may contain index-only rows for module proposals;
        # those rows have no per-block `effective` metadata in this file.  The
        # template's file-level rule still declares them non-effective, while
        # each module body is checked independently below.
        if (
            active_count
            and active_count[0] != "none"
            and not effective_values
            and not is_root_index
        ):
            issues.append("active-change-missing-effective-marker")
        issues.extend(
            change_block_semantic_issues(
                text,
                root_index=(root is not None and path == root / "logic_change.md"),
            )
        )
    elif kind == "version":
        invalid = sorted(set(values.get("status", [])) - VERSION_STATUSES)
        if invalid:
            issues.append("invalid-version-status:" + ",".join(invalid))
        if any(value != "true" for value in values.get("immutable", [])):
            issues.append("version-must-mark-immutable-true")
        if "correction" in values.get("status", []) and not has_meaningful_value(
            values, "corrects"
        ):
            issues.append("correction-needs-corrects")
        version_ids = values.get("version_id", [])
        if version_ids and any(
            not VERSION_ID_RE.fullmatch(value) for value in version_ids
        ):
            issues.append("invalid-version-id")
        slugs = values.get("version_slug", [])
        if slugs and any(not VERSION_SLUG_RE.fullmatch(value) for value in slugs):
            issues.append("invalid-version-slug")
        change_ids = values.get("change_id", [])
        has_change = any(
            value not in {"", "none", "unknown", "n/a"} for value in change_ids
        )
        governance_mode = (values.get("governance_mode") or [""])[0]
        governance_ref = (values.get("governance_ref") or [""])[0]
        changed_by = (values.get("changed_by") or [""])[0]
        if governance_mode not in GOVERNANCE_MODES:
            issues.append("invalid-version-governance-mode")
        if not has_meaningful_value(values, "governance_ref"):
            issues.append("version-needs-governance-ref")
        issues.extend(
            governance_evidence_issues(
                values,
                label="version",
                collaborative_required=governance_mode == "collaborative",
            )
        )
        if has_change and is_none_like(changed_by):
            issues.append("change-version-needs-changed-by")
        if has_change and not has_meaningful_value(values, "proposal_commit_or_blob"):
            issues.append("change-id-needs-proposal-commit-or-blob")
        proposal_revision = (values.get("proposal_revision") or [""])[0]
        decision_record = (values.get("decision_record") or [""])[0]
        decision_state = (values.get("decision_state") or [""])[0]
        confirmed_revision = (values.get("confirmed_proposal_revision") or [""])[0]
        decision_confirmed_by = (values.get("decision_confirmed_by") or [""])[0]
        decision_ref = (values.get("decision_ref") or [""])[0]
        decision_confirmed_at = (values.get("decision_confirmed_at") or [""])[0]
        semantic_review_state = (values.get("semantic_review_state") or [""])[0]
        semantic_reviewed_by = (values.get("semantic_reviewed_by") or [""])[0]
        semantic_review_ref = (values.get("semantic_review_ref") or [""])[0]
        semantic_reviewed_at = (values.get("semantic_reviewed_at") or [""])[0]
        if decision_record not in DECISION_RECORD_POLICIES:
            issues.append("invalid-decision-record-policy")
        if decision_state not in FINAL_DECISION_STATES:
            issues.append("invalid-final-decision-state")
        if semantic_review_state not in FINAL_SEMANTIC_REVIEW_STATES:
            issues.append("invalid-final-semantic-review-state")
        intent_status = (values.get("intent_status") or [""])[0]
        if intent_status and intent_status not in INTENT_STATUSES:
            issues.append("invalid-final-intent-status")
        intent_distilled_at = (values.get("intent_distilled_at") or [""])[0]
        if intent_distilled_at and not is_iso_date(intent_distilled_at):
            issues.append("final-intent-distilled-at-must-be-date")
        topic_id = (values.get("topic_id") or [""])[0]
        if not is_none_like(topic_id):
            for field in (
                "topic_shared_context",
                "topic_shared_constraints",
                "topic_discussion_refs",
                "topic_final_conclusion",
            ):
                if not has_meaningful_value(values, field):
                    issues.append(f"topic-version-needs-{field}")
        if has_change:
            trace = (values.get("intent_traceability") or [""])[0]
            issues.extend(traceability_issues(trace, label="version"))
        if has_change and not POSITIVE_INTEGER_RE.fullmatch(proposal_revision):
            issues.append("change-id-needs-final-proposal-revision")
        if not has_change and not is_none_like(proposal_revision):
            issues.append("record-without-change-must-mark-proposal-revision-none")
        if (
            (values.get("final_proposal_snapshot") or [""])[0]
            != "embedded"
        ):
            issues.append("final-proposal-snapshot-must-be-embedded")
        if decision_record == "required":
            for field in (
                "intent_source_refs",
                "intent_digest",
                "intent_status",
                "intent_distilled_by",
                "intent_distilled_at",
                "snapshot_source",
                "decision_confirmation",
                "current_behavior",
                "proposed_rule",
                "selected_option",
                "alternatives_and_tradeoffs",
                "decision_why",
                "scope_and_consumers",
                "compatibility_and_exit",
                "acceptance_and_rollback",
                "semantic_review_conclusion",
            ):
                value = (values.get(field) or [""])[0]
                if is_none_like(value) or value == "not-required":
                    issues.append(f"required-decision-record-needs-{field}")
            if decision_state == "confirmed":
                if confirmed_revision != proposal_revision:
                    issues.append("final-confirmed-revision-mismatch")
                if not POSITIVE_INTEGER_RE.fullmatch(confirmed_revision):
                    issues.append("invalid-final-confirmed-proposal-revision")
                if is_none_like(decision_confirmed_by):
                    issues.append("final-confirmed-decision-needs-confirmed-by")
                if is_none_like(decision_ref):
                    issues.append("final-confirmed-decision-needs-decision-ref")
                if not is_iso_date(decision_confirmed_at):
                    issues.append("final-decision-confirmed-at-must-be-date")
            elif decision_state == "not-confirmed":
                for field, value in (
                    ("confirmed_proposal_revision", confirmed_revision),
                    ("decision_confirmed_by", decision_confirmed_by),
                    ("decision_ref", decision_ref),
                    ("decision_confirmed_at", decision_confirmed_at),
                ):
                    if not is_none_like(value):
                        issues.append(f"final-not-confirmed-decision-needs-{field}-none")
            elif decision_state == "not-required":
                issues.append("required-decision-record-cannot-be-not-required")
        if semantic_review_state in {"passed", "failed"}:
            if is_none_like(semantic_reviewed_by):
                issues.append("final-semantic-review-needs-reviewed-by")
            if is_none_like(semantic_review_ref):
                issues.append("final-semantic-review-needs-review-ref")
            if not is_iso_date(semantic_reviewed_at):
                issues.append("final-semantic-reviewed-at-must-be-date")
        elif semantic_review_state == "not-applicable":
            for field, value in (
                ("semantic_reviewed_by", semantic_reviewed_by),
                ("semantic_review_ref", semantic_review_ref),
                ("semantic_reviewed_at", semantic_reviewed_at),
            ):
                if not is_none_like(value):
                    issues.append(f"not-applicable-semantic-review-needs-{field}-none")
        if "effective" in values.get("status", []) and decision_record == "required":
            if decision_state != "confirmed":
                issues.append("effective-decision-record-needs-confirmed-decision")
            if semantic_review_state != "passed":
                issues.append("effective-decision-record-needs-passed-semantic-review")
        if (
            governance_mode == "collaborative"
            and decision_record == "required"
            and semantic_review_state == "passed"
            and (
                semantic_reviewed_by == "self"
                or semantic_reviewed_by == changed_by
            )
        ):
            issues.append("collaborative-high-risk-review-must-be-independent")
        result_anchored_statuses = {"effective", "rolled-back", "correction"}
        if result_anchored_statuses.intersection(
            values.get("status", [])
        ) and not has_meaningful_value(values, "after_commit"):
            issues.append("completed-version-needs-result-revision")
        verification_values = values.get("rollback_or_restore_verified", [])
        verification_token = ""
        verification_evidence = ""
        if len(verification_values) == 1:
            match = re.match(
                r"^(yes|no|not-applicable)(?:\b|$)",
                verification_values[0],
            )
            if match:
                verification_token = match.group(1)
                verification_evidence = verification_values[0][match.end() :].strip(
                    " +:;-"
                )
        if not verification_token:
            issues.append("invalid-rollback-or-restore-verification")
        elif verification_token in {"yes", "no"} and not verification_evidence:
            issues.append("rollback-or-restore-verification-needs-evidence")
        if "rolled-back" in values.get("status", []) and verification_token != "yes":
            issues.append("rolled-back-version-needs-verified-restore")
        removal_values = values.get("temporary_structure_removed", [])
        invalid_removal = sorted(set(removal_values) - {"yes", "no", "not-applicable"})
        if invalid_removal:
            issues.append(
                "invalid-temporary-structure-removed:" + ",".join(invalid_removal)
            )
        if "no" in removal_values:
            issues.append("completed-version-cannot-leave-working-temp")
        if "yes" in removal_values and not has_meaningful_value(
            values, "logic_temp_cleanup"
        ):
            issues.append("removed-temp-needs-cleanup-evidence")
    elif kind == "adr":
        invalid = sorted(set(values.get("status", [])) - ADR_STATUSES)
        if invalid:
            issues.append("invalid-adr-status:" + ",".join(invalid))
        invalid_intent_statuses = sorted(
            set(values.get("intent_status", [])) - INTENT_STATUSES
        )
        if invalid_intent_statuses:
            issues.append(
                "invalid-adr-intent-status:" + ",".join(invalid_intent_statuses)
            )
        for value in values.get("intent_distilled_at", []):
            if not is_iso_date(value):
                issues.append("adr-intent-distilled-at-must-be-date")
        confirmed_statuses = {"accepted", "active", "transitional"}
        if "inferred" in values.get(
            "confidence", []
        ) and confirmed_statuses.intersection(values.get("status", [])):
            issues.append("inference-cannot-be-active")
        if confirmed_statuses.intersection(values.get("status", [])):
            if (values.get("intent_status") or [""])[0] == "inferred":
                issues.append("inferred-intent-cannot-be-active-adr")
            if not has_meaningful_value(values, "decision_confirmed_by"):
                issues.append("active-decision-needs-confirmed-by")
            if not has_meaningful_value(values, "decision_ref"):
                issues.append("active-decision-needs-decision-ref")
            confirmed_at = (values.get("decision_confirmed_at") or [""])[0]
            if not is_iso_date(confirmed_at):
                issues.append("active-decision-confirmed-at-must-be-date")
            if values.get("immutable", []) != ["true"]:
                issues.append("active-decision-must-be-immutable")
            change_id = (values.get("change_id") or [""])[0]
            proposal_revision = (values.get("proposal_revision") or [""])[0]
            confirmed_revision = (
                values.get("confirmed_proposal_revision") or [""]
            )[0]
            if not is_none_like(change_id):
                if not POSITIVE_INTEGER_RE.fullmatch(proposal_revision):
                    issues.append("active-decision-needs-proposal-revision")
                if confirmed_revision != proposal_revision:
                    issues.append("active-decision-confirmed-revision-mismatch")
            if not has_meaningful_value(values, "immutable_decision_record"):
                issues.append("active-decision-needs-immutable-record")
        if "transitional" in values.get("status", []) and not has_lifecycle_trigger(
            values, "valid_until"
        ):
            issues.append("transitional-decision-needs-valid-until")
        if "transitional" in values.get("status", []) and not has_lifecycle_trigger(
            values, "review_due"
        ):
            issues.append("transitional-decision-needs-review-date")
    elif kind == "backup":
        sensitive = set(values.get("contains_sensitive_data", []))
        if sensitive - {"yes", "no"}:
            issues.append("invalid-sensitive-data-marker")
    elif kind == "temp":
        invalid = sorted(set(values.get("state", [])) - TEMP_STATES)
        if invalid:
            issues.append("invalid-temp-state:" + ",".join(invalid))
        if any(value != "true" for value in values.get("disposable", [])):
            issues.append("temp-must-be-disposable-true")
        version_ids = values.get("version_id", [])
        if not version_ids or any(
            not VERSION_ID_RE.fullmatch(value) for value in version_ids
        ):
            issues.append("invalid-version-id")
        proposal_revisions = values.get("proposal_revision", [])
        if len(proposal_revisions) != 1 or not POSITIVE_INTEGER_RE.fullmatch(
            proposal_revisions[0] if proposal_revisions else ""
        ):
            issues.append("invalid-proposal-revision")
        slugs = values.get("version_slug", [])
        if not slugs or any(not VERSION_SLUG_RE.fullmatch(value) for value in slugs):
            issues.append("invalid-version-slug")
        expires_values = values.get("expires", [])
        for value in expires_values:
            try:
                date.fromisoformat(value)
            except ValueError:
                issues.append("temp-expires-must-be-date")

    return sorted(set(issues))


def path_reference_issues(path: Path, root: Path, keys: tuple[str, ...]) -> list[str]:
    text, error = read_text(path)
    if error:
        return [f"unreadable:{error}"]
    values = control_values_raw(text)
    issues: list[str] = []
    for key in keys:
        value = (values.get(key) or [""])[0].strip()
        if not value or value.lower() in {"none", "unknown", "n/a"}:
            continue
        value = value.strip("<>")
        candidate = (path.parent / value).resolve()
        if not is_within(candidate, root):
            issues.append(f"{key}-outside-project:{value}")
            continue
        if not candidate.is_file():
            issues.append(f"{key}-not-found:{value}")
        elif candidate.name.lower() != "logic_readme.md":
            issues.append(f"{key}-must-target-logic_readme:{value}")
        elif (
            key == "current_policy"
            and candidate != (path.parent / "logic_readme.md").resolve()
        ):
            issues.append(f"{key}-must-match-scope:{value}")
        elif key == "parent":
            try:
                path.parent.resolve().relative_to(candidate.parent.resolve())
            except ValueError:
                issues.append(f"{key}-must-be-ancestor:{value}")
    return sorted(set(issues))


def placeholder_issues(path: Path) -> list[str]:
    text, error = read_text(path)
    if error:
        return [f"unreadable:{error}"]
    issues: list[str] = []
    for key, value in CONTROL_RE.findall(text):
        normalized = value.strip().lower()
        if (
            contains_angle_placeholder(normalized)
            or normalized.startswith("yyyy")
            or normalized == "..."
        ):
            issues.append(f"placeholder:{key}")
    return sorted(set(issues))


def audit_module(path: Path, files: list[Path], root: Path) -> ModuleAudit:
    readme = path / "logic_readme.md"
    change = path / "logic_change.md"
    readme_sections: list[str] = []
    readme_fields: list[str] = []
    change_sections: list[str] = []
    change_fields: list[str] = []
    semantic: list[str] = []
    broken_links: list[str] = []
    v2_issues: list[str] = []
    module_binding_issues: list[str] = []
    relative = "." if path == root else path.relative_to(root).as_posix()

    if readme.exists():
        readme_sections, readme_fields, links = inspect_markdown(
            readme, root, REQUIRED_README_SECTIONS, REQUIRED_README_FIELDS
        )
        semantic.extend(
            f"logic_readme:{item}"
            for item in semantic_issues(readme, "readme", root=root)
        )
        semantic.extend(f"logic_readme:{item}" for item in placeholder_issues(readme))
        semantic.extend(
            f"logic_readme:{item}"
            for item in path_reference_issues(readme, root, ("parent",))
        )
        broken_links.extend(f"logic_readme:{item}" for item in links)
        required_readme_v2_fields = set(REQUIRED_README_FIELDS_V2)
        if relative == ".":
            required_readme_v2_fields |= REQUIRED_README_FIELDS_V2_ROOT
        required_readme_v2_sections = set(REQUIRED_README_SECTIONS_V2)
        if relative == ".":
            required_readme_v2_sections |= REQUIRED_README_SECTIONS_V2_ROOT
        v2_sections, v2_fields, _ = inspect_markdown(
            readme, root, required_readme_v2_sections, required_readme_v2_fields
        )
        v2_issues.extend(f"logic_readme:missing-section:{item}" for item in v2_sections)
        v2_issues.extend(f"logic_readme:missing-field:{item}" for item in v2_fields)
        text, error = read_text(readme)
        if not error:
            document_control = markdown_section_text(text, "文档控制")
            values = control_values(document_control)
            raw_values = control_values_raw(document_control)
            all_values = control_values(text)
            all_raw_values = control_values_raw(text)
            if relative == ".":
                coverage_values = all_values.get("coverage_policy", [])
                if len(coverage_values) != 1 or coverage_values[0] not in {
                    "governed-boundaries",
                    "registry-every-folder",
                }:
                    module_binding_issues.append(
                        "root-invalid-coverage-policy:"
                        + (",".join(coverage_values) or "missing")
                    )
                membership_policy = all_values.get("membership_policy", [])
                if membership_policy != ["root-registry-first"]:
                    module_binding_issues.append(
                        "root-membership-policy-must-be-root-registry-first"
                    )
                if len(
                    all_values.get("layer_policy", [])
                ) != 1 or not has_meaningful_value(all_values, "layer_policy"):
                    module_binding_issues.append("root-layer-policy-must-be-meaningful")
                version_roots = all_raw_values.get("version_root", [])
                if (
                    len(version_roots) != 1
                    or normalize_scope_path(version_roots[0]).casefold()
                    != CURRENT_HISTORY_ROOT.casefold()
                ):
                    module_binding_issues.append(
                        "root-version-root-must-be-logic_version"
                    )
                temp_roots = all_raw_values.get("temp_root", [])
                expected_temp_root = f"{CURRENT_HISTORY_ROOT}/working"
                if (
                    len(temp_roots) != 1
                    or normalize_scope_path(temp_roots[0]).casefold()
                    != expected_temp_root.casefold()
                ):
                    module_binding_issues.append(
                        "root-temp-root-must-be-logic_version-working"
                    )
                for field, expected in (
                    ("membership", "in-system"),
                    ("scope_type", "root"),
                    ("parent", "none"),
                    ("parent_module_id", "none"),
                    ("registry_status", "registered"),
                ):
                    if values.get(field, []) != [expected]:
                        module_binding_issues.append(
                            f"root-{field.replace('_', '-')}-must-be-{expected}"
                        )
            else:
                copied_root_fields = sorted(
                    REQUIRED_README_FIELDS_V2_ROOT.intersection(raw_values)
                )
                for field in copied_root_fields:
                    module_binding_issues.append(
                        f"module-must-inherit-root-only-field:{field}"
                    )
                if markdown_table_rows(text, "范围登记表"):
                    module_binding_issues.append(
                        "module-must-not-copy-root-scope-registry"
                    )
            scope_path = (raw_values.get("scope_path") or [""])[0]
            scope_alias = (raw_values.get("scope") or [""])[0]
            if (
                scope_alias
                and scope_path
                and normalize_scope_path(scope_alias)
                != normalize_scope_path(scope_path)
            ):
                module_binding_issues.append(
                    f"logic_readme:scope-alias-mismatch:{scope_alias}!={scope_path}"
                )
            if scope_path and normalize_scope_path(scope_path) != relative:
                module_binding_issues.append(
                    f"logic_readme:scope_path-mismatch:{scope_path}!={relative}"
                )
            policies = values.get("module_doc_policy", [])
            policy = policies[0] if policies else ""
            if relative == "." and policy and policy != "paired":
                module_binding_issues.append("root-module-doc-policy-must-be-paired")
            if policy == "paired" and not change.exists():
                module_binding_issues.append("paired-policy-missing-logic_change")
            if policy == "readme-only" and change.exists():
                module_binding_issues.append("readme-only-policy-forbids-logic_change")
            if policy == "inherited":
                module_binding_issues.append(
                    "inherited-policy-forbids-local-logic-docs"
                )
            canonical = (raw_values.get("canonical_readme") or [""])[0].strip("<>")
            expected_readme = (
                "logic_readme.md" if relative == "." else f"{relative}/logic_readme.md"
            )
            if canonical.lower() in {"", "none", "unknown"}:
                module_binding_issues.append(
                    "canonical_readme-must-point-to-current-file"
                )
            elif normalize_scope_path(canonical) != expected_readme:
                module_binding_issues.append(f"canonical_readme-mismatch:{canonical}")
            canonical_change = (raw_values.get("canonical_change") or [""])[0].strip(
                "<>"
            )
            expected_change = (
                "logic_change.md" if relative == "." else f"{relative}/logic_change.md"
            )
            if policy == "paired":
                if canonical_change.lower() in {"", "none", "unknown"}:
                    module_binding_issues.append("paired-policy-needs-canonical-change")
                elif normalize_scope_path(canonical_change) != expected_change:
                    module_binding_issues.append(
                        f"canonical_change-mismatch:{canonical_change}"
                    )
            elif policy == "readme-only" and canonical_change.lower() not in {
                "none",
                "n/a",
            }:
                module_binding_issues.append(
                    "readme-only-canonical-change-must-be-none"
                )

    if change.exists():
        change_sections, change_fields, links = inspect_markdown(
            change, root, REQUIRED_CHANGE_SECTIONS, REQUIRED_CHANGE_FIELDS
        )
        semantic.extend(
            f"logic_change:{item}"
            for item in semantic_issues(change, "change", root=root)
        )
        semantic.extend(f"logic_change:{item}" for item in placeholder_issues(change))
        semantic.extend(
            f"logic_change:{item}"
            for item in path_reference_issues(change, root, ("current_policy",))
        )
        broken_links.extend(f"logic_change:{item}" for item in links)
        required_change_v2_fields = set(REQUIRED_CHANGE_FIELDS_V2)
        if relative == ".":
            required_change_v2_fields |= REQUIRED_CHANGE_FIELDS_V2_ROOT
        v2_sections, v2_fields, _ = inspect_markdown(
            change, root, REQUIRED_CHANGE_SECTIONS_V2, required_change_v2_fields
        )
        v2_issues.extend(f"logic_change:missing-section:{item}" for item in v2_sections)
        v2_issues.extend(f"logic_change:missing-field:{item}" for item in v2_fields)
        text, error = read_text(change)
        if not error:
            document_control = markdown_section_text(text, "文档控制")
            change_values = control_values(document_control)
            raw_change_values = control_values_raw(document_control)
            headings = {heading.strip() for heading in HEADING_RE.findall(text)}
            linked_roots = change_values.get("linked_root_changes", [])
            if (
                relative != "."
                and any(
                    value not in {"", "none", "unknown", "n/a"}
                    for value in linked_roots
                )
                and not any("关联根议案" in heading for heading in headings)
            ):
                v2_issues.append("logic_change:linked-root-needs-link-section")
            scope_path = (raw_change_values.get("scope_path") or [""])[0]
            scope_alias = (raw_change_values.get("scope") or [""])[0]
            if (
                scope_alias
                and scope_path
                and normalize_scope_path(scope_alias)
                != normalize_scope_path(scope_path)
            ):
                module_binding_issues.append(
                    f"logic_change:scope-alias-mismatch:{scope_alias}!={scope_path}"
                )
            if scope_path and normalize_scope_path(scope_path) != relative:
                module_binding_issues.append(
                    f"logic_change:scope_path-mismatch:{scope_path}!={relative}"
                )
            if readme.exists():
                readme_text, _ = read_text(readme)
                readme_values = control_values(readme_text)
                readme_id = (readme_values.get("module_id") or [""])[0]
                change_id = (change_values.get("module_id") or [""])[0]
                if readme_id and change_id and readme_id != change_id:
                    module_binding_issues.append(
                        f"module_id-mismatch:{readme_id}!={change_id}"
                    )

    return ModuleAudit(
        path=relative,
        has_source_files=any(is_source_file(file) for file in files),
        has_runtime_data=(
            any(is_runtime_data_file(file) for file in files)
            or looks_like_runtime_data_directory(path, root)
        ),
        has_test_files=any(is_test_file(file, root) for file in files),
        has_generated_files=any(is_generated_file(file) for file in files),
        logic_readme=readme.exists(),
        logic_change=change.exists(),
        change_without_readme=change.exists() and not readme.exists(),
        missing_readme_sections=readme_sections,
        missing_readme_fields=readme_fields,
        missing_change_sections=change_sections,
        missing_change_fields=change_fields,
        semantic_issues=sorted(set(semantic)),
        broken_links=sorted(set(broken_links)),
        v2_issues=sorted(set(v2_issues)),
        module_binding_issues=sorted(set(module_binding_issues)),
    )
