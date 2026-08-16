#!/usr/bin/env python3
"""Read-only audit for Recall module policy, proposals, tests, and version history."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".agents",
    ".claude",
    ".codex",
    ".codex-tmp",
    ".idea",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "site-packages",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    "tmp",
    "temp",
    "backup",
    "backups",
    "logic_version",
    "logic_archive",
}

AGENT_PRIVATE_DIR_NAMES = {
    ".agents",
    ".claude",
    ".codex",
    ".cursor",
    ".gemini",
    ".github",
    ".idea",
    ".roo",
    ".windsurf",
}
AGENT_ENTRY_CONFIG_DIRS = {
    "AGENTS.md": ".agents",
    "CLAUDE.md": ".claude",
}

CURRENT_HISTORY_ROOT = "logic_version"
LEGACY_HISTORY_ROOTS = {"logic_archive"}
HISTORY_ALLOWED_CHILDREN = {"index.md", "records", "working", "decisions", "backups"}

BACKUP_DIR_NAMES = {
    "backup",
    "backups",
    "old",
    "old-files",
    "old_files",
    "v1-copy",
}

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".graphql",
    ".h",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".prisma",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}

RUNTIME_DATA_SUFFIXES = {
    ".db",
    ".db3",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".jsonl",
    ".parquet",
    ".arrow",
    ".feather",
    ".dump",
}
RUNTIME_DATA_DIR_NAMES = {
    "postgres-data",
    "runtime-data",
    "db-data",
    "cache",
    "caches",
    "logs",
    "log",
    "日志",
    "uploads",
    "upload",
}

TEST_NAME_RE = re.compile(
    r"(^test_.+|.+(?:[._-](?:test|spec|e2e))\.[^.]+$|.+_test\.[^.]+$)",
    re.IGNORECASE,
)
CAMEL_TEST_NAME_RE = re.compile(r"^.+(?:Test|Tests)\.[^.]+$")
TEST_DIRECTORY_NAMES = {"test", "tests", "__tests__", "spec", "specs", "e2e"}
VERSION_SLUG_RE = re.compile(r"^logic_version-\d{8}-\d{3}-.+$", re.IGNORECASE)
VERSION_ID_RE = re.compile(r"^ver-\d{8}-\d{3}$", re.IGNORECASE)
TOPIC_ID_RE = re.compile(r"^topic-[a-z0-9][a-z0-9-]*$", re.IGNORECASE)
INTENT_ID_RE = re.compile(r"^INT-\d{8}-\d{3}$", re.IGNORECASE)
RULE_ID_RE = re.compile(r"^RULE-[A-Z0-9][A-Z0-9-]*$", re.IGNORECASE)
VERSION_ID_TOKEN_RE = re.compile(r"^VER-\d{8}-\d{3}$", re.IGNORECASE)
TRACE_TEST_RE = re.compile(r"^test:[^;<>]+$", re.IGNORECASE)
REVIEW_INTERVAL_RE = re.compile(r"(?:^|[;, ]+)interval:(\d+)([dwmy])(?:$|[;, ]+)", re.IGNORECASE)
REVIEW_DUE_RE = re.compile(r"(?:^|[;, ]+)due:(\d{4}-\d{2}-\d{2})(?:$|[;, ]+)", re.IGNORECASE)

REQUIRED_README_SECTIONS = {
    "文档控制",
    "目标与边界",
    "当前制度",
    "代码地图",
    "数据与控制流",
    "消费者与公共契约",
    "不可破坏约束",
    "兼容与迁移制度",
    "测试与验证",
    "有效决策索引",
    "活跃议案入口",
    "修改检查清单",
}

REQUIRED_README_SECTIONS_V2 = REQUIRED_README_SECTIONS | {
    "范围登记与归属",
    "代码、生成物与运行数据边界",
    "当前限制",
}

REQUIRED_README_SECTIONS_V2_ROOT = {"责任记录约定"}

REQUIRED_README_FIELDS = {
    "doc_id",
    "scope",
    "parent",
    "status",
    "owner",
    "governance_mode",
    "governance_ref",
    "governance_evidence",
    "governance_verification",
    "governance_verified_at",
    "effective_from",
    "last_verified",
    "review_trigger",
    "source_of_truth",
    "source_decisions",
}

REQUIRED_README_FIELDS_V2 = REQUIRED_README_FIELDS | {
    "module_id",
    "scope_path",
    "parent_module_id",
    "membership",
    "scope_type",
    "layer",
    "module_doc_policy",
    "intent_summary",
    "intent_sources",
    "decision_validity",
    "validity_evidence",
    "canonical_readme",
    "canonical_change",
    "owned_paths",
    "child_policy",
    "data_owner",
    "registry_status",
}

REQUIRED_README_FIELDS_V2_ROOT = {
    "coverage_policy",
    "membership_policy",
    "layer_policy",
    "version_root",
    "temp_root",
}

REQUIRED_CHANGE_SECTIONS = {
    "文档控制",
    "议案规则",
    "讨论主题索引",
    "活跃议案索引",
}

REQUIRED_CHANGE_FIELDS = {
    "scope",
    "current_policy",
    "owner",
    "governance_mode",
    "governance_ref",
    "governance_evidence",
    "governance_verification",
    "governance_verified_at",
    "last_updated",
    "active_changes",
}

REQUIRED_CHANGE_SECTIONS_V2 = REQUIRED_CHANGE_SECTIONS

REQUIRED_CHANGE_FIELDS_V2 = REQUIRED_CHANGE_FIELDS | {
    "scope_path",
    "module_id",
}

REQUIRED_CHANGE_FIELDS_V2_ROOT: set[str] = set()

CURRENT_README_SECTIONS = {
    "文档控制",
    "范围登记与归属",
    "当前制度",
    "代码地图",
    "活跃议案入口",
}
CURRENT_README_FIELDS = {
    "module_id",
    "scope",
    "scope_path",
    "parent",
    "parent_module_id",
    "membership",
    "scope_type",
    "module_doc_policy",
    "owner",
    "governance_mode",
    "governance_ref",
    "governance_evidence",
    "governance_verification",
    "governance_verified_at",
    "last_verified",
    "registry_status",
    "canonical_readme",
    "canonical_change",
    "coverage_policy",
    "membership_policy",
    "layer_policy",
    "version_root",
    "temp_root",
}
CURRENT_POLICY_HEADERS = [
    "rule_id",
    "规则等级",
    "当前有效规则/行为",
    "why（仅一句可审计摘要）",
    "决策记录",
    "决策依据",
    "验证证据",
    "validity",
    "last_reviewed",
    "review_owner",
]
CURRENT_CHANGE_SECTIONS = {
    "文档控制",
    "议案规则",
    "讨论主题索引",
    "活跃议案索引",
}
CURRENT_CHANGE_FIELDS = {
    "scope",
    "scope_path",
    "module_id",
    "current_policy",
    "owner",
    "governance_mode",
    "governance_ref",
    "governance_evidence",
    "governance_verification",
    "governance_verified_at",
    "last_updated",
    "active_changes",
}
FORMAL_CHANGE_BLOCK_SECTIONS = {
    "元数据",
    "当前状态、代码逻辑与差距",
    "拟议制度",
    "意图来源与可审计提炼",
    "必要理由与来源",
    "决策检查点",
    "方案与决策",
    "消费者与影响",
    "兼容、迁移与回滚",
    "测试案例与审核矩阵",
    "实施与验收门槛",
    "开放问题与用户澄清",
    "晋升与归档",
}
FORMAL_CHANGE_BLOCK_FIELDS = {
    "status",
    "effective",
    "topic_id",
    "proposal_revision",
    "recall_route",
    "decision_gate",
    "decision_state",
    "confirmed_proposal_revision",
    "decision_confirmed_by",
    "decision_ref",
    "decision_confirmed_at",
    "decision_record",
    "semantic_review_state",
    "semantic_reviewed_by",
    "semantic_review_ref",
    "semantic_reviewed_at",
    "owner",
    "changed_by",
    "proposer",
    "created",
    "last_status_change",
    "review_due",
    "target_effective",
    "scope",
    "affected_scopes",
    "related_modules",
    "related_decisions",
    "authority_surfaces",
    "based_on",
    "depends_on",
    "conflicts_with",
    "conflict_resolution",
    "history_retention",
    "runtime_state",
    "runtime_environments",
    "feature_flag",
    "blocked_by",
    "next_action",
    "unblock_condition",
    "reserved_version_id",
    "version_slug",
    "temp_path",
    "docs_impact",
    "current_behavior",
    "current_logic_fit",
    "baseline_tests",
    "user_intent_gap",
    "intent_source_refs",
    "intent_digest",
    "intent_non_goals",
    "intent_constraints",
    "intent_acceptance",
    "intent_status",
    "intent_distilled_by",
    "intent_distilled_at",
    "decision_needed_because",
    "decision_question",
    "confirmation_request",
    "confirmation_result",
    "questions_for_user",
    "target_logic_sections",
    "version_record",
    "close_condition",
    "temp_cleanup",
}
FORMAL_MEANINGFUL_FIELDS = {
    "proposer",
    "current_behavior",
    "current_logic_fit",
    "baseline_tests",
    "intent_source_refs",
    "intent_digest",
    "intent_distilled_by",
    "intent_traceability",
    "target_logic_sections",
    "close_condition",
}
FORMAL_TABLE_HEADERS = {
    "方案与决策": ["方案", "收益", "风险/坏处", "复杂度增量", "状态"],
    "消费者与影响": [
        "行为/契约",
        "artifact_layer",
        "producer",
        "consumer",
        "environment",
        "影响",
        "证据",
    ],
}

REQUIRED_VERSION_SECTIONS = {
    "记录控制",
    "来源与意图提炼",
    "决策确认与最终议案",
    "变更摘要",
    "影响与消费者",
    "兼容、迁移与回滚",
    "测试与审核",
    "关联",
}

REQUIRED_VERSION_FIELDS = {
    "version_id",
    "version_slug",
    "status",
    "immutable",
    "governance_mode",
    "governance_ref",
    "governance_evidence",
    "governance_verification",
    "governance_verified_at",
    "governance_execution_ref",
    "date",
    "scope",
    "affected_scopes",
    "changed_layers",
    "change_id",
    "topic_id",
    "changed_by",
    "proposal_commit_or_blob",
    "proposal_revision",
    "decision_record",
    "decision_state",
    "confirmed_proposal_revision",
    "decision_confirmed_by",
    "decision_ref",
    "decision_confirmed_at",
    "semantic_review_state",
    "semantic_reviewed_by",
    "semantic_review_ref",
    "semantic_reviewed_at",
    "intent_source_refs",
    "intent_digest",
    "intent_non_goals",
    "intent_constraints",
    "intent_acceptance",
    "intent_status",
    "intent_distilled_by",
    "intent_distilled_at",
    "intent_traceability",
    "intent_traceability",
    "final_proposal_snapshot",
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
    "before_commit",
    "after_commit",
    "corrects",
    "rollback_or_restore_verified",
    "temporary_structure_removed",
    "logic_temp_cleanup",
}

REQUIRED_ARCHIVE_INDEX_SECTIONS = {
    "索引控制",
    "不可变决策记录",
    "活跃临时记录",
    "决策记录",
    "备份清单",
    "读取策略",
}

REQUIRED_ARCHIVE_INDEX_FIELDS = {
    "history_format",
    "history_root",
    "root_only",
    "allowed_children",
    "last_updated",
    "owner",
}

REQUIRED_BACKUP_SECTIONS = {
    "文件清单",
    "恢复步骤",
    "删除条件",
}

REQUIRED_BACKUP_FIELDS = {
    "backup_id",
    "change_id",
    "version_id",
    "created",
    "created_by",
    "reason",
    "retention_until",
    "contains_sensitive_data",
    "storage",
}

REQUIRED_TEMP_SECTIONS = {
    "临时记录控制",
    "使用边界",
    "已核实事实",
    "待确认问题与选择",
    "受影响文件、层和测试",
    "清理与晋升",
}

REQUIRED_TEMP_FIELDS = {
    "temp_id",
    "source_change_id",
    "proposal_revision",
    "version_id",
    "version_slug",
    "scope",
    "affected_scopes",
    "owner",
    "created",
    "last_updated",
    "expires",
    "state",
    "disposable",
    "sensitive_data",
    "purpose",
    "source_of_truth",
    "cleanup_condition",
    "temp_path",
    "promote_to",
    "final_cleanup",
}

REQUIRED_ADR_SECTIONS = {
    "元数据",
    "问题与上下文",
    "用户意图与约束",
    "证据",
    "决定",
    "选择理由",
    "备选方案",
    "后果",
    "消费者与不变量",
    "兼容性矩阵",
    "迁移与回滚",
    "验证",
    "关联",
}

REQUIRED_ADR_FIELDS = {
    "status",
    "scope",
    "owner",
    "created",
    "valid_from",
    "valid_until",
    "last_verified",
    "review_due",
    "decision_source",
    "intent_source_refs",
    "intent_digest",
    "intent_non_goals",
    "intent_constraints",
    "intent_acceptance",
    "intent_status",
    "intent_distilled_by",
    "intent_distilled_at",
    "change_id",
    "proposal_revision",
    "decision_confirmed_by",
    "decision_ref",
    "decision_confirmed_at",
    "immutable",
    "confirmed_proposal_revision",
    "immutable_decision_record",
    "confidence",
    "supersedes",
    "superseded_by",
}

README_STATUSES = {"active", "transitional"}
CHANGE_STATUSES = {
    "draft",
    "awaiting-decision",
    "implementing",
    "verifying",
    "promoting",
    "blocked",
}
DECISION_GATES = {"required", "not-required"}
RECALL_ROUTES = {"simple", "medium", "high"}
DECISION_STATES = {"pending", "confirmed", "not-required"}
FINAL_DECISION_STATES = {"confirmed", "not-confirmed", "not-required"}
DECISION_RECORD_POLICIES = {"required", "not-required"}
INTENT_STATUSES = {"confirmed", "source-derived", "inferred", "mixed"}
SEMANTIC_REVIEW_STATES = {"pending", "passed", "failed", "not-applicable"}
FINAL_SEMANTIC_REVIEW_STATES = {"passed", "failed", "not-applicable"}
GOVERNANCE_MODES = {"personal", "collaborative"}
GOVERNANCE_VERIFICATION_STATES = {"verified", "recorded", "unavailable", "not-applicable"}
CONFLICT_RESOLUTIONS = {
    "none",
    "unresolved",
    "merge",
    "supersede",
    "sequence-and-revalidate",
}
HISTORY_RETENTION_POLICIES = {"none", "compact", "full"}
RUNTIME_STATES = {
    "not-implemented",
    "implemented-unmerged",
    "merged-not-deployed",
    "deployed-guarded",
    "deployed-active",
}
VERSION_STATUSES = {
    "effective",
    "rejected",
    "cancelled",
    "rolled-back",
    "correction",
}
ADR_STATUSES = {
    "proposed",
    "accepted",
    "active",
    "transitional",
    "deprecated",
    "superseded",
    "archived",
    "rejected",
}

MEMBERSHIP_STATUSES = {
    "in-system",
    "external",
    "generated",
    "dependency",
    "unclassified",
}
SCOPE_TYPES = {
    "root",
    "module",
    "data-boundary",
    "preprocess",
    "test",
    "generated",
}
LAYERS = {
    "runtime-code",
    "runtime-config",
    "runtime-data",
    "preprocess",
    "test-fixture",
    "generated",
    "dependency",
    "external",
}
MODULE_DOC_POLICIES = {"paired", "readme-only", "inherited"}
COORDINATION_ROLES = {"root-coordinator", "module-owner", "linked-module"}
TEMP_STATES = {"working", "ready-to-promote"}
DECISION_AUTHORITY_STATUSES = {"active", "suspended", "retired"}
TEST_LEVELS = {
    "unit",
    "component",
    "contract",
    "integration",
    "e2e",
    "migration",
    "runtime",
}

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
CONTROL_RE = re.compile(r"^\s*-\s+([a-z_]+)\s*:\s*(.*?)\s*$", re.MULTILINE)
HISTORY_NAME_RE = re.compile(r"^logic_version(?:[-_].+)?\.md$", re.IGNORECASE)
CANONICAL_VERSION_RE = re.compile(r"^logic_version-\d{8}-\d{3}-.+\.md$", re.IGNORECASE)
VERSION_FILENAME_RE = re.compile(
    r"^logic_version-(\d{8})-(\d{3})-(.+)\.md$", re.IGNORECASE
)
ADR_NAME_RE = re.compile(r"^ADR-\d{8}-\d{3}.*\.md$", re.IGNORECASE)
PARALLEL_CURRENT_RE = re.compile(
    r"^(logic_readme|logic_change)(?:[-_].+)\.md$", re.IGNORECASE
)
CHANGE_HEADING_RE = re.compile(r"^\s*##\s+(CHG-[A-Z0-9][A-Z0-9-]*)\b", re.IGNORECASE)
DECISION_AUTHORITY_ID_RE = re.compile(r"^AUTH-[A-Z0-9][A-Z0-9-]*$", re.IGNORECASE)
POSITIVE_INTEGER_RE = re.compile(r"^[1-9]\d*$")
DEPENDENCY_REFERENCE_RE = re.compile(
    r"^(CHG-[A-Z0-9][A-Z0-9-]*)@revision-([1-9]\d*)$", re.IGNORECASE
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only audit of current policy/proposals, tests, agent entrypoints, "
            "and optional legacy module/history governance."
        )
    )
    parser.add_argument("project_root", type=Path, help="Project directory to inspect")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help=(
            "Maximum directory depth below the project root for non-strict-v2 "
            "inventory; the default is unlimited"
        ),
    )
    parser.add_argument(
        "--all-dirs",
        action="store_true",
        help="Treat every non-excluded directory as a documentation candidate",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional directory name to exclude; repeat as needed",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print JSON instead of text"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Return 1 for missing root policy/change entry, malformed documents, "
            "broken links, misplaced history, or invalid existing agent entrypoints"
        ),
    )
    parser.add_argument(
        "--strict-v2",
        action="store_true",
        help=(
            "Legacy migration audit for distributed/module-local Recall v2 "
            "documents, history roots, and controlled logic_temp records; "
            "do not use this as the root-only release audit"
        ),
    )
    parser.add_argument(
        "--current-state",
        action="store_true",
        help=(
            "Run a lightweight root-only logic-map audit: current documents, "
            "scope routes, active CHG lifecycle/declared coordination metadata, and "
            "at least one agent entrypoint. It does not claim to audit code semantics."
        ),
    )
    parser.add_argument(
        "--formal-review",
        action="store_true",
        help=(
            "Run the root-only current-state checks plus complete active-CHG "
            "sections and current test-review matrices. Code semantics still "
            "require a Codex, Claude, or human review."
        ),
    )
    parser.add_argument(
        "--require-test-matrix",
        action="store_true",
        help=(
            "Require status-aware baseline/post-change matrices for active changes "
            "and completed version records; test-file discovery remains evidence, "
            "not an unconditional requirement"
        ),
    )
    parser.add_argument(
        "--require-agent-entry",
        choices=("codex", "claude", "both"),
        help=(
            "Require a valid root AGENTS.md plus .agents/, CLAUDE.md plus .claude/, "
            "or both for the agents actually enabled in this project. Current/formal "
            "profiles already require at least one root entry."
        ),
    )
    return parser.parse_args()


def relative_depth(path: Path, root: Path) -> int:
    return len(path.relative_to(root).parts)


def is_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES


def is_runtime_data_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in RUNTIME_DATA_SUFFIXES


def looks_like_runtime_data_directory(path: Path, root: Path) -> bool:
    if path == root:
        return False
    return any(
        part.lower() in RUNTIME_DATA_DIR_NAMES for part in path.relative_to(root).parts
    )


def is_test_file(path: Path, root: Path | None = None) -> bool:
    scoped_parts = (
        path.relative_to(root).parts[:-1]
        if root is not None and is_within(path, root)
        else path.parent.parts
    )
    return path.is_file() and (
        bool(TEST_NAME_RE.match(path.name))
        or bool(CAMEL_TEST_NAME_RE.match(path.name))
        or any(part.casefold() in TEST_DIRECTORY_NAMES for part in scoped_parts)
    )


def is_generated_file(path: Path) -> bool:
    lowered = path.name.lower()
    return path.is_file() and (
        lowered.endswith((".min.js", ".min.css", ".map"))
        or "generated" in {part.lower() for part in path.parts}
    )


def is_dependency_tree_root(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """Identify a vendored Python virtualenv before it becomes a map candidate."""
    if path == root:
        return False
    names = {name.lower() for name in file_names}
    return "pyvenv.cfg" in names


def is_nested_project_root(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """Identify a separately-governed project vendored inside this one.

    A subdirectory whose own ``logic_readme.md`` declares ``scope: .`` plus
    ``scope_type: root`` is another project's root (a vendored dependency,
    a bundled example, or an audit fixture), not a module of this project.

    Auditing it as a module corrupts the enclosing result: its ``module_id``
    is usually ``MOD-ROOT`` too, so it displaces the real root document in
    the ``module_id``-keyed maps, which then makes the genuine root scope
    look like it has no governance parent.  It is also counted as an
    unregistered governance directory even though registering it would be
    wrong -- it is not in this project's scope hierarchy at all.
    """
    if path == root:
        return False
    if "logic_readme.md" not in {name.lower() for name in file_names}:
        return False
    text, error = read_text(path / "logic_readme.md")
    if error:
        return False
    # Read the document-control block only.  ``control_values`` over the whole
    # file also picks up per-scope sections (e.g. a nested ``- scope_path: src``
    # for a sub-module), which would mask the root declaration.
    values = control_values(markdown_section_text(text, "文档控制"))
    declared_scopes = {
        normalize_scope_path(value)
        for field in ("scope", "scope_path")
        for value in values.get(field, [])
    }
    return declared_scopes == {"."} and (values.get("scope_type") or [""])[0] == "root"


def is_foreign_subtree(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """A subtree whose contents must not be attributed to this project.

    Covers vendored Python environments and separately-governed projects
    nested inside this one.  Scanners that report "this project has a
    problem" must prune these, otherwise another project's parallel files,
    stray temp records or misplaced history get blamed on this one.
    """
    return is_dependency_tree_root(path, root, file_names) or is_nested_project_root(
        path, root, file_names
    )


def iter_directories(
    root: Path,
    max_depth: int | None,
    excludes: set[str],
    nested_project_roots: list[str] | None = None,
) -> Iterable[tuple[Path, list[Path]]]:
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_dependency_tree_root(current, root, file_names):
            # Do not report the environment itself or descend into its
            # site-packages as if they were project modules.
            dir_names[:] = []
            continue
        if is_nested_project_root(current, root, file_names):
            # Skip the nested root and its whole subtree; its modules belong
            # to that project's registry, not to this one.
            if nested_project_roots is not None:
                nested_project_roots.append(current.relative_to(root).as_posix())
            dir_names[:] = []
            continue
        depth = relative_depth(current, root)
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in excludes
            and not name.startswith(".")
            and (max_depth is None or depth < max_depth)
        )
        yield current, [current / name for name in file_names]


def normalize_link_target(raw: str) -> str | None:
    target = raw.strip().strip("<>")
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    return target or None


def audit_links(document: Path, text: str, root: Path) -> list[str]:
    broken: list[str] = []
    for raw in MARKDOWN_LINK_RE.findall(text):
        target = normalize_link_target(raw)
        if target is None:
            continue
        candidate = (document.parent / target).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            broken.append(f"outside-project:{raw}")
            continue
        if not candidate.exists():
            broken.append(raw)
    return sorted(set(broken))


def read_text(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig"), None
        except (OSError, UnicodeDecodeError) as exc:
            return "", str(exc)
    except OSError as exc:
        return "", str(exc)


def inspect_markdown(
    path: Path,
    root: Path,
    required_sections: set[str],
    required_fields: set[str],
) -> tuple[list[str], list[str], list[str]]:
    text, error = read_text(path)
    if error:
        return [], [], [f"unreadable:{error}"]
    headings = {heading.strip() for heading in HEADING_RE.findall(text)}
    fields = {match[0] for match in CONTROL_RE.findall(text)}
    return (
        sorted(required_sections - headings),
        sorted(required_fields - fields),
        audit_links(path, text, root),
    )


def control_values_raw(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for key, value in CONTROL_RE.findall(text):
        values.setdefault(key, []).append(value.strip())
    return values


def control_values(text: str) -> dict[str, list[str]]:
    return {
        key: [value.lower() for value in entries]
        for key, entries in control_values_raw(text).items()
    }


def normalize_scope_path(value: str) -> str:
    normalized = value.strip().strip("<>").replace("\\", "/").strip()
    if normalized.lower() in {"root", "project-root", "all-project", "全项目"}:
        return "."
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.rstrip("/")
    return normalized or "."


def scope_parts(value: str) -> tuple[str, ...]:
    normalized = normalize_scope_path(value)
    return () if normalized == "." else tuple(normalized.split("/"))


def is_scope_ancestor(parent: str, child: str) -> bool:
    parent_parts = scope_parts(parent)
    child_parts = scope_parts(child)
    return (
        len(parent_parts) < len(child_parts)
        and child_parts[: len(parent_parts)] == parent_parts
    )


def split_control_list(value: str) -> set[str]:
    return {
        normalize_scope_path(item.strip(" `[]"))
        for item in re.split(r"[,;，；]", value)
        if item.strip(" `[]")
    }


def actual_case_relative(root: Path, relative: str) -> tuple[Path, str] | None:
    """Resolve a repository-relative directory while preserving on-disk casing."""
    current = root
    actual_parts: list[str] = []
    for requested in scope_parts(relative):
        try:
            children = [child for child in current.iterdir() if child.is_dir()]
        except OSError:
            return None
        exact = next((child for child in children if child.name == requested), None)
        if exact is None:
            folded = [
                child
                for child in children
                if child.name.casefold() == requested.casefold()
            ]
            if len(folded) != 1:
                return None
            exact = folded[0]
        current = exact
        actual_parts.append(exact.name)
    return current, "/".join(actual_parts) or "."


def markdown_table_rows(text: str, heading_fragment: str) -> list[dict[str, str]]:
    """Parse the first Markdown table following a matching heading."""
    lines = text.splitlines()
    heading_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("#") and heading_fragment in line
        ),
        None,
    )
    if heading_index is None:
        return []
    section_end = next(
        (
            index
            for index in range(heading_index + 1, len(lines))
            if lines[index].lstrip().startswith("#")
        ),
        len(lines),
    )
    table_start = next(
        (
            index
            for index in range(heading_index + 1, section_end)
            if lines[index].strip().startswith("|")
        ),
        None,
    )
    if table_start is None:
        return []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    headers = cells(lines[table_start])
    separator_index = table_start + 1
    if separator_index >= section_end:
        return []
    separators = cells(lines[separator_index])
    if len(separators) != len(headers) or not all(
        re.fullmatch(r":?-{3,}:?", value) for value in separators
    ):
        return []
    rows: list[dict[str, str]] = []
    for line in lines[separator_index + 1 : section_end]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        values = cells(stripped)
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def markdown_table_headers(text: str, heading_fragment: str) -> list[str]:
    """Return the validated header row for the first table in a section."""
    lines = text.splitlines()
    heading_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("#") and heading_fragment in line
        ),
        None,
    )
    if heading_index is None:
        return []
    section_end = next(
        (
            index
            for index in range(heading_index + 1, len(lines))
            if lines[index].lstrip().startswith("#")
        ),
        len(lines),
    )
    table_start = next(
        (
            index
            for index in range(heading_index + 1, section_end)
            if lines[index].strip().startswith("|")
        ),
        None,
    )
    if table_start is None or table_start + 1 >= section_end:
        return []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    headers = cells(lines[table_start])
    separators = cells(lines[table_start + 1])
    if len(separators) != len(headers) or not all(
        re.fullmatch(r":?-{3,}:?", value) for value in separators
    ):
        return []
    return headers


def markdown_section_text(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if re.fullmatch(rf"\s*##\s+{re.escape(heading)}\s*", line)
        ),
        None,
    )
    if start is None:
        return ""
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if re.match(r"^\s*##\s+", lines[index])
        ),
        len(lines),
    )
    return chr(10).join(lines[start:end])


def cell_link_parts(cell: str) -> tuple[str | None, str | None]:
    match = MARKDOWN_LINK_RE.search(cell)
    if not match:
        return None, None
    raw = match.group(1).strip().strip("<>")
    fragment = raw.split("#", 1)[1].split("?", 1)[0] if "#" in raw else None
    return normalize_link_target(raw), fragment


def cell_link_target(cell: str) -> str | None:
    target, _ = cell_link_parts(cell)
    return target


def is_immutable_decision_record_link(cell: str) -> bool:
    """Accept only a concrete ADR or immutable VER link for a key rule."""
    target = cell_link_target(cell)
    if target is None:
        return False
    normalized = target.removeprefix("./").replace("\\", "/")
    path = Path(normalized)
    parts = tuple(part.casefold() for part in path.parts)
    if parts[:2] == ("logic_version", "records"):
        return bool(CANONICAL_VERSION_RE.fullmatch(path.name))
    if parts[:2] == ("logic_version", "decisions"):
        return bool(ADR_NAME_RE.fullmatch(path.name))
    return False


def normalize_change_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return (
        candidate.upper()
        if re.fullmatch(r"CHG-[A-Z0-9][A-Z0-9-]*", candidate, re.IGNORECASE)
        else ""
    )


def normalize_topic_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return candidate.upper() if TOPIC_ID_RE.fullmatch(candidate) else ""


def normalize_authority_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return candidate.upper() if DECISION_AUTHORITY_ID_RE.fullmatch(candidate) else ""


def change_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    starts = [
        index for index, line in enumerate(lines) if CHANGE_HEADING_RE.match(line)
    ]
    blocks: dict[str, str] = {}
    for position, start in enumerate(starts):
        match = CHANGE_HEADING_RE.match(lines[start])
        change_id = normalize_change_id(match.group(1)) if match else ""
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        if change_id:
            blocks[change_id] = chr(10).join(lines[start:end])
    return blocks


def change_affected_scopes(values: dict[str, list[str]]) -> set[str]:
    affected: set[str] = set()
    for value in values.get("affected_scopes", []):
        affected |= split_control_list(value)
    return affected


def has_meaningful_value(values: dict[str, list[str]], key: str) -> bool:
    return any(
        value not in {"", "none", "unknown", "n/a", "not-applicable", "..."}
        and not contains_angle_placeholder(value)
        and not value.startswith("yyyy")
        and "event-driven" not in value
        for value in values.get(key, [])
    )


def has_lifecycle_trigger(values: dict[str, list[str]], key: str) -> bool:
    return has_meaningful_value(values, key) or any(
        value == "event-driven" for value in values.get(key, [])
    )


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


NONE_LIKE_CONTROL_VALUES = {"", "none", "unknown", "n/a", "not-applicable", "..."}


def is_none_like(value: str) -> bool:
    return value.strip().casefold() in NONE_LIKE_CONTROL_VALUES


ANGLE_PLACEHOLDER_RE = re.compile(r"<[^<>\r\n]+>")


def contains_angle_placeholder(value: str) -> bool:
    """Detect template placeholders without mistaking traceability arrows for them."""
    return bool(ANGLE_PLACEHOLDER_RE.search(value))


def is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def relationship_items(raw_values: dict[str, list[str]], key: str) -> list[str]:
    """Split a CHG relationship field without treating values as file scopes."""
    return [
        item.strip(" `[]")
        for value in raw_values.get(key, [])
        for item in re.split(r"[,;，；]", value)
        if item.strip(" `[]")
    ]


def change_coordination_issues(blocks: dict[str, str]) -> list[str]:
    """Validate declared relationships between active CHGs in one root ledger.

    This intentionally validates only declared coordination.  It cannot prove
    that two code paths really are independent, so a missing declaration still
    requires human/code-semantic review.
    """
    issues: list[str] = []
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
    waiting_statuses = {"awaiting-decision", "blocked"}
    implementation_statuses = {"implementing", "verifying", "promoting"}

    for change_id, block in blocks.items():
        raw_values = control_values_raw(block)
        values = control_values(block)

        def one_value(key: str) -> str:
            field_values = raw_values.get(key, [])
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
        if not authority_non_none:
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
        if history_retention not in HISTORY_RETENTION_POLICIES:
            issues.append(
                f"{change_id}:invalid-history-retention:{history_retention}"
            )
        if (values.get("recall_route") or [""])[0] == "high" and history_retention != "full":
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
        if runtime_state not in RUNTIME_STATES:
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
        if conflict_resolution not in CONFLICT_RESOLUTIONS:
            issues.append(
                f"{change_id}:invalid-conflict-resolution:{conflict_resolution}"
            )
        elif has_conflict and conflict_resolution == "none":
            issues.append(f"{change_id}:conflicts-need-resolution")
        elif not has_conflict and conflict_resolution != "none":
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
        }

    dependency_graph: dict[str, set[str]] = {change_id: set() for change_id in entries}
    for change_id, entry in entries.items():
        status = str(entry["status"])
        for target, revision in entry["dependencies"]:  # type: ignore[index]
            target_entry = entries.get(target)
            if target_entry is None:
                issues.append(f"{change_id}:dependency-target-not-active:{target}")
                continue
            dependency_graph[change_id].add(target)
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
        issues.append("dependency-cycle:" + ",".join(cycle))

    checked_conflict_pairs: set[tuple[str, str]] = set()
    for change_id, entry in entries.items():
        for target in sorted(entry["conflict_ids"]):  # type: ignore[index]
            target_entry = entries.get(target)
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
            if target and target not in entries:
                issues.append(f"{change_id}:blocked-by-target-not-active:{target}")

    return sorted(set(issues))


def change_lifecycle_issues(
    change_id: str,
    values: dict[str, list[str]],
    raw_values: dict[str, list[str]],
) -> list[str]:
    """Validate version-bound decision confirmation and semantic review metadata."""
    issues: list[str] = []

    def one_value(key: str) -> str:
        entries = raw_values.get(key, [])
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
    if recall_route == "high" and decision_gate != "required":
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
        if len(topic_values) != 1:
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
        issues.extend(change_lifecycle_issues(change_id, values, raw_values))
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


def audit_formal_review(root: Path, test_inventory: dict, temp_working: dict) -> dict:
    proposal_issues: list[str] = []
    change_text, error = read_text(root / "logic_change.md")
    if error:
        proposal_issues.append(f"unreadable-root-logic_change:{error}")
    else:
        for change_id, block in change_blocks(change_text).items():
            headings = {
                match.group(1).strip()
                for match in re.finditer(r"^\s*###\s+(.+?)\s*$", block, re.MULTILINE)
            }
            for section in sorted(FORMAL_CHANGE_BLOCK_SECTIONS - headings):
                proposal_issues.append(f"{change_id}:missing-formal-section:{section}")
            raw_values = control_values_raw(block)
            normalized_values = control_values(block)
            for field in sorted(FORMAL_CHANGE_BLOCK_FIELDS - set(raw_values)):
                proposal_issues.append(f"{change_id}:missing-formal-field:{field}")
            for field in FORMAL_CHANGE_BLOCK_FIELDS.intersection(raw_values):
                entries = raw_values[field]
                if len(entries) != 1:
                    proposal_issues.append(
                        f"{change_id}:formal-field-must-appear-once:{field}"
                    )
                elif "<" in entries[0] or ">" in entries[0] or entries[0] == "...":
                    proposal_issues.append(
                        f"{change_id}:formal-field-is-placeholder:{field}"
                    )
            for field in sorted(FORMAL_MEANINGFUL_FIELDS):
                entries = raw_values.get(field, [])
                if len(entries) == 1 and not has_meaningful_value(
                    normalized_values, field
                ):
                    proposal_issues.append(
                        f"{change_id}:formal-field-needs-meaningful-evidence:{field}"
                    )

            intent_status_entries = raw_values.get("intent_status", [])
            if len(intent_status_entries) == 1 and (
                intent_status_entries[0].casefold() not in INTENT_STATUSES
            ):
                proposal_issues.append(
                    f"{change_id}:invalid-formal-intent-status:"
                    f"{intent_status_entries[0] or 'empty'}"
                )
            intent_date_entries = raw_values.get("intent_distilled_at", [])
            if len(intent_date_entries) == 1 and not is_iso_date(
                intent_date_entries[0]
            ):
                proposal_issues.append(
                    f"{change_id}:formal-intent-distilled-at-must-be-date"
                )

            decision_gate = (normalized_values.get("decision_gate") or [""])[0]
            if decision_gate == "required":
                for field in (
                    "decision_needed_because",
                    "decision_question",
                    "confirmation_request",
                ):
                    value = (normalized_values.get(field) or [""])[0]
                    if not has_meaningful_value(normalized_values, field) or value == "not-required":
                        proposal_issues.append(
                            f"{change_id}:required-decision-needs-formal-{field}"
                        )

            for field in ("created", "last_status_change"):
                entries = raw_values.get(field, [])
                if len(entries) == 1:
                    try:
                        date.fromisoformat(entries[0])
                    except ValueError:
                        proposal_issues.append(
                            f"{change_id}:formal-field-must-be-date:{field}"
                        )
            for field, allowed_tokens in (
                ("review_due", {"event-driven"}),
                ("target_effective", {"event-driven", "unknown"}),
            ):
                entries = raw_values.get(field, [])
                if len(entries) == 1 and entries[0].casefold() not in allowed_tokens:
                    try:
                        date.fromisoformat(entries[0])
                    except ValueError:
                        proposal_issues.append(
                            f"{change_id}:formal-field-needs-date-or-lifecycle-token:"
                            f"{field}"
                        )

            reserved_version = (raw_values.get("reserved_version_id") or [""])[0]
            version_slug = (raw_values.get("version_slug") or [""])[0]
            has_reserved_version = reserved_version.casefold() != "none"
            has_version_slug = version_slug.casefold() != "none"
            if has_reserved_version and not VERSION_ID_RE.fullmatch(reserved_version):
                proposal_issues.append(
                    f"{change_id}:invalid-reserved-version-id:{reserved_version}"
                )
            if has_version_slug and not VERSION_SLUG_RE.fullmatch(version_slug):
                proposal_issues.append(
                    f"{change_id}:invalid-version-slug:{version_slug}"
                )
            if has_reserved_version != has_version_slug:
                proposal_issues.append(
                    f"{change_id}:reserved-version-id-and-slug-must-be-paired"
                )
            if (
                has_reserved_version
                and has_version_slug
                and VERSION_ID_RE.fullmatch(reserved_version)
                and VERSION_SLUG_RE.fullmatch(version_slug)
            ):
                expected_slug_prefix = reserved_version.casefold().replace(
                    "ver-", "logic_version-", 1
                )
                if not version_slug.casefold().startswith(expected_slug_prefix + "-"):
                    proposal_issues.append(
                        f"{change_id}:reserved-version-id-slug-mismatch"
                    )

            for table_name, expected_headers in FORMAL_TABLE_HEADERS.items():
                headers = markdown_table_headers(block, table_name)
                rows = markdown_table_rows(block, table_name)
                if headers != expected_headers:
                    proposal_issues.append(
                        f"{change_id}:invalid-formal-table-columns:{table_name}"
                    )
                if not rows:
                    proposal_issues.append(
                        f"{change_id}:missing-formal-table:{table_name}"
                    )
                    continue
                for index, row in enumerate(rows, start=1):
                    for header in expected_headers:
                        value = row.get(header, "").strip()
                        if (
                            not value
                            or value.casefold() in {"none", "unknown", "n/a", "..."}
                            or "<" in value
                            or ">" in value
                        ):
                            proposal_issues.append(
                                f"{change_id}:formal-table-{table_name}-row-{index}-"
                                f"missing-{header}"
                            )
                if table_name == "方案与决策":
                    selected_count = 0
                    for index, row in enumerate(rows, start=1):
                        status = row.get("状态", "").strip().casefold()
                        if status not in {"candidate", "selected", "rejected"}:
                            proposal_issues.append(
                                f"{change_id}:formal-option-row-{index}-invalid-status:"
                                f"{status or 'empty'}"
                            )
                        if status == "selected":
                            selected_count += 1
                    if selected_count != 1:
                        proposal_issues.append(
                            f"{change_id}:formal-options-need-exactly-one-selected"
                        )
                    if decision_gate == "required" and len(rows) < 3:
                        proposal_issues.append(
                            f"{change_id}:required-decision-needs-three-options"
                        )
                if table_name == "消费者与影响":
                    for index, row in enumerate(rows, start=1):
                        layer = row.get("artifact_layer", "").strip().casefold()
                        if layer not in LAYERS:
                            proposal_issues.append(
                                f"{change_id}:formal-impact-row-{index}-invalid-layer:"
                                f"{layer or 'empty'}"
                            )

    return {
        "proposal_issues": sorted(set(proposal_issues)),
        "test_matrix_issues": list(test_inventory.get("matrix_issues", [])),
        "temp_reference_issues": sorted(
            set(temp_working.get("change_temp_link_issues", []))
        ),
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


def audit_temp_working(root: Path, audits: list[ModuleAudit]) -> dict:
    history_root = root / CURRENT_HISTORY_ROOT
    working_root = history_root / "working"
    index = history_root / "index.md"
    active_ids = active_change_ids(root, audits)
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
    index_text = ""
    if index.is_file():
        index_text, _ = read_text(index)
    index_rows = markdown_table_rows(index_text, "活跃临时记录")

    def canonical_index_temp_path(row: dict[str, str]) -> str | None:
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

    def index_entry_label(row: dict[str, str]) -> str:
        version_id = row.get("version_id", "").strip("` ") or "unknown-version"
        change_id = (
            normalize_change_id(row.get("change_id", ""))
            or row.get("change_id", "").strip("` ")
            or "unknown-change"
        )
        target = cell_link_target(row.get("path", "")) or "missing-path"
        return f"{version_id}:{change_id}:{target}"

    indexed_temp_paths = [(row, canonical_index_temp_path(row)) for row in index_rows]

    records: list[str] = []
    malformed: list[dict] = []
    missing_temp: list[str] = []
    orphan_change_ids: list[str] = []
    expired: list[str] = []
    forbidden_files: list[str] = []
    unindexed: list[str] = []
    extra_entries: list[str] = []
    stale_index_entries: list[str] = []
    change_temp_link_issues: list[str] = []

    for change_id, (_, change_block) in active_blocks.items():
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
        temp_candidate = (root / normalized_temp).resolve()
        expected_prefix = f"{CURRENT_HISTORY_ROOT.casefold()}/working/"
        if (
            not normalized_temp.casefold().startswith(expected_prefix)
            or not is_within(temp_candidate, working_root)
            or temp_candidate.name.casefold() != "logic_temp.md"
        ):
            change_temp_link_issues.append(
                f"{change_id.upper()}:invalid-declared-temp-path:{declared_temp}"
            )
            continue
        if not temp_candidate.is_file():
            change_temp_link_issues.append(
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
            change_temp_link_issues.append(
                f"{change_id.upper()}:declared-temp-source-mismatch:{declared_temp}"
            )

    if not working_root.is_dir():
        stale_index_entries.extend(index_entry_label(row) for row in index_rows)
        return {
            "exists": False,
            "records": records,
            "malformed": malformed,
            "missing_logic_temp": missing_temp,
            "orphan_change_ids": orphan_change_ids,
            "expired": expired,
            "forbidden_files": forbidden_files,
            "unindexed": unindexed,
            "extra_entries": extra_entries,
            "stale_index_entries": sorted(set(stale_index_entries)),
            "change_temp_link_issues": sorted(set(change_temp_link_issues)),
        }

    for entry in sorted(working_root.iterdir()):
        if not entry.is_dir():
            extra_entries.append(entry.relative_to(root).as_posix())
            continue
        if not VERSION_SLUG_RE.fullmatch(entry.name):
            extra_entries.append(entry.relative_to(root).as_posix())
        temp = entry / "logic_temp.md"
        if not temp.is_file():
            missing_temp.append(entry.relative_to(root).as_posix())
            continue
        relative_temp = temp.relative_to(root).as_posix()
        records.append(relative_temp)
        sections, fields, links = inspect_markdown(
            temp, root, REQUIRED_TEMP_SECTIONS, REQUIRED_TEMP_FIELDS
        )
        semantic = semantic_issues(temp, "temp")
        semantic.extend(placeholder_issues(temp))
        semantic.extend(f"broken-link:{link}" for link in links)
        text_value, error = read_text(temp)
        values = control_values(text_value) if not error else {}
        raw_values = control_values_raw(text_value) if not error else {}
        version_id = (values.get("version_id") or [""])[0]
        if version_id.casefold() in completed_version_ids:
            semantic.append(f"working-temp-conflicts-completed-version:{version_id}")

        version_slug = (raw_values.get("version_slug") or [""])[0]
        if version_slug and version_slug != entry.name:
            semantic.append(
                f"version-slug-folder-mismatch:{version_slug}!={entry.name}"
            )
        temp_path = (raw_values.get("temp_path") or [""])[0].strip("<>")
        if temp_path and normalize_scope_path(temp_path) != relative_temp:
            semantic.append(f"temp-path-mismatch:{temp_path}!={relative_temp}")

        source_ids = values.get("source_change_id", [])
        for source_id in source_ids:
            if source_id not in {item.lower() for item in active_ids}:
                orphan_change_ids.append(f"{relative_temp}:{source_id}")
                continue
            change_file, change_block = active_blocks[source_id.casefold()]
            change_raw = control_values_raw(change_block)
            registered_temp = (change_raw.get("temp_path") or [""])[0].strip("<>")
            if normalize_scope_path(registered_temp) != relative_temp:
                semantic.append(
                    f"source-change-temp-path-mismatch:{registered_temp or 'missing'}!={relative_temp}"
                )

        truth_ref = (raw_values.get("source_of_truth") or [""])[0].strip("<>")
        if truth_ref and truth_ref.lower() not in {"none", "unknown"}:
            truth_path = (root / truth_ref).resolve()
            if (
                not is_within(truth_path, root)
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

        expires_value = (values.get("expires") or [""])[0]
        if expires_value:
            try:
                if date.fromisoformat(expires_value) < date.today():
                    expired.append(relative_temp)
            except ValueError:
                semantic.append(f"invalid-expires:{expires_value}")

        matching_index_rows = [
            row
            for row, indexed_path in indexed_temp_paths
            if indexed_path == relative_temp
        ]
        if not matching_index_rows:
            unindexed.append(relative_temp)
        else:
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

        if sections or fields or semantic:
            malformed.append(
                {
                    "path": relative_temp,
                    "missing_sections": sections,
                    "missing_fields": fields,
                    "semantic_issues": sorted(set(semantic)),
                }
            )

        for nested in entry.rglob("*"):
            if not nested.is_file() or nested == temp:
                continue
            name = nested.name.lower()
            if (
                name in {"logic_readme.md", "logic_change.md", "logic_temp.md"}
                or HISTORY_NAME_RE.match(nested.name)
                or ADR_NAME_RE.match(nested.name)
                or is_source_file(nested)
                or is_runtime_data_file(nested)
            ):
                forbidden_files.append(nested.relative_to(root).as_posix())

    record_set = set(records)
    for row, indexed_path in indexed_temp_paths:
        if indexed_path is None or indexed_path not in record_set:
            stale_index_entries.append(index_entry_label(row))

    return {
        "exists": True,
        "records": sorted(records),
        "malformed": malformed,
        "missing_logic_temp": sorted(missing_temp),
        "orphan_change_ids": sorted(set(orphan_change_ids)),
        "expired": sorted(set(expired)),
        "forbidden_files": sorted(set(forbidden_files)),
        "unindexed": sorted(set(unindexed)),
        "extra_entries": sorted(set(extra_entries)),
        "stale_index_entries": sorted(set(stale_index_entries)),
        "change_temp_link_issues": sorted(set(change_temp_link_issues)),
    }


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


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

    def canonical_table_target(cell: str) -> str | None:
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

    unindexed: list[str] = []
    id_paths: dict[str, list[str]] = {}
    row_mismatches: list[str] = []
    expected_paths_by_kind: dict[str, set[str]] = {
        kind: {path for row_kind, _, path, _ in expected if row_kind == kind}
        for kind in table_specs
    }
    for kind, identity, path, status in expected:
        rows, id_column, status_column, path_column = table_specs[kind]
        matching_rows = [
            row
            for row in rows
            if canonical_table_target(row.get(path_column, "")) == path
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
    for _, identity, path, _ in expected:
        if identity:
            id_paths.setdefault(identity.casefold(), []).append(path)
    duplicate_ids = sorted(
        f"{identity}:{','.join(paths)}"
        for identity, paths in id_paths.items()
        if len(paths) > 1
    )

    unknown_links: list[str] = []
    for kind, (rows, id_column, _, path_column) in table_specs.items():
        for row in rows:
            relative = canonical_table_target(row.get(path_column, ""))
            row_id = row.get(id_column, "").strip("` ") or "unknown"
            if relative is None:
                unknown_links.append(f"{kind}:invalid-row:{row_id}")
            elif relative not in expected_paths_by_kind[kind]:
                unknown_links.append(relative)

    return {
        "unindexed_records": sorted(set(unindexed)),
        "duplicate_ids": duplicate_ids,
        "row_mismatches": sorted(set(row_mismatches)),
        "unknown_record_links": sorted(set(unknown_links)),
        "error": None,
    }


def audit_archive(root: Path) -> dict:
    archive = root / CURRENT_HISTORY_ROOT
    versions_root = archive / "records"
    decisions_root = archive / "decisions"
    backups_root = archive / "backups"
    working_root = archive / "working"
    index = archive / "index.md"
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
                or path.name.lower()
                in {"logic_readme.md", "logic_change.md", "logic_temp.md"}
            )
        )

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

    version_records = (
        sorted(
            path
            for path in versions_root.rglob("*.md")
            if HISTORY_NAME_RE.match(path.name)
        )
        if versions_root.is_dir()
        else []
    )
    if versions_root.is_dir():
        for path in versions_root.rglob("*"):
            if path.is_dir():
                extra_paths.append(path.relative_to(root).as_posix() + "/")
            elif not (
                path.parent == versions_root
                and CANONICAL_VERSION_RE.fullmatch(path.name)
            ):
                extra_paths.append(path.relative_to(root).as_posix())
    malformed_versions: list[dict] = []
    version_id_values = {
        identity
        for path in version_records
        for identity, error in [archive_record_identity(path, "version")]
        if identity and not error
    }
    archive_broken_links: list[str] = []

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

    decision_records = (
        sorted(
            path
            for path in decisions_root.rglob("*.md")
            if ADR_NAME_RE.match(path.name)
        )
        if decisions_root.is_dir()
        else []
    )
    if decisions_root.is_dir():
        for path in decisions_root.rglob("*"):
            if path.is_dir():
                extra_paths.append(path.relative_to(root).as_posix() + "/")
            elif not (
                path.parent == decisions_root and ADR_NAME_RE.fullmatch(path.name)
            ):
                extra_paths.append(path.relative_to(root).as_posix())
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

    has_records = bool(
        version_records
        or decision_records
        or backup_sets
        or (working_root.is_dir() and any(working_root.iterdir()))
    )
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
            index_consistency = audit_index_consistency(
                index, root, version_records, decision_records, backup_sets
            )
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
                    "unknown-links="
                    + ",".join(index_consistency["unknown_record_links"])
                )
            if index_consistency["error"]:
                consistency_details.append(index_consistency["error"])
            if consistency_details:
                index_issue = ";".join(
                    [item for item in [index_issue] if item] + consistency_details
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


def audit_test_inventory(
    root: Path,
    audits: list[ModuleAudit],
    max_depth: int | None,
    excludes: set[str],
    *,
    include_history: bool = True,
) -> dict:
    test_files: list[str] = []
    configs: list[str] = []
    categories: set[str] = set()
    config_names = {
        "package.json",
        "pyproject.toml",
        "pytest.ini",
        "tox.ini",
        "vitest.config.js",
        "vitest.config.ts",
        "jest.config.js",
        "jest.config.ts",
        "playwright.config.js",
        "playwright.config.ts",
        "cypress.config.js",
        "cypress.config.ts",
    }
    for _, files in iter_directories(root, max_depth, excludes):
        for path in files:
            name = path.name
            relative = path.relative_to(root).as_posix()
            if name.lower() in config_names:
                configs.append(relative)
            if not is_test_file(path, root):
                continue
            test_files.append(relative)
            lowered = relative.lower()
            matched_category = False
            if any(token in lowered for token in ("e2e", "playwright", "cypress")):
                categories.add("e2e")
                matched_category = True
            if any(
                token in lowered for token in ("frontend", "ui", "component", "browser")
            ):
                categories.add("frontend")
                matched_category = True
            if any(token in lowered for token in ("backend", "api", "server")):
                categories.add("backend/api")
                matched_category = True
            if any(
                token in lowered for token in ("migration", "schema", "database", "db")
            ):
                categories.add("migration/data")
                matched_category = True
            if not matched_category:
                categories.add("unit/unspecified")

    matrix_issues: list[str] = []
    placeholder_values = {"", "...", "none", "unknown", "n/a", "tbd", "pending"}
    result_tokens = {"pass", "fail", "not-run", "not-applicable"}

    def missing_value(value: str) -> bool:
        normalized = value.strip().casefold()
        return (
            normalized in placeholder_values or "<" in normalized or ">" in normalized
        )

    def result_token(value: str) -> str:
        return value.strip().casefold().split(":", 1)[0]

    def has_reason(value: str) -> bool:
        return ":" in value and bool(value.split(":", 1)[1].strip())

    def has_evidence_locator(value: str) -> bool:
        if MARKDOWN_LINK_RE.search(value):
            return True
        for marker in (
            "command:",
            "ci:",
            "log:",
            "path:",
            "issue:",
            "risk:",
            "risk-accepted:",
            "decision-ref:",
            "not-run:",
        ):
            match = re.search(
                rf"{re.escape(marker)}\s*([^;|]+)", value, re.IGNORECASE
            )
            if match and not missing_value(match.group(1)):
                return True
        return False

    def has_reviewer_and_date(value: str) -> bool:
        date_candidates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", value)
        has_valid_date = False
        for candidate in date_candidates:
            try:
                date.fromisoformat(candidate)
            except ValueError:
                continue
            has_valid_date = True
            break
        reviewer = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", value).strip(
            " +,;|/"
        )
        return has_valid_date and not missing_value(reviewer)

    def has_risk_waiver(evidence: str) -> bool:
        def marker_value(marker: str) -> str:
            match = re.search(
                rf"{re.escape(marker)}\s*([^;|]+)",
                evidence,
                re.IGNORECASE,
            )
            return match.group(1).strip() if match else ""

        risk = marker_value("risk-accepted:")
        decision_ref = marker_value("decision-ref:")
        owner = marker_value("compensation-owner:")
        due = marker_value("due:")
        if any(missing_value(value) for value in (risk, decision_ref, owner, due)):
            return False
        try:
            return date.fromisoformat(due) >= date.today()
        except ValueError:
            return False

    change_required_fields = (
        "test_level",
        "case",
        "target/command",
        "baseline",
        "expected",
        "post-change",
        "evidence",
        "reviewer/date",
    )
    for audit in audits:
        if not audit.logic_change:
            continue
        directory = root if audit.path == "." else root / audit.path
        change = directory / "logic_change.md"
        text_value, error = read_text(change)
        if error:
            continue
        for change_id, block in change_blocks(text_value).items():
            rows = markdown_table_rows(block, "测试案例与审核矩阵")
            label = f"{audit.path}:{change_id}"
            if not rows:
                matrix_issues.append(f"{label}:missing-test-review-matrix")
                continue
            status = (control_values(block).get("status") or ["draft"])[0]
            for index, row in enumerate(rows, start=1):
                for field in change_required_fields:
                    if missing_value(row.get(field, "")):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-missing-{field}"
                        )
                baseline = row.get("baseline", "")
                post_change = row.get("post-change", "")
                evidence = row.get("evidence", "")
                reviewer = row.get("reviewer/date", "")
                test_level = row.get("test_level", "").strip().casefold()
                if test_level not in TEST_LEVELS:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-test-level:{test_level or 'empty'}"
                    )
                for field, value in (
                    ("baseline", baseline),
                    ("post-change", post_change),
                ):
                    token = result_token(value)
                    if token not in result_tokens:
                        matrix_issues.append(
                            f"{label}:test-row-{index}-invalid-{field}:{token or 'empty'}"
                        )
                    elif token in {"not-run", "not-applicable"} and not has_reason(
                        value
                    ):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-{field}-needs-reason"
                        )
                if not missing_value(evidence) and not has_evidence_locator(evidence):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-evidence-needs-locator"
                    )
                if not missing_value(reviewer) and not has_reviewer_and_date(reviewer):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-reviewer-needs-date"
                    )
                if (
                    status in {"implementing", "verifying"}
                    and result_token(baseline) == "not-run"
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-baseline-required-for-{status}"
                    )
                if (
                    status == "verifying"
                    and result_token(post_change) == "not-run"
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-post-change-required-for-verifying"
                    )
                if result_token(post_change) == "fail":
                    matrix_issues.append(
                        f"{label}:test-row-{index}-post-change-failed"
                    )

    records_root = root / CURRENT_HISTORY_ROOT / "records"
    if include_history and records_root.is_dir():
        for record in sorted(records_root.glob("logic_version-*.md")):
            record_text, record_error = read_text(record)
            if record_error:
                continue
            rows = markdown_table_rows(record_text, "测试与审核")
            label = record.relative_to(root).as_posix()
            if not rows:
                matrix_issues.append(f"{label}:missing-version-test-review-matrix")
                continue
            status = (control_values(record_text).get("status") or [""])[0]
            required = (
                "test_level",
                "case/command",
                "baseline",
                "post-change",
                "result",
                "evidence",
                "reviewer/date",
            )
            for index, row in enumerate(rows, start=1):
                for field in required:
                    if missing_value(row.get(field, "")):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-missing-{field}"
                        )
                evidence = row.get("evidence", "")
                reviewer = row.get("reviewer/date", "")
                result = row.get("result", "")
                test_level = row.get("test_level", "").strip().casefold()
                if test_level not in TEST_LEVELS:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-test-level:{test_level or 'empty'}"
                    )
                for field in ("baseline", "post-change"):
                    value = row.get(field, "")
                    field_token = result_token(value)
                    if field_token not in result_tokens:
                        matrix_issues.append(
                            f"{label}:test-row-{index}-invalid-{field}:{field_token or 'empty'}"
                        )
                    elif field_token in {
                        "not-run",
                        "not-applicable",
                    } and not has_reason(value):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-{field}-needs-reason"
                        )
                token = result_token(result)
                if token not in result_tokens:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-result:{token or 'empty'}"
                    )
                elif token in {"not-run", "not-applicable"} and not has_reason(result):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-result-needs-reason"
                    )
                if not missing_value(evidence) and not has_evidence_locator(evidence):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-evidence-needs-locator"
                    )
                if not missing_value(reviewer) and not has_reviewer_and_date(reviewer):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-reviewer-needs-date"
                    )
                if (
                    status in {"effective", "rolled-back", "correction"}
                    and token
                    not in {
                        "pass",
                        "not-applicable",
                    }
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-completed-version-needs-pass-or-waiver"
                    )
    return {
        "test_files": sorted(test_files),
        "configs": sorted(configs),
        "categories": sorted(categories),
        "matrix_issues": sorted(set(matrix_issues)),
        "limitation": "Discovery proves only that files/configs exist, not that tests ran or passed.",
    }


def audit_density(root: Path, audits: list[ModuleAudit]) -> dict:
    """Check document density and bloat."""
    issues = []

    # Hard limits from references/field-vocabulary.md
    LIMITS = {
        "SKILL.md": 200,
        "logic_readme.md": 400,
        "logic_change.md": 300,
    }

    for filename, limit in LIMITS.items():
        path = root / filename
        if path.exists():
            text, error = read_text(path)
            if not error:
                lines = text.count('\n') + 1
                if lines > limit:
                    issues.append(f"{filename}:exceeds-hard-limit:{lines}>{limit}")

    # Check individual CHG density in logic_change.md
    change_path = root / "logic_change.md"
    if change_path.exists():
        text, error = read_text(change_path)
        if not error:
            for change_id, block in change_blocks(text).items():
                lines = block.count('\n') + 1
                if lines > 80:
                    issues.append(f"{change_id}:exceeds-chg-limit:{lines}>80")

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
        "limits_checked": list(LIMITS.keys()),
    }


def collect_audit(args: argparse.Namespace) -> dict:
    root = args.project_root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    if args.max_depth is not None and args.max_depth < 0:
        raise ValueError("--max-depth must be zero or greater")
    if args.strict_v2 and args.max_depth is not None:
        raise ValueError(
            "--strict-v2 requires an unlimited scan; omit --max-depth and use "
            "--exclude for known dependency or generated trees"
        )
    selected_profiles = sum(
        bool(value)
        for value in (args.current_state, args.formal_review, args.strict_v2)
    )
    if selected_profiles > 1:
        raise ValueError(
            "--current-state, --formal-review, and --strict-v2 are mutually exclusive"
        )
    if args.current_state and args.require_test_matrix:
        raise ValueError(
            "--current-state does not inspect historical test matrices; run a "
            "--formal-review instead of combining it with --require-test-matrix"
        )

    current_profile = args.current_state or args.formal_review
    if current_profile and args.max_depth is not None:
        raise ValueError(
            "current/formal root-only audits require an unlimited scan; omit --max-depth"
        )

    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    audits: list[ModuleAudit] = []
    skipped_dirs = 0
    nested_project_roots: list[str] = []

    for directory, files in iter_directories(
        root, args.max_depth, excludes, nested_project_roots
    ):
        is_root = directory == root
        has_source = any(is_source_file(file) for file in files)
        has_runtime_data = any(
            is_runtime_data_file(file) for file in files
        ) or looks_like_runtime_data_directory(directory, root)
        has_test = any(is_test_file(file, root) for file in files)
        has_docs = (directory / "logic_readme.md").exists() or (
            directory / "logic_change.md"
        ).exists()
        if (
            args.all_dirs
            or is_root
            or has_source
            or has_runtime_data
            or has_test
            or has_docs
        ):
            audits.append(audit_module(directory, files, root))
        else:
            skipped_dirs += 1

    missing_map_candidates = [
        audit.path
        for audit in audits
        if audit.has_source_files and not audit.logic_readme
    ]
    runtime_data_candidates = [
        audit.path
        for audit in audits
        if audit.has_runtime_data and not audit.logic_readme
    ]
    malformed_maps = [
        audit.path
        for audit in audits
        if (
            (
                audit.logic_readme
                and (audit.missing_readme_sections or audit.missing_readme_fields)
            )
            or (
                audit.logic_change
                and (audit.missing_change_sections or audit.missing_change_fields)
            )
            or audit.semantic_issues
            or audit.change_without_readme
        )
    ]

    archive = unscanned_archive_report() if current_profile else audit_archive(root)
    proposal_integrity = (
        {
            "duplicate_ids": [],
            "missing_root_index": [],
            "unknown_root_index": [],
            "route_issues": [],
            "cross_module_link_issues": [],
            "authority_registry_issues": [],
            "authority_issues": [],
            "closed_change_ids_still_active": [],
        }
        if current_profile
        else audit_proposal_integrity(root, audits)
    )
    closed_change_records: dict[str, list[str]] = {}
    if not current_profile:
        for relative_record in archive["version_records"]:
            record_path = root / relative_record
            record_text, record_error = read_text(record_path)
            if record_error:
                continue
            record_values = control_values_raw(record_text)
            for raw_change_id in record_values.get("change_id", []):
                change_id = normalize_change_id(raw_change_id)
                if change_id:
                    closed_change_records.setdefault(change_id, []).append(
                        relative_record
                    )
        still_active = active_change_ids(root, audits).intersection(
            closed_change_records
        )
        proposal_integrity["closed_change_ids_still_active"] = sorted(
            f"{change_id}:{','.join(sorted(closed_change_records[change_id]))}"
            for change_id in still_active
        )
    module_routes = audit_module_routes(root, audits)
    registered_inherited_scopes = {
        normalize_scope_path(row.get("scope_path", ""))
        for row in module_routes["rows"]
        if row.get("doc_policy", "").strip().lower() == "inherited"
    }

    root_policy_text, _ = read_text(root / "logic_readme.md")
    root_policy_values = control_values(root_policy_text)
    registry_every_folder = "registry-every-folder" in root_policy_values.get(
        "coverage_policy", []
    )
    if registry_every_folder and not args.all_dirs:
        module_routes["route_issues"] = sorted(
            set(module_routes["route_issues"])
            | {"registry-every-folder-policy-requires---all-dirs"}
        )
    if registry_every_folder and args.all_dirs:
        registered_scopes = {
            normalize_scope_path(row.get("scope_path", ""))
            for row in module_routes["rows"]
            if row.get("scope_path", "").strip()
        }
        module_routes["route_issues"] = sorted(
            set(module_routes["route_issues"])
            | {
                f"registry-every-folder-unregistered:{audit.path}"
                for audit in audits
                if audit.path != "." and audit.path not in registered_scopes
            }
        )

    def covered_without_local_doc(scope: str) -> bool:
        if any(
            inherited == scope or is_scope_ancestor(inherited, scope)
            for inherited in registered_inherited_scopes
        ):
            return True
        candidates = [
            audit
            for audit in audits
            if audit.logic_readme
            and audit.path != "."
            and is_scope_ancestor(audit.path, scope)
        ]
        if not candidates:
            return False
        owner = max(candidates, key=lambda audit: len(scope_parts(audit.path)))
        owner_text, owner_error = read_text(root / owner.path / "logic_readme.md")
        if owner_error:
            return False
        raw_values = control_values_raw(owner_text)
        policy_values = control_values(owner_text)
        child_policy = (policy_values.get("child_policy") or [""])[0]
        if child_policy not in {"inherit", "review-before-split"}:
            return False
        patterns = {
            item.strip()
            for value in raw_values.get("owned_paths", [])
            for item in re.split(r"[,;，；]", value)
            if item.strip()
        }
        return any(
            scope == normalize_scope_path(pattern)
            or is_scope_ancestor(normalize_scope_path(pattern), scope)
            or fnmatchcase(scope, normalize_scope_path(pattern))
            for pattern in patterns
        )

    missing_map_candidates = [
        scope
        for scope in missing_map_candidates
        if not covered_without_local_doc(scope)
    ]
    runtime_data_candidates = [
        scope
        for scope in runtime_data_candidates
        if not covered_without_local_doc(scope)
    ]
    temp_working = audit_temp_working(root, audits)
    test_inventory = audit_test_inventory(
        root,
        audits,
        args.max_depth,
        excludes,
        include_history=not current_profile,
    )
    if args.current_state:
        test_inventory["matrix_issues"] = []
    if current_profile:
        misplaced_versions, misplaced_decisions = [], []
    else:
        misplaced_versions, misplaced_decisions = find_misplaced_records(root, excludes)
    parallel_current = find_parallel_current_candidates(root, excludes)
    nonroot_current_documents = find_nonroot_current_documents(
        root, excludes, registered_child_readme_paths(root)
    )
    misplaced_temp = find_misplaced_temp_records(root, excludes)
    entrypoints, private_knowledge, private_candidates = audit_agent_entrypoints(root)
    required_entry_names: set[str] = set()
    if args.require_agent_entry in {"codex", "both"}:
        required_entry_names.add("AGENTS.md")
    if args.require_agent_entry in {"claude", "both"}:
        required_entry_names.add("CLAUDE.md")
    missing_required_entries = sorted(
        entry["path"]
        for entry in entrypoints
        if entry["path"] in required_entry_names and not entry["exists"]
    )
    missing_default_agent_entry = current_profile and not any(
        entry["exists"] for entry in entrypoints
    )
    scattered_backups = (
        [] if current_profile else find_scattered_backup_candidates(root)
    )
    current_integrity = audit_current_state_integrity(
        root, audits, module_routes, all_dirs=args.all_dirs
    )
    density = audit_density(root, audits)
    formal_review = (
        audit_formal_review(root, test_inventory, temp_working)
        if args.formal_review
        else {
            "proposal_issues": [],
            "test_matrix_issues": [],
            "temp_reference_issues": [],
        }
    )

    limitations = [
        "A directory candidate is not automatically a meaningful governance boundary.",
        "The audit does not prove dependency, consumer, deployment, or runtime coverage.",
        "Backup-like directory names are advisory candidates, not confirmed violations.",
        "A missing AGENTS.md/.agents or CLAUDE.md/.claude pair fails only when --require-agent-entry selects it; an invalid existing entrypoint always fails strict mode.",
        "Agent read-order validation is a textual pointer check, not proof of agent runtime behavior.",
        "Private-directory content candidates are heuristic; inspect them before classifying as business truth.",
        "Missing maps are prompts for review, not automatic file-creation instructions.",
        "Runtime-data candidates require classification; they are not automatically code modules.",
        "Test discovery does not prove that any test ran or passed.",
        "Zero discovered test files is not by itself a failure; active and closed changes must still carry status-appropriate matrix evidence or an allowed not-applicable reason.",
    ]
    if current_profile:
        limitations = [
            "This root-only profile checks current-document structure, scope routes, active CHG lifecycle and declared coordination metadata, and agent entrypoints.",
            "It does not prove code semantics, undeclared dependencies, consumers, deployment, runtime behavior, or that discovered tests passed.",
            "History format and completed-version evidence do not determine this profile's result.",
        ]
        if args.formal_review:
            limitations.append(
                "Formal-review validates evidence containers and current test matrices; Codex, Claude, or a human must still inspect the affected code and runtime evidence."
            )

    reported_modules = [asdict(audit) for audit in audits]
    if current_profile:
        for module in reported_modules:
            module["missing_readme_sections"] = []
            module["missing_readme_fields"] = []
            module["missing_change_sections"] = []
            module["missing_change_fields"] = []
            module["v2_issues"] = []
            module["module_binding_issues"] = []

    current_gate_failed = current_profile and (
        any(current_integrity.values())
        or bool(nonroot_current_documents)
        or bool(parallel_current)
        or any(entry["exists"] and entry["issues"] for entry in entrypoints)
        or bool(private_knowledge)
        or bool(missing_required_entries)
        or bool(missing_default_agent_entry)
        or (args.formal_review and any(formal_review.values()))
    )

    return {
        "project_root": str(root),
        "candidate_policy": (
            "all directories"
            if args.all_dirs
            else "root, source/runtime-data/test, or documented directories"
        ),
        "max_depth": args.max_depth,
        "profile": (
            "current-state"
            if args.current_state
            else "formal-review"
            if args.formal_review
            else "v2"
            if args.strict_v2
            else "base"
        ),
        "excluded_names": sorted(excludes),
        "summary": {
            "candidate_directories": len(audits),
            "skipped_directories": skipped_dirs,
            "logic_readmes": sum(audit.logic_readme for audit in audits),
            "logic_changes": sum(audit.logic_change for audit in audits),
            "version_records": len(archive["version_records"]),
            "decision_records": len(archive["decision_records"]),
            "missing_map_candidates": len(missing_map_candidates),
            "runtime_data_candidates": len(runtime_data_candidates),
            "malformed_current_docs": (
                int(bool(current_integrity["document_issues"]))
                if current_profile
                else len(malformed_maps)
            ),
            "v2_document_gaps": (
                0
                if current_profile
                else sum(len(audit.v2_issues) for audit in audits)
            ),
            "module_binding_issues": (
                0
                if current_profile
                else sum(len(audit.module_binding_issues) for audit in audits)
            ),
            "module_route_issues": (
                len(module_routes["route_issues"])
                + len(module_routes["duplicate_module_ids"])
                + len(module_routes["duplicate_scope_paths"])
                + len(module_routes["unregistered_governance_dirs"])
                + len(module_routes["hierarchy_issues"])
            ),
            "logic_temp_records": len(temp_working["records"]),
            "logic_temp_issues": (
                len(temp_working["malformed"])
                + len(temp_working["missing_logic_temp"])
                + len(temp_working["orphan_change_ids"])
                + len(temp_working["expired"])
                + len(temp_working["forbidden_files"])
                + len(temp_working["unindexed"])
                + len(temp_working["extra_entries"])
                + len(temp_working["stale_index_entries"])
                + len(temp_working["change_temp_link_issues"])
            ),
            "test_files": len(test_inventory["test_files"]),
            "test_matrix_issues": len(test_inventory["matrix_issues"]),
            "broken_links": (
                sum(len(audit.broken_links) for audit in audits)
                + len(archive["broken_links"])
            ),
            "misplaced_history": len(misplaced_versions) + len(misplaced_decisions),
            "agent_entrypoint_issues": sum(
                len(entry["issues"]) for entry in entrypoints if entry["exists"]
            ),
            "missing_required_agent_entries": len(missing_required_entries),
            "missing_default_agent_entry": int(missing_default_agent_entry),
            "current_integrity_issues": sum(
                len(current_integrity[key])
                for key in (
                    "document_issues",
                    "scope_registry_issues",
                    "proposal_issues",
                    "responsibility_issues",
                )
            ),
            "formal_review_issues": sum(
                len(formal_review[key])
                for key in (
                    "proposal_issues",
                    "test_matrix_issues",
                    "temp_reference_issues",
                )
            ),
            "density_issues": len(density["issues"]),
            "private_agent_knowledge_files": len(private_knowledge),
            "private_agent_knowledge_candidates": len(private_candidates),
            "duplicate_change_ids": len(proposal_integrity["duplicate_ids"]),
            "unindexed_module_changes": len(proposal_integrity["missing_root_index"]),
            "unknown_root_change_ids": len(proposal_integrity["unknown_root_index"]),
            "closed_changes_still_active": len(
                proposal_integrity["closed_change_ids_still_active"]
            ),
            "parallel_current_candidates": len(parallel_current),
            "nonroot_current_documents": len(nonroot_current_documents),
            "misplaced_logic_temp": len(misplaced_temp),
        },
        "missing_map_candidates": missing_map_candidates,
        "runtime_data_candidates": runtime_data_candidates,
        "modules": reported_modules,
        "archive": archive,
        "module_routes": module_routes,
        "logic_temp": temp_working,
        "test_inventory": test_inventory,
        "misplaced_version_records": misplaced_versions,
        "misplaced_decision_records": misplaced_decisions,
        "parallel_current_candidates": parallel_current,
        "current_state_nonroot_documents": nonroot_current_documents,
        "misplaced_logic_temp": misplaced_temp,
        "scattered_backup_candidates": scattered_backups,
        "agent_entrypoints": entrypoints,
        "required_agent_entry": args.require_agent_entry,
        "missing_required_agent_entries": missing_required_entries,
        "missing_default_agent_entry": missing_default_agent_entry,
        "private_agent_knowledge_files": private_knowledge,
        "private_agent_knowledge_candidates": private_candidates,
        "proposal_integrity": proposal_integrity,
        "current_integrity": current_integrity,
        "density": density,
        "formal_review": formal_review,
        "static_gate": {
            "performed": current_profile,
            "passed": (not current_gate_failed) if current_profile else None,
            "scope": (
                "current-logic-map-and-formal-evidence-containers"
                if args.formal_review
                else "current-logic-map"
                if args.current_state
                else "not-requested"
            ),
            "meaning": (
                "Static document gate only; this is not a code-semantic review result."
                if current_profile
                else "No current/formal static gate was requested."
            ),
        },
        "semantic_review": {
            "performed": False,
            "status": "not-performed",
            "required_for_complete_review": current_profile,
            "scope": (
                "static-logic-map-and-evidence-container-checks"
                if current_profile
                else "not-requested"
            ),
            "next_step": (
                "Inspect affected code, callers, schema, tests, test results, and "
                "runtime evidence with Codex, Claude, or a human reviewer."
                if current_profile
                else "none"
            ),
        },
        "limitations": limitations,
    }


def print_text(report: dict) -> None:
    summary = report["summary"]
    lightweight_current = report["profile"] == "current-state"
    formal_review_profile = report["profile"] == "formal-review"
    current_profile = lightweight_current or formal_review_profile
    depth_label = (
        "unlimited" if report["max_depth"] is None else str(report["max_depth"])
    )
    print(f"Project: {report['project_root']}")
    print(
        f"Policy: {report['candidate_policy']}; max depth: {depth_label}; "
        f"profile: {report['profile']}"
    )
    if current_profile:
        print(
            "Summary: "
            f"{summary['candidate_directories']} scanned directories, "
            f"{summary['logic_readmes']} current policies, "
            f"{summary['logic_changes']} active-change files, "
            f"{summary['current_integrity_issues']} current-integrity issues, "
            f"{summary['formal_review_issues']} formal-review issues"
        )
        print(
            "Static gate: "
            + ("PASS" if report["static_gate"]["passed"] else "FAIL")
        )
        print(
            "Semantic review: NOT PERFORMED; inspect affected code, callers, "
            "schema, tests, results, and runtime evidence separately."
        )
    else:
        print(
            "Summary: "
            f"{summary['candidate_directories']} candidates, "
            f"{summary['logic_readmes']} current policies, "
            f"{summary['logic_changes']} active-change files, "
            f"{summary['version_records']} version records, "
            f"{summary['logic_temp_records']} working temp records, "
            f"{summary['malformed_current_docs']} malformed current documents, "
            f"{summary['broken_links']} broken links, "
            f"{summary['misplaced_history']} misplaced history records"
        )

    root_module = next(
        (module for module in report["modules"] if module["path"] == "."), None
    )
    missing_root_entries: list[str] = []
    if root_module is None or not root_module["logic_readme"]:
        missing_root_entries.append("logic_readme.md")
    if root_module is None or not root_module["logic_change"]:
        missing_root_entries.append("logic_change.md")
    if missing_root_entries:
        print("\nMissing root entries:")
        for name in missing_root_entries:
            print(f"  - {name}")

    if report["current_state_nonroot_documents"]:
        print("\nNon-root current documents:")
        for path in report["current_state_nonroot_documents"]:
            print(f"  - {path}")

    if not current_profile and report["missing_map_candidates"]:
        print("\nMissing-map candidates (review boundaries before creating files):")
        for path in report["missing_map_candidates"]:
            print(f"  - {path}")

    if not current_profile and report["runtime_data_candidates"]:
        print("\nRuntime-data candidates (classify; do not assume code module):")
        for path in report["runtime_data_candidates"]:
            print(f"  - {path}")

    problems = [
        module
        for module in report["modules"]
        if (
            module["missing_readme_sections"]
            or module["missing_readme_fields"]
            or module["missing_change_sections"]
            or module["missing_change_fields"]
            or module["semantic_issues"]
            or module["change_without_readme"]
            or module["broken_links"]
        )
    ]
    if problems and not current_profile:
        print("\nCurrent-document problems:")
        for module in problems:
            print(f"  - {module['path']}")
            if module["change_without_readme"]:
                print("    logic_change exists without logic_readme")
            if module["missing_readme_sections"]:
                print(
                    "    logic_readme missing sections: "
                    + ", ".join(module["missing_readme_sections"])
                )
            if module["missing_readme_fields"]:
                print(
                    "    logic_readme missing fields: "
                    + ", ".join(module["missing_readme_fields"])
                )
            if module["missing_change_sections"]:
                print(
                    "    logic_change missing sections: "
                    + ", ".join(module["missing_change_sections"])
                )
            if module["missing_change_fields"]:
                print(
                    "    logic_change missing fields: "
                    + ", ".join(module["missing_change_fields"])
                )
            if module["semantic_issues"]:
                print("    semantic issues: " + ", ".join(module["semantic_issues"]))
            if module["broken_links"]:
                print("    broken links: " + ", ".join(module["broken_links"]))

    v2_modules = [
        module
        for module in report["modules"]
        if module["v2_issues"] or module["module_binding_issues"]
    ]
    if v2_modules and not current_profile:
        print("\nRecall v2 document/binding gaps:")
        for module in v2_modules:
            print(f"  - {module['path']}")
            if module["v2_issues"]:
                print("    v2 fields/sections: " + ", ".join(module["v2_issues"]))
            if module["module_binding_issues"]:
                print("    binding: " + ", ".join(module["module_binding_issues"]))

    routes = report["module_routes"]
    route_problem_lists = (
        routes["route_issues"],
        routes["duplicate_module_ids"],
        routes["duplicate_scope_paths"],
        routes["unregistered_governance_dirs"],
        routes["hierarchy_issues"],
    )
    if not current_profile and any(route_problem_lists):
        print("\nModule-route problems:")
        for key in (
            "route_issues",
            "duplicate_module_ids",
            "duplicate_scope_paths",
            "unregistered_governance_dirs",
            "hierarchy_issues",
        ):
            for item in routes[key]:
                print(f"  - {key}: {item}")

    current_integrity = report["current_integrity"]
    if current_profile and any(current_integrity.values()):
        print("\nCurrent-state integrity problems:")
        for key in (
            "document_issues",
            "scope_registry_issues",
            "proposal_issues",
            "responsibility_issues",
        ):
            for item in current_integrity[key]:
                print(f"  - {key}: {item}")

    formal_review = report["formal_review"]
    if formal_review_profile and any(formal_review.values()):
        print("\nFormal-review evidence problems:")
        for key in (
            "proposal_issues",
            "test_matrix_issues",
            "temp_reference_issues",
        ):
            for item in formal_review[key]:
                print(f"  - {key}: {item}")

    archive = report["archive"]
    proposal_integrity = report["proposal_integrity"]
    if not current_profile and (
        proposal_integrity["duplicate_ids"]
        or proposal_integrity["missing_root_index"]
        or proposal_integrity["unknown_root_index"]
        or proposal_integrity["route_issues"]
        or proposal_integrity["cross_module_link_issues"]
        or proposal_integrity["authority_registry_issues"]
        or proposal_integrity["authority_issues"]
        or proposal_integrity["closed_change_ids_still_active"]
    ):
        print("\nActive-proposal problems:")
        for item in proposal_integrity["duplicate_ids"]:
            print(f"  - duplicate CHG-ID: {item}")
        for item in proposal_integrity["missing_root_index"]:
            print(f"  - module proposal missing from root index: {item}")
        for item in proposal_integrity["unknown_root_index"]:
            print(f"  - root index references unknown CHG-ID: {item}")
        for item in proposal_integrity["route_issues"]:
            print(f"  - proposal route: {item}")
        for item in proposal_integrity["cross_module_link_issues"]:
            print(f"  - cross-module link: {item}")
        for item in proposal_integrity["authority_registry_issues"]:
            print(f"  - decision-authority registry: {item}")
        for item in proposal_integrity["authority_issues"]:
            print(f"  - decision-authority: {item}")
        for item in proposal_integrity["closed_change_ids_still_active"]:
            print(f"  - closed change still active: {item}")

    archive_issues = (
        archive["malformed_versions"]
        or archive["malformed_decisions"]
        or archive["backups_missing_manifest"]
        or archive["malformed_backups"]
        or archive["broken_links"]
        or archive["index"] not in {"ok", "not-needed"}
        or archive["index_consistency"]["unindexed_records"]
        or archive["index_consistency"]["duplicate_ids"]
        or archive["index_consistency"]["row_mismatches"]
        or archive["index_consistency"]["unknown_record_links"]
        or report["misplaced_version_records"]
        or report["misplaced_decision_records"]
        or archive["duplicate_history_roots"]
        or archive["extra_paths"]
        or archive["forbidden_current_docs"]
        or archive["legacy_records"]
    )
    if archive_issues and not current_profile:
        print("\nLogic-version/history problems:")
        if archive["duplicate_history_roots"]:
            print("  - both logic_version and legacy logic_archive exist")
        for path in archive["legacy_records"]:
            print(f"  - legacy history record requires review/migration: {path}")
        for path in archive["extra_paths"]:
            print(f"  - unexpected logic_version path: {path}")
        for path in archive["forbidden_current_docs"]:
            print(f"  - current truth stored under logic_version: {path}")
        if archive["index"] not in {"ok", "not-needed"}:
            print(f"  - index: {archive['index']}")
        for item in archive["malformed_versions"]:
            print(f"  - malformed version: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for item in archive["malformed_decisions"]:
            print(f"  - malformed decision: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for path in archive["backups_missing_manifest"]:
            print(f"  - backup missing manifest: {path}")
        for item in archive["malformed_backups"]:
            print(f"  - malformed backup manifest: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for path in report["misplaced_version_records"]:
            print(f"  - misplaced version: {path}")
        for path in report["misplaced_decision_records"]:
            print(f"  - misplaced decision: {path}")
        for item in archive["broken_links"]:
            print(f"  - broken logic_version link: {item}")
        for path in archive["index_consistency"]["unindexed_records"]:
            print(f"  - logic_version record not indexed: {path}")
        for item in archive["index_consistency"]["duplicate_ids"]:
            print(f"  - duplicate logic_version id: {item}")
        for item in archive["index_consistency"]["row_mismatches"]:
            print(f"  - logic_version index row mismatch: {item}")
        for path in archive["index_consistency"]["unknown_record_links"]:
            print(f"  - unknown logic_version record link: {path}")

    temp = report["logic_temp"]
    if not current_profile and summary["logic_temp_issues"]:
        print("\nLogic-temp problems:")
        for item in temp["malformed"]:
            print(f"  - malformed: {item['path']}")
            if item.get("missing_sections"):
                print("    missing sections: " + ", ".join(item["missing_sections"]))
            if item.get("missing_fields"):
                print("    missing fields: " + ", ".join(item["missing_fields"]))
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for key in (
            "missing_logic_temp",
            "orphan_change_ids",
            "expired",
            "forbidden_files",
            "unindexed",
            "extra_entries",
            "stale_index_entries",
            "change_temp_link_issues",
        ):
            for item in temp[key]:
                print(f"  - {key}: {item}")

    if report["parallel_current_candidates"]:
        print("\nParallel current-truth candidates:")
        for path in report["parallel_current_candidates"]:
            print(f"  - {path}")

    if not current_profile and report["misplaced_logic_temp"]:
        print("\nMisplaced logic_temp records:")
        for path in report["misplaced_logic_temp"]:
            print(f"  - {path}")

    if not current_profile and report["test_inventory"]["matrix_issues"]:
        print("\nTest-matrix findings:")
        for item in report["test_inventory"]["matrix_issues"]:
            print(f"  - {item}")

    entry_issues = [
        entry
        for entry in report["agent_entrypoints"]
        if entry["exists"] and entry["issues"]
    ]
    if entry_issues or report["private_agent_knowledge_files"]:
        print("\nAgent-entry problems:")
        for entry in entry_issues:
            print(f"  - {entry['path']}: {', '.join(entry['issues'])}")
        for path in report["private_agent_knowledge_files"]:
            print(f"  - business knowledge stored in agent-private path: {path}")
    if report["missing_required_agent_entries"]:
        print("\nMissing required agent entries:")
        for path in report["missing_required_agent_entries"]:
            print(f"  - {path}")
    if report["missing_default_agent_entry"]:
        print("\nMissing agent entry:")
        print(
            "  - current/formal profiles require at least one root AGENTS.md or "
            "CLAUDE.md with its matching .agents/ or .claude/ directory"
        )
    if report["private_agent_knowledge_candidates"]:
        print("\nAgent-private knowledge candidates (review):")
        for path in report["private_agent_knowledge_candidates"]:
            print(f"  - {path}")

    if report["scattered_backup_candidates"]:
        print("\nBackup-like directories to review (advisory):")
        for path in report["scattered_backup_candidates"]:
            print(f"  - {path}")

    print("\nLimitations:")
    for limitation in report["limitations"]:
        print(f"  - {limitation}")


def strict_failure(
    report: dict,
    *,
    v2: bool = False,
    current_state: bool = False,
    formal_review: bool = False,
    require_test_matrix: bool = False,
) -> bool:
    root_module = next(
        (module for module in report["modules"] if module["path"] == "."), None
    )
    if (
        root_module is None
        or not root_module["logic_readme"]
        or not root_module["logic_change"]
    ):
        return True

    if current_state or formal_review:
        current_integrity = report.get("current_integrity", {})
        if any(
            current_integrity.get(key, [])
            for key in (
                "document_issues",
                "scope_registry_issues",
                "proposal_issues",
                "responsibility_issues",
            )
        ):
            return True
        if (
            report["current_state_nonroot_documents"]
            or report["parallel_current_candidates"]
        ):
            return True
        if any(
            entry["exists"] and entry["issues"] for entry in report["agent_entrypoints"]
        ):
            return True
        if report["private_agent_knowledge_files"]:
            return True
        if report["missing_required_agent_entries"] or report.get(
            "missing_default_agent_entry", False
        ):
            return True
        if formal_review:
            formal = report.get("formal_review", {})
            if any(
                formal.get(key, [])
                for key in (
                    "proposal_issues",
                    "test_matrix_issues",
                    "temp_reference_issues",
                )
            ):
                return True
        return False

    if any(
        module["change_without_readme"]
        or module["missing_readme_sections"]
        or module["missing_readme_fields"]
        or module["missing_change_sections"]
        or module["missing_change_fields"]
        or module["semantic_issues"]
        or module["broken_links"]
        for module in report["modules"]
    ):
        return True

    proposal_integrity = report["proposal_integrity"]
    if (
        proposal_integrity["duplicate_ids"]
        or proposal_integrity["missing_root_index"]
        or proposal_integrity["unknown_root_index"]
        or proposal_integrity["closed_change_ids_still_active"]
        or proposal_integrity["authority_issues"]
    ):
        return True

    archive = report["archive"]
    if (
        archive["index"] not in {"ok", "not-needed"}
        or archive["malformed_versions"]
        or archive["malformed_decisions"]
        or archive["backups_missing_manifest"]
        or archive["malformed_backups"]
        or archive["broken_links"]
        or archive["index_consistency"]["unindexed_records"]
        or archive["index_consistency"]["duplicate_ids"]
        or archive["index_consistency"]["row_mismatches"]
        or archive["index_consistency"]["unknown_record_links"]
        or report["misplaced_version_records"]
        or report["misplaced_decision_records"]
        or archive["duplicate_history_roots"]
        or archive["extra_paths"]
        or archive["forbidden_current_docs"]
    ):
        return True

    if report["parallel_current_candidates"]:
        return True

    if any(
        entry["exists"] and entry["issues"] for entry in report["agent_entrypoints"]
    ):
        return True

    if report["private_agent_knowledge_files"]:
        return True

    if report["missing_required_agent_entries"]:
        return True

    if require_test_matrix and report["test_inventory"]["matrix_issues"]:
        return True

    if v2:
        if report["missing_map_candidates"] or report["runtime_data_candidates"]:
            return True
        if any(
            module["v2_issues"] or module["module_binding_issues"]
            for module in report["modules"]
        ):
            return True
        if report["misplaced_logic_temp"]:
            return True
        routes = report["module_routes"]
        if any(
            routes[key]
            for key in (
                "route_issues",
                "duplicate_module_ids",
                "duplicate_scope_paths",
                "unregistered_governance_dirs",
                "hierarchy_issues",
            )
        ):
            return True
        if (
            proposal_integrity["route_issues"]
            or proposal_integrity["cross_module_link_issues"]
            or proposal_integrity["authority_registry_issues"]
        ):
            return True
        temp = report["logic_temp"]
        if any(
            temp[key]
            for key in (
                "malformed",
                "missing_logic_temp",
                "orphan_change_ids",
                "expired",
                "forbidden_files",
                "unindexed",
                "extra_entries",
                "stale_index_entries",
                "change_temp_link_issues",
            )
        ):
            return True
        if not archive["exists"] or archive["index"] != "ok" or archive["legacy_roots"]:
            return True

    return False


def main() -> int:
    args = parse_args()
    try:
        report = collect_audit(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)

    strict_requested = (
        args.strict
        or args.strict_v2
        or args.current_state
        or args.formal_review
        or args.require_test_matrix
        or bool(args.require_agent_entry)
    )
    return (
        1
        if strict_requested
        and strict_failure(
            report,
            v2=args.strict_v2,
            current_state=args.current_state,
            formal_review=args.formal_review,
            require_test_matrix=args.require_test_matrix,
        )
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
