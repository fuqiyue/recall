"""范围路由、议案完整性与 current-state 静态门。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable
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
    change_field_tier,
    cross_ledger_rule_conflicts,
    change_coordination_issues,
    change_heading_ids,
    change_index_ids,
    governance_evidence_issues,
    review_freshness_issues,
)
from .semantic import (
    ModuleAudit,
)

_PLACEHOLDER_VALUES = {"none", "unknown", "n/a", "..."}


# ---------------------------------------------------------------------------
# 范围路由（audit_module_routes）
# ---------------------------------------------------------------------------


def _empty_route_report(issue: str) -> dict:
    """Build the route report returned when the root logic_readme is unusable."""
    return {
        "rows": [],
        "route_issues": [issue],
        "duplicate_module_ids": [],
        "duplicate_scope_paths": [],
        "unregistered_governance_dirs": [],
        "hierarchy_issues": [],
    }


@dataclass
class _RouteContext:
    """范围登记表逐行核查的输入与累积结果。"""

    root: Path
    root_readme: Path
    audits: list[ModuleAudit]
    audits_by_scope: dict[str, ModuleAudit]
    route_issues: list[str] = field(default_factory=list)
    module_ids: dict[str, list[str]] = field(default_factory=dict)
    scope_paths: dict[str, list[str]] = field(default_factory=dict)
    registered_scopes: set[str] = field(default_factory=set)
    root_rows: int = 0


@dataclass
class _RouteRow:
    """单条范围登记行解析后的派生值。"""

    row: dict[str, str]
    module_id: str
    scope_value: str
    membership: str
    doc_policy: str
    scope_dir: Path
    actual_scope: str
    parent_scope: str | None
    parent_audit: ModuleAudit | None


def _nearest_documented_parent(audits: list[ModuleAudit], scope: str) -> str | None:
    """Return the deepest documented ancestor scope of `scope`, if any."""
    candidates = [
        audit.path
        for audit in audits
        if audit.logic_readme and is_scope_ancestor(audit.path, scope)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: len(scope_parts(item)))


def _check_route_row_attributes(
    ctx: _RouteContext, module_id: str, owner: str, membership: str, doc_policy: str
) -> None:
    """核查登记行的 owner / membership / doc_policy 取值。"""
    if (
        not owner
        or owner.casefold() in _PLACEHOLDER_VALUES
        or "<" in owner
        or ">" in owner
    ):
        ctx.route_issues.append(f"{module_id}:route-row-missing-owner")

    if not membership:
        ctx.route_issues.append(f"{module_id}:route-row-missing-membership")
    elif membership not in MEMBERSHIP_STATUSES:
        ctx.route_issues.append(f"{module_id}:invalid-membership:{membership}")
    if doc_policy not in MODULE_DOC_POLICIES:
        ctx.route_issues.append(f"{module_id}:invalid-doc-policy:{doc_policy}")


def _check_route_policy_placement(ctx: _RouteContext, info: _RouteRow) -> None:
    """核查根行必须 in-system/paired；非根 paired 行是二级领域文档（部门法）。

    RULE-018 一二级拆分法（VER-20260903-004）：根 logic_readme 是宪法，
    ``doc_policy: paired`` 的非根登记行是部门法——readme + change 成对，
    领域 CHG 正文只在领域账本，根账本保留全项目索引（公报）。
    out-of-system 行不得声称 paired。
    """
    if info.scope_value == ".":
        ctx.root_rows += 1
        if info.membership != "in-system" or info.doc_policy != "paired":
            ctx.route_issues.append("root-route-must-be-in-system-paired")
    elif info.membership != "in-system" and info.doc_policy == "paired":
        ctx.route_issues.append(f"{info.module_id}:paired-policy-needs-in-system")


def _check_route_local_docs(ctx: _RouteContext, info: _RouteRow) -> None:
    """核查 doc_policy 与本地 logic_readme / logic_change 文件存在性是否一致。"""
    local_readme = info.scope_dir / "logic_readme.md"
    local_change = info.scope_dir / "logic_change.md"
    module_id = info.module_id
    if info.doc_policy == "paired":
        if not local_readme.is_file():
            ctx.route_issues.append(f"{module_id}:paired-missing-local-readme")
        if not local_change.is_file():
            ctx.route_issues.append(f"{module_id}:paired-missing-local-change")
    elif info.doc_policy == "readme-only":
        if not local_readme.is_file():
            ctx.route_issues.append(f"{module_id}:readme-only-missing-local-readme")
        if local_change.exists():
            ctx.route_issues.append(f"{module_id}:readme-only-forbids-local-change")
    elif info.doc_policy == "inherited":
        if local_readme.exists() or local_change.exists():
            ctx.route_issues.append(f"{module_id}:inherited-forbids-local-logic-docs")
        if info.membership == "in-system" and info.parent_scope is None:
            ctx.route_issues.append(f"{module_id}:inherited-needs-governance-parent")


def _expected_route_targets(info: _RouteRow) -> dict[str, str | None]:
    """Compute the expected logic_readme / logic_change link targets for a row."""
    local_prefix = "" if info.actual_scope == "." else info.actual_scope + "/"
    if info.doc_policy == "paired":
        return {
            "logic_readme": local_prefix + "logic_readme.md",
            "logic_change": local_prefix + "logic_change.md",
        }
    if info.doc_policy == "readme-only":
        return {
            "logic_readme": local_prefix + "logic_readme.md",
            "logic_change": None,
        }
    parent_scope = info.parent_scope
    parent_audit = info.parent_audit
    parent_prefix = (
        "" if parent_scope == "." else ((parent_scope + "/") if parent_scope else "")
    )
    return {
        "logic_readme": (parent_prefix + "logic_readme.md" if parent_scope else None),
        "logic_change": (
            parent_prefix + "logic_change.md"
            if parent_scope and parent_audit and parent_audit.logic_change
            else None
        ),
    }


def _check_inherited_scope_anchor(
    ctx: _RouteContext, info: _RouteRow, fragment: str, target_path: Path
) -> None:
    """核查 inherited 子模块的 logic_readme 链接携带并命中显式范围锚点。"""
    if not fragment:
        ctx.route_issues.append(
            f"{info.module_id}:logic_readme-route-needs-scope-anchor"
        )
        return
    target_text, target_error = read_text(target_path)
    explicit_anchor = f'<a id="{fragment.casefold()}"></a>'
    if target_error or explicit_anchor not in target_text.casefold():
        ctx.route_issues.append(
            f"{info.module_id}:logic_readme-scope-anchor-not-found:{fragment}"
        )


def _check_route_target_control(
    ctx: _RouteContext, info: _RouteRow, column: str, target_path: Path
) -> None:
    """核查链接目标文档控制字段（module_id / scope_path / membership / policy）与登记行一致。"""
    target_text, target_error = read_text(target_path)
    if target_error or info.doc_policy == "inherited":
        return
    module_id = info.module_id
    values = control_values(target_text)
    raw_values = control_values_raw(target_text)
    target_id = (values.get("module_id") or [""])[0]
    if target_id and target_id != module_id:
        ctx.route_issues.append(f"{module_id}:{column}-module-id-mismatch:{target_id}")
    raw_target_scope = (raw_values.get("scope_path") or [""])[0]
    target_scope = normalize_scope_path(raw_target_scope)
    if raw_target_scope and target_scope != info.actual_scope:
        ctx.route_issues.append(
            f"{module_id}:{column}-scope-mismatch:{target_scope}!={info.actual_scope}"
        )
    if column == "logic_readme":
        target_membership = (values.get("membership") or [""])[0]
        target_policy = (values.get("module_doc_policy") or [""])[0]
        if target_membership and target_membership != info.membership:
            ctx.route_issues.append(
                f"{module_id}:membership-mismatch:{target_membership}!={info.membership}"
            )
        if target_policy and target_policy != info.doc_policy:
            ctx.route_issues.append(
                f"{module_id}:doc-policy-mismatch:{target_policy}!={info.doc_policy}"
            )


def _check_route_link_cell(
    ctx: _RouteContext,
    info: _RouteRow,
    column: str,
    expected_name: str,
    expected_target: str | None,
) -> None:
    """核查登记行中一个路由链接单元格（logic_readme 或 logic_change）。"""
    module_id = info.module_id
    cell = info.row.get(column, "")
    target, fragment = cell_link_parts(cell)
    declared_none = cell.strip().strip("`").lower() in {"", "none", "n/a"}
    if not target:
        if not declared_none:
            ctx.route_issues.append(f"{module_id}:{column}-must-be-markdown-link")
        required = expected_target is not None and (
            info.doc_policy in {"paired", "readme-only"}
            or info.membership == "in-system"
        )
        if required:
            ctx.route_issues.append(f"{module_id}:missing-{column}-link")
        return
    if expected_target is None:
        ctx.route_issues.append(f"{module_id}:{column}-must-be-none")
        return
    if normalize_scope_path(target) != normalize_scope_path(expected_target):
        ctx.route_issues.append(
            f"{module_id}:{column}-route-mismatch:{target}!={expected_target}"
        )
    target_path = (ctx.root_readme.parent / target).resolve()
    if not is_within(target_path, ctx.root):
        ctx.route_issues.append(f"{module_id}:{column}-outside-project:{target}")
        return
    if not target_path.is_file():
        ctx.route_issues.append(f"{module_id}:{column}-not-found:{target}")
        return
    if target_path.name.lower() != expected_name:
        ctx.route_issues.append(f"{module_id}:{column}-wrong-name:{target}")
    if (
        column == "logic_readme"
        and info.scope_value != "."
        and info.membership == "in-system"
        and info.doc_policy == "inherited"
    ):
        _check_inherited_scope_anchor(ctx, info, fragment, target_path)
    _check_route_target_control(ctx, info, column, target_path)


def _check_route_row(ctx: _RouteContext, row: dict[str, str]) -> None:
    """核查一条范围登记行：标识、属性、范围解析、本地文档与路由链接。"""
    module_id = row.get("module_id", "").strip().lower()
    scope_value = normalize_scope_path(row.get("scope_path", ""))
    membership = row.get("membership", "").strip().lower()
    doc_policy = row.get("doc_policy", "paired").strip().lower()
    owner = row.get("owner", "").strip()
    if not module_id or "<" in module_id or "..." in module_id:
        ctx.route_issues.append("route-row-missing-module_id")
        return
    if not scope_value or "<" in scope_value or "..." in scope_value:
        ctx.route_issues.append(f"{module_id}:route-row-missing-scope_path")
        return
    ctx.module_ids.setdefault(module_id, []).append(scope_value)
    ctx.scope_paths.setdefault(scope_value.casefold(), []).append(module_id)
    ctx.registered_scopes.add(scope_value)

    _check_route_row_attributes(ctx, module_id, owner, membership, doc_policy)
    resolved_scope = actual_case_relative(ctx.root, scope_value)
    if resolved_scope is None:
        ctx.route_issues.append(f"{module_id}:scope-not-found:{scope_value}")
        return
    scope_dir, actual_scope = resolved_scope
    if actual_scope != scope_value:
        ctx.route_issues.append(
            f"{module_id}:scope-case-mismatch:{scope_value}!={actual_scope}"
        )

    parent_scope = _nearest_documented_parent(ctx.audits, actual_scope)
    info = _RouteRow(
        row=row,
        module_id=module_id,
        scope_value=scope_value,
        membership=membership,
        doc_policy=doc_policy,
        scope_dir=scope_dir,
        actual_scope=actual_scope,
        parent_scope=parent_scope,
        parent_audit=ctx.audits_by_scope.get(parent_scope) if parent_scope else None,
    )
    _check_route_policy_placement(ctx, info)
    _check_route_local_docs(ctx, info)
    expected_targets = _expected_route_targets(info)
    for column, expected_name in (
        ("logic_readme", "logic_readme.md"),
        ("logic_change", "logic_change.md"),
    ):
        _check_route_link_cell(
            ctx, info, column, expected_name, expected_targets.get(column)
        )


def _collect_docs_by_id(
    root: Path, audits: list[ModuleAudit]
) -> dict[str, tuple[str, dict[str, list[str]], dict[str, list[str]]]]:
    """Collect (scope, values, raw_values) of every documented module keyed by module_id."""
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
    return docs_by_id


def _check_hierarchy(
    root: Path,
    docs_by_id: dict[str, tuple[str, dict[str, list[str]], dict[str, list[str]]]],
) -> list[str]:
    """核查每个子模块的 parent_module_id / parent 指向最近的治理父级。"""
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
    return hierarchy_issues


def audit_module_routes(root: Path, audits: list[ModuleAudit]) -> dict:
    root_readme = root / "logic_readme.md"
    if not root_readme.is_file():
        return _empty_route_report("missing-root-logic_readme")

    root_text, error = read_text(root_readme)
    if error:
        return _empty_route_report(f"unreadable-root-logic_readme:{error}")

    rows = markdown_table_rows(root_text, "范围登记表")
    ctx = _RouteContext(
        root=root,
        root_readme=root_readme,
        audits=audits,
        audits_by_scope={audit.path: audit for audit in audits},
    )
    for row in rows:
        _check_route_row(ctx, row)

    duplicate_module_ids = sorted(
        f"{module_id}:{','.join(scopes)}"
        for module_id, scopes in ctx.module_ids.items()
        if len(scopes) > 1
    )
    duplicate_scope_paths = sorted(
        f"{scope}:{','.join(ids)}"
        for scope, ids in ctx.scope_paths.items()
        if len(ids) > 1
    )

    documented_scopes = {
        audit.path for audit in audits if audit.path != "." and audit.logic_readme
    }
    unregistered = sorted(documented_scopes - ctx.registered_scopes)
    hierarchy_issues = _check_hierarchy(root, _collect_docs_by_id(root, audits))

    if not rows:
        ctx.route_issues.append("missing-or-empty-root-scope-registry-table")
    elif ctx.root_rows != 1:
        ctx.route_issues.append(f"root-route-row-count-must-be-one:{ctx.root_rows}")

    return {
        "rows": rows,
        "route_issues": sorted(set(ctx.route_issues)),
        "duplicate_module_ids": duplicate_module_ids,
        "duplicate_scope_paths": duplicate_scope_paths,
        "unregistered_governance_dirs": unregistered,
        "hierarchy_issues": sorted(set(hierarchy_issues)),
    }


# ---------------------------------------------------------------------------
# 议案完整性（audit_proposal_integrity）
# ---------------------------------------------------------------------------


@dataclass
class _ProposalContext:
    """议案完整性核查的共享输入与累积结果。"""

    root: Path
    root_change: Path
    root_text: str
    texts_by_scope: dict[str, str]
    local_root_ids: set[str]
    registry_rows: dict[str, dict[str, str]]
    route_issues: list[str] = field(default_factory=list)
    cross_module_link_issues: list[str] = field(default_factory=list)
    authority_registry_issues: list[str] = field(default_factory=list)
    authority_issues: list[str] = field(default_factory=list)
    coordinated_owner_scopes: set[tuple[str, str]] = field(default_factory=set)
    coordinated_scopes: dict[str, set[str]] = field(default_factory=dict)


def _collect_proposal_texts(
    root: Path, audits: list[ModuleAudit]
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Collect every readable logic_change text and its heading ids keyed by scope."""
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
    return ids_by_scope, texts_by_scope


