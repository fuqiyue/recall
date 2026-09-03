"""logic_version 归档/索引/临时目录/入口/密度等仓库级检查。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from recall_common import run_git  # RULE-021：Git 调用只此一份
from .constants import (
    ADR_NAME_RE,
    AGENT_ENTRY_CONFIG_DIRS,
    AGENT_PRIVATE_DIR_NAMES,
    BACKUP_DIR_NAMES,
    CANONICAL_VERSION_RE,
    CURRENT_HISTORY_ROOT,
    DEFAULT_EXCLUDES,
    HISTORY_ALLOWED_CHILDREN,
    HISTORY_NAME_RE,
    LEGACY_HISTORY_ROOTS,
    PARALLEL_CURRENT_RE,
    REQUIRED_ADR_FIELDS,
    REQUIRED_ADR_SECTIONS,
    REQUIRED_ARCHIVE_INDEX_FIELDS,
    REQUIRED_ARCHIVE_INDEX_SECTIONS,
    REQUIRED_BACKUP_FIELDS,
    REQUIRED_BACKUP_SECTIONS,
    REQUIRED_TEMP_FIELDS,
    REQUIRED_TEMP_SECTIONS,
    REQUIRED_VERSION_FIELDS,
    REQUIRED_VERSION_SECTIONS,
    VERSION_FILENAME_RE,
    VERSION_ID_RE,
    VERSION_SLUG_RE,
)
from .textutil import (
    cell_link_target,
    change_blocks,
    control_values,
    control_values_raw,
    inspect_markdown,
    is_within,
    markdown_table_rows,
    normalize_change_id,
    normalize_scope_path,
    read_text,
)
from .fsclassify import (
    is_foreign_subtree,
    is_runtime_data_file,
    is_source_file,
)
from .changes import (
    change_heading_ids,
)
from .semantic import (
    ModuleAudit,
    placeholder_issues,
    semantic_issues,
)
from .integrity import (
    active_change_ids,
)

_CURRENT_DOC_NAMES = {"logic_readme.md", "logic_change.md", "logic_temp.md"}


# ---------------------------------------------------------------------------
# logic_version/working 临时工作区（audit_temp_working）
# ---------------------------------------------------------------------------


@dataclass
class _TempWorkingContext:
    """logic_version/working 核查的输入与累积结果。"""

    root: Path
    history_root: Path
    working_root: Path
    active_ids: set[str]
    active_blocks: dict[str, tuple[Path, str]]
    completed_version_ids: set[str]
    indexed_temp_paths: list[tuple[dict[str, str], str | None]]
    records: list[str] = field(default_factory=list)
    malformed: list[dict] = field(default_factory=list)
    missing_temp: list[str] = field(default_factory=list)
    orphan_change_ids: list[str] = field(default_factory=list)
    expired: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    unindexed: list[str] = field(default_factory=list)
    extra_entries: list[str] = field(default_factory=list)
    stale_index_entries: list[str] = field(default_factory=list)
    change_temp_link_issues: list[str] = field(default_factory=list)

    def result(self, exists: bool) -> dict:
        return {
            "exists": exists,
            "records": sorted(self.records),
            "malformed": self.malformed,
            "missing_logic_temp": sorted(self.missing_temp),
            "orphan_change_ids": sorted(set(self.orphan_change_ids)),
            "expired": sorted(set(self.expired)),
            "forbidden_files": sorted(set(self.forbidden_files)),
            "unindexed": sorted(set(self.unindexed)),
            "extra_entries": sorted(set(self.extra_entries)),
            "stale_index_entries": sorted(set(self.stale_index_entries)),
            "change_temp_link_issues": sorted(set(self.change_temp_link_issues)),
        }


def _collect_active_change_blocks(
    root: Path, audits: list[ModuleAudit]
) -> dict[str, tuple[Path, str]]:
    """Collect (logic_change path, block text) for every active change id (casefolded)."""
    active_blocks: dict[str, tuple[Path, str]] = {}
    for audit in audits:
        if not audit.logic_change:
            continue
        directory = root if audit.path == "." else root / audit.path
        change_file = directory / "logic_change.md"
        change_text, change_error = read_text(change_file)
        if change_error:
            continue
        for change_id, block in change_blocks(change_text).items():
            active_blocks[change_id.casefold()] = (change_file, block)
    return active_blocks


def _collect_completed_version_ids(history_root: Path) -> set[str]:
    """Collect casefolded version_id values of every archived version record."""
    completed_version_ids: set[str] = set()
    records_root = history_root / "records"
    if records_root.is_dir():
        for record in records_root.glob("logic_version-*.md"):
            record_text, record_error = read_text(record)
            if record_error:
                continue
            for version_id in control_values(record_text).get("version_id", []):
                if VERSION_ID_RE.fullmatch(version_id):
                    completed_version_ids.add(version_id.casefold())
    return completed_version_ids


def _canonical_index_temp_path(
    root: Path, history_root: Path, row: dict[str, str]
) -> str | None:
    """Resolve an index row's temp `path` link to a root-relative posix path."""
    target = cell_link_target(row.get("path", ""))
    if not target:
        return None
    normalized = target.replace("\\", "/").strip()
    candidate = (
        root / normalized
        if normalized.casefold().startswith(f"{CURRENT_HISTORY_ROOT.casefold()}/")
        else history_root / normalized
    ).resolve()
    if not is_within(candidate, history_root):
        return None
    return candidate.relative_to(root).as_posix()


def _index_entry_label(row: dict[str, str]) -> str:
    """Render a stable `version:change:path` label for an index row."""
    version_id = row.get("version_id", "").strip("` ") or "unknown-version"
    change_id = (
        normalize_change_id(row.get("change_id", ""))
        or row.get("change_id", "").strip("` ")
        or "unknown-change"
    )
    target = cell_link_target(row.get("path", "")) or "missing-path"
    return f"{version_id}:{change_id}:{target}"


