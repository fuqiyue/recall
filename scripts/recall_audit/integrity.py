"""范围路由、议案完整性与 current-state 静态门。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from .constants import (
    CURRENT_CHANGE_FIELDS,
    CURRENT_CHANGE_SECTIONS,
    CURRENT_POLICY_HEADERS,
    CURRENT_README_FIELDS,
    CURRENT_README_SECTIONS,
    DECISION_AUTHORITY_STATUSES,
    GOVERNANCE_MODES,
    MARKDOWN_LINK_RE,
    MEMBERSHIP_STATUSES,
    MODULE_DOC_POLICIES,
)
from .textutil import (
    actual_case_relative,
    cell_link_parts,
    cell_link_target,
    change_affected_scopes,
    change_blocks,
    control_values,
    control_values_raw,
    has_meaningful_value,
    inspect_markdown,
    is_immutable_decision_record_link,
    is_iso_date,
    is_none_like,
    is_scope_ancestor,
    is_within,
    markdown_section_text,
    markdown_table_headers,
    markdown_table_rows,
    normalize_authority_id,
    normalize_change_id,
    normalize_scope_path,
    normalize_topic_id,
    read_text,
    scope_parts,
    split_control_list,
)
from .changes import (
    change_coordination_issues,
    change_heading_ids,
    change_index_ids,
    governance_evidence_issues,
    review_freshness_issues,
)
from .semantic import (
    ModuleAudit,
)

def audit_module_routes(root: Path, audits: list[ModuleAudit]) -> dict:
    root_readme = root / "logic_readme.md"
    if not root_readme.is_file():
        return {
            "rows": [],
            "route_issues": ["missing-root-logic_readme"],
            "duplicate_module_ids": [],
            "duplicate_scope_paths": [],
            "unregistered_governance_dirs": [],
            "hierarchy_issues": [],
        }

    root_text, error = read_text(root_readme)
    if error:
        return {
            "rows": [],
            "route_issues": [f"unreadable-root-logic_readme:{error}"],
            "duplicate_module_ids": [],
            "duplicate_scope_paths": [],
            "unregistered_governance_dirs": [],
            "hierarchy_issues": [],
        }

    rows = markdown_table_rows(root_text, "范围登记表")
    route_issues: list[str] = []
    module_ids: dict[str, list[str]] = {}
    scope_paths: dict[str, list[str]] = {}
    registered_scopes: set[str] = set()
    root_rows = 0

    audits_by_scope = {audit.path: audit for audit in audits}

    def nearest_documented_parent(scope: str) -> str | None:
        candidates = [
            audit.path
            for audit in audits
            if audit.logic_readme and is_scope_ancestor(audit.path, scope)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: len(scope_parts(item)))

    for row in rows:
        module_id = row.get("module_id", "").strip().lower()
        scope_value = normalize_scope_path(row.get("scope_path", ""))
        membership = row.get("membership", "").strip().lower()
        doc_policy = row.get("doc_policy", "paired").strip().lower()
        owner = row.get("owner", "").strip()
        if not module_id or "<" in module_id or "..." in module_id:
            route_issues.append("route-row-missing-module_id")
            continue
        if not scope_value or "<" in scope_value or "..." in scope_value:
            route_issues.append(f"{module_id}:route-row-missing-scope_path")
            continue
        module_ids.setdefault(module_id, []).append(scope_value)
        scope_paths.setdefault(scope_value.casefold(), []).append(module_id)
        registered_scopes.add(scope_value)

        if (
            not owner
            or owner.casefold() in {"none", "unknown", "n/a", "..."}
            or "<" in owner
            or ">" in owner
        ):
            route_issues.append(f"{module_id}:route-row-missing-owner")

        if not membership:
            route_issues.append(f"{module_id}:route-row-missing-membership")
        elif membership not in MEMBERSHIP_STATUSES:
            route_issues.append(f"{module_id}:invalid-membership:{membership}")
        if doc_policy not in MODULE_DOC_POLICIES:
            route_issues.append(f"{module_id}:invalid-doc-policy:{doc_policy}")
        resolved_scope = actual_case_relative(root, scope_value)
        if resolved_scope is None:
            route_issues.append(f"{module_id}:scope-not-found:{scope_value}")
            continue
        scope_dir, actual_scope = resolved_scope
        if actual_scope != scope_value:
            route_issues.append(
                f"{module_id}:scope-case-mismatch:{scope_value}!={actual_scope}"
            )

        if scope_value == ".":
            root_rows += 1
            if membership != "in-system" or doc_policy != "paired":
                route_issues.append("root-route-must-be-in-system-paired")
        elif membership == "in-system" and doc_policy == "paired":
            # 非根模块可 inherited（默认）或 readme-only（经确认拆分的子文档）。
            # paired 仅限根：logic_change 全项目唯一（INV-002）。
            route_issues.append(f"{module_id}:paired-policy-root-only")

        local_readme = scope_dir / "logic_readme.md"
        local_change = scope_dir / "logic_change.md"
        parent_scope = nearest_documented_parent(actual_scope)
        parent_audit = audits_by_scope.get(parent_scope) if parent_scope else None

        if doc_policy == "paired":
            if not local_readme.is_file():
                route_issues.append(f"{module_id}:paired-missing-local-readme")
            if not local_change.is_file():
                route_issues.append(f"{module_id}:paired-missing-local-change")
        elif doc_policy == "readme-only":
            if not local_readme.is_file():
                route_issues.append(f"{module_id}:readme-only-missing-local-readme")
            if local_change.exists():
                route_issues.append(f"{module_id}:readme-only-forbids-local-change")
        elif doc_policy == "inherited":
            if local_readme.exists() or local_change.exists():
                route_issues.append(f"{module_id}:inherited-forbids-local-logic-docs")
            if membership == "in-system" and parent_scope is None:
                route_issues.append(f"{module_id}:inherited-needs-governance-parent")

        local_prefix = "" if actual_scope == "." else actual_scope + "/"
        expected_targets: dict[str, str | None]
        if doc_policy == "paired":
            expected_targets = {
                "logic_readme": local_prefix + "logic_readme.md",
                "logic_change": local_prefix + "logic_change.md",
            }
        elif doc_policy == "readme-only":
            expected_targets = {
                "logic_readme": local_prefix + "logic_readme.md",
                "logic_change": None,
            }
        else:
            parent_prefix = (
                ""
                if parent_scope == "."
                else ((parent_scope + "/") if parent_scope else "")
            )
            expected_targets = {
                "logic_readme": (
                    parent_prefix + "logic_readme.md" if parent_scope else None
                ),
                "logic_change": (
                    parent_prefix + "logic_change.md"
                    if parent_scope and parent_audit and parent_audit.logic_change
                    else None
                ),
            }

        for column, expected_name in (
            ("logic_readme", "logic_readme.md"),
            ("logic_change", "logic_change.md"),
        ):
            cell = row.get(column, "")
            target, fragment = cell_link_parts(cell)
            declared_none = cell.strip().strip("`").lower() in {"", "none", "n/a"}
            expected_target = expected_targets.get(column)
            if not target:
                if not declared_none:
                    route_issues.append(f"{module_id}:{column}-must-be-markdown-link")
                required = expected_target is not None and (
                    doc_policy in {"paired", "readme-only"} or membership == "in-system"
                )
                if required:
                    route_issues.append(f"{module_id}:missing-{column}-link")
                continue
            if expected_target is None:
                route_issues.append(f"{module_id}:{column}-must-be-none")
                continue
            if normalize_scope_path(target) != normalize_scope_path(expected_target):
                route_issues.append(
                    f"{module_id}:{column}-route-mismatch:{target}!={expected_target}"
                )
            target_path = (root_readme.parent / target).resolve()
            if not is_within(target_path, root):
                route_issues.append(f"{module_id}:{column}-outside-project:{target}")
                continue
            if not target_path.is_file():
                route_issues.append(f"{module_id}:{column}-not-found:{target}")
                continue
            if target_path.name.lower() != expected_name:
                route_issues.append(f"{module_id}:{column}-wrong-name:{target}")
            if (
                column == "logic_readme"
                and scope_value != "."
                and membership == "in-system"
                and doc_policy == "inherited"
            ):
                if not fragment:
                    route_issues.append(
                        f"{module_id}:logic_readme-route-needs-scope-anchor"
                    )
                else:
                    target_text, target_error = read_text(target_path)
                    explicit_anchor = f'<a id="{fragment.casefold()}"></a>'
                    if target_error or explicit_anchor not in target_text.casefold():
                        route_issues.append(
                            f"{module_id}:logic_readme-scope-anchor-not-found:{fragment}"
                        )
            target_text, target_error = read_text(target_path)
            if not target_error and doc_policy != "inherited":
                values = control_values(target_text)
                raw_values = control_values_raw(target_text)
                target_id = (values.get("module_id") or [""])[0]
                if target_id and target_id != module_id:
                    route_issues.append(
                        f"{module_id}:{column}-module-id-mismatch:{target_id}"
                    )
                raw_target_scope = (raw_values.get("scope_path") or [""])[0]
                target_scope = normalize_scope_path(raw_target_scope)
                if raw_target_scope and target_scope != actual_scope:
                    route_issues.append(
                        f"{module_id}:{column}-scope-mismatch:{target_scope}!={actual_scope}"
                    )
                if column == "logic_readme":
                    target_membership = (values.get("membership") or [""])[0]
                    target_policy = (values.get("module_doc_policy") or [""])[0]
                    if target_membership and target_membership != membership:
                        route_issues.append(
                            f"{module_id}:membership-mismatch:{target_membership}!={membership}"
                        )
                    if target_policy and target_policy != doc_policy:
                        route_issues.append(
                            f"{module_id}:doc-policy-mismatch:{target_policy}!={doc_policy}"
                        )

    duplicate_module_ids = sorted(
        f"{module_id}:{','.join(scopes)}"
        for module_id, scopes in module_ids.items()
        if len(scopes) > 1
    )
    duplicate_scope_paths = sorted(
        f"{scope}:{','.join(ids)}" for scope, ids in scope_paths.items() if len(ids) > 1
    )

    documented_scopes = {
        audit.path for audit in audits if audit.path != "." and audit.logic_readme
    }
    unregistered = sorted(documented_scopes - registered_scopes)

    docs_by_id: dict[str, tuple[str, dict[str, list[str]], dict[str, list[str]]]] = {}
    for audit in audits:
        if not audit.logic_readme:
            continue
        directory = root if audit.path == "." else root / audit.path
        text_value, text_error = read_text(directory / "logic_readme.md")
        if text_error:
            continue
        values = control_values(text_value)
        raw_values = control_values_raw(text_value)
        module_id = (values.get("module_id") or [""])[0]
        if module_id:
            docs_by_id[module_id] = (audit.path, values, raw_values)

    hierarchy_issues: list[str] = []
    for module_id, (scope, values, raw_values) in docs_by_id.items():
        if scope == ".":
            continue
        parent_id = (values.get("parent_module_id") or [""])[0]
        candidates = [
            (other_scope, other_id)
            for other_id, (other_scope, _, _) in docs_by_id.items()
            if other_scope != scope and (is_scope_ancestor(other_scope, scope))
        ]
        if not candidates:
            hierarchy_issues.append(f"{module_id}:no-governance-parent")
            continue
        nearest_scope, nearest_id = max(
            candidates,
            key=lambda item: 0 if item[0] == "." else len(Path(item[0]).parts),
        )
        if parent_id and parent_id != nearest_id:
            hierarchy_issues.append(
                f"{module_id}:parent-module-mismatch:{parent_id}!={nearest_id}"
            )
        parent_ref = (raw_values.get("parent") or [""])[0].strip("<>")
        scope_dir = root / scope
        expected_parent_path = (
            root / "logic_readme.md"
            if nearest_scope == "."
            else root / nearest_scope / "logic_readme.md"
        ).resolve()
        actual_parent_path = (scope_dir / parent_ref).resolve() if parent_ref else None
        expected_parent_relative = expected_parent_path.relative_to(root).as_posix()
        declared_parent_relative = (
            actual_parent_path.relative_to(root).as_posix()
            if actual_parent_path is not None and is_within(actual_parent_path, root)
            else ""
        )
        if actual_parent_path is not None and (
            actual_parent_path != expected_parent_path
            or declared_parent_relative != expected_parent_relative
        ):
            hierarchy_issues.append(
                f"{module_id}:parent-path-mismatch:{parent_ref}!={expected_parent_relative}"
            )

    if not rows:
        route_issues.append("missing-or-empty-root-scope-registry-table")
    elif root_rows != 1:
        route_issues.append(f"root-route-row-count-must-be-one:{root_rows}")

    return {
        "rows": rows,
        "route_issues": sorted(set(route_issues)),
        "duplicate_module_ids": duplicate_module_ids,
        "duplicate_scope_paths": duplicate_scope_paths,
        "unregistered_governance_dirs": unregistered,
        "hierarchy_issues": sorted(set(hierarchy_issues)),
    }


def audit_proposal_integrity(root: Path, audits: list[ModuleAudit]) -> dict:
    ids_by_scope: dict[str, list[str]] = {}
    texts_by_scope: dict[str, str] = {}
    for audit in audits:
        if not audit.logic_change:
            continue
        directory = root if audit.path == "." else root / audit.path
        text, error = read_text(directory / "logic_change.md")
        if error:
            continue
        texts_by_scope[audit.path] = text
        ids_by_scope[audit.path] = change_heading_ids(text)

    all_ids: dict[str, list[str]] = {}
    for scope, ids in ids_by_scope.items():
        for change_id in ids:
            all_ids.setdefault(change_id, []).append(scope)
    duplicate_ids = sorted(
        f"{change_id}:{','.join(scopes)}"
        for change_id, scopes in all_ids.items()
        if len(scopes) > 1
    )

    root_change = root / "logic_change.md"
    root_text = texts_by_scope.get(".", "")
    root_index_ids = change_index_ids(root_text) if root_text else set()
    local_root_ids = set(ids_by_scope.get(".", []))
    module_ids = {
        change_id
        for scope, ids in ids_by_scope.items()
        if scope != "."
        for change_id in ids
    }
    missing_root_index: list[str] = []
    for scope, ids in ids_by_scope.items():
        if scope == ".":
            continue
        if scope not in root_text:
            missing_root_index.append(scope)
        for change_id in ids:
            if change_id not in root_index_ids:
                missing_root_index.append(change_id)
    unknown_root_index = sorted(root_index_ids - local_root_ids - module_ids)

    route_issues: list[str] = []
    for row in markdown_table_rows(root_text, "活跃议案索引"):
        change_id = normalize_change_id(row.get("change_id", ""))
        if not change_id:
            continue
        proposal_cell = row.get("proposal_path", "")
        target = cell_link_target(proposal_cell)
        if not target:
            route_issues.append(f"{change_id}:proposal-path-must-be-markdown-link")
            continue
        target_path = (root / target).resolve()
        if (
            not is_within(target_path, root)
            or not target_path.is_file()
            or target_path.name.lower() != "logic_change.md"
        ):
            route_issues.append(f"{change_id}:invalid-proposal-path:{target}")
            continue
        target_text, target_error = read_text(target_path)
        target_block = change_blocks(target_text).get(change_id)
        if target_error or target_block is None:
            route_issues.append(f"{change_id}:proposal-body-not-found:{target}")
            continue
        target_values = control_values(target_block)
        for column, field in (
            ("status", "status"),
            ("scope", "scope"),
            ("owner", "owner"),
        ):
            indexed_value = row.get(column, "").strip().casefold()
            body_value = (target_values.get(field) or [""])[0]
            if indexed_value != body_value:
                route_issues.append(
                    f"{change_id}:root-index-{column}-mismatch:{indexed_value or 'empty'}!={body_value or 'empty'}"
                )

    registry_text, _ = read_text(root / "logic_readme.md")
    registry_rows = {
        normalize_scope_path(row.get("scope_path", "")): row
        for row in markdown_table_rows(registry_text, "范围登记表")
        if row.get("scope_path", "").strip()
    }
    authority_rows = markdown_table_rows(registry_text, "决策权限登记")
    authority_registry_issues: list[str] = []
    active_authority_scopes: dict[str, set[str]] = {}
    authority_row_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(authority_rows, start=1):
        authority_id = normalize_authority_id(row.get("authority_id", ""))
        scope_raw = row.get("scope_path", "").strip("` ")
        scope = normalize_scope_path(scope_raw) if scope_raw else ""
        status = row.get("status", "").strip().casefold()
        evidence = row.get("evidence", "").strip("` ")
        if not authority_id:
            authority_registry_issues.append(
                f"authority-row-{index}:invalid-authority-id"
            )
        if not scope:
            authority_registry_issues.append(
                f"authority-row-{index}:missing-scope-path"
            )
        elif scope not in registry_rows:
            authority_registry_issues.append(
                f"authority-row-{index}:scope-not-registered:{scope}"
            )
        if status not in DECISION_AUTHORITY_STATUSES:
            authority_registry_issues.append(
                f"authority-row-{index}:invalid-status:{status or 'empty'}"
            )
        if not evidence or evidence.casefold() in {"none", "unknown", "n/a", "..."}:
            authority_registry_issues.append(f"authority-row-{index}:missing-evidence")
        row_key = (authority_id, scope)
        if authority_id and scope:
            if row_key in authority_row_keys:
                authority_registry_issues.append(
                    f"duplicate-decision-authority-registration:{authority_id}:{scope}"
                )
            authority_row_keys.add(row_key)
        if authority_id and scope and status == "active":
            active_authority_scopes.setdefault(authority_id, set()).add(scope)

    authority_issues: list[str] = []
    for proposal_scope, proposal_text in texts_by_scope.items():
        for change_id, block in change_blocks(proposal_text).items():
            values = control_values(block)
            raw_values = control_values_raw(block)
            statuses = set(values.get("status", []))
            if not statuses.intersection({"implementing", "verifying", "promoting"}):
                continue
            uses_legacy_authority = bool(authority_rows) or any(
                field in raw_values
                for field in (
                    "decision_authority",
                    "authority_evidence",
                    "approved_by",
                )
            )
            if not uses_legacy_authority:
                continue
            authority_values = [
                normalize_authority_id(value)
                for value in raw_values.get("decision_authority", [])
                if value.strip()
            ]
            authority_values = [value for value in authority_values if value]
            if len(authority_values) != 1:
                authority_issues.append(
                    f"{change_id}:advanced-status-needs-one-registered-decision-authority"
                )
                continue
            authority_id = authority_values[0]
            registered_scopes = active_authority_scopes.get(authority_id, set())
            if not registered_scopes:
                authority_issues.append(
                    f"{change_id}:decision-authority-not-active-or-not-registered:{authority_id}"
                )
            approved_by_values = [
                normalize_authority_id(value)
                for value in raw_values.get("approved_by", [])
                if value.strip()
            ]
            approved_by_values = [value for value in approved_by_values if value]
            if approved_by_values != [authority_id]:
                authority_issues.append(
                    f"{change_id}:approved-by-must-match-decision-authority"
                )
            affected_scopes = change_affected_scopes(raw_values)
            if not affected_scopes:
                authority_issues.append(
                    f"{change_id}:advanced-status-needs-affected-scopes"
                )
                continue
            for affected_scope in affected_scopes:
                if affected_scope not in registry_rows:
                    authority_issues.append(
                        f"{change_id}:affected-scope-not-registered:{affected_scope}"
                    )
                elif not any(
                    registered_scope == affected_scope
                    or is_scope_ancestor(registered_scope, affected_scope)
                    for registered_scope in registered_scopes
                ):
                    authority_issues.append(
                        f"{change_id}:decision-authority-outside-registered-scope:"
                        f"{authority_id}:{affected_scope}"
                    )

    cross_module_link_issues: list[str] = []
    for proposal_scope, proposal_text in texts_by_scope.items():
        if proposal_scope == ".":
            continue
        for change_id, block in change_blocks(proposal_text).items():
            affected_scopes = change_affected_scopes(control_values_raw(block))
            if not affected_scopes:
                cross_module_link_issues.append(
                    f"{change_id}:module-proposal-needs-affected-scopes"
                )
                continue
            owner_scopes: set[str] = set()
            for affected_scope in affected_scopes:
                registry_row = registry_rows.get(affected_scope)
                if registry_row is None:
                    cross_module_link_issues.append(
                        f"{change_id}:affected-scope-not-registered:{affected_scope}"
                    )
                    continue
                owner_target = cell_link_target(registry_row.get("logic_change", ""))
                if not owner_target:
                    cross_module_link_issues.append(
                        f"{change_id}:affected-scope-has-no-proposal-owner:{affected_scope}"
                    )
                    continue
                owner_path = (root / owner_target).resolve()
                if (
                    not is_within(owner_path, root)
                    or owner_path.name.casefold() != "logic_change.md"
                ):
                    cross_module_link_issues.append(
                        f"{change_id}:affected-scope-invalid-proposal-owner:"
                        f"{affected_scope}:{owner_target}"
                    )
                    continue
                owner_scopes.add(owner_path.parent.relative_to(root).as_posix() or ".")
            if owner_scopes != {proposal_scope}:
                cross_module_link_issues.append(
                    f"{change_id}:module-proposal-must-be-root-canonical:"
                    f"proposal={proposal_scope};owners={','.join(sorted(owner_scopes)) or 'none'}"
                )

    coordination_rows = markdown_table_rows(root_text, "跨模块协调索引")
    coordinated_owner_scopes: set[tuple[str, str]] = set()
    coordinated_scopes: dict[str, set[str]] = {}

    def has_exact_root_link(cell: str, source_file: Path, change_id: str) -> bool:
        target, fragment = cell_link_parts(cell)
        if not target or not fragment:
            return False
        candidate = (source_file.parent / target).resolve()
        return (
            candidate == root_change.resolve()
            and fragment.casefold() == change_id.casefold()
        )

    for row in coordination_rows:
        change_id = normalize_change_id(row.get("change_id", ""))
        affected_scope = normalize_scope_path(row.get("affected_scope", ""))
        if not change_id:
            continue
        if change_id not in local_root_ids:
            cross_module_link_issues.append(
                f"{change_id}:cross-module-body-must-be-root-canonical"
            )
        if not affected_scope or affected_scope == ".":
            cross_module_link_issues.append(f"{change_id}:invalid-affected-scope")
            continue
        coordinated_scopes.setdefault(change_id, set()).add(affected_scope)
        registry_row = registry_rows.get(affected_scope)
        if registry_row is None:
            cross_module_link_issues.append(
                f"{change_id}:affected-scope-not-registered:{affected_scope}"
            )
            continue

        resolved_targets: dict[str, Path] = {}
        for column, expected in (
            ("module_logic_readme", "logic_readme.md"),
            ("module_logic_change", "logic_change.md"),
        ):
            cell = row.get(column, "")
            target = cell_link_target(cell)
            registry_target = cell_link_target(
                registry_row.get(
                    "logic_readme" if expected == "logic_readme.md" else "logic_change",
                    "",
                )
            )
            if not registry_target:
                if cell.strip().casefold() not in {"none", "n/a", "not-applicable"}:
                    cross_module_link_issues.append(
                        f"{change_id}:{column}-must-be-none-for-unrouted-scope"
                    )
                continue
            if not target:
                cross_module_link_issues.append(
                    f"{change_id}:{column}-must-be-markdown-link"
                )
                continue
            if normalize_scope_path(target) != normalize_scope_path(registry_target):
                cross_module_link_issues.append(
                    f"{change_id}:{column}-registry-route-mismatch:{target}!={registry_target}"
                )
            target_path = (root / target).resolve()
            if (
                not is_within(target_path, root)
                or not target_path.is_file()
                or target_path.name.lower() != expected
            ):
                cross_module_link_issues.append(
                    f"{change_id}:invalid-{column}:{target}"
                )
                continue
            resolved_targets[column] = target_path

        module_change = resolved_targets.get("module_logic_change")
        registry_policy = registry_row.get("doc_policy", "").strip().casefold()
        registry_membership = registry_row.get("membership", "").strip().casefold()
        if module_change is None:
            if registry_policy == "paired" or (
                registry_policy == "inherited" and registry_membership == "in-system"
            ):
                cross_module_link_issues.append(
                    f"{change_id}:affected-scope-missing-paired-owner-route:{affected_scope}"
                )
        else:
            owner_scope = module_change.parent.relative_to(root).as_posix()
            owner_scope = owner_scope or "."
            owner_registry = registry_rows.get(owner_scope)
            if owner_scope != "." and (
                owner_registry is None
                or owner_registry.get("doc_policy", "").strip().casefold() != "paired"
            ):
                cross_module_link_issues.append(
                    f"{change_id}:affected-scope-owner-must-be-paired:{affected_scope}->{owner_scope}"
                )
            coordinated_owner_scopes.add((change_id, owner_scope))
            if module_change.resolve() != root_change.resolve():
                module_text, module_error = read_text(module_change)
                if not module_error:
                    raw_values = control_values_raw(module_text)
                    linked_value = " ".join(raw_values.get("linked_root_changes", []))
                    linked_ok = any(
                        has_exact_root_link(match.group(0), module_change, change_id)
                        for match in re.finditer(r"\[[^\]]+\]\([^)]+\)", linked_value)
                    )
                    if not linked_ok:
                        cross_module_link_issues.append(
                            f"{change_id}:module-file-control-missing-root-link:{affected_scope}"
                        )
                    module_rows = markdown_table_rows(module_text, "关联根议案")
                    matching_rows = [
                        item
                        for item in module_rows
                        if normalize_change_id(item.get("change_id", "")) == change_id
                    ]
                    if not matching_rows or not any(
                        has_exact_root_link(
                            item.get("root_proposal", ""),
                            module_change,
                            change_id,
                        )
                        for item in matching_rows
                    ):
                        cross_module_link_issues.append(
                            f"{change_id}:module-link-table-missing-root-link:{affected_scope}"
                        )
        anchor = f'<a id="{change_id.lower()}"></a>'
        if anchor not in root_text.lower():
            cross_module_link_issues.append(
                f"{change_id}:root-proposal-missing-explicit-anchor"
            )

    root_blocks = change_blocks(root_text)
    for change_id, block in root_blocks.items():
        raw_values = control_values_raw(block)
        declared = set()
        for value in raw_values.get("affected_scopes", []):
            declared |= split_control_list(value)
        non_root_declared = declared - {"."}
        table_scopes = coordinated_scopes.get(change_id, set())
        if non_root_declared != table_scopes:
            cross_module_link_issues.append(
                f"{change_id}:affected-scope-coordination-mismatch:"
                f"declared={','.join(sorted(non_root_declared)) or 'none'};"
                f"indexed={','.join(sorted(table_scopes)) or 'none'}"
            )

    for scope, module_text in texts_by_scope.items():
        if scope == ".":
            continue
        module_change = root / scope / "logic_change.md"
        for row in markdown_table_rows(module_text, "关联根议案"):
            change_id = normalize_change_id(row.get("change_id", ""))
            if not change_id:
                continue
            if (change_id, scope) not in coordinated_owner_scopes:
                cross_module_link_issues.append(
                    f"{change_id}:orphan-module-root-link:{scope}"
                )
            if not has_exact_root_link(
                row.get("root_proposal", ""), module_change, change_id
            ):
                cross_module_link_issues.append(
                    f"{change_id}:invalid-module-root-link:{scope}"
                )

    return {
        "duplicate_ids": duplicate_ids,
        "missing_root_index": sorted(set(missing_root_index)),
        "unknown_root_index": unknown_root_index,
        "route_issues": sorted(set(route_issues)),
        "cross_module_link_issues": sorted(set(cross_module_link_issues)),
        "authority_registry_issues": sorted(set(authority_registry_issues)),
        "authority_issues": sorted(set(authority_issues)),
        "closed_change_ids_still_active": [],
    }


def audit_current_state_integrity(
    root: Path,
    audits: list[ModuleAudit],
    module_routes: dict,
    *,
    all_dirs: bool,
) -> dict:
    document_issues: list[str] = []
    scope_registry_issues: list[str] = []
    proposal_issues: list[str] = []
    responsibility_issues: list[str] = []

    root_module = next((audit for audit in audits if audit.path == "."), None)
    readme = root / "logic_readme.md"
    change = root / "logic_change.md"
    if root_module is None or not readme.is_file():
        document_issues.append("missing-root-logic_readme")
    if root_module is None or not change.is_file():
        document_issues.append("missing-root-logic_change")
    if document_issues:
        return {
            "document_issues": sorted(set(document_issues)),
            "scope_registry_issues": [],
            "proposal_issues": [],
            "responsibility_issues": [],
        }

    readme_sections, readme_fields, readme_links = inspect_markdown(
        readme, root, CURRENT_README_SECTIONS, CURRENT_README_FIELDS
    )
    change_sections, change_fields, change_links = inspect_markdown(
        change, root, CURRENT_CHANGE_SECTIONS, CURRENT_CHANGE_FIELDS
    )
    document_issues.extend(
        f"logic_readme:missing-section:{item}" for item in readme_sections
    )
    document_issues.extend(
        f"logic_readme:missing-field:{item}" for item in readme_fields
    )
    document_issues.extend(f"logic_readme:broken-link:{item}" for item in readme_links)
    document_issues.extend(
        f"logic_change:missing-section:{item}" for item in change_sections
    )
    document_issues.extend(
        f"logic_change:missing-field:{item}" for item in change_fields
    )
    document_issues.extend(f"logic_change:broken-link:{item}" for item in change_links)

    readme_text, readme_error = read_text(readme)
    change_text, change_error = read_text(change)
    if readme_error:
        document_issues.append(f"logic_readme:unreadable:{readme_error}")
    if change_error:
        document_issues.append(f"logic_change:unreadable:{change_error}")
    if readme_error or change_error:
        return {
            "document_issues": sorted(set(document_issues)),
            "scope_registry_issues": [],
            "proposal_issues": [],
            "responsibility_issues": [],
        }

    if re.search(r"^\s*##\s+决策权限登记\s*$", readme_text, re.MULTILINE):
        responsibility_issues.append(
            "logic_readme:legacy-decision-authority-registry-must-be-migrated"
        )

    current_policy_rows = markdown_table_rows(readme_text, "当前制度")
    current_policy_headers = markdown_table_headers(readme_text, "当前制度")
    if current_policy_headers != CURRENT_POLICY_HEADERS:
        document_issues.append("logic_readme:current-policy-invalid-columns")
    if not current_policy_rows:
        document_issues.append("logic_readme:current-policy-needs-at-least-one-row")
    for index, row in enumerate(current_policy_rows, start=1):
        rule_id = row.get("rule_id", "").strip()
        rule_level = row.get("规则等级", "").strip().casefold()
        rule = row.get("当前有效规则/行为", "").strip()
        why = row.get("why（仅一句可审计摘要）", "").strip()
        if any(
            not value
            or value.casefold() in {"none", "unknown", "n/a", "..."}
            or "<" in value
            or ">" in value
            for value in (rule_id, rule, why)
        ):
            document_issues.append(
                f"logic_readme:current-policy-row-{index}-needs-rule-and-why"
            )
        if rule_level not in {"key", "ordinary"}:
            document_issues.append(
                f"logic_readme:current-policy-row-{index}-invalid-rule-level:"
                f"{rule_level or 'empty'}"
            )
        if rule_level == "key" and not is_immutable_decision_record_link(
            row.get("决策记录", "")
        ):
            document_issues.append(
                f"logic_readme:current-policy-row-{index}-key-needs-immutable-decision-link"
            )
        last_reviewed = row.get("last_reviewed", "").strip()
        if not is_iso_date(last_reviewed):
            document_issues.append(
                f"logic_readme:current-policy-row-{index}-last-reviewed-must-be-date"
            )

    code_map_headers = markdown_table_headers(readme_text, "代码地图")
    code_map_rows = markdown_table_rows(readme_text, "代码地图")
    expected_code_map_headers = [
        "路径/稳定锚点",
        "artifact_class/layer",
        "职责",
        "输入",
        "输出",
        "权威来源",
        "可直接编辑",
        "关联测试",
    ]
    if code_map_headers != expected_code_map_headers:
        document_issues.append("logic_readme:code-map-invalid-columns")
    if not code_map_rows:
        document_issues.append("logic_readme:code-map-needs-at-least-one-row")
    for index, row in enumerate(code_map_rows, start=1):
        for column in ("路径/稳定锚点", "artifact_class/layer", "职责", "权威来源"):
            value = row.get(column, "").strip()
            if (
                not value
                or value.casefold() in {"none", "unknown", "n/a", "..."}
                or "<" in value
                or ">" in value
            ):
                document_issues.append(
                    f"logic_readme:code-map-row-{index}-missing-{column}"
                )

    readme_control = markdown_section_text(readme_text, "文档控制")
    readme_values = control_values(readme_control)
    readme_raw = control_values_raw(readme_control)
    # `registry_status` and the two canonical pointers are defined under
    # "范围登记与归属" by references/logic-readme-template.md, not under
    # "文档控制".  Read the registry section as a fallback so a
    # template-conformant document is not reported as missing them; the
    # single-value requirement below still applies to the merged result.
    registry_control = markdown_section_text(readme_text, "范围登记与归属")
    registry_values = control_values(registry_control)
    registry_raw = control_values_raw(registry_control)

    def registered_field(field: str, raw: bool = False) -> list[str]:
        """Look the field up in 文档控制 first, then 范围登记与归属."""
        primary = (readme_raw if raw else readme_values).get(field, [])
        if primary:
            return primary
        return (registry_raw if raw else registry_values).get(field, [])

    expected_readme_values = {
        "module_id": "mod-root",
        "scope": ".",
        "scope_path": ".",
        "parent": "none",
        "parent_module_id": "none",
        "membership": "in-system",
        "scope_type": "root",
        "module_doc_policy": "paired",
        "registry_status": "registered",
    }
    for field, expected in expected_readme_values.items():
        values = registered_field(field)
        normalized = [
            normalize_scope_path(value) if field in {"scope", "scope_path"} else value
            for value in values
        ]
        if normalized != [expected]:
            document_issues.append(
                f"logic_readme:{field}-must-be-single-{expected}:"
                + (",".join(values) or "missing")
            )
    if len(readme_raw.get("owner", [])) != 1 or not has_meaningful_value(
        readme_values, "owner"
    ):
        document_issues.append("logic_readme:owner-must-be-single-meaningful-value")
    readme_governance_mode = (readme_values.get("governance_mode") or [""])[0]
    readme_governance_ref = (readme_values.get("governance_ref") or [""])[0]
    if readme_values.get("governance_mode", []) != [readme_governance_mode] or (
        readme_governance_mode not in GOVERNANCE_MODES
    ):
        document_issues.append("logic_readme:invalid-governance-mode")
    if len(readme_raw.get("governance_ref", [])) != 1 or not has_meaningful_value(
        readme_values, "governance_ref"
    ):
        document_issues.append("logic_readme:governance-ref-must-be-meaningful")
    document_issues.extend(
        governance_evidence_issues(readme_values, label="logic_readme")
    )
    last_verified = readme_raw.get("last_verified", [])
    if len(last_verified) != 1:
        document_issues.append("logic_readme:last_verified-must-appear-once")
    else:
        try:
            date.fromisoformat(last_verified[0])
        except ValueError:
            document_issues.append("logic_readme:last_verified-must-be-date")
    if len(last_verified) == 1:
        readme_trigger = (readme_values.get("review_trigger") or [""])[0]
        document_issues.extend(
            review_freshness_issues(
                last_verified[0], readme_trigger, label="logic_readme"
            )
        )
        for index, row in enumerate(current_policy_rows, start=1):
            reviewed = row.get("last_reviewed", "").strip()
            if is_iso_date(reviewed):
                document_issues.extend(
                    review_freshness_issues(
                        reviewed,
                        readme_trigger,
                        label=f"logic_readme:current-policy-row-{index}",
                    )
                )
    for field, expected in (
        ("canonical_readme", "logic_readme.md"),
        ("canonical_change", "logic_change.md"),
    ):
        values = registered_field(field, raw=True)
        normalized = [normalize_scope_path(value.strip("<>")) for value in values]
        if normalized != [expected]:
            document_issues.append(
                f"logic_readme:{field}-must-be-{expected}:"
                + (",".join(values) or "missing")
            )
    coverage = control_values(readme_text).get("coverage_policy", [])
    if coverage not in (["governed-boundaries"], ["registry-every-folder"]):
        document_issues.append(
            "logic_readme:invalid-coverage-policy:" + (",".join(coverage) or "missing")
        )
    if coverage == ["registry-every-folder"] and not all_dirs:
        scope_registry_issues.append("registry-every-folder-policy-requires---all-dirs")
    all_readme_values = control_values(readme_text)
    all_readme_raw = control_values_raw(readme_text)
    if all_readme_values.get("membership_policy", []) != ["root-registry-first"]:
        document_issues.append(
            "logic_readme:membership_policy-must-be-root-registry-first"
        )
    if len(all_readme_raw.get("layer_policy", [])) != 1 or not has_meaningful_value(
        all_readme_values, "layer_policy"
    ):
        document_issues.append(
            "logic_readme:layer_policy-must-be-single-meaningful-value"
        )
    for field, expected in (
        ("version_root", "logic_version"),
        ("temp_root", "logic_version/working"),
    ):
        values = all_readme_raw.get(field, [])
        normalized = [normalize_scope_path(value) for value in values]
        if normalized != [expected]:
            document_issues.append(
                f"logic_readme:{field}-must-be-{expected}:"
                + (",".join(values) or "missing")
            )

    change_control = markdown_section_text(change_text, "文档控制")
    change_values = control_values(change_control)
    change_raw = control_values_raw(change_control)
    for field, expected in (
        ("scope", "."),
        ("scope_path", "."),
        ("module_id", "mod-root"),
    ):
        values = change_values.get(field, [])
        normalized = [
            normalize_scope_path(value) if field in {"scope", "scope_path"} else value
            for value in values
        ]
        if normalized != [expected]:
            document_issues.append(
                f"logic_change:{field}-must-be-single-{expected}:"
                + (",".join(values) or "missing")
            )
    current_policy = [
        normalize_scope_path(value.strip("<>"))
        for value in change_raw.get("current_policy", [])
    ]
    if current_policy != ["logic_readme.md"]:
        document_issues.append(
            "logic_change:current_policy-must-be-logic_readme.md:"
            + (",".join(change_raw.get("current_policy", [])) or "missing")
        )
    for field in (
        "owner",
        "governance_mode",
        "governance_ref",
        "last_updated",
        "active_changes",
    ):
        if len(change_raw.get(field, [])) != 1:
            document_issues.append(
                f"logic_change:{field}-must-appear-once:"
                f"{len(change_raw.get(field, []))}"
            )
    if not has_meaningful_value(change_values, "owner"):
        document_issues.append("logic_change:owner-must-be-meaningful")
    change_governance_mode = (change_values.get("governance_mode") or [""])[0]
    change_governance_ref = (change_values.get("governance_ref") or [""])[0]
    if change_governance_mode not in GOVERNANCE_MODES:
        document_issues.append("logic_change:invalid-governance-mode")
    if not has_meaningful_value(change_values, "governance_ref"):
        document_issues.append("logic_change:governance-ref-must-be-meaningful")
    document_issues.extend(
        governance_evidence_issues(change_values, label="logic_change")
    )
    if change_governance_mode != readme_governance_mode:
        document_issues.append("governance-mode-mismatch-between-current-documents")
    if change_governance_ref != readme_governance_ref:
        document_issues.append("governance-ref-mismatch-between-current-documents")
    last_updated = change_raw.get("last_updated", [])
    if len(last_updated) == 1:
        try:
            date.fromisoformat(last_updated[0])
        except ValueError:
            document_issues.append("logic_change:last_updated-must-be-date")

    for issue in root_module.semantic_issues:
        if issue.startswith("logic_change:") and any(
            marker in issue
            for marker in (
                "missing-changed-by",
                "legacy-reviewed_by",
                "legacy-review_ref",
            )
        ):
            responsibility_issues.append(issue)
        elif issue.startswith("logic_change:CHG-"):
            proposal_issues.append(issue.removeprefix("logic_change:"))
        else:
            document_issues.append(issue)

    for key in (
        "route_issues",
        "duplicate_module_ids",
        "duplicate_scope_paths",
        "unregistered_governance_dirs",
        "hierarchy_issues",
    ):
        scope_registry_issues.extend(
            f"{key}:{item}" for item in module_routes.get(key, [])
        )

    registered_scopes = {
        normalize_scope_path(row.get("scope_path", ""))
        for row in module_routes.get("rows", [])
        if row.get("scope_path", "").strip()
    }
    module_scopes = {
        row.get("module_id", "").strip().casefold(): normalize_scope_path(
            row.get("scope_path", "")
        )
        for row in module_routes.get("rows", [])
        if row.get("module_id", "").strip() and row.get("scope_path", "").strip()
    }
    module_anchor_scopes: dict[str, str] = {}
    for row in module_routes.get("rows", []):
        target, fragment = cell_link_parts(row.get("logic_readme", ""))
        scope_path = normalize_scope_path(row.get("scope_path", ""))
        if target == "logic_readme.md" and fragment and scope_path:
            module_anchor_scopes[fragment.casefold()] = scope_path
    body_id_list = change_heading_ids(change_text)
    body_ids = set(body_id_list)
    duplicate_body_ids = sorted(
        {change_id for change_id in body_id_list if body_id_list.count(change_id) > 1}
    )
    for change_id in duplicate_body_ids:
        proposal_issues.append(f"duplicate-change-body:{change_id}")

    declared_active_changes = (change_raw.get("active_changes") or [""])[0]
    expected_active_changes = str(len(body_id_list)) if body_id_list else "none"
    if declared_active_changes.casefold() != expected_active_changes:
        proposal_issues.append(
            "active_changes-count-mismatch:"
            f"{declared_active_changes or 'missing'}!={expected_active_changes}"
        )
    index_rows = markdown_table_rows(change_text, "活跃议案索引")
    index_ids = {
        change_id
        for row in index_rows
        for change_id in [normalize_change_id(row.get("change_id", ""))]
        if change_id
    }
    if body_ids != index_ids:
        missing = sorted(body_ids - index_ids)
        extra = sorted(index_ids - body_ids)
        if missing:
            proposal_issues.append("ids-missing-from-index:" + ",".join(missing))
        if extra:
            proposal_issues.append("index-ids-without-body:" + ",".join(extra))

    expected_topic_headers = [
        "topic_id",
        "同类议题/共享问题",
        "coordinator",
        "discussion_refs",
        "related_changes",
        "status",
    ]
    topic_headers = markdown_table_headers(change_text, "讨论主题索引")
    if topic_headers != expected_topic_headers:
        document_issues.append("logic_change:topic-index-invalid-columns")
    topic_rows = markdown_table_rows(change_text, "讨论主题索引")
    topic_members: dict[str, set[str]] = {}
    topics_by_change: dict[str, set[str]] = {}
    for index, row in enumerate(topic_rows, start=1):
        topic_id = normalize_topic_id(row.get("topic_id", ""))
        if not topic_id:
            proposal_issues.append(f"topic-index-row-{index}:invalid-topic-id")
            continue
        if topic_id in topic_members:
            proposal_issues.append(f"topic-index-duplicate-topic-id:{topic_id}")
            continue
        related_value = row.get("related_changes", "")
        related_items = [
            item.strip(" `[]")
            for item in re.split(r"[,;，；]", related_value)
            if item.strip(" `[]")
        ]
        related_ids: set[str] = set()
        invalid_related_items: list[str] = []
        has_none = False
        for item in related_items:
            if item.casefold() == "none":
                has_none = True
                continue
            change_id = normalize_change_id(item)
            if change_id:
                if change_id in related_ids:
                    proposal_issues.append(
                        f"topic-index-row-{index}:duplicate-related-change:{change_id}"
                    )
                related_ids.add(change_id)
            else:
                invalid_related_items.append(item)
        if not related_items or invalid_related_items:
            proposal_issues.append(
                f"topic-index-row-{index}:related-changes-must-be-chg-or-none"
            )
        if has_none and related_ids:
            proposal_issues.append(
                f"topic-index-row-{index}:related-changes-cannot-mix-none"
            )
        topic_members[topic_id] = related_ids
        for related_change in related_ids:
            if related_change not in body_ids:
                proposal_issues.append(
                    f"topic-index-row-{index}:unknown-active-change:{related_change}"
                )
            topics_by_change.setdefault(related_change, set()).add(topic_id)

    declared_topics_by_change: dict[str, str] = {}

    for change_id, block in change_blocks(change_text).items():
        values = control_values(block)
        raw_values = control_values_raw(block)
        legacy_authority_fields = sorted(
            {"decision_authority", "authority_evidence", "approved_by"}
            & set(raw_values)
        )
        if legacy_authority_fields:
            responsibility_issues.append(
                f"{change_id}:legacy-authority-fields-must-be-migrated:"
                + ",".join(legacy_authority_fields)
            )
        legacy_review_fields = sorted({"reviewed_by", "review_ref"} & set(raw_values))
        if legacy_review_fields:
            responsibility_issues.append(
                f"{change_id}:legacy-ambiguous-review-fields-must-be-migrated:"
                + ",".join(legacy_review_fields)
            )
        for field in ("status", "effective", "owner", "changed_by", "scope"):
            entries = raw_values.get(field, [])
            if len(entries) != 1:
                target = (
                    responsibility_issues
                    if field in {"owner", "changed_by"}
                    else proposal_issues
                )
                target.append(f"{change_id}:{field}-must-appear-once:{len(entries)}")
        if values.get("effective", []) != ["false"]:
            proposal_issues.append(f"{change_id}:effective-must-be-false")
        for field in ("owner", "changed_by"):
            if not has_meaningful_value(values, field):
                responsibility_issues.append(f"{change_id}:missing-{field}")
        if (
            readme_governance_mode == "collaborative"
            and (values.get("decision_gate") or [""])[0] == "required"
            and (values.get("semantic_review_state") or [""])[0] == "passed"
        ):
            changed_by = (values.get("changed_by") or [""])[0]
            reviewed_by = (values.get("semantic_reviewed_by") or [""])[0]
            if reviewed_by == "self" or reviewed_by == changed_by:
                responsibility_issues.append(
                    f"{change_id}:collaborative-high-risk-review-must-be-independent"
                )

        topic_values = raw_values.get("topic_id", [])
        if len(topic_values) != 1:
            proposal_issues.append(
                f"{change_id}:topic-id-must-appear-once:{len(topic_values)}"
            )
        else:
            topic_value = topic_values[0]
            if is_none_like(topic_value):
                if change_id in topics_by_change:
                    proposal_issues.append(
                        f"{change_id}:topic-index-lists-change-with-topic-id-none"
                    )
            else:
                topic_id = normalize_topic_id(topic_value)
                if not topic_id:
                    proposal_issues.append(f"{change_id}:invalid-topic-id:{topic_value}")
                else:
                    declared_topics_by_change[change_id] = topic_id
                    if topic_id not in topic_members:
                        proposal_issues.append(f"{change_id}:topic-not-indexed:{topic_id}")
                    elif change_id not in topic_members[topic_id]:
                        proposal_issues.append(
                            f"{change_id}:topic-index-missing-change:{topic_id}"
                        )

        affected_scopes = change_affected_scopes(raw_values)
        if not affected_scopes:
            proposal_issues.append(f"{change_id}:missing-affected-scopes")
        for affected_scope in sorted(affected_scopes):
            if affected_scope not in registered_scopes:
                proposal_issues.append(
                    f"{change_id}:affected-scope-not-registered:{affected_scope}"
                )

        primary_scope = normalize_scope_path((raw_values.get("scope") or [""])[0])
        if (
            primary_scope in registered_scopes
            and primary_scope not in affected_scopes
        ):
            proposal_issues.append(
                f"{change_id}:primary-scope-missing-from-affected-scopes:"
                f"{primary_scope}"
            )

        related_module_ids = {
            match.group(0).casefold()
            for raw_value in raw_values.get("related_modules", [])
            for match in re.finditer(
                r"\bMOD-[A-Z0-9][A-Z0-9-]*\b", raw_value, re.IGNORECASE
            )
        }
        recognized_related_reference = bool(related_module_ids)
        for raw_value in raw_values.get("related_modules", []):
            for match in MARKDOWN_LINK_RE.finditer(raw_value):
                recognized_related_reference = True
                target, fragment = cell_link_parts(match.group(0))
                if target != "logic_readme.md" or not fragment:
                    proposal_issues.append(
                        f"{change_id}:related-module-link-must-target-root-policy-anchor"
                    )
                    continue
                related_scope = module_anchor_scopes.get(fragment.casefold())
                if related_scope is None:
                    proposal_issues.append(
                        f"{change_id}:related-module-anchor-not-registered:{fragment}"
                    )
                elif related_scope not in affected_scopes:
                    proposal_issues.append(
                        f"{change_id}:related-module-anchor-scope-missing-from-affected-scopes:"
                        f"{fragment}:{related_scope}"
                    )
        related_values = raw_values.get("related_modules", [])
        if (
            related_values
            and any(value.casefold() != "none" for value in related_values)
            and not recognized_related_reference
        ):
            proposal_issues.append(
                f"{change_id}:related-modules-needs-registered-id-or-root-anchor"
            )
        for module_id in sorted(related_module_ids):
            related_scope = module_scopes.get(module_id)
            if related_scope is None:
                proposal_issues.append(
                    f"{change_id}:related-module-not-registered:{module_id}"
                )
            elif related_scope not in affected_scopes:
                proposal_issues.append(
                    f"{change_id}:related-module-scope-missing-from-affected-scopes:"
                    f"{module_id}:{related_scope}"
                )

        matching_rows = [
            row
            for row in index_rows
            if normalize_change_id(row.get("change_id", "")) == change_id
        ]
        if len(matching_rows) != 1:
            proposal_issues.append(
                f"{change_id}:index-row-count-must-be-one:{len(matching_rows)}"
            )
            continue
        row = matching_rows[0]
        target, fragment = cell_link_parts(row.get("proposal_path", ""))
        if target != "logic_change.md" or fragment != change_id.casefold():
            proposal_issues.append(
                f"{change_id}:proposal-path-must-target-logic_change-anchor"
            )
        anchor = f'<a id="{change_id.casefold()}"></a>'
        anchor_count = change_text.casefold().count(anchor)
        if anchor_count != 1:
            proposal_issues.append(
                f"{change_id}:explicit-anchor-count-must-be-one:{anchor_count}"
            )
        for column, field in (
            ("status", "status"),
            ("scope", "scope"),
            ("owner", "owner"),
        ):
            indexed = row.get(column, "").strip().casefold()
            body_value = (values.get(field) or [""])[0]
            if indexed != body_value:
                proposal_issues.append(
                    f"{change_id}:index-{column}-mismatch:{indexed or 'empty'}!={body_value or 'empty'}"
                )

    for change_id, topic_ids in topics_by_change.items():
        declared_topic = declared_topics_by_change.get(change_id)
        if len(topic_ids) > 1:
            proposal_issues.append(
                f"{change_id}:multiple-topic-memberships:"
                + ",".join(sorted(topic_ids))
            )
        elif declared_topic and declared_topic not in topic_ids:
            proposal_issues.append(
                f"{change_id}:topic-index-and-body-mismatch:"
                + ",".join(sorted(topic_ids))
                + f"!={declared_topic}"
            )

    proposal_issues.extend(change_coordination_issues(change_blocks(change_text)))

    return {
        "document_issues": sorted(set(document_issues)),
        "scope_registry_issues": sorted(set(scope_registry_issues)),
        "proposal_issues": sorted(set(proposal_issues)),
        "responsibility_issues": sorted(set(responsibility_issues)),
    }


def active_change_ids(root: Path, audits: list[ModuleAudit]) -> set[str]:
    ids: set[str] = set()
    for audit in audits:
        if not audit.logic_change:
            continue
        directory = root if audit.path == "." else root / audit.path
        text, error = read_text(directory / "logic_change.md")
        if not error:
            ids.update(change_heading_ids(text))
    return ids