def _check_root_index_coverage(
    ids_by_scope: dict[str, list[str]], root_text: str
) -> tuple[list[str], list[str]]:
    """核查模块议案与范围是否被根索引覆盖，返回 (missing_root_index, unknown_root_index)。"""
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
    return missing_root_index, unknown_root_index


def _check_root_index_routes(ctx: _ProposalContext) -> None:
    """核查根活跃议案索引每行的 proposal_path 链接及 status/scope/owner 与正文一致。"""
    for row in markdown_table_rows(ctx.root_text, "活跃议案索引"):
        change_id = normalize_change_id(row.get("change_id", ""))
        if not change_id:
            continue
        proposal_cell = row.get("proposal_path", "")
        target = cell_link_target(proposal_cell)
        if not target:
            ctx.route_issues.append(f"{change_id}:proposal-path-must-be-markdown-link")
            continue
        target_path = (ctx.root / target).resolve()
        if (
            not is_within(target_path, ctx.root)
            or not target_path.is_file()
            or target_path.name.lower() != "logic_change.md"
        ):
            ctx.route_issues.append(f"{change_id}:invalid-proposal-path:{target}")
            continue
        target_text, target_error = read_text(target_path)
        target_block = change_blocks(target_text).get(change_id)
        if target_error or target_block is None:
            ctx.route_issues.append(f"{change_id}:proposal-body-not-found:{target}")
            continue
        target_values = control_values(target_block)
        for column, field_name in (
            ("status", "status"),
            ("scope", "scope"),
            ("owner", "owner"),
        ):
            indexed_value = row.get(column, "").strip().casefold()
            body_value = (target_values.get(field_name) or [""])[0]
            if indexed_value != body_value:
                ctx.route_issues.append(
                    f"{change_id}:root-index-{column}-mismatch:{indexed_value or 'empty'}!={body_value or 'empty'}"
                )


def _check_authority_registry(
    ctx: _ProposalContext, authority_rows: list[dict[str, str]]
) -> dict[str, set[str]]:
    """核查旧式决策权限登记表每行，返回 active 权限 -> 已登记范围集合。"""
    active_authority_scopes: dict[str, set[str]] = {}
    authority_row_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(authority_rows, start=1):
        authority_id = normalize_authority_id(row.get("authority_id", ""))
        scope_raw = row.get("scope_path", "").strip("` ")
        scope = normalize_scope_path(scope_raw) if scope_raw else ""
        status = row.get("status", "").strip().casefold()
        evidence = row.get("evidence", "").strip("` ")
        if not authority_id:
            ctx.authority_registry_issues.append(
                f"authority-row-{index}:invalid-authority-id"
            )
        if not scope:
            ctx.authority_registry_issues.append(
                f"authority-row-{index}:missing-scope-path"
            )
        elif scope not in ctx.registry_rows:
            ctx.authority_registry_issues.append(
                f"authority-row-{index}:scope-not-registered:{scope}"
            )
        if status not in DECISION_AUTHORITY_STATUSES:
            ctx.authority_registry_issues.append(
                f"authority-row-{index}:invalid-status:{status or 'empty'}"
            )
        if not evidence or evidence.casefold() in _PLACEHOLDER_VALUES:
            ctx.authority_registry_issues.append(
                f"authority-row-{index}:missing-evidence"
            )
        row_key = (authority_id, scope)
        if authority_id and scope:
            if row_key in authority_row_keys:
                ctx.authority_registry_issues.append(
                    f"duplicate-decision-authority-registration:{authority_id}:{scope}"
                )
            authority_row_keys.add(row_key)
        if authority_id and scope and status == "active":
            active_authority_scopes.setdefault(authority_id, set()).add(scope)
    return active_authority_scopes