def _check_declared_temp_paths(ctx: _TempWorkingContext) -> None:
    """核查每个活跃议案声明的 temp_path 位于 working 下、存在且回指该议案。"""
    for change_id, (_, change_block) in ctx.active_blocks.items():
        change_raw = control_values_raw(change_block)
        declared_temp = (change_raw.get("temp_path") or [""])[0].strip("<>")
        if declared_temp.casefold() in {
            "",
            "none",
            "unknown",
            "n/a",
            "not-applicable",
        }:
            continue
        normalized_temp = normalize_scope_path(declared_temp)
        temp_candidate = (ctx.root / normalized_temp).resolve()
        expected_prefix = f"{CURRENT_HISTORY_ROOT.casefold()}/working/"
        if (
            not normalized_temp.casefold().startswith(expected_prefix)
            or not is_within(temp_candidate, ctx.working_root)
            or temp_candidate.name.casefold() != "logic_temp.md"
        ):
            ctx.change_temp_link_issues.append(
                f"{change_id.upper()}:invalid-declared-temp-path:{declared_temp}"
            )
            continue
        if not temp_candidate.is_file():
            ctx.change_temp_link_issues.append(
                f"{change_id.upper()}:declared-temp-not-found:{declared_temp}"
            )
            continue
        temp_text, temp_error = read_text(temp_candidate)
        temp_source_ids = {
            normalize_change_id(value)
            for value in control_values(temp_text).get("source_change_id", [])
            if normalize_change_id(value)
        }
        if temp_error or temp_source_ids != {change_id.upper()}:
            ctx.change_temp_link_issues.append(
                f"{change_id.upper()}:declared-temp-source-mismatch:{declared_temp}"
            )


def _check_temp_identity(
    ctx: _TempWorkingContext,
    entry: Path,
    relative_temp: str,
    values: dict[str, list[str]],
    raw_values: dict[str, list[str]],
    semantic: list[str],
) -> None:
    """核查 logic_temp 的 version_id 未与已完成版本冲突、slug 与目录名一致、temp_path 自指正确。"""
    version_id = (values.get("version_id") or [""])[0]
    if version_id.casefold() in ctx.completed_version_ids:
        semantic.append(f"working-temp-conflicts-completed-version:{version_id}")

    version_slug = (raw_values.get("version_slug") or [""])[0]
    if version_slug and version_slug != entry.name:
        semantic.append(f"version-slug-folder-mismatch:{version_slug}!={entry.name}")
    temp_path = (raw_values.get("temp_path") or [""])[0].strip("<>")
    if temp_path and normalize_scope_path(temp_path) != relative_temp:
        semantic.append(f"temp-path-mismatch:{temp_path}!={relative_temp}")


def _check_temp_sources(
    ctx: _TempWorkingContext,
    relative_temp: str,
    values: dict[str, list[str]],
    raw_values: dict[str, list[str]],
    semantic: list[str],
) -> None:
    """核查 source_change_id 均为活跃议案且回指本 temp，source_of_truth 指向含正文的 logic_change。"""
    source_ids = values.get("source_change_id", [])
    for source_id in source_ids:
        if source_id not in {item.lower() for item in ctx.active_ids}:
            ctx.orphan_change_ids.append(f"{relative_temp}:{source_id}")
            continue
        change_file, change_block = ctx.active_blocks[source_id.casefold()]
        change_raw = control_values_raw(change_block)
        registered_temp = (change_raw.get("temp_path") or [""])[0].strip("<>")
        if normalize_scope_path(registered_temp) != relative_temp:
            semantic.append(
                f"source-change-temp-path-mismatch:{registered_temp or 'missing'}!={relative_temp}"
            )

    truth_ref = (raw_values.get("source_of_truth") or [""])[0].strip("<>")
    if truth_ref and truth_ref.lower() not in {"none", "unknown"}:
        truth_path = (ctx.root / truth_ref).resolve()
        if (
            not is_within(truth_path, ctx.root)
            or not truth_path.is_file()
            or truth_path.name.lower() != "logic_change.md"
        ):
            semantic.append(f"invalid-source-of-truth:{truth_ref}")
        else:
            truth_text, truth_error = read_text(truth_path)
            truth_ids = {item.casefold() for item in change_heading_ids(truth_text)}
            if truth_error or not all(
                source_id.casefold() in truth_ids for source_id in source_ids
            ):
                semantic.append(f"source-of-truth-missing-change-body:{truth_ref}")


def _check_temp_expiry(
    ctx: _TempWorkingContext,
    relative_temp: str,
    values: dict[str, list[str]],
    semantic: list[str],
) -> str:
    """核查 expires 为合法日期并登记已过期记录；返回原始 expires 值。"""
    expires_value = (values.get("expires") or [""])[0]
    if expires_value:
        try:
            if date.fromisoformat(expires_value) < date.today():
                ctx.expired.append(relative_temp)
        except ValueError:
            semantic.append(f"invalid-expires:{expires_value}")
    return expires_value


def _check_temp_index_rows(
    ctx: _TempWorkingContext,
    relative_temp: str,
    values: dict[str, list[str]],
    expires_value: str,
    semantic: list[str],
) -> None:
    """核查 logic_version/index.md 活跃临时记录表恰有一行且身份/状态/到期与 temp 一致。"""
    matching_index_rows = [
        row
        for row, indexed_path in ctx.indexed_temp_paths
        if indexed_path == relative_temp
    ]
    if not matching_index_rows:
        ctx.unindexed.append(relative_temp)
        return
    version_id = (values.get("version_id") or [""])[0]
    source_id = (values.get("source_change_id") or [""])[0]
    state = (values.get("state") or [""])[0]
    if len(matching_index_rows) != 1:
        semantic.append("logic-version-index-temp-duplicate-entry")
    for row in matching_index_rows:
        if row.get("version_id", "").strip(
            "` "
        ).casefold() != version_id.casefold() or normalize_change_id(
            row.get("change_id", "")
        ) != normalize_change_id(source_id):
            semantic.append("logic-version-index-temp-identity-mismatch")
        if row.get("state", "").strip("` ").casefold() != state.casefold():
            semantic.append("logic-version-index-temp-state-mismatch")
        if row.get("expires", "").strip("` ") != expires_value:
            semantic.append("logic-version-index-temp-expires-mismatch")


def _collect_forbidden_files(ctx: _TempWorkingContext, entry: Path, temp: Path) -> None:
    """登记工作目录内除 logic_temp 外的现行文档、归档记录、源码与运行数据文件。"""
    for nested in entry.rglob("*"):
        if not nested.is_file() or nested == temp:
            continue
        name = nested.name.lower()
        if (
            name in _CURRENT_DOC_NAMES
            or HISTORY_NAME_RE.match(nested.name)
            or ADR_NAME_RE.match(nested.name)
            or is_source_file(nested)
            or is_runtime_data_file(nested)
        ):
            ctx.forbidden_files.append(nested.relative_to(ctx.root).as_posix())


