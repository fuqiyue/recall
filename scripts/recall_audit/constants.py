"""审计器常量：排除目录、字段词汇、表头别名、正则与阈值。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re

from recall_common import CHANGE_ID_PATTERN, CHANGE_ID_RE  # noqa: E402,F401  RULE-021

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

# RULE-023：CHG 块字段要求按治理模式分档（references/field-vocabulary.md 的
# collaborative / compliance 层）。personal 模式下这些字段"缺则不查、写则照查"；
# status / effective / proposal_revision / recall_route / changed_by 与实施前的
# decision_confirmed_by + decision_confirmed_at 在所有模式都必填。
PERSONAL_OPTIONAL_CHANGE_FIELDS = {
    # collaborative 层
    "topic_id",
    "authority_surfaces",
    "based_on",
    "depends_on",
    "conflicts_with",
    "conflict_resolution",
    "semantic_review_state",
    "semantic_reviewed_by",
    "semantic_review_ref",
    "semantic_reviewed_at",
    # compliance 层
    "decision_gate",
    "decision_state",
    "decision_record",
    "decision_ref",
    "confirmed_proposal_revision",
    "reserved_version_id",
    "version_slug",
    "runtime_state",
    "runtime_environments",
    "feature_flag",
    "history_retention",
    "intent_source_refs",
    "intent_traceability",
    "docs_impact",
    "governance_execution_ref",
}

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
    "domain",  # RULE-018 二级领域文档（部门法）
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
# 议案编号正则来自 recall_common（RULE-021 ③：validate / conflicts / 审计器同一份）
CHANGE_HEADING_RE = re.compile(rf"^\s*##\s+({CHANGE_ID_PATTERN})\b", re.IGNORECASE)
DECISION_AUTHORITY_ID_RE = re.compile(r"^AUTH-[A-Z0-9][A-Z0-9-]*$", re.IGNORECASE)
POSITIVE_INTEGER_RE = re.compile(r"^[1-9]\d*$")
DEPENDENCY_REFERENCE_RE = re.compile(
    rf"^({CHANGE_ID_PATTERN})@revision-([1-9]\d*)$", re.IGNORECASE
)


NONE_LIKE_CONTROL_VALUES = {"", "none", "unknown", "n/a", "not-applicable", "..."}


ANGLE_PLACEHOLDER_RE = re.compile(r"<[^<>\r\n]+>")
# 行内代码段：占位符识别前剔除，`<meta>` 之类的代码不算模板占位符
CODE_SPAN_RE = re.compile(r"`[^`\r\n]*`")
# 围栏代码块（``` 或 ~~~）：链接可达性检查前剔除，示例里的 `[ID](path)` 不算真实链接
FENCED_CODE_RE = re.compile(
    r"^(`{3,}|~{3,})[^\r\n]*\r?\n.*?^\1[ \t]*$", re.MULTILINE | re.DOTALL
)
# 空账本的 active_changes：模板写 none，消费项目也常写 0，两者同义
EMPTY_LEDGER_COUNT_VALUES = {"none", "0"}