def _check_block_authority(
    ctx: _ProposalContext,
    change_id: str,
    raw_values: dict[str, list[str]],
    active_authority_scopes: dict[str, set[str]],
) -> None:
    """核查一条推进态议案的 decision_authority / approved_by / affected_scopes 权限覆盖。"""
    authority_values = [
        normalize_authority_id(value)
        for value in raw_values.get("decision_authority", [])
        if value.strip()
    ]
    authority_values = [value for value in authority_values if value]
    if len(authority_values) != 1:
        ctx.authority_issues.append(
            f"{change_id}:advanced-status-needs-one-registered-decision-authority"
        )
        return
    authority_id = authority_values[0]
    registered_scopes = active_authority_scopes.get(authority_id, set())
    if not registered_scopes:
        ctx.authority_issues.append(
            f"{change_id}:decision-authority-not-active-or-not-registered:{authority_id}"
        )
    approved_by_values = [
        normalize_authority_id(value)
        for value in raw_values.get("approved_by", [])
        if value.strip()
    ]
    approved_by_values = [value for value in approved_by_values if value]
    if approved_by_values != [authority_id]:
        ctx.authority_issues.append(
            f"{change_id}:approved-by-must-match-decision-authority"
        )
    affected_scopes = change_affected_scopes(raw_values)
    if not affected_scopes:
        ctx.authority_issues.append(
            f"{change_id}:advanced-status-needs-affected-scopes"
        )
        return
    for affected_scope in affected_scopes:
        if affected_scope not in ctx.registry_rows:
            ctx.authority_issues.append(
                f"{change_id}:affected-scope-not-registered:{affected_scope}"
            )
        elif not any(
            registered_scope == affected_scope
            or is_scope_ancestor(registered_scope, affected_scope)
            for registered_scope in registered_scopes
        ):
            ctx.authority_issues.append(
                f"{change_id}:decision-authority-outside-registered-scope:"
                f"{authority_id}:{affected_scope}"
            )


def _check_proposal_authorities(
    ctx: _ProposalContext,
    authority_rows: list[dict[str, str]],
    active_authority_scopes: dict[str, set[str]],
) -> None:
    """对所有使用旧式权限字段的推进态议案逐条核查决策权限。"""
    for proposal_text in ctx.texts_by_scope.values():
        for change_id, block in change_blocks(proposal_text).items():
            values = control_values(block)
            raw_values = control_values_raw(block)
            statuses = set(values.get("status", []))
            if not statuses.intersection({"implementing", "verifying", "promoting"}):
                continue
            uses_legacy_authority = bool(authority_rows) or any(
                field_name in raw_values
                for field_name in (
                    "decision_authority",
                    "authority_evidence",
                    "approved_by",
                )
            )
            if not uses_legacy_authority:
                continue
            _check_block_authority(ctx, change_id, raw_values, active_authority_scopes)


def _check_module_proposal_owners(ctx: _ProposalContext) -> None:
    """核查模块级议案的 affected_scopes 归属方均为该模块自身（否则应根正典）。"""
    for proposal_scope, proposal_text in ctx.texts_by_scope.items():
        if proposal_scope == ".":
            continue
        for change_id, block in change_blocks(proposal_text).items():
            affected_scopes = change_affected_scopes(control_values_raw(block))
            if not affected_scopes:
                ctx.cross_module_link_issues.append(
                    f"{change_id}:module-proposal-needs-affected-scopes"
                )
                continue
            owner_scopes: set[str] = set()
            for affected_scope in affected_scopes:
                registry_row = ctx.registry_rows.get(affected_scope)
                if registry_row is None:
                    ctx.cross_module_link_issues.append(
                        f"{change_id}:affected-scope-not-registered:{affected_scope}"
                    )
                    continue
                owner_target = cell_link_target(registry_row.get("logic_change", ""))
                if not owner_target:
                    ctx.cross_module_link_issues.append(
                        f"{change_id}:affected-scope-has-no-proposal-owner:{affected_scope}"
                    )
                    continue
                owner_path = (ctx.root / owner_target).resolve()
                if (
                    not is_within(owner_path, ctx.root)
                    or owner_path.name.casefold() != "logic_change.md"
                ):
                    ctx.cross_module_link_issues.append(
                        f"{change_id}:affected-scope-invalid-proposal-owner:"
                        f"{affected_scope}:{owner_target}"
                    )
                    continue
                owner_scopes.add(
                    owner_path.parent.relative_to(ctx.root).as_posix() or "."
                )
            # RULE-018 两级模型：领域议案必须影响自身领域；可再列其他领域
            # （跨领域），但触及根（宪法）就是修宪案，正文须在根账本。
            if proposal_scope not in owner_scopes:
                ctx.cross_module_link_issues.append(
                    f"{change_id}:domain-proposal-must-include-own-scope:"
                    f"proposal={proposal_scope};owners={','.join(sorted(owner_scopes)) or 'none'}"
                )
            if "." in owner_scopes or "." in affected_scopes:
                ctx.cross_module_link_issues.append(
                    f"{change_id}:constitution-amendment-must-live-in-root-change:{proposal_scope}"
                )


def _has_exact_root_link(
    root_change: Path, cell: str, source_file: Path, change_id: str
) -> bool:
    """Return True when `cell` links exactly to root logic_change.md#<change_id>."""
    target, fragment = cell_link_parts(cell)
    if not target or not fragment:
        return False
    candidate = (source_file.parent / target).resolve()
    return (
        candidate == root_change.resolve()
        and fragment.casefold() == change_id.casefold()
    )


def _resolve_coordination_targets(
    ctx: _ProposalContext,
    row: dict[str, str],
    change_id: str,
    registry_row: dict[str, str],
) -> dict[str, Path]:
    """核查协调索引行的 module_logic_readme / module_logic_change 链接并解析为路径。"""
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
                ctx.cross_module_link_issues.append(
                    f"{change_id}:{column}-must-be-none-for-unrouted-scope"
                )
            continue
        if not target:
            ctx.cross_module_link_issues.append(
                f"{change_id}:{column}-must-be-markdown-link"
            )
            continue
        if normalize_scope_path(target) != normalize_scope_path(registry_target):
            ctx.cross_module_link_issues.append(
                f"{change_id}:{column}-registry-route-mismatch:{target}!={registry_target}"
            )
        target_path = (ctx.root / target).resolve()
        if (
            not is_within(target_path, ctx.root)
            or not target_path.is_file()
            or target_path.name.lower() != expected
        ):
            ctx.cross_module_link_issues.append(
                f"{change_id}:invalid-{column}:{target}"
            )
            continue
        resolved_targets[column] = target_path
    return resolved_targets


def _check_module_change_root_links(
    ctx: _ProposalContext, change_id: str, affected_scope: str, module_change: Path
) -> None:
    """核查模块 logic_change 的文件控制与关联根议案表均精确回链根议案。"""
    module_text, module_error = read_text(module_change)
    if module_error:
        return
    raw_values = control_values_raw(module_text)
    linked_value = " ".join(raw_values.get("linked_root_changes", []))
    linked_ok = any(
        _has_exact_root_link(ctx.root_change, match.group(0), module_change, change_id)
        for match in re.finditer(r"\[[^\]]+\]\([^)]+\)", linked_value)
    )
    if not linked_ok:
        ctx.cross_module_link_issues.append(
            f"{change_id}:module-file-control-missing-root-link:{affected_scope}"
        )
    module_rows = markdown_table_rows(module_text, "关联根议案")
    matching_rows = [
        item
        for item in module_rows
        if normalize_change_id(item.get("change_id", "")) == change_id
    ]
    if not matching_rows or not any(
        _has_exact_root_link(
            ctx.root_change,
            item.get("root_proposal", ""),
            module_change,
            change_id,
        )
        for item in matching_rows
    ):
        ctx.cross_module_link_issues.append(
            f"{change_id}:module-link-table-missing-root-link:{affected_scope}"
        )


def _check_coordination_owner(
    ctx: _ProposalContext,
    change_id: str,
    affected_scope: str,
    registry_row: dict[str, str],
    module_change: Path | None,
) -> None:
    """核查协调索引行的受影响范围拥有 paired 归属方，并记录归属范围。"""
    registry_policy = registry_row.get("doc_policy", "").strip().casefold()
    registry_membership = registry_row.get("membership", "").strip().casefold()
    if module_change is None:
        if registry_policy == "paired" or (
            registry_policy == "inherited" and registry_membership == "in-system"
        ):
            ctx.cross_module_link_issues.append(
                f"{change_id}:affected-scope-missing-paired-owner-route:{affected_scope}"
            )
        return
    owner_scope = module_change.parent.relative_to(ctx.root).as_posix()
    owner_scope = owner_scope or "."
    owner_registry = ctx.registry_rows.get(owner_scope)
    if owner_scope != "." and (
        owner_registry is None
        or owner_registry.get("doc_policy", "").strip().casefold() != "paired"
    ):
        ctx.cross_module_link_issues.append(
            f"{change_id}:affected-scope-owner-must-be-paired:{affected_scope}->{owner_scope}"
        )
    ctx.coordinated_owner_scopes.add((change_id, owner_scope))
    if module_change.resolve() != ctx.root_change.resolve():
        _check_module_change_root_links(ctx, change_id, affected_scope, module_change)