def _check_working_entry(ctx: _TempWorkingContext, entry: Path) -> None:
    """核查 working 下一个条目：目录命名、logic_temp 结构与语义、索引对账与禁入文件。"""
    if not entry.is_dir():
        ctx.extra_entries.append(entry.relative_to(ctx.root).as_posix())
        return
    if not VERSION_SLUG_RE.fullmatch(entry.name):
        ctx.extra_entries.append(entry.relative_to(ctx.root).as_posix())
    temp = entry / "logic_temp.md"
    if not temp.is_file():
        ctx.missing_temp.append(entry.relative_to(ctx.root).as_posix())
        return
    relative_temp = temp.relative_to(ctx.root).as_posix()
    ctx.records.append(relative_temp)
    sections, fields, links = inspect_markdown(
        temp, ctx.root, REQUIRED_TEMP_SECTIONS, REQUIRED_TEMP_FIELDS
    )
    semantic = semantic_issues(temp, "temp")
    semantic.extend(placeholder_issues(temp))
    semantic.extend(f"broken-link:{link}" for link in links)
    text_value, error = read_text(temp)
    values = control_values(text_value) if not error else {}
    raw_values = control_values_raw(text_value) if not error else {}
    _check_temp_identity(ctx, entry, relative_temp, values, raw_values, semantic)
    _check_temp_sources(ctx, relative_temp, values, raw_values, semantic)
    expires_value = _check_temp_expiry(ctx, relative_temp, values, semantic)
    _check_temp_index_rows(ctx, relative_temp, values, expires_value, semantic)

    if sections or fields or semantic:
        ctx.malformed.append(
            {
                "path": relative_temp,
                "missing_sections": sections,
                "missing_fields": fields,
                "semantic_issues": sorted(set(semantic)),
            }
        )

    _collect_forbidden_files(ctx, entry, temp)


def audit_temp_working(root: Path, audits: list[ModuleAudit]) -> dict:
    history_root = root / CURRENT_HISTORY_ROOT
    working_root = history_root / "working"
    index = history_root / "index.md"
    index_text = ""
    if index.is_file():
        index_text, _ = read_text(index)
    index_rows = markdown_table_rows(index_text, "活跃临时记录")
    ctx = _TempWorkingContext(
        root=root,
        history_root=history_root,
        working_root=working_root,
        active_ids=active_change_ids(root, audits),
        active_blocks=_collect_active_change_blocks(root, audits),
        completed_version_ids=_collect_completed_version_ids(history_root),
        indexed_temp_paths=[
            (row, _canonical_index_temp_path(root, history_root, row))
            for row in index_rows
        ],
    )

    _check_declared_temp_paths(ctx)

    if not working_root.is_dir():
        ctx.stale_index_entries.extend(_index_entry_label(row) for row in index_rows)
        return ctx.result(exists=False)

    for entry in sorted(working_root.iterdir()):
        _check_working_entry(ctx, entry)

    record_set = set(ctx.records)
    for row, indexed_path in ctx.indexed_temp_paths:
        if indexed_path is None or indexed_path not in record_set:
            ctx.stale_index_entries.append(_index_entry_label(row))

    return ctx.result(exists=True)


def archive_record_identity(path: Path, kind: str) -> tuple[str | None, str | None]:
    text, error = read_text(path)
    if error:
        return None, error
    values = control_values(text)
    if kind == "version":
        return (values.get("version_id") or [None])[0], None
    if kind == "backup":
        return (values.get("backup_id") or [None])[0], None
    return path.stem, None



def _collect_expected_index_entries(
    index: Path,
    version_records: list[Path],
    decision_records: list[Path],
    backup_sets: list[Path],
) -> list[tuple[str, str | None, str, str | None]]:
    """Collect (kind, identity, index-relative path, status) for every archived record."""
    expected: list[tuple[str, str | None, str, str | None]] = []
    for path in version_records:
        identity, _ = archive_record_identity(path, "version")
        record_text, _ = read_text(path)
        status = (control_values(record_text).get("status") or [None])[0]
        expected.append(
            ("version", identity, path.relative_to(index.parent).as_posix(), status)
        )
    for path in decision_records:
        identity, _ = archive_record_identity(path, "decision")
        record_text, _ = read_text(path)
        status = (control_values(record_text).get("status") or [None])[0]
        expected.append(
            ("decision", identity, path.relative_to(index.parent).as_posix(), status)
        )
    for backup in backup_sets:
        manifest = backup / "manifest.md"
        if manifest.is_file():
            identity, _ = archive_record_identity(manifest, "backup")
            expected.append(
                (
                    "backup",
                    identity,
                    manifest.relative_to(index.parent).as_posix(),
                    None,
                )
            )
    return expected


def _canonical_table_target(root: Path, index: Path, cell: str) -> str | None:
    """Resolve an index table link cell to an index-relative posix path (None if invalid)."""
    target = cell_link_target(cell)
    if not target:
        return None
    normalized = target.replace("\\", "/").strip()
    candidate = (
        root / normalized
        if normalized.casefold().startswith(f"{CURRENT_HISTORY_ROOT.casefold()}/")
        else index.parent / normalized
    ).resolve()
    if not is_within(candidate, index.parent):
        return None
    return candidate.relative_to(index.parent.resolve()).as_posix()


def _check_index_rows(
    root: Path,
    index: Path,
    expected: list[tuple[str, str | None, str, str | None]],
    table_specs: dict[str, tuple[list[dict[str, str]], str, str | None, str]],
) -> tuple[list[str], list[str]]:
    """核查每条归档记录在索引表中恰有一行且 id/status 一致；返回 (unindexed, row_mismatches)。"""
    unindexed: list[str] = []
    row_mismatches: list[str] = []
    for kind, identity, path, status in expected:
        rows, id_column, status_column, path_column = table_specs[kind]
        matching_rows = [
            row
            for row in rows
            if _canonical_table_target(root, index, row.get(path_column, "")) == path
        ]
        if not matching_rows:
            unindexed.append(path)
            continue
        if len(matching_rows) != 1:
            row_mismatches.append(f"{path}:duplicate-row")
        row = matching_rows[0]
        indexed_identity = row.get(id_column, "").strip("` ")
        if identity and indexed_identity.casefold() != identity.casefold():
            row_mismatches.append(f"{path}:id")
        if (
            status_column
            and status
            and row.get(status_column, "").strip("` ").casefold() != status.casefold()
        ):
            row_mismatches.append(f"{path}:status")
    return unindexed, row_mismatches


def _collect_unknown_index_links(
    root: Path,
    index: Path,
    expected: list[tuple[str, str | None, str, str | None]],
    table_specs: dict[str, tuple[list[dict[str, str]], str, str | None, str]],
) -> list[str]:
    """登记索引表中无法解析或不对应任何归档记录的行链接。"""
    expected_paths_by_kind: dict[str, set[str]] = {
        kind: {path for row_kind, _, path, _ in expected if row_kind == kind}
        for kind in table_specs
    }
    unknown_links: list[str] = []
    for kind, (rows, id_column, _, path_column) in table_specs.items():
        for row in rows:
            relative = _canonical_table_target(root, index, row.get(path_column, ""))
            row_id = row.get(id_column, "").strip("` ") or "unknown"
            if relative is None:
                unknown_links.append(f"{kind}:invalid-row:{row_id}")
            elif relative not in expected_paths_by_kind[kind]:
                unknown_links.append(relative)
    return unknown_links


def audit_index_consistency(
    index: Path,
    root: Path,
    version_records: list[Path],
    decision_records: list[Path],
    backup_sets: list[Path],
) -> dict:
    index_text, error = read_text(index)
    if error:
        return {
            "unindexed_records": [],
            "duplicate_ids": [],
            "row_mismatches": [],
            "unknown_record_links": [],
            "error": f"unreadable:{error}",
        }

    expected = _collect_expected_index_entries(
        index, version_records, decision_records, backup_sets
    )
    table_specs = {
        "version": (
            markdown_table_rows(index_text, "不可变决策记录"),
            "version_id",
            "status",
            "path",
        ),
        "decision": (
            markdown_table_rows(index_text, "决策记录"),
            "ADR",
            "status",
            "path",
        ),
        "backup": (
            markdown_table_rows(index_text, "备份清单"),
            "backup_id",
            None,
            "manifest",
        ),
    }

    unindexed, row_mismatches = _check_index_rows(root, index, expected, table_specs)
    id_paths: dict[str, list[str]] = {}
    for _, identity, path, _ in expected:
        if identity:
            id_paths.setdefault(identity.casefold(), []).append(path)
    duplicate_ids = sorted(
        f"{identity}:{','.join(paths)}"
        for identity, paths in id_paths.items()
        if len(paths) > 1
    )
    unknown_links = _collect_unknown_index_links(root, index, expected, table_specs)

    return {
        "unindexed_records": sorted(set(unindexed)),
        "duplicate_ids": duplicate_ids,
        "row_mismatches": sorted(set(row_mismatches)),
        "unknown_record_links": sorted(set(unknown_links)),
        "error": None,
    }


# ---------------------------------------------------------------------------
# logic_version 归档整体（audit_archive）
# ---------------------------------------------------------------------------


def _collect_legacy_history(root: Path, archive: Path) -> tuple[list[str], bool, list[str]]:
    """Collect legacy history roots, whether they coexist with the current one, and their records."""
    legacy_roots = sorted(
        name for name in LEGACY_HISTORY_ROOTS if (root / name).is_dir()
    )
    duplicate_history_roots = bool(archive.is_dir() and legacy_roots)
    legacy_records: list[str] = []
    for name in legacy_roots:
        legacy_records.extend(
            path.relative_to(root).as_posix()
            for path in (root / name).rglob("*")
            if path.is_file()
            and (
                HISTORY_NAME_RE.match(path.name)
                or ADR_NAME_RE.match(path.name)
                or path.name.lower() in _CURRENT_DOC_NAMES
            )
        )
    return legacy_roots, duplicate_history_roots, legacy_records


def _collect_archive_layout_issues(
    root: Path, archive: Path, working_root: Path
) -> tuple[list[str], list[str]]:
    """登记归档根下不允许的子项、误放的现行文档与 working 外的 logic_temp；返回 (extra_paths, forbidden_current_docs)。"""
    extra_paths: list[str] = []
    forbidden_current_docs: list[str] = []
    if archive.is_dir():
        for child in archive.iterdir():
            if child.name not in HISTORY_ALLOWED_CHILDREN:
                extra_paths.append(child.relative_to(root).as_posix())
        for path in archive.rglob("*"):
            if not path.is_file():
                continue
            lowered = path.name.lower()
            if lowered in {"logic_readme.md", "logic_change.md"}:
                forbidden_current_docs.append(path.relative_to(root).as_posix())
            if lowered == "logic_temp.md" and not is_within(path, working_root):
                extra_paths.append(path.relative_to(root).as_posix())
    return extra_paths, forbidden_current_docs


def _collect_archive_records(
    root: Path,
    records_root: Path,
    name_re: re.Pattern[str],
    canonical_re: re.Pattern[str],
    extra_paths: list[str],
) -> list[Path]:
    """List records under `records_root` matching `name_re`; register non-canonical entries as extra paths."""
    records = (
        sorted(path for path in records_root.rglob("*.md") if name_re.match(path.name))
        if records_root.is_dir()
        else []
    )
    if records_root.is_dir():
        for path in records_root.rglob("*"):
            if path.is_dir():
                extra_paths.append(path.relative_to(root).as_posix() + "/")
            elif not (path.parent == records_root and canonical_re.fullmatch(path.name)):
                extra_paths.append(path.relative_to(root).as_posix())
    return records