def _check_coordination_row(ctx: _ProposalContext, row: dict[str, str]) -> None:
    """核查跨模块协调索引的一行。"""
    change_id = normalize_change_id(row.get("change_id", ""))
    affected_scope = normalize_scope_path(row.get("affected_scope", ""))
    if not change_id:
        return
    if change_id not in ctx.local_root_ids:
        ctx.cross_module_link_issues.append(
            f"{change_id}:cross-module-body-must-be-root-canonical"
        )
    if not affected_scope or affected_scope == ".":
        ctx.cross_module_link_issues.append(f"{change_id}:invalid-affected-scope")
        return
    ctx.coordinated_scopes.setdefault(change_id, set()).add(affected_scope)
    registry_row = ctx.registry_rows.get(affected_scope)
    if registry_row is None:
        ctx.cross_module_link_issues.append(
            f"{change_id}:affected-scope-not-registered:{affected_scope}"
        )
        return

    resolved_targets = _resolve_coordination_targets(ctx, row, change_id, registry_row)
    _check_coordination_owner(
        ctx,
        change_id,
        affected_scope,
        registry_row,
        resolved_targets.get("module_logic_change"),
    )
    anchor = f'<a id="{change_id.lower()}"></a>'
    if anchor not in ctx.root_text.lower():
        ctx.cross_module_link_issues.append(
            f"{change_id}:root-proposal-missing-explicit-anchor"
        )


def _check_declared_vs_coordinated_scopes(ctx: _ProposalContext) -> None:
    """核查根议案正文 affected_scopes（去根）与协调索引登记范围一致。"""
    for change_id, block in change_blocks(ctx.root_text).items():
        raw_values = control_values_raw(block)
        declared = set()
        for value in raw_values.get("affected_scopes", []):
            declared |= split_control_list(value)
        non_root_declared = declared - {"."}
        table_scopes = ctx.coordinated_scopes.get(change_id, set())
        if non_root_declared != table_scopes:
            ctx.cross_module_link_issues.append(
                f"{change_id}:affected-scope-coordination-mismatch:"
                f"declared={','.join(sorted(non_root_declared)) or 'none'};"
                f"indexed={','.join(sorted(table_scopes)) or 'none'}"
            )


def _check_module_root_link_tables(ctx: _ProposalContext) -> None:
    """核查模块 logic_change 的关联根议案表无孤儿行且回链精确。"""
    for scope, module_text in ctx.texts_by_scope.items():
        if scope == ".":
            continue
        module_change = ctx.root / scope / "logic_change.md"
        for row in markdown_table_rows(module_text, "关联根议案"):
            change_id = normalize_change_id(row.get("change_id", ""))
            if not change_id:
                continue
            if (change_id, scope) not in ctx.coordinated_owner_scopes:
                ctx.cross_module_link_issues.append(
                    f"{change_id}:orphan-module-root-link:{scope}"
                )
            if not _has_exact_root_link(
                ctx.root_change, row.get("root_proposal", ""), module_change, change_id
            ):
                ctx.cross_module_link_issues.append(
                    f"{change_id}:invalid-module-root-link:{scope}"
                )


def audit_proposal_integrity(root: Path, audits: list[ModuleAudit]) -> dict:
    ids_by_scope, texts_by_scope = _collect_proposal_texts(root, audits)

    all_ids: dict[str, list[str]] = {}
    for scope, ids in ids_by_scope.items():
        for change_id in ids:
            all_ids.setdefault(change_id, []).append(scope)
    duplicate_ids = sorted(
        f"{change_id}:{','.join(scopes)}"
        for change_id, scopes in all_ids.items()
        if len(scopes) > 1
    )

    root_text = texts_by_scope.get(".", "")
    missing_root_index, unknown_root_index = _check_root_index_coverage(
        ids_by_scope, root_text
    )

    registry_text, _ = read_text(root / "logic_readme.md")
    ctx = _ProposalContext(
        root=root,
        root_change=root / "logic_change.md",
        root_text=root_text,
        texts_by_scope=texts_by_scope,
        local_root_ids=set(ids_by_scope.get(".", [])),
        registry_rows={
            normalize_scope_path(row.get("scope_path", "")): row
            for row in markdown_table_rows(registry_text, "范围登记表")
            if row.get("scope_path", "").strip()
        },
    )
    _check_root_index_routes(ctx)

    authority_rows = markdown_table_rows(registry_text, "决策权限登记")
    active_authority_scopes = _check_authority_registry(ctx, authority_rows)
    _check_proposal_authorities(ctx, authority_rows, active_authority_scopes)

    _check_module_proposal_owners(ctx)
    for row in markdown_table_rows(root_text, "跨模块协调索引"):
        _check_coordination_row(ctx, row)
    _check_declared_vs_coordinated_scopes(ctx)
    _check_module_root_link_tables(ctx)

    return {
        "duplicate_ids": duplicate_ids,
        "missing_root_index": sorted(set(missing_root_index)),
        "unknown_root_index": unknown_root_index,
        "route_issues": sorted(set(ctx.route_issues)),
        "cross_module_link_issues": sorted(set(ctx.cross_module_link_issues)),
        "authority_registry_issues": sorted(set(ctx.authority_registry_issues)),
        "authority_issues": sorted(set(ctx.authority_issues)),
        "closed_change_ids_still_active": [],
    }


# ---------------------------------------------------------------------------
# current-state 静态门（audit_current_state_integrity）
# ---------------------------------------------------------------------------


@dataclass
class _CurrentStateContext:
    """current-state 静态门的输入、中间查找表与四类问题清单。"""

    root: Path
    all_dirs: bool
    module_routes: dict
    readme_text: str = ""
    change_text: str = ""
    readme_governance_mode: str = ""
    readme_governance_ref: str = ""
    change_raw: dict[str, list[str]] = field(default_factory=dict)
    current_policy_rows: list[dict[str, str]] = field(default_factory=list)
    registered_scopes: set[str] = field(default_factory=set)
    module_scopes: dict[str, str] = field(default_factory=dict)
    module_anchor_scopes: dict[str, str] = field(default_factory=dict)
    index_rows: list[dict[str, str]] = field(default_factory=list)
    gazette_rows: list[dict[str, str]] = field(default_factory=list)
    domain_change_ids: dict[str, str] = field(default_factory=dict)
    ledger_blocks: dict[str, dict[str, str]] = field(default_factory=dict)
    ledger_modes: dict[str, str] = field(default_factory=dict)
    rule_dates: dict[str, str] = field(default_factory=dict)
    body_ids: set[str] = field(default_factory=set)
    topic_members: dict[str, set[str]] = field(default_factory=dict)
    topics_by_change: dict[str, set[str]] = field(default_factory=dict)
    declared_topics_by_change: dict[str, str] = field(default_factory=dict)
    document_issues: list[str] = field(default_factory=list)
    scope_registry_issues: list[str] = field(default_factory=list)
    proposal_issues: list[str] = field(default_factory=list)
    responsibility_issues: list[str] = field(default_factory=list)

    def result(self) -> dict:
        return {
            "document_issues": sorted(set(self.document_issues)),
            "scope_registry_issues": sorted(set(self.scope_registry_issues)),
            "proposal_issues": sorted(set(self.proposal_issues)),
            "responsibility_issues": sorted(set(self.responsibility_issues)),
        }


def _check_root_document_shape(
    ctx: _CurrentStateContext, readme: Path, change: Path
) -> None:
    """核查根两份现行文档的必备章节、字段与链接可达性。"""
    readme_sections, readme_fields, readme_links = inspect_markdown(
        readme, ctx.root, CURRENT_README_SECTIONS, CURRENT_README_FIELDS
    )
    change_sections, change_fields, change_links = inspect_markdown(
        change, ctx.root, CURRENT_CHANGE_SECTIONS, CURRENT_CHANGE_FIELDS
    )
    issues = ctx.document_issues
    issues.extend(f"logic_readme:missing-section:{item}" for item in readme_sections)
    issues.extend(f"logic_readme:missing-field:{item}" for item in readme_fields)
    issues.extend(f"logic_readme:broken-link:{item}" for item in readme_links)
    issues.extend(f"logic_change:missing-section:{item}" for item in change_sections)
    issues.extend(f"logic_change:missing-field:{item}" for item in change_fields)
    issues.extend(f"logic_change:broken-link:{item}" for item in change_links)


def _check_legacy_authority_registry(ctx: _CurrentStateContext) -> None:
    """核查根 logic_readme 不再保留旧式“决策权限登记”章节。"""
    if re.search(r"^\s*##\s+决策权限登记\s*$", ctx.readme_text, re.MULTILINE):
        ctx.responsibility_issues.append(
            "logic_readme:legacy-decision-authority-registry-must-be-migrated"
        )


def _check_current_policy_table(ctx: _CurrentStateContext) -> None:
    """核查“当前制度”表的列、非空行以及每行规则/why/等级/决策链接/复核日期。"""
    current_policy_rows = markdown_table_rows(ctx.readme_text, "当前制度")
    ctx.current_policy_rows = current_policy_rows
    current_policy_headers = markdown_table_headers(ctx.readme_text, "当前制度")
    if current_policy_headers != CURRENT_POLICY_HEADERS:
        ctx.document_issues.append("logic_readme:current-policy-invalid-columns")
    if not current_policy_rows:
        ctx.document_issues.append("logic_readme:current-policy-needs-at-least-one-row")
    for index, row in enumerate(current_policy_rows, start=1):
        rule_id = row.get("rule_id", "").strip()
        rule_level = row.get("规则等级", "").strip().casefold()
        rule = row.get("当前有效规则/行为", "").strip()
        why = row.get("why（仅一句可审计摘要）", "").strip()
        if any(
            not value
            or value.casefold() in _PLACEHOLDER_VALUES
            or "<" in value
            or ">" in value
            for value in (rule_id, rule, why)
        ):
            ctx.document_issues.append(
                f"logic_readme:current-policy-row-{index}-needs-rule-and-why"
            )
        if rule_level not in {"key", "ordinary"}:
            ctx.document_issues.append(
                f"logic_readme:current-policy-row-{index}-invalid-rule-level:"
                f"{rule_level or 'empty'}"
            )
        if rule_level == "key" and not is_immutable_decision_record_link(
            row.get("决策记录", "")
        ):
            ctx.document_issues.append(
                f"logic_readme:current-policy-row-{index}-key-needs-immutable-decision-link"
            )
        last_reviewed = row.get("last_reviewed", "").strip()
        if not is_iso_date(last_reviewed):
            ctx.document_issues.append(
                f"logic_readme:current-policy-row-{index}-last-reviewed-must-be-date"
            )
        elif rule_id:
            ctx.rule_dates[rule_id.upper()] = last_reviewed