def _check_version_records(
    root: Path,
    versions_root: Path,
    version_records: list[Path],
    archive_broken_links: list[str],
) -> list[dict]:
    """核查每份版本记录的结构、语义、文件名/ID/slug 一致与 correction 目标；返回 malformed 列表。"""
    malformed_versions: list[dict] = []
    version_id_values = {
        identity
        for path in version_records
        for identity, error in [archive_record_identity(path, "version")]
        if identity and not error
    }
    for path in version_records:
        sections, fields, links = inspect_markdown(
            path, root, REQUIRED_VERSION_SECTIONS, REQUIRED_VERSION_FIELDS
        )
        semantic = semantic_issues(path, "version")
        semantic.extend(placeholder_issues(path))
        text, _ = read_text(path)
        values = control_values(text)
        raw_values = control_values_raw(text)
        filename_match = VERSION_FILENAME_RE.fullmatch(path.name)
        version_ids = values.get("version_id", [])
        if filename_match and version_ids:
            expected_id = f"ver-{filename_match.group(1)}-{filename_match.group(2)}"
            if any(value != expected_id for value in version_ids):
                semantic.append("version-id-filename-mismatch")
        slugs = raw_values.get("version_slug", [])
        if slugs and any(slug != path.stem for slug in slugs):
            semantic.append("version-slug-filename-mismatch")
        if path.parent != versions_root:
            semantic.append("version-record-must-be-direct-child-of-records")
        if "correction" in values.get("status", []):
            for target in values.get("corrects", []):
                if target not in {"", "none"} and target not in version_id_values:
                    semantic.append("correction-target-not-found:" + target)
        if sections or fields or semantic or not CANONICAL_VERSION_RE.match(path.name):
            malformed_versions.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "invalid_filename": not bool(CANONICAL_VERSION_RE.match(path.name)),
                    "missing_sections": sections,
                    "missing_fields": fields,
                    "semantic_issues": semantic,
                }
            )
        archive_broken_links.extend(
            f"{path.relative_to(root).as_posix()}:{item}" for item in links
        )
    return malformed_versions


def _check_decision_records(
    root: Path, decision_records: list[Path], archive_broken_links: list[str]
) -> list[dict]:
    """核查每份 ADR 的结构与语义；返回 malformed 列表。"""
    malformed_decisions: list[dict] = []
    for path in decision_records:
        sections, fields, links = inspect_markdown(
            path, root, REQUIRED_ADR_SECTIONS, REQUIRED_ADR_FIELDS
        )
        semantic = semantic_issues(path, "adr")
        semantic.extend(placeholder_issues(path))
        if sections or fields or semantic:
            malformed_decisions.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "missing_sections": sections,
                    "missing_fields": fields,
                    "semantic_issues": semantic,
                }
            )
        archive_broken_links.extend(
            f"{path.relative_to(root).as_posix()}:{item}" for item in links
        )
    return malformed_decisions


def _check_backup_manifests(
    root: Path, backup_sets: list[Path], archive_broken_links: list[str]
) -> list[dict]:
    """核查每个备份集 manifest.md 的结构与语义；返回 malformed 列表。"""
    malformed_backups: list[dict] = []
    for path in backup_sets:
        manifest = path / "manifest.md"
        if not manifest.is_file():
            continue
        sections, fields, links = inspect_markdown(
            manifest, root, REQUIRED_BACKUP_SECTIONS, REQUIRED_BACKUP_FIELDS
        )
        semantic = semantic_issues(manifest, "backup")
        semantic.extend(placeholder_issues(manifest))
        if sections or fields or semantic:
            malformed_backups.append(
                {
                    "path": manifest.relative_to(root).as_posix(),
                    "missing_sections": sections,
                    "missing_fields": fields,
                    "semantic_issues": semantic,
                }
            )
        archive_broken_links.extend(
            f"{manifest.relative_to(root).as_posix()}:{item}" for item in links
        )
    return malformed_backups


def _check_index_control(
    root: Path, index: Path, text: str, archive_broken_links: list[str]
) -> str | None:
    """核查 index.md 的必备章节/字段与控制值（history_root/format/root_only/allowed_children）；返回问题摘要。"""
    sections, fields, links = inspect_markdown(
        index,
        root,
        REQUIRED_ARCHIVE_INDEX_SECTIONS,
        REQUIRED_ARCHIVE_INDEX_FIELDS,
    )
    index_values = control_values(text)
    history_roots = index_values.get("history_root", [])
    if (
        len(history_roots) != 1
        or normalize_scope_path(history_roots[0] if history_roots else "")
        != CURRENT_HISTORY_ROOT
    ):
        fields.append("history_root-must-be-logic_version")
    if index_values.get("history_format", []) != ["2"]:
        fields.append("history_format-must-be-2")
    if index_values.get("root_only", []) != ["true"]:
        fields.append("root_only-must-be-true")
    allowed_values = index_values.get("allowed_children", [])
    allowed_children = {
        item.strip()
        for value in allowed_values
        for item in re.split(r"[,;，；]", value)
        if item.strip()
    }
    if len(allowed_values) != 1 or allowed_children != {
        item.casefold() for item in HISTORY_ALLOWED_CHILDREN
    }:
        fields.append("allowed_children-mismatch")
    index_issue: str | None = None
    if sections or fields:
        details = []
        if sections:
            details.append("missing-sections=" + ",".join(sections))
        if fields:
            details.append("missing-fields=" + ",".join(fields))
        index_issue = ";".join(details)
    archive_broken_links.extend(
        f"{CURRENT_HISTORY_ROOT}/index.md:{item}" for item in links
    )
    return index_issue


def _summarize_index_consistency(index_consistency: dict) -> list[str]:
    """Render the non-empty index-consistency findings as `key=...` detail strings."""
    consistency_details = []
    if index_consistency["unindexed_records"]:
        consistency_details.append(
            "unindexed=" + ",".join(index_consistency["unindexed_records"])
        )
    if index_consistency["duplicate_ids"]:
        consistency_details.append(
            "duplicate-ids=" + ",".join(index_consistency["duplicate_ids"])
        )
    if index_consistency["row_mismatches"]:
        consistency_details.append(
            "row-mismatches=" + ",".join(index_consistency["row_mismatches"])
        )
    if index_consistency["unknown_record_links"]:
        consistency_details.append(
            "unknown-links=" + ",".join(index_consistency["unknown_record_links"])
        )
    if index_consistency["error"]:
        consistency_details.append(index_consistency["error"])
    return consistency_details


def _check_archive_index(
    root: Path,
    index: Path,
    has_records: bool,
    version_records: list[Path],
    decision_records: list[Path],
    backup_sets: list[Path],
    archive_broken_links: list[str],
) -> tuple[str | None, dict]:
    """核查 logic_version/index.md 存在性、控制字段与记录对账；返回 (index_issue, index_consistency)。"""
    index_issue: str | None = None
    index_consistency = {
        "unindexed_records": [],
        "duplicate_ids": [],
        "row_mismatches": [],
        "unknown_record_links": [],
        "error": None,
    }
    if has_records and not index.is_file():
        index_issue = "missing"
    elif index.is_file():
        text, error = read_text(index)
        if error:
            index_issue = f"unreadable:{error}"
        else:
            index_issue = _check_index_control(root, index, text, archive_broken_links)
            index_consistency = audit_index_consistency(
                index, root, version_records, decision_records, backup_sets
            )
            consistency_details = _summarize_index_consistency(index_consistency)
            if consistency_details:
                index_issue = ";".join(
                    [item for item in [index_issue] if item] + consistency_details
                )
    return index_issue, index_consistency