def _check_code_map_table(ctx: _CurrentStateContext) -> None:
    """核查“代码地图”表的列与每行关键列非空。"""
    code_map_headers = markdown_table_headers(ctx.readme_text, "代码地图")
    code_map_rows = markdown_table_rows(ctx.readme_text, "代码地图")
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
        ctx.document_issues.append("logic_readme:code-map-invalid-columns")
    if not code_map_rows:
        ctx.document_issues.append("logic_readme:code-map-needs-at-least-one-row")
    for index, row in enumerate(code_map_rows, start=1):
        for column in ("路径/稳定锚点", "artifact_class/layer", "职责", "权威来源"):
            value = row.get(column, "").strip()
            if (
                not value
                or value.casefold() in _PLACEHOLDER_VALUES
                or "<" in value
                or ">" in value
            ):
                ctx.document_issues.append(
                    f"logic_readme:code-map-row-{index}-missing-{column}"
                )


_FieldLookup = Callable[..., list[str]]


def _check_readme_identity_fields(
    ctx: _CurrentStateContext,
    registered_field: _FieldLookup,
    readme_values: dict[str, list[str]],
    readme_raw: dict[str, list[str]],
) -> None:
    """核查根 logic_readme 身份字段（module_id/scope/parent/membership 等）与 owner。"""
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
    for field_name, expected in expected_readme_values.items():
        values = registered_field(field_name)
        normalized = [
            normalize_scope_path(value) if field_name in {"scope", "scope_path"} else value
            for value in values
        ]
        if normalized != [expected]:
            ctx.document_issues.append(
                f"logic_readme:{field_name}-must-be-single-{expected}:"
                + (",".join(values) or "missing")
            )
    if len(readme_raw.get("owner", [])) != 1 or not has_meaningful_value(
        readme_values, "owner"
    ):
        ctx.document_issues.append("logic_readme:owner-must-be-single-meaningful-value")


def _check_readme_governance(
    ctx: _CurrentStateContext,
    readme_values: dict[str, list[str]],
    readme_raw: dict[str, list[str]],
) -> None:
    """核查根 logic_readme 的 governance_mode / governance_ref / 治理证据，并记录供比对。"""
    readme_governance_mode = (readme_values.get("governance_mode") or [""])[0]
    readme_governance_ref = (readme_values.get("governance_ref") or [""])[0]
    ctx.readme_governance_mode = readme_governance_mode
    ctx.readme_governance_ref = readme_governance_ref
    if readme_values.get("governance_mode", []) != [readme_governance_mode] or (
        readme_governance_mode not in GOVERNANCE_MODES
    ):
        ctx.document_issues.append("logic_readme:invalid-governance-mode")
    if len(readme_raw.get("governance_ref", [])) != 1 or not has_meaningful_value(
        readme_values, "governance_ref"
    ):
        ctx.document_issues.append("logic_readme:governance-ref-must-be-meaningful")
    ctx.document_issues.extend(
        governance_evidence_issues(readme_values, label="logic_readme")
    )


def _check_readme_freshness(
    ctx: _CurrentStateContext,
    readme_values: dict[str, list[str]],
    readme_raw: dict[str, list[str]],
) -> None:
    """核查 last_verified 唯一且为日期，并按 review_trigger 评估文档与制度行的新鲜度。"""
    last_verified = readme_raw.get("last_verified", [])
    if len(last_verified) != 1:
        ctx.document_issues.append("logic_readme:last_verified-must-appear-once")
    else:
        try:
            date.fromisoformat(last_verified[0])
        except ValueError:
            ctx.document_issues.append("logic_readme:last_verified-must-be-date")
    if len(last_verified) == 1:
        readme_trigger = (readme_values.get("review_trigger") or [""])[0]
        ctx.document_issues.extend(
            review_freshness_issues(
                last_verified[0], readme_trigger, label="logic_readme"
            )
        )
        for index, row in enumerate(ctx.current_policy_rows, start=1):
            reviewed = row.get("last_reviewed", "").strip()
            if is_iso_date(reviewed):
                ctx.document_issues.extend(
                    review_freshness_issues(
                        reviewed,
                        readme_trigger,
                        label=f"logic_readme:current-policy-row-{index}",
                    )
                )


def _check_readme_canonical_pointers(
    ctx: _CurrentStateContext, registered_field: _FieldLookup
) -> None:
    """核查 canonical_readme / canonical_change 指向根两份现行文档。"""
    for field_name, expected in (
        ("canonical_readme", "logic_readme.md"),
        ("canonical_change", "logic_change.md"),
    ):
        values = registered_field(field_name, raw=True)
        normalized = [normalize_scope_path(value.strip("<>")) for value in values]
        if normalized != [expected]:
            ctx.document_issues.append(
                f"logic_readme:{field_name}-must-be-{expected}:"
                + (",".join(values) or "missing")
            )


def _check_readme_repository_policies(ctx: _CurrentStateContext) -> None:
    """核查全文级 coverage_policy / membership_policy / layer_policy / version_root / temp_root。"""
    coverage = control_values(ctx.readme_text).get("coverage_policy", [])
    if coverage not in (["governed-boundaries"], ["registry-every-folder"]):
        ctx.document_issues.append(
            "logic_readme:invalid-coverage-policy:" + (",".join(coverage) or "missing")
        )
    if coverage == ["registry-every-folder"] and not ctx.all_dirs:
        ctx.scope_registry_issues.append(
            "registry-every-folder-policy-requires---all-dirs"
        )
    all_readme_values = control_values(ctx.readme_text)
    all_readme_raw = control_values_raw(ctx.readme_text)
    if all_readme_values.get("membership_policy", []) != ["root-registry-first"]:
        ctx.document_issues.append(
            "logic_readme:membership_policy-must-be-root-registry-first"
        )
    if len(all_readme_raw.get("layer_policy", [])) != 1 or not has_meaningful_value(
        all_readme_values, "layer_policy"
    ):
        ctx.document_issues.append(
            "logic_readme:layer_policy-must-be-single-meaningful-value"
        )
    for field_name, expected in (
        ("version_root", "logic_version"),
        ("temp_root", "logic_version/working"),
    ):
        values = all_readme_raw.get(field_name, [])
        normalized = [normalize_scope_path(value) for value in values]
        if normalized != [expected]:
            ctx.document_issues.append(
                f"logic_readme:{field_name}-must-be-{expected}:"
                + (",".join(values) or "missing")
            )


def _check_readme_control(ctx: _CurrentStateContext) -> None:
    """核查根 logic_readme 文档控制区：身份字段、治理、新鲜度、正典指针与仓库策略。"""
    readme_control = markdown_section_text(ctx.readme_text, "文档控制")
    readme_values = control_values(readme_control)
    readme_raw = control_values_raw(readme_control)
    # `registry_status` and the two canonical pointers are defined under
    # "范围登记与归属" by references/logic-readme-template.md, not under
    # "文档控制".  Read the registry section as a fallback so a
    # template-conformant document is not reported as missing them; the
    # single-value requirement below still applies to the merged result.
    registry_control = markdown_section_text(ctx.readme_text, "范围登记与归属")
    registry_values = control_values(registry_control)
    registry_raw = control_values_raw(registry_control)

    def registered_field(field_name: str, raw: bool = False) -> list[str]:
        """Look the field up in 文档控制 first, then 范围登记与归属."""
        primary = (readme_raw if raw else readme_values).get(field_name, [])
        if primary:
            return primary
        return (registry_raw if raw else registry_values).get(field_name, [])

    _check_readme_identity_fields(ctx, registered_field, readme_values, readme_raw)
    _check_readme_governance(ctx, readme_values, readme_raw)
    _check_readme_freshness(ctx, readme_values, readme_raw)
    _check_readme_canonical_pointers(ctx, registered_field)
    _check_readme_repository_policies(ctx)