def audit_archive(root: Path) -> dict:
    archive = root / CURRENT_HISTORY_ROOT
    versions_root = archive / "records"
    decisions_root = archive / "decisions"
    backups_root = archive / "backups"
    working_root = archive / "working"
    index = archive / "index.md"
    legacy_roots, duplicate_history_roots, legacy_records = _collect_legacy_history(
        root, archive
    )
    extra_paths, forbidden_current_docs = _collect_archive_layout_issues(
        root, archive, working_root
    )

    archive_broken_links: list[str] = []
    version_records = _collect_archive_records(
        root, versions_root, HISTORY_NAME_RE, CANONICAL_VERSION_RE, extra_paths
    )
    malformed_versions = _check_version_records(
        root, versions_root, version_records, archive_broken_links
    )
    decision_records = _collect_archive_records(
        root, decisions_root, ADR_NAME_RE, ADR_NAME_RE, extra_paths
    )
    malformed_decisions = _check_decision_records(
        root, decision_records, archive_broken_links
    )

    backup_sets = (
        sorted(path for path in backups_root.iterdir() if path.is_dir())
        if backups_root.is_dir()
        else []
    )
    backups_missing_manifest = [
        path.relative_to(root).as_posix()
        for path in backup_sets
        if not (path / "manifest.md").is_file()
    ]
    malformed_backups = _check_backup_manifests(root, backup_sets, archive_broken_links)

    has_records = bool(
        version_records
        or decision_records
        or backup_sets
        or (working_root.is_dir() and any(working_root.iterdir()))
    )
    index_issue, index_consistency = _check_archive_index(
        root,
        index,
        has_records,
        version_records,
        decision_records,
        backup_sets,
        archive_broken_links,
    )

    return {
        "scanned": True,
        "scan_reason": "full-archive-audit",
        "exists": archive.is_dir(),
        "root": CURRENT_HISTORY_ROOT,
        "legacy_roots": legacy_roots,
        "legacy_records": sorted(set(legacy_records)),
        "duplicate_history_roots": duplicate_history_roots,
        "extra_paths": sorted(set(extra_paths)),
        "forbidden_current_docs": sorted(set(forbidden_current_docs)),
        "index": "ok"
        if index.is_file() and index_issue is None
        else index_issue or "not-needed",
        "index_consistency": index_consistency,
        "version_records": [
            path.relative_to(root).as_posix() for path in version_records
        ],
        "decision_records": [
            path.relative_to(root).as_posix() for path in decision_records
        ],
        "backup_sets": [path.relative_to(root).as_posix() for path in backup_sets],
        "malformed_versions": malformed_versions,
        "malformed_decisions": malformed_decisions,
        "backups_missing_manifest": backups_missing_manifest,
        "malformed_backups": malformed_backups,
        "broken_links": sorted(set(archive_broken_links)),
    }


def unscanned_archive_report() -> dict:
    """Return a stable archive shape without reading historical records."""
    return {
        "scanned": False,
        "scan_reason": "current-profile-reads-history-only-when-directly-referenced",
        "exists": False,
        "root": CURRENT_HISTORY_ROOT,
        "legacy_roots": [],
        "legacy_records": [],
        "duplicate_history_roots": False,
        "extra_paths": [],
        "forbidden_current_docs": [],
        "index": "not-scanned",
        "index_consistency": {
            "unindexed_records": [],
            "duplicate_ids": [],
            "row_mismatches": [],
            "unknown_record_links": [],
            "error": None,
        },
        "version_records": [],
        "decision_records": [],
        "backup_sets": [],
        "malformed_versions": [],
        "malformed_decisions": [],
        "backups_missing_manifest": [],
        "malformed_backups": [],
        "broken_links": [],
    }


def find_misplaced_records(
    root: Path, excludes: set[str]
) -> tuple[list[str], list[str]]:
    archive = root / CURRENT_HISTORY_ROOT
    versions_root = archive / "records"
    decisions_root = archive / "decisions"
    misplaced_versions: list[str] = []
    misplaced_decisions: list[str] = []

    record_excludes = excludes - {
        CURRENT_HISTORY_ROOT,
        "backup",
        "backups",
    }
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_foreign_subtree(current, root, file_names):
            dir_names[:] = []
            continue
        dir_names[:] = [
            name
            for name in dir_names
            if name not in record_excludes and not name.startswith(".")
        ]
        for name in dir_names:
            candidate = current / name
            if (
                name.casefold() == CURRENT_HISTORY_ROOT.casefold()
                and candidate.resolve() != archive.resolve()
            ):
                misplaced_versions.append(candidate.relative_to(root).as_posix() + "/")
        for name in file_names:
            path = current / name
            if HISTORY_NAME_RE.match(name) and not is_within(path, versions_root):
                misplaced_versions.append(path.relative_to(root).as_posix())
            if (
                name.lower() == "index.md"
                and current.name.lower() == CURRENT_HISTORY_ROOT
                and current.resolve() != archive.resolve()
            ):
                misplaced_versions.append(path.relative_to(root).as_posix())
            if ADR_NAME_RE.match(name) and not is_within(path, decisions_root):
                misplaced_decisions.append(path.relative_to(root).as_posix())

    return sorted(set(misplaced_versions)), sorted(set(misplaced_decisions))


def find_parallel_current_candidates(root: Path, excludes: set[str]) -> list[str]:
    candidates: list[str] = []
    scan_excludes = excludes - {
        CURRENT_HISTORY_ROOT,
        *LEGACY_HISTORY_ROOTS,
        *AGENT_PRIVATE_DIR_NAMES,
        "backup",
        "backups",
    }
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_foreign_subtree(current, root, file_names):
            dir_names[:] = []
            continue
        dir_names[:] = [
            name
            for name in dir_names
            if name not in scan_excludes
        ]
        for name in file_names:
            if PARALLEL_CURRENT_RE.match(name):
                candidates.append((current / name).relative_to(root).as_posix())
    return sorted(set(candidates))