def _check_change_control(ctx: _CurrentStateContext) -> None:
    """核查根 logic_change 文档控制区，并与 logic_readme 的治理模式/引用比对。"""
    change_control = markdown_section_text(ctx.change_text, "文档控制")
    change_values = control_values(change_control)
    change_raw = control_values_raw(change_control)
    ctx.change_raw = change_raw
    for field_name, expected in (
        ("scope", "."),
        ("scope_path", "."),
        ("module_id", "mod-root"),
    ):
        values = change_values.get(field_name, [])
        normalized = [
            normalize_scope_path(value) if field_name in {"scope", "scope_path"} else value
            for value in values
        ]
        if normalized != [expected]:
            ctx.document_issues.append(
                f"logic_change:{field_name}-must-be-single-{expected}:"
                + (",".join(values) or "missing")
            )
    current_policy = [
        normalize_scope_path(value.strip("<>"))
        for value in change_raw.get("current_policy", [])
    ]
    if current_policy != ["logic_readme.md"]:
        ctx.document_issues.append(
            "logic_change:current_policy-must-be-logic_readme.md:"
            + (",".join(change_raw.get("current_policy", [])) or "missing")
        )
    for field_name in (
        "owner",
        "governance_mode",
        "governance_ref",
        "last_updated",
        "active_changes",
    ):
        if len(change_raw.get(field_name, [])) != 1:
            ctx.document_issues.append(
                f"logic_change:{field_name}-must-appear-once:"
                f"{len(change_raw.get(field_name, []))}"
            )
    if not has_meaningful_value(change_values, "owner"):
        ctx.document_issues.append("logic_change:owner-must-be-meaningful")
    change_governance_mode = (change_values.get("governance_mode") or [""])[0]
    change_governance_ref = (change_values.get("governance_ref") or [""])[0]
    if change_governance_mode not in GOVERNANCE_MODES:
        ctx.document_issues.append("logic_change:invalid-governance-mode")
    if not has_meaningful_value(change_values, "governance_ref"):
        ctx.document_issues.append("logic_change:governance-ref-must-be-meaningful")
    ctx.document_issues.extend(
        governance_evidence_issues(change_values, label="logic_change")
    )
    if change_governance_mode != ctx.readme_governance_mode:
        ctx.document_issues.append(
            "governance-mode-mismatch-between-current-documents"
        )
    if change_governance_ref != ctx.readme_governance_ref:
        ctx.document_issues.append("governance-ref-mismatch-between-current-documents")
    last_updated = change_raw.get("last_updated", [])
    if len(last_updated) == 1:
        try:
            date.fromisoformat(last_updated[0])
        except ValueError:
            ctx.document_issues.append("logic_change:last_updated-must-be-date")


def _classify_root_semantic_issues(
    ctx: _CurrentStateContext, root_module: ModuleAudit
) -> None:
    """将根模块语义问题分流到 responsibility / proposal / document 三类清单。"""
    for issue in root_module.semantic_issues:
        if issue.startswith("logic_change:") and any(
            marker in issue
            for marker in (
                "missing-changed-by",
                "legacy-reviewed_by",
                "legacy-review_ref",
            )
        ):
            ctx.responsibility_issues.append(issue)
        elif issue.startswith("logic_change:CHG-"):
            ctx.proposal_issues.append(issue.removeprefix("logic_change:"))
        else:
            ctx.document_issues.append(issue)


def _collect_scope_registry_issues(ctx: _CurrentStateContext) -> None:
    """Fold module-route findings into scope_registry_issues with their key prefix."""
    for key in (
        "route_issues",
        "duplicate_module_ids",
        "duplicate_scope_paths",
        "unregistered_governance_dirs",
        "hierarchy_issues",
    ):
        ctx.scope_registry_issues.extend(
            f"{key}:{item}" for item in ctx.module_routes.get(key, [])
        )


def _collect_registry_lookups(ctx: _CurrentStateContext) -> None:
    """Build registered-scope, module-id->scope and anchor->scope lookups from route rows."""
    rows = ctx.module_routes.get("rows", [])
    ctx.registered_scopes = {
        normalize_scope_path(row.get("scope_path", ""))
        for row in rows
        if row.get("scope_path", "").strip()
    }
    ctx.module_scopes = {
        row.get("module_id", "").strip().casefold(): normalize_scope_path(
            row.get("scope_path", "")
        )
        for row in rows
        if row.get("module_id", "").strip() and row.get("scope_path", "").strip()
    }
    module_anchor_scopes: dict[str, str] = {}
    for row in rows:
        target, fragment = cell_link_parts(row.get("logic_readme", ""))
        scope_path = normalize_scope_path(row.get("scope_path", ""))
        if target == "logic_readme.md" and fragment and scope_path:
            module_anchor_scopes[fragment.casefold()] = scope_path
    ctx.module_anchor_scopes = module_anchor_scopes


def _check_change_body_index(ctx: _CurrentStateContext) -> None:
    """核查议案正文 ID 无重复、active_changes 计数正确、正文与活跃索引双向一致。"""
    body_id_list = change_heading_ids(ctx.change_text)
    body_ids = set(body_id_list)
    ctx.body_ids = body_ids
    duplicate_body_ids = sorted(
        {change_id for change_id in body_id_list if body_id_list.count(change_id) > 1}
    )
    for change_id in duplicate_body_ids:
        ctx.proposal_issues.append(f"duplicate-change-body:{change_id}")

    declared_active_changes = (ctx.change_raw.get("active_changes") or [""])[0]
    expected_active_changes = str(len(body_id_list)) if body_id_list else "none"
    if declared_active_changes.casefold() != expected_active_changes:
        ctx.proposal_issues.append(
            "active_changes-count-mismatch:"
            f"{declared_active_changes or 'missing'}!={expected_active_changes}"
        )
    all_index_rows = markdown_table_rows(ctx.change_text, "活跃议案索引")
    # RULE-018：根索引是全项目公报——指向领域账本的行（proposal_path 目标不是
    # 本文件）在 _check_gazette_rows 单独核查，不参与"正文 <-> 索引"双向比对。
    index_rows = []
    for row in all_index_rows:
        target, _fragment = cell_link_parts(row.get("proposal_path", ""))
        if target and normalize_scope_path(target) != "logic_change.md":
            ctx.gazette_rows.append(row)
        else:
            index_rows.append(row)
    ctx.index_rows = index_rows
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
            ctx.proposal_issues.append("ids-missing-from-index:" + ",".join(missing))
        if extra:
            ctx.proposal_issues.append("index-ids-without-body:" + ",".join(extra))


def _check_topic_index(ctx: _CurrentStateContext) -> None:
    """核查“讨论主题索引”表的列与每行 topic_id / related_changes，并建立主题成员表。"""
    expected_topic_headers = [
        "topic_id",
        "同类议题/共享问题",
        "coordinator",
        "discussion_refs",
        "related_changes",
        "status",
    ]
    topic_headers = markdown_table_headers(ctx.change_text, "讨论主题索引")
    if topic_headers != expected_topic_headers:
        ctx.document_issues.append("logic_change:topic-index-invalid-columns")
    topic_rows = markdown_table_rows(ctx.change_text, "讨论主题索引")
    for index, row in enumerate(topic_rows, start=1):
        topic_id = normalize_topic_id(row.get("topic_id", ""))
        if not topic_id:
            ctx.proposal_issues.append(f"topic-index-row-{index}:invalid-topic-id")
            continue
        if topic_id in ctx.topic_members:
            ctx.proposal_issues.append(f"topic-index-duplicate-topic-id:{topic_id}")
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
                    ctx.proposal_issues.append(
                        f"topic-index-row-{index}:duplicate-related-change:{change_id}"
                    )
                related_ids.add(change_id)
            else:
                invalid_related_items.append(item)
        if not related_items or invalid_related_items:
            ctx.proposal_issues.append(
                f"topic-index-row-{index}:related-changes-must-be-chg-or-none"
            )
        if has_none and related_ids:
            ctx.proposal_issues.append(
                f"topic-index-row-{index}:related-changes-cannot-mix-none"
            )
        ctx.topic_members[topic_id] = related_ids
        for related_change in related_ids:
            if related_change not in ctx.body_ids:
                ctx.proposal_issues.append(
                    f"topic-index-row-{index}:unknown-active-change:{related_change}"
                )
            ctx.topics_by_change.setdefault(related_change, set()).add(topic_id)


def _check_block_responsibility(
    ctx: _CurrentStateContext,
    change_id: str,
    values: dict[str, list[str]],
    raw_values: dict[str, list[str]],
) -> None:
    """核查议案块的旧字段迁移、单值字段、effective、owner/changed_by 与独立评审。"""
    legacy_authority_fields = sorted(
        {"decision_authority", "authority_evidence", "approved_by"} & set(raw_values)
    )
    if legacy_authority_fields:
        ctx.responsibility_issues.append(
            f"{change_id}:legacy-authority-fields-must-be-migrated:"
            + ",".join(legacy_authority_fields)
        )
    legacy_review_fields = sorted({"reviewed_by", "review_ref"} & set(raw_values))
    if legacy_review_fields:
        ctx.responsibility_issues.append(
            f"{change_id}:legacy-ambiguous-review-fields-must-be-migrated:"
            + ",".join(legacy_review_fields)
        )
    for field_name in ("status", "effective", "owner", "changed_by", "scope"):
        entries = raw_values.get(field_name, [])
        if len(entries) != 1:
            target = (
                ctx.responsibility_issues
                if field_name in {"owner", "changed_by"}
                else ctx.proposal_issues
            )
            target.append(f"{change_id}:{field_name}-must-appear-once:{len(entries)}")
    if values.get("effective", []) != ["false"]:
        ctx.proposal_issues.append(f"{change_id}:effective-must-be-false")
    for field_name in ("owner", "changed_by"):
        if not has_meaningful_value(values, field_name):
            ctx.responsibility_issues.append(f"{change_id}:missing-{field_name}")
    if (
        ctx.readme_governance_mode == "collaborative"
        and (values.get("decision_gate") or [""])[0] == "required"
        and (values.get("semantic_review_state") or [""])[0] == "passed"
    ):
        changed_by = (values.get("changed_by") or [""])[0]
        reviewed_by = (values.get("semantic_reviewed_by") or [""])[0]
        if reviewed_by == "self" or reviewed_by == changed_by:
            ctx.responsibility_issues.append(
                f"{change_id}:collaborative-high-risk-review-must-be-independent"
            )


def _check_block_topic(
    ctx: _CurrentStateContext,
    change_id: str,
    raw_values: dict[str, list[str]],
    tier: str = "full",
) -> None:
    """核查议案块 topic_id 唯一、合法，且与讨论主题索引双向一致。

    RULE-023：personal 档可省略 topic_id，缺省视同 none。
    """
    topic_values = raw_values.get("topic_id", [])
    if not topic_values and tier == "personal":
        topic_values = ["none"]
    if len(topic_values) != 1:
        ctx.proposal_issues.append(
            f"{change_id}:topic-id-must-appear-once:{len(topic_values)}"
        )
        return
    topic_value = topic_values[0]
    if is_none_like(topic_value):
        if change_id in ctx.topics_by_change:
            ctx.proposal_issues.append(
                f"{change_id}:topic-index-lists-change-with-topic-id-none"
            )
        return
    topic_id = normalize_topic_id(topic_value)
    if not topic_id:
        ctx.proposal_issues.append(f"{change_id}:invalid-topic-id:{topic_value}")
        return
    ctx.declared_topics_by_change[change_id] = topic_id
    if topic_id not in ctx.topic_members:
        ctx.proposal_issues.append(f"{change_id}:topic-not-indexed:{topic_id}")
    elif change_id not in ctx.topic_members[topic_id]:
        ctx.proposal_issues.append(f"{change_id}:topic-index-missing-change:{topic_id}")


def _check_block_scopes(
    ctx: _CurrentStateContext, change_id: str, raw_values: dict[str, list[str]]
) -> set[str]:
    """核查议案块 affected_scopes 非空、已登记且包含主 scope；返回受影响范围集合。"""
    affected_scopes = change_affected_scopes(raw_values)
    if not affected_scopes:
        ctx.proposal_issues.append(f"{change_id}:missing-affected-scopes")
    for affected_scope in sorted(affected_scopes):
        if affected_scope not in ctx.registered_scopes:
            ctx.proposal_issues.append(
                f"{change_id}:affected-scope-not-registered:{affected_scope}"
            )

    primary_scope = normalize_scope_path((raw_values.get("scope") or [""])[0])
    if primary_scope in ctx.registered_scopes and primary_scope not in affected_scopes:
        ctx.proposal_issues.append(
            f"{change_id}:primary-scope-missing-from-affected-scopes:"
            f"{primary_scope}"
        )
    return affected_scopes


def _check_block_related_modules(
    ctx: _CurrentStateContext,
    change_id: str,
    raw_values: dict[str, list[str]],
    affected_scopes: set[str],
) -> None:
    """核查 related_modules 引用为已登记 MOD-ID 或根制度锚点，且其范围落在 affected_scopes 内。"""
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
                ctx.proposal_issues.append(
                    f"{change_id}:related-module-link-must-target-root-policy-anchor"
                )
                continue
            related_scope = ctx.module_anchor_scopes.get(fragment.casefold())
            if related_scope is None:
                ctx.proposal_issues.append(
                    f"{change_id}:related-module-anchor-not-registered:{fragment}"
                )
            elif related_scope not in affected_scopes:
                ctx.proposal_issues.append(
                    f"{change_id}:related-module-anchor-scope-missing-from-affected-scopes:"
                    f"{fragment}:{related_scope}"
                )
    related_values = raw_values.get("related_modules", [])
    if (
        related_values
        and any(value.casefold() != "none" for value in related_values)
        and not recognized_related_reference
    ):
        ctx.proposal_issues.append(
            f"{change_id}:related-modules-needs-registered-id-or-root-anchor"
        )
    for module_id in sorted(related_module_ids):
        related_scope = ctx.module_scopes.get(module_id)
        if related_scope is None:
            ctx.proposal_issues.append(
                f"{change_id}:related-module-not-registered:{module_id}"
            )
        elif related_scope not in affected_scopes:
            ctx.proposal_issues.append(
                f"{change_id}:related-module-scope-missing-from-affected-scopes:"
                f"{module_id}:{related_scope}"
            )


def _check_block_index_row(
    ctx: _CurrentStateContext, change_id: str, values: dict[str, list[str]]
) -> None:
    """核查议案块在活跃索引中恰有一行，且链接、显式锚点与 status/scope/owner 一致。"""
    matching_rows = [
        row
        for row in ctx.index_rows
        if normalize_change_id(row.get("change_id", "")) == change_id
    ]
    if len(matching_rows) != 1:
        ctx.proposal_issues.append(
            f"{change_id}:index-row-count-must-be-one:{len(matching_rows)}"
        )
        return
    row = matching_rows[0]
    target, fragment = cell_link_parts(row.get("proposal_path", ""))
    if target != "logic_change.md" or fragment != change_id.casefold():
        ctx.proposal_issues.append(
            f"{change_id}:proposal-path-must-target-logic_change-anchor"
        )
    anchor = f'<a id="{change_id.casefold()}"></a>'
    anchor_count = ctx.change_text.casefold().count(anchor)
    if anchor_count != 1:
        ctx.proposal_issues.append(
            f"{change_id}:explicit-anchor-count-must-be-one:{anchor_count}"
        )
    for column, field_name in (
        ("status", "status"),
        ("scope", "scope"),
        ("owner", "owner"),
    ):
        indexed = row.get(column, "").strip().casefold()
        body_value = (values.get(field_name) or [""])[0]
        if indexed != body_value:
            ctx.proposal_issues.append(
                f"{change_id}:index-{column}-mismatch:{indexed or 'empty'}!={body_value or 'empty'}"
            )


def _check_change_blocks(ctx: _CurrentStateContext) -> None:
    """逐个议案块核查责任字段、主题、范围、关联模块与索引行。"""
    ledger_mode = (control_values(ctx.change_text).get("governance_mode") or [""])[0]
    root_blocks = change_blocks(ctx.change_text)
    ctx.ledger_blocks["logic_change.md"] = root_blocks
    ctx.ledger_modes["logic_change.md"] = ledger_mode
    for change_id, block in root_blocks.items():
        values = control_values(block)
        raw_values = control_values_raw(block)
        tier = change_field_tier(values, ledger_mode)
        _check_block_responsibility(ctx, change_id, values, raw_values)
        _check_block_topic(ctx, change_id, raw_values, tier)
        affected_scopes = _check_block_scopes(ctx, change_id, raw_values)
        _check_block_related_modules(ctx, change_id, raw_values, affected_scopes)
        _check_block_index_row(ctx, change_id, values)


def _check_topic_memberships(ctx: _CurrentStateContext) -> None:
    """核查每个议案至多属于一个主题，且索引归属与正文声明一致。"""
    for change_id, topic_ids in ctx.topics_by_change.items():
        declared_topic = ctx.declared_topics_by_change.get(change_id)
        if len(topic_ids) > 1:
            ctx.proposal_issues.append(
                f"{change_id}:multiple-topic-memberships:"
                + ",".join(sorted(topic_ids))
            )
        elif declared_topic and declared_topic not in topic_ids:
            ctx.proposal_issues.append(
                f"{change_id}:topic-index-and-body-mismatch:"
                + ",".join(sorted(topic_ids))
                + f"!={declared_topic}"
            )


# ---------------------------------------------------------------------------
# RULE-018 一二级拆分法：领域（部门法）文档与根公报核查
# ---------------------------------------------------------------------------


def _registered_domain_rows(ctx: _CurrentStateContext) -> list[tuple[str, str]]:
    """范围登记表中 in-system + paired 的非根行 -> [(module_id, scope_path)]。"""
    domains: list[tuple[str, str]] = []
    for row in ctx.module_routes.get("rows", []):
        policy = (row.get("doc_policy") or "").strip().strip("`").casefold()
        membership = (row.get("membership") or "").strip().strip("`").casefold()
        scope = normalize_scope_path(row.get("scope_path", ""))
        if policy != "paired" or membership != "in-system" or scope in {"", "."}:
            continue
        domains.append((row.get("module_id", "").strip(), scope))
    return domains


def _check_domain_readme(ctx: _CurrentStateContext, scope: str) -> None:
    """领域 readme 的"当前制度"与"代码地图"表同受根表列/行检查（规则行搬迁不降级）。"""
    readme = ctx.root / scope / "logic_readme.md"
    text, error = read_text(readme)
    if error:
        ctx.document_issues.append(f"{scope}/logic_readme:unreadable:{error}")
        return
    label = f"{scope}/logic_readme"
    headers = markdown_table_headers(text, "当前制度")
    if headers != CURRENT_POLICY_HEADERS:
        ctx.document_issues.append(f"{label}:current-policy-invalid-columns")
    for index, row in enumerate(markdown_table_rows(text, "当前制度"), start=1):
        rule_id = row.get("rule_id", "").strip()
        rule_level = row.get("规则等级", "").strip().casefold()
        rule = row.get("当前有效规则/行为", "").strip()
        why = row.get("why（仅一句可审计摘要）", "").strip()
        if any(
            not value or value.casefold() in _PLACEHOLDER_VALUES or "<" in value or ">" in value
            for value in (rule_id, rule, why)
        ):
            ctx.document_issues.append(f"{label}:current-policy-row-{index}-needs-rule-and-why")
        if rule_level not in {"key", "ordinary"}:
            ctx.document_issues.append(
                f"{label}:current-policy-row-{index}-invalid-rule-level:{rule_level or 'empty'}"
            )
        if rule_level == "key" and not is_immutable_decision_record_link(row.get("决策记录", "")):
            ctx.document_issues.append(
                f"{label}:current-policy-row-{index}-key-needs-immutable-decision-link"
            )
        last_reviewed = row.get("last_reviewed", "").strip()
        if not is_iso_date(last_reviewed):
            ctx.document_issues.append(f"{label}:current-policy-row-{index}-last-reviewed-must-be-date")
        elif rule_id:
            ctx.rule_dates[rule_id.upper()] = last_reviewed
    for index, row in enumerate(markdown_table_rows(text, "代码地图"), start=1):
        for column in ("路径/稳定锚点", "artifact_class/layer", "职责", "权威来源"):
            value = row.get(column, "").strip()
            if not value or value.casefold() in _PLACEHOLDER_VALUES or "<" in value or ">" in value:
                ctx.document_issues.append(f"{label}:code-map-row-{index}-missing-{column}")