def registered_child_readme_paths(root: Path) -> set[str]:
    """Casefolded relative paths of child readmes registered as readme-only.

    只有根范围登记表中 in-system + readme-only 的行才使子文档
    `<scope_path>/logic_readme.md` 合法（RULE-018）；logic_change 永不豁免。
    """
    text, error = read_text(root / "logic_readme.md")
    if error:
        return set()
    allowed: set[str] = set()
    for row in markdown_table_rows(text, "范围登记表"):
        policy = (row.get("doc_policy") or "").strip().strip("`").lower()
        membership = (row.get("membership") or "").strip().strip("`").lower()
        scope_raw = (row.get("scope_path") or "").strip().strip("`")
        if policy != "readme-only" or membership != "in-system":
            continue
        scope_norm = normalize_scope_path(scope_raw)
        if scope_norm and scope_norm != ".":
            allowed.add(f"{scope_norm}/logic_readme.md".casefold())
    return allowed


def audit_root_doc_coverage(root: Path) -> dict:
    """对账：git 跟踪的 Markdown 顶层入口必须被 owned_paths ∪ unmapped_paths 覆盖。

    平行真源检测只认 logic_readme/logic_change 命名模式；改名换姓的制度
    副本（历史事故：README 重述三条通道、SUMMARY 类总结文档）只能靠登记
    对账发现（INV-001 / RULE-019）。只对 .md 文件做顶层归属检查；git 不可用、
    非 git 仓库或根文档未声明 owned_paths 时跳过（checked=False，不影响门）。
    """
    skipped = {"checked": False, "unregistered": []}
    text, error = read_text(root / "logic_readme.md")
    if error:
        return skipped
    owned_match = re.search(r'^\s*-\s*owned_paths\s*[：:]\s*(.+)$', text, re.MULTILINE)
    if not owned_match:
        return skipped
    unmapped_match = re.search(
        r'^\s*-\s*unmapped_paths\s*[：:]\s*(.+)$', text, re.MULTILINE
    )

    def parse_entries(value: str) -> set[str]:
        entries: set[str] = set()
        for raw in re.split(r'[,;，；]', value):
            item = re.sub(r'[（(][^）)]*[）)]', '', raw).strip().strip('/').strip()
            if item and item.lower() != 'none':
                entries.add(item.casefold())
        return entries

    registered = parse_entries(owned_match.group(1))
    if unmapped_match:
        registered |= parse_entries(unmapped_match.group(1))

    ok, stdout, _ = run_git(
        ["-c", "core.quotepath=false", "ls-files", "--", "*.md"], cwd=root, timeout=15
    )
    if not ok:
        return skipped

    unregistered: set[str] = set()
    for line in stdout.splitlines():
        rel = line.strip().strip('"')
        if not rel:
            continue
        top = rel.split('/', 1)[0]
        if top.casefold() not in registered:
            unregistered.add(top)
    return {"checked": True, "unregistered": sorted(unregistered)}


def find_nonroot_current_documents(
    root: Path, excludes: set[str], allowed_child_readmes: set[str] | None = None
) -> list[str]:
    """Find duplicate current-truth files outside the project root."""
    allowed = allowed_child_readmes or set()
    candidates: list[str] = []
    scan_excludes = excludes - {
        CURRENT_HISTORY_ROOT,
        *LEGACY_HISTORY_ROOTS,
        *AGENT_PRIVATE_DIR_NAMES,
        "backup",
        "backups",
    }
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_foreign_subtree(current, root, file_names):
            dir_names[:] = []
            continue
        dir_names[:] = [
            name
            for name in dir_names
            if name not in scan_excludes
        ]
        if current == root:
            continue
        for name in file_names:
            if name.casefold() in {"logic_readme.md", "logic_change.md"}:
                relative = (current / name).relative_to(root).as_posix()
                if (
                    name.casefold() == "logic_readme.md"
                    and relative.casefold() in allowed
                ):
                    continue
                candidates.append(relative)
    return sorted(set(candidates))


def find_misplaced_temp_records(root: Path, excludes: set[str]) -> list[str]:
    canonical = root / CURRENT_HISTORY_ROOT / "working"
    candidates: list[str] = []
    scan_excludes = excludes - {CURRENT_HISTORY_ROOT}
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_foreign_subtree(current, root, file_names):
            dir_names[:] = []
            continue
        dir_names[:] = [
            name
            for name in dir_names
            if name not in scan_excludes and not name.startswith(".")
        ]
        for name in file_names:
            if name.lower() != "logic_temp.md":
                continue
            path = current / name
            if not is_within(path, canonical):
                candidates.append(path.relative_to(root).as_posix())
    return sorted(set(candidates))


def find_scattered_backup_candidates(root: Path) -> list[str]:
    candidates: list[str] = []
    hard_excludes = DEFAULT_EXCLUDES - {CURRENT_HISTORY_ROOT, *LEGACY_HISTORY_ROOTS}

    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_foreign_subtree(current, root, file_names):
            dir_names[:] = []
            continue
        kept: list[str] = []
        for name in dir_names:
            path = current / name
            if (
                name in ({CURRENT_HISTORY_ROOT} | LEGACY_HISTORY_ROOTS)
                and current == root
            ):
                continue
            lowered = name.lower()
            looks_like_backup = (
                lowered in BACKUP_DIR_NAMES
                or lowered.startswith(
                    ("backup-", "backup_", "old-", "old_", "v1-copy-", "v1-copy_")
                )
                or lowered.endswith(("-backup", "_backup", "-old", "_old"))
            )
            if looks_like_backup:
                candidates.append(path.relative_to(root).as_posix())
                continue
            if name in hard_excludes or name.startswith("."):
                continue
            kept.append(name)
        dir_names[:] = kept

    return sorted(set(candidates))


def audit_agent_entrypoints(root: Path) -> tuple[list[dict], list[str], list[str]]:
    reports: list[dict] = []
    private_knowledge: list[str] = []
    private_candidates: list[str] = []

    for name, config_dir in AGENT_ENTRY_CONFIG_DIRS.items():
        path = root / name
        config_path = root / config_dir
        report = {
            "path": name,
            "config_dir": config_dir,
            "exists": path.is_file(),
            "config_dir_exists": config_path.is_dir(),
            "issues": [],
        }
        if path.is_file():
            text, error = read_text(path)
            if error:
                report["issues"].append(f"unreadable:{error}")
            else:
                lowered = text.lower()
                readme_at = lowered.find("logic_readme.md")
                change_at = lowered.find("logic_change.md")
                if readme_at < 0:
                    report["issues"].append("missing-logic_readme-pointer")
                if change_at < 0:
                    report["issues"].append("missing-logic_change-pointer")
                if readme_at >= 0 and change_at >= 0 and readme_at > change_at:
                    report["issues"].append("read-order-must-start-with-logic_readme")
                # Accept an explicit project-root placeholder or unambiguous
                # repository-relative paths.  A leading slash is deliberately
                # rejected because it can be interpreted as an OS-root path.
                root_order_markers = (
                    "recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md",
                    "recall_root_order: logic_readme.md -> logic_change.md",
                )
                if not any(marker in lowered for marker in root_order_markers):
                    report["issues"].append(
                        "missing-marker:recall_root_order: project-root/logic_readme.md -> project-root/logic_change.md"
                    )
                for marker in (
                    "recall_change_effective: false",
                    "recall_business_truth: project-root-current-logic-docs",
                    "recall_history_root: <project-root>/logic_version",
                    f"recall_agent_config_root: <project-root>/{config_dir}",
                ):
                    if marker not in lowered:
                        report["issues"].append("missing-marker:" + marker)
                if not config_path.is_dir():
                    report["issues"].append(
                        f"missing-agent-config-directory:{config_dir}"
                    )
        reports.append(report)

    for private_name in sorted(AGENT_PRIVATE_DIR_NAMES):
        private_root = root / private_name
        if not private_root.is_dir():
            continue
        for path in private_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() != ".md":
                if is_source_file(path):
                    private_candidates.append(path.relative_to(root).as_posix())
                continue
            if (
                path.name in {"logic_readme.md", "logic_change.md", "logic_temp.md"}
                or HISTORY_NAME_RE.match(path.name)
                or ADR_NAME_RE.match(path.name)
            ):
                private_knowledge.append(path.relative_to(root).as_posix())
                continue
            try:
                if path.stat().st_size > 200_000:
                    continue
                text, error = read_text(path)
            except OSError:
                continue
            if error:
                continue
            lowered = text.lower()
            business_signals = sum(
                signal in lowered
                for signal in (
                    "logic_readme.md",
                    "logic_change.md",
                    "当前制度",
                    "活跃议案",
                    "不可破坏约束",
                )
            )
            is_short_pointer = "recall_root_order:" in lowered and len(text) < 3_000
            if business_signals >= 2 and not is_short_pointer:
                private_candidates.append(path.relative_to(root).as_posix())

    return (
        reports,
        sorted(set(private_knowledge)),
        sorted(set(private_candidates)),
    )


def audit_density(root: Path, audits: list[ModuleAudit]) -> dict:
    """Check document density and bloat.

    ``issues`` 记录越过硬上限的文件；``notices`` 记录越过目标值但未到硬上限的
    文件（VER-20260903-002：目标 250/130/150 此前只写在文档里、无机器提示，
    根文档 323 行时没有任何信号）。两者都只是 advisory，不影响静态门。
    """
    issues = []
    notices = []

    # Hard limits and soft targets from references/field-vocabulary.md
    LIMITS = {
        "SKILL.md": 200,
        "logic_readme.md": 400,
        "logic_change.md": 300,
    }
    TARGETS = {
        "SKILL.md": 130,
        "logic_readme.md": 250,
        "logic_change.md": 150,
    }

    for filename, limit in LIMITS.items():
        path = root / filename
        if path.exists():
            text, error = read_text(path)
            if not error:
                lines = text.count('\n') + 1
                if lines > limit:
                    issues.append(f"{filename}:exceeds-hard-limit:{lines}>{limit}")
                elif lines > TARGETS.get(filename, limit):
                    notices.append(
                        f"{filename}:over-target:{lines}>{TARGETS[filename]}"
                        f" (hard limit {limit}; compress or archive before it bites)"
                    )

    # RULE-018：已登记的 readme-only 子文档与根文档同受行数上限约束，
    # 否则拆分后的子文档成为无上限的膨胀区
    root_readme_text, root_readme_error = read_text(root / "logic_readme.md")
    if not root_readme_error:
        child_limit = LIMITS["logic_readme.md"]
        for row in markdown_table_rows(root_readme_text, "范围登记表"):
            policy = (row.get("doc_policy") or "").strip().strip("`").lower()
            membership = (row.get("membership") or "").strip().strip("`").lower()
            scope_raw = (row.get("scope_path") or "").strip().strip("`")
            if policy != "readme-only" or membership != "in-system":
                continue
            scope_norm = normalize_scope_path(scope_raw)
            if not scope_norm or scope_norm == ".":
                continue
            child = root / scope_norm / "logic_readme.md"
            if child.exists():
                text, error = read_text(child)
                if not error:
                    lines = text.count('\n') + 1
                    if lines > child_limit:
                        issues.append(
                            f"{scope_norm}/logic_readme.md:"
                            f"exceeds-hard-limit:{lines}>{child_limit}"
                        )

    # Check individual CHG density in logic_change.md
    change_path = root / "logic_change.md"
    if change_path.exists():
        text, error = read_text(change_path)
        if not error:
            for change_id, block in change_blocks(text).items():
                lines = block.count('\n') + 1
                if lines > 80:
                    issues.append(f"{change_id}:exceeds-chg-limit:{lines}>80")
                elif lines > 40:
                    # RULE-023：单条 CHG 目标 15-40 行（field-vocabulary），越过目标先提示
                    notices.append(f"{change_id}:over-chg-target:{lines}>40 (hard limit 80)")

    # Warn on accumulated blocked CHGs
    blocked_count = 0
    if change_path.exists():
        text, error = read_text(change_path)
        if not error:
            for change_id, block in change_blocks(text).items():
                values = control_values(block)
                status = (values.get("status") or [""])[0]
                if status == "blocked":
                    blocked_count += 1
    if blocked_count > 2:
        issues.append(f"logic_change.md:blocked-accumulation:{blocked_count}>2")

    return {
        "issues": issues,
        "notices": notices,
        "limits_checked": list(LIMITS.keys()),
    }