def _check_domain_block(
    ctx: _CurrentStateContext,
    scope: str,
    change_id: str,
    block: str,
    local_rows: list[dict[str, str]],
    ledger_mode: str,
) -> None:
    """核查一条领域 CHG：责任字段、范围归属、本地索引行与根公报行。"""
    values = control_values(block)
    raw_values = control_values_raw(block)
    _check_block_responsibility(ctx, change_id, values, raw_values)
    affected_scopes = change_affected_scopes(raw_values)
    if not affected_scopes:
        ctx.proposal_issues.append(f"{change_id}:missing-affected-scopes")
    for affected_scope in sorted(affected_scopes):
        if affected_scope not in ctx.registered_scopes:
            ctx.proposal_issues.append(f"{change_id}:affected-scope-not-registered:{affected_scope}")
    if affected_scopes and scope not in affected_scopes:
        ctx.proposal_issues.append(f"{change_id}:domain-proposal-must-include-own-scope:{scope}")
    if "." in affected_scopes:
        ctx.proposal_issues.append(f"{change_id}:constitution-amendment-must-live-in-root-change")
    matching = [
        row for row in local_rows if normalize_change_id(row.get("change_id", "")) == change_id
    ]
    if len(matching) != 1:
        ctx.proposal_issues.append(f"{change_id}:index-row-count-must-be-one:{len(matching)}")
    else:
        target, fragment = cell_link_parts(matching[0].get("proposal_path", ""))
        if target != "logic_change.md" or fragment != change_id.casefold():
            ctx.proposal_issues.append(f"{change_id}:proposal-path-must-target-logic_change-anchor")
        indexed_status = matching[0].get("status", "").strip().casefold()
        if indexed_status != (values.get("status") or [""])[0]:
            ctx.proposal_issues.append(f"{change_id}:index-status-mismatch:{indexed_status or 'empty'}")
    gazette = [
        row for row in ctx.gazette_rows if normalize_change_id(row.get("change_id", "")) == change_id
    ]
    if len(gazette) != 1:
        ctx.proposal_issues.append(f"{change_id}:domain-change-missing-from-root-index:{scope}")
    else:
        target, fragment = cell_link_parts(gazette[0].get("proposal_path", ""))
        expected = f"{scope}/logic_change.md"
        if normalize_scope_path(target or "") != expected or fragment != change_id.casefold():
            ctx.proposal_issues.append(f"{change_id}:root-index-must-link-domain-change:{expected}")
        gazette_status = gazette[0].get("status", "").strip().casefold()
        if gazette_status != (values.get("status") or [""])[0]:
            ctx.proposal_issues.append(f"{change_id}:root-index-status-mismatch:{gazette_status or 'empty'}")


def _check_domain_change(ctx: _CurrentStateContext, scope: str) -> None:
    """核查一份领域账本：文档控制绑定、正文计数、每条 CHG。"""
    change = ctx.root / scope / "logic_change.md"
    text, error = read_text(change)
    if error:
        ctx.document_issues.append(f"{scope}/logic_change:unreadable:{error}")
        return
    label = f"{scope}/logic_change"
    control_text = markdown_section_text(text, "文档控制")
    control = control_values(control_text)
    raw_control = control_values_raw(control_text)
    declared_scope = normalize_scope_path(
        (raw_control.get("scope_path") or raw_control.get("scope") or [""])[0]
    )
    if declared_scope != scope:
        ctx.document_issues.append(f"{label}:scope_path-must-be-{scope}")
    current_policy = normalize_scope_path((raw_control.get("current_policy") or [""])[0])
    if current_policy not in {"logic_readme.md", f"{scope}/logic_readme.md"}:
        ctx.document_issues.append(f"{label}:current_policy-must-be-domain-logic_readme")
    ledger_mode = (control.get("governance_mode") or [""])[0]
    if ledger_mode and ctx.readme_governance_mode and ledger_mode != ctx.readme_governance_mode:
        ctx.document_issues.append(f"{label}:governance-mode-must-match-root:{ledger_mode}")
    body_ids = change_heading_ids(text)
    for change_id in body_ids:
        if change_id in ctx.body_ids or change_id in ctx.domain_change_ids:
            ctx.proposal_issues.append(f"duplicate-change-body:{change_id}")
        ctx.domain_change_ids[change_id] = scope
    declared = (control.get("active_changes") or [""])[0]
    expected = str(len(body_ids)) if body_ids else "none"
    if declared.casefold() != expected:
        ctx.proposal_issues.append(
            f"{label}:active_changes-count-mismatch:{declared or 'missing'}!={expected}"
        )
    local_rows = markdown_table_rows(text, "活跃议案索引")
    blocks = change_blocks(text)
    ctx.ledger_blocks[f"{scope}/logic_change.md"] = blocks
    ctx.ledger_modes[f"{scope}/logic_change.md"] = ledger_mode
    for change_id, block in blocks.items():
        _check_domain_block(ctx, scope, change_id, block, local_rows, ledger_mode)
    # 协调检查（依赖/冲突/影响面重叠）在所有账本收集完后统一执行：_check_ledger_coordination


def _check_gazette_rows(ctx: _CurrentStateContext) -> None:
    """根公报行必须指向已登记领域账本中确有正文的 CHG。"""
    for row in ctx.gazette_rows:
        change_id = normalize_change_id(row.get("change_id", ""))
        target, _fragment = cell_link_parts(row.get("proposal_path", ""))
        if not change_id or not target:
            continue
        if ctx.domain_change_ids.get(change_id) is None:
            ctx.proposal_issues.append(f"{change_id}:root-index-target-body-not-found:{target}")


def _check_ledger_coordination(ctx: _CurrentStateContext) -> None:
    """协调检查（依赖/冲突/影响面重叠）以整本账本为单位，并能看见其余账本的活跃 CHG。

    RULE-023：账本的 governance_mode 决定块的字段档位。RULE-018：根议案与领域议案
    互写 conflicts_with / depends_on 是一法多议案的规定解法，目标解析必须跨账本，
    否则规定解法本身会被打成 conflict-target-not-active，门永远过不去。
    """
    for label, blocks in ctx.ledger_blocks.items():
        others = {key: value for key, value in ctx.ledger_blocks.items() if key != label}
        ctx.proposal_issues.extend(
            change_coordination_issues(
                blocks, ledger_mode=ctx.ledger_modes.get(label, ""), other_ledgers=others
            )
        )


def _check_domain_documents(ctx: _CurrentStateContext, audits: list[ModuleAudit]) -> None:
    """RULE-018：逐个已登记领域核查 readme 表格、账本与公报一致性，并并入模块语义问题。"""
    domain_scopes = {scope for _, scope in _registered_domain_rows(ctx)}
    for scope in sorted(domain_scopes):
        if (ctx.root / scope / "logic_readme.md").is_file():
            _check_domain_readme(ctx, scope)
        if (ctx.root / scope / "logic_change.md").is_file():
            _check_domain_change(ctx, scope)
    _check_gazette_rows(ctx)
    # 一法多议案：跨账本目标规则冲突 + 旧议案基线失效（VER-20260904-001）
    ctx.proposal_issues.extend(cross_ledger_rule_conflicts(ctx.ledger_blocks, ctx.rule_dates))
    for audit in audits:
        if audit.path not in domain_scopes:
            continue
        for issue in audit.semantic_issues + audit.module_binding_issues + audit.broken_links:
            if issue.startswith("logic_change:CHG-"):
                ctx.proposal_issues.append(issue.removeprefix("logic_change:"))
            elif "missing-changed-by" in issue:
                ctx.responsibility_issues.append(f"{audit.path}:{issue}")
            else:
                ctx.document_issues.append(f"{audit.path}:{issue}")


def audit_current_state_integrity(
    root: Path,
    audits: list[ModuleAudit],
    module_routes: dict,
    *,
    all_dirs: bool,
) -> dict:
    ctx = _CurrentStateContext(root=root, all_dirs=all_dirs, module_routes=module_routes)

    root_module = next((audit for audit in audits if audit.path == "."), None)
    readme = root / "logic_readme.md"
    change = root / "logic_change.md"
    if root_module is None or not readme.is_file():
        ctx.document_issues.append("missing-root-logic_readme")
    if root_module is None or not change.is_file():
        ctx.document_issues.append("missing-root-logic_change")
    if ctx.document_issues:
        return ctx.result()

    _check_root_document_shape(ctx, readme, change)

    readme_text, readme_error = read_text(readme)
    change_text, change_error = read_text(change)
    if readme_error:
        ctx.document_issues.append(f"logic_readme:unreadable:{readme_error}")
    if change_error:
        ctx.document_issues.append(f"logic_change:unreadable:{change_error}")
    if readme_error or change_error:
        return ctx.result()
    ctx.readme_text = readme_text
    ctx.change_text = change_text

    _check_legacy_authority_registry(ctx)
    _check_current_policy_table(ctx)
    _check_code_map_table(ctx)
    _check_readme_control(ctx)
    _check_change_control(ctx)
    _classify_root_semantic_issues(ctx, root_module)
    _collect_scope_registry_issues(ctx)
    _collect_registry_lookups(ctx)
    _check_change_body_index(ctx)
    _check_topic_index(ctx)
    _check_change_blocks(ctx)
    _check_topic_memberships(ctx)
    _check_domain_documents(ctx, audits)
    _check_ledger_coordination(ctx)

    return ctx.result()


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
