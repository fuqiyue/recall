import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "audit_logic_map.py"
SPEC = importlib.util.spec_from_file_location("audit_logic_map", SCRIPT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def audit_args(
    root: Path,
    *,
    current_state: bool = False,
    formal_review: bool = False,
    require_agent_entry: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        project_root=root,
        max_depth=None,
        all_dirs=False,
        exclude=[],
        json=False,
        strict=False,
        strict_v2=False,
        current_state=current_state,
        formal_review=formal_review,
        require_test_matrix=False,
        require_agent_entry=require_agent_entry,
    )


def agent_entry(*, legacy_marker: bool = False, tool: str = "codex") -> str:
    business_truth = (
        "project-root-and-module-logic-docs"
        if legacy_marker
        else "project-root-current-logic-docs"
    )
    config_root = ".agents" if tool == "codex" else ".claude"
    return f"""# Agent entry

RECALL_ROOT_ORDER: <project-root>/logic_readme.md -> <project-root>/logic_change.md
RECALL_CHANGE_EFFECTIVE: false
RECALL_BUSINESS_TRUTH: {business_truth}
RECALL_HISTORY_ROOT: <project-root>/logic_version
RECALL_AGENT_CONFIG_ROOT: <project-root>/{config_root}
"""


INHERITED_APP_ROW = "| MOD-APP | src | in-system | module/runtime-code | inherited | [app policy](logic_readme.md#scope-mod-app) | [changes](logic_change.md) | self | active |"

README_ONLY_APP_ROW = "| MOD-APP | src | in-system | module/runtime-code | readme-only | [app policy](src/logic_readme.md) | none | self | active |"

PAIRED_APP_ROW = "| MOD-APP | src | in-system | module/runtime-code | paired | [app policy](src/logic_readme.md) | [changes](src/logic_change.md) | self | active |"


def child_readme(policy: str = "readme-only") -> str:
    return f"""# App module logic

## 文档控制

- doc_id: LOGIC-DEMO-APP
- module_id: MOD-APP
- scope: src
- scope_path: src
- parent: ../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: module
- layer: runtime-code
- module_doc_policy: {policy}
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:demo-repository
- governance_evidence: git:demo-repository
- governance_verification: recorded
- governance_verified_at: 2026-07-22
- effective_from: 2026-07-22
- last_verified: 2026-07-22
- review_trigger: interval:90d; event:release
- source_of_truth: src/app.py
- source_decisions: none
- intent_summary: keep the app module logic discoverable
- intent_sources: user-confirmed:2026-07-22
- decision_validity: valid
- validity_evidence: user-confirmed:2026-07-22

## 范围登记与归属

- canonical_readme: src/logic_readme.md
- canonical_change: none
- owned_paths: src
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-APP-OUTPUT | ordinary | Keep the module output stable. | Callers rely on the current shape. | none | user-confirmed:2026-07-22 | src/app.py | valid | 2026-07-22 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| src/app.py | source/runtime-code | application | input | output | code | yes | none |

## 活跃议案入口

- 唯一入口：[logic_change.md](../logic_change.md)
- 相关 CHG-ID：none
"""


def root_readme(
    *,
    full: bool,
    scope_path: str = ".",
    governance_mode: str = "personal",
    governance_ref: str = "git:demo-repository",
) -> str:
    controls = f"""## 文档控制

- doc_id: LOGIC-DEMO
- module_id: MOD-ROOT
- scope: .
- scope_path: {scope_path}
- parent: none
- parent_module_id: none
- membership: in-system
- scope_type: root
- layer: runtime-code
- module_doc_policy: paired
- status: active
- owner: self
- governance_mode: {governance_mode}
- governance_ref: {governance_ref}
- governance_evidence: git:demo-repository
- governance_verification: recorded
- governance_verified_at: 2026-07-22
- effective_from: 2026-07-22
- last_verified: 2026-07-22
- review_trigger: interval:90d; event:release
- source_of_truth: src/app.py
- source_decisions: none
- intent_summary: keep current project logic discoverable
- intent_sources: user-confirmed:2026-07-22
- decision_validity: valid
- validity_evidence: user-confirmed:2026-07-22
- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: src
- child_policy: inherit
- data_owner: none
- registry_status: registered
"""
    registry = """## 范围登记与归属

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: runtime-code and test
- version_root: logic_version/
- temp_root: logic_version/working/

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [root](logic_readme.md) | [changes](logic_change.md) | self | active |
| MOD-APP | src | in-system | module/runtime-code | inherited | [app policy](logic_readme.md#scope-mod-app) | [changes](logic_change.md) | self | active |

<a id="scope-mod-app"></a>
### MOD-APP: Application

- scope_path: src
"""
    minimal_sections = """## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-OUTPUT | key | Preserve the output contract. | Keep callers stable while implementation changes. | [VER-20260722-001](logic_version/records/logic_version-20260722-001-output-contract.md) | user-confirmed:2026-07-22 | src/app.py + tests/test_app.py | valid | 2026-07-22 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| src/app.py | source/runtime-code | application | input | output | code | yes | tests/test_app.py |

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
"""
    if not full:
        return "# Demo Logic\n\n" + controls + "\n" + registry + "\n" + minimal_sections

    formal_sections = """## 目标与边界

Demo boundary.

## 数据与控制流

input -> application -> output

## 消费者与公共契约

No external consumer.

## 不可破坏约束

- INV-001: preserve output contract.

## 兼容与迁移制度

No legacy state.

## 代码、生成物与运行数据边界

Source and tests are separate.

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | INV-001 | python -m unittest | pass | tests/test_app.py |

## 有效决策索引

none

## 当前限制

none

## 修改检查清单

- [ ] review affected code

## 责任记录约定

The scope owner records responsibility, not access control.
"""
    return (
        "# Demo Logic\n\n"
        + controls
        + "\n"
        + registry
        + "\n"
        + minimal_sections
        + "\n"
        + formal_sections
    )


def change_document(
    *,
    full: bool,
    status: str = "implementing",
    affected_scopes: str | None = "src",
    changed_by: str | None = "self",
    proposal_path: str = "[CHG-20260722-001](logic_change.md#chg-20260722-001)",
    include_matrix: bool = True,
    decision_gate: str = "not-required",
    decision_state: str | None = None,
    proposal_revision: str = "1",
    recall_route: str | None = None,
    authority_surfaces: str = "RULE-OUTPUT",
    based_on: str | None = None,
    depends_on: str = "none",
    conflicts_with: str = "none",
    conflict_resolution: str = "none",
    history_retention: str | None = None,
    runtime_state: str = "not-implemented",
    runtime_environments: str = "none",
    feature_flag: str = "none",
    governance_mode: str = "personal",
    governance_ref: str = "git:demo-repository",
    topic_id: str = "none",
) -> str:
    affected_line = (
        f"- affected_scopes: {affected_scopes}\n" if affected_scopes is not None else ""
    )
    changed_line = f"- changed_by: {changed_by}\n" if changed_by is not None else ""
    resolved_based_on = based_on or (
        "policy: logic_readme.md#rule-output; code: snapshot:before-change; "
        f"surfaces: {authority_surfaces}"
    )
    resolved_decision_state = decision_state or (
        "confirmed"
        if decision_gate == "required" and status in {"implementing", "verifying"}
        else "pending"
        if decision_gate == "required"
        else "not-required"
    )
    resolved_recall_route = recall_route or (
        "high" if decision_gate == "required" else "medium"
    )
    confirmed = resolved_decision_state == "confirmed"
    decision_record = "required" if decision_gate == "required" else "not-required"
    resolved_history_retention = history_retention or (
        "full" if decision_gate == "required" else "none"
    )
    reserved_version = (
        "VER-20260722-001"
        if decision_gate == "required" and status in {"implementing", "verifying"}
        else "none"
    )
    version_slug = (
        "logic_version-20260722-001-src"
        if reserved_version != "none"
        else "none"
    )
    confirmed_revision = proposal_revision if confirmed else "none"
    confirmed_by = "user" if confirmed else "none"
    decision_ref = "user-confirmed:2026-07-22" if confirmed else "none"
    confirmed_at = "2026-07-22" if confirmed else "none"
    base = f"""# Demo Active Changes

## 文档控制

- scope: .
- scope_path: .
- module_id: MOD-ROOT
- current_policy: logic_readme.md
- owner: self
- governance_mode: {governance_mode}
- governance_ref: {governance_ref}
- governance_evidence: git:demo-repository
- governance_verification: recorded
- governance_verified_at: 2026-07-22
- last_updated: 2026-07-22
- active_changes: 1

## 议案规则

- All entries are non-effective until promoted.

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260722-001 | {status} | src | self | test | none | {proposal_path} | 2026-07-22 |

<a id="chg-20260722-001"></a>
## CHG-20260722-001: Test proposal

### 元数据

- status: {status}
- effective: false
- topic_id: {topic_id}
- proposal_revision: {proposal_revision}
- recall_route: {resolved_recall_route}
- decision_gate: {decision_gate}
- decision_state: {resolved_decision_state}
- confirmed_proposal_revision: {confirmed_revision}
- decision_confirmed_by: {confirmed_by}
- decision_ref: {decision_ref}
- decision_confirmed_at: {confirmed_at}
- decision_record: {decision_record}
- semantic_review_state: pending
- semantic_reviewed_by: none
- semantic_review_ref: none
- semantic_reviewed_at: none
- governance_execution_ref: none
- owner: self
{changed_line}- proposer: user
- created: 2026-07-22
- last_status_change: 2026-07-22
- review_due: event-driven
- target_effective: event-driven
- scope: src
{affected_line}- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)
- related_decisions: none
- authority_surfaces: {authority_surfaces}
- based_on: {resolved_based_on}
- depends_on: {depends_on}
- conflicts_with: {conflicts_with}
- conflict_resolution: {conflict_resolution}
- history_retention: {resolved_history_retention}
- runtime_state: {runtime_state}
- runtime_environments: {runtime_environments}
- feature_flag: {feature_flag}
- blocked_by: none
- next_action: implement
- unblock_condition: none
- reserved_version_id: {reserved_version}
- version_slug: {version_slug}
- temp_path: none
- docs_impact: logic_readme: none; code-map: none; tests: update; history: none
"""
    if not full:
        return (
            base
            + """
### 当前状态、代码逻辑与差距

- current_behavior: current code behavior

### 拟议制度

Keep the output contract.

### 兼容、迁移与回滚

Rollback the code change.

### 开放问题与用户澄清

- questions_for_user: none
"""
        )

    matrix = (
        """
| test_level | case | target/command | baseline | expected | post-change | evidence | reviewer/date |
|---|---|---|---|---|---|---|---|
| unit | output contract | python -m unittest | pass | pass | pass | command: python -m unittest | self + 2026-07-22 |
"""
        if include_matrix
        else "No matrix recorded.\n"
    )
    return (
        base
        + f"""
### 当前状态、代码逻辑与差距

- current_behavior: current code behavior verified by tests
- current_logic_fit: existing application boundary can contain the change
- baseline_tests: python -m unittest; pass; 2026-07-22
- user_intent_gap: none

### 拟议制度

Keep the output contract.

### 意图来源与可审计提炼

- intent_source_refs: task:demo-20260722
- intent_digest: Preserve the requested output behavior while changing implementation.
- intent_non_goals: not-specified
- intent_constraints: Preserve the output contract.
- intent_acceptance: Unit tests preserve the output contract.
- intent_status: source-derived
- intent_distilled_by: self
- intent_distilled_at: 2026-07-22
- intent_traceability: INT-20260722-001 -> RULE-OUTPUT -> test:tests/test_app.py#output-contract -> VER-20260722-001

### 必要理由与来源

- why: preserve current behavior while implementing the requested change

### 决策检查点

- decision_needed_because: not-required
- decision_question: not-required
- confirmation_request: not-required
- confirmation_result: not-required

### 方案与决策

| 方案 | 收益 | 风险/坏处 | 复杂度增量 | 状态 |
|---|---|---|---|---|
| A | minimal change | low | low | selected |

### 消费者与影响

| 行为/契约 | artifact_layer | producer | consumer | environment | 影响 | 证据 |
|---|---|---|---|---|---|---|
| output | runtime-code | app | test | local | preserved | tests/test_app.py |

### 兼容、迁移与回滚

No legacy state; rollback the code change.

### 测试案例与审核矩阵

{matrix}
### 实施与验收门槛

- [x] current behavior recorded

### 开放问题与用户澄清

- questions_for_user: none

### 晋升与归档

- target_logic_sections: 当前制度
- version_record: none
- close_condition: verification complete
- temp_cleanup: none
"""
    )


def append_active_change(
    document: str,
    *,
    change_id: str,
    status: str = "draft",
    proposal_revision: str = "1",
    authority_surfaces: str = "RULE-INPUT",
    depends_on: str = "none",
    conflicts_with: str = "none",
    conflict_resolution: str = "none",
) -> str:
    """Append a valid lightweight CHG body to a root-only fixture."""
    source = change_document(
        full=False,
        status=status,
        proposal_revision=proposal_revision,
        authority_surfaces=authority_surfaces,
        depends_on=depends_on,
        conflicts_with=conflicts_with,
        conflict_resolution=conflict_resolution,
    )
    source_anchor = '<a id="chg-20260722-001"></a>'
    block = source[source.index(source_anchor) :]
    block = block.replace("CHG-20260722-001", change_id).replace(
        "chg-20260722-001", change_id.casefold()
    )
    block = "\n".join(
        f"- depends_on: {depends_on}"
        if line.startswith("- depends_on:")
        else f"- conflicts_with: {conflicts_with}"
        if line.startswith("- conflicts_with:")
        else line
        for line in block.splitlines()
    )
    active_count = len(AUDIT.change_blocks(document))
    document = document.replace(
        f"- active_changes: {active_count}",
        f"- active_changes: {active_count + 1}",
        1,
    )
    index_row = (
        f"| {change_id} | {status} | src | self | test | none | "
        f"[{change_id}](logic_change.md#{change_id.casefold()}) | 2026-07-22 |"
    )
    document = document.replace(
        "\n\n" + source_anchor,
        "\n" + index_row + "\n\n" + source_anchor,
        1,
    )
    return document + "\n" + block


class RootOnlyAuditTests(unittest.TestCase):
    def write_project(
        self,
        root: Path,
        *,
        full: bool = False,
        write_agent: bool = True,
        governance_mode: str = "personal",
        governance_ref: str = "git:demo-repository",
        **change_kwargs: object,
    ) -> None:
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("def run(): return 1\n", encoding="utf-8")
        record = (
            root
            / "logic_version"
            / "records"
            / "logic_version-20260722-001-output-contract.md"
        )
        record.parent.mkdir(parents=True)
        record.write_text("# Decision record\n", encoding="utf-8")
        (root / "logic_readme.md").write_text(
            root_readme(
                full=full,
                governance_mode=governance_mode,
                governance_ref=governance_ref,
            ),
            encoding="utf-8",
        )
        (root / "logic_change.md").write_text(
            change_document(
                full=full,
                governance_mode=governance_mode,
                governance_ref=governance_ref,
                **change_kwargs,
            ),
            encoding="utf-8",
        )
        if write_agent:
            (root / ".agents").mkdir()
            (root / "AGENTS.md").write_text(agent_entry(), encoding="utf-8")

    def collect(self, root: Path, *, formal: bool = False) -> dict:
        return AUDIT.collect_audit(
            audit_args(root, current_state=not formal, formal_review=formal)
        )

    def fails(self, report: dict, *, formal: bool = False) -> bool:
        return AUDIT.strict_failure(
            report, current_state=not formal, formal_review=formal
        )

    def test_current_state_accepts_lightweight_root_only_map(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            report = self.collect(root)

        self.assertFalse(self.fails(report))
        self.assertEqual(report["summary"]["v2_document_gaps"], 0)
        self.assertFalse(any(module["v2_issues"] for module in report["modules"]))
        self.assertFalse(report["semantic_review"]["performed"])
        self.assertEqual(report["semantic_review"]["status"], "not-performed")
        self.assertTrue(report["static_gate"]["passed"])
        self.assertFalse(report["archive"]["scanned"])

    def test_active_deployed_behavior_must_be_promoted_and_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                runtime_state="deployed-active",
                runtime_environments="production",
            )
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:deployed-active-must-be-promoted-and-closed",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_topic_can_group_active_change_without_changing_chg_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, topic_id="TOPIC-20260722-001")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "|---|---|---|---|---|---|\n\n## 活跃议案索引",
                "|---|---|---|---|---|---|\n"
                "| TOPIC-20260722-001 | output behavior | self | task:demo | "
                "CHG-20260722-001 | open |\n\n## 活跃议案索引",
                1,
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertFalse(report["current_integrity"]["proposal_issues"])
        self.assertFalse(self.fails(report))

    def test_topic_membership_must_match_change_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "|---|---|---|---|---|---|\n\n## 活跃议案索引",
                "|---|---|---|---|---|---|\n"
                "| TOPIC-20260722-001 | output behavior | self | task:demo | "
                "CHG-20260722-001 | open |\n\n## 活跃议案索引",
                1,
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:topic-index-lists-change-with-topic-id-none",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_topic_related_changes_cannot_mix_none_and_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, topic_id="TOPIC-20260722-001")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "|---|---|---|---|---|---|\n\n## 活跃议案索引",
                "|---|---|---|---|---|---|\n"
                "| TOPIC-20260722-001 | output behavior | self | task:demo | "
                "none; CHG-20260722-001 | open |\n\n## 活跃议案索引",
                1,
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "topic-index-row-1:related-changes-cannot-mix-none",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_change_cannot_belong_to_multiple_topics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, topic_id="TOPIC-20260722-001")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "|---|---|---|---|---|---|\n\n## 活跃议案索引",
                "|---|---|---|---|---|---|\n"
                "| TOPIC-20260722-001 | output behavior | self | task:demo | "
                "CHG-20260722-001 | open |\n"
                "| TOPIC-20260722-002 | output behavior | self | task:demo | "
                "CHG-20260722-001 | open |\n\n## 活跃议案索引",
                1,
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:multiple-topic-memberships:"
            "TOPIC-20260722-001,TOPIC-20260722-002",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_collaborative_high_risk_review_must_be_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                governance_mode="collaborative",
                governance_ref="pr-ci:demo-policy",
                decision_gate="required",
            )
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "- semantic_review_state: pending\n"
                "- semantic_reviewed_by: none\n"
                "- semantic_review_ref: none\n"
                "- semantic_reviewed_at: none",
                "- semantic_review_state: passed\n"
                "- semantic_reviewed_by: self\n"
                "- semantic_review_ref: pr:42\n"
                "- semantic_reviewed_at: 2026-07-22",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:collaborative-high-risk-review-must-be-independent",
            report["current_integrity"]["responsibility_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_current_documents_must_share_governance_control(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "- governance_ref: git:demo-repository",
                "- governance_ref: git:other-repository",
                1,
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "governance-ref-mismatch-between-current-documents",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_collaborative_governance_requires_verified_typed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                governance_mode="collaborative",
                governance_ref="pr:42;ci:build-7",
            )
            report = self.collect(root)

        issues = report["current_integrity"]["document_issues"]
        self.assertIn(
            "logic_readme:collaborative-governance-evidence-must-be-verified",
            issues,
        )
        self.assertIn(
            "logic_change:collaborative-governance-evidence-must-be-verified",
            issues,
        )
        self.assertTrue(self.fails(report))

    def test_collaborative_governance_rejects_git_only_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                governance_mode="collaborative",
                governance_ref="branch-protection:main",
            )
            for name in ("logic_readme.md", "logic_change.md"):
                path = root / name
                document = path.read_text(encoding="utf-8").replace(
                    "- governance_verification: recorded",
                    "- governance_verification: verified",
                )
                path.write_text(document, encoding="utf-8")
            report = self.collect(root)

        issues = report["current_integrity"]["document_issues"]
        self.assertIn(
            "logic_readme:governance-evidence-needs-typed-reference",
            issues,
        )
        self.assertIn(
            "logic_change:governance-evidence-needs-typed-reference",
            issues,
        )
        self.assertTrue(self.fails(report))

    def test_stale_policy_review_interval_fails_current_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            readme = (root / "logic_readme.md").read_text(encoding="utf-8")
            readme = readme.replace(
                "- last_verified: 2026-07-22",
                "- last_verified: 2025-01-01",
            ).replace(
                "| valid | 2026-07-22 | self |",
                "| valid | 2025-01-01 | self |",
            )
            (root / "logic_readme.md").write_text(readme, encoding="utf-8")
            report = self.collect(root)

        issues = report["current_integrity"]["document_issues"]
        self.assertTrue(
            any(issue.startswith("logic_readme:review-interval-expired:") for issue in issues)
        )
        self.assertTrue(
            any(
                issue.startswith(
                    "logic_readme:current-policy-row-1:review-interval-expired:"
                )
                for issue in issues
            )
        )
        self.assertTrue(self.fails(report))

    def test_current_state_cli_returns_success_for_valid_map(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    str(root),
                    "--current-state",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)

    def test_current_state_requires_at_least_one_agent_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, write_agent=False)
            report = self.collect(root)

        self.assertTrue(report["missing_default_agent_entry"])
        self.assertTrue(self.fails(report))

    def test_codex_entry_requires_agents_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / ".agents").rmdir()
            report = self.collect(root)

        entry = next(
            item for item in report["agent_entrypoints"] if item["path"] == "AGENTS.md"
        )
        self.assertIn("missing-agent-config-directory:.agents", entry["issues"])
        self.assertTrue(self.fails(report))

    def test_claude_entry_requires_claude_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / "CLAUDE.md").write_text(
                agent_entry(tool="claude"), encoding="utf-8"
            )
            report = self.collect(root)

        entry = next(
            item for item in report["agent_entrypoints"] if item["path"] == "CLAUDE.md"
        )
        self.assertIn("missing-agent-config-directory:.claude", entry["issues"])
        self.assertTrue(self.fails(report))

    def test_legacy_agent_marker_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / "AGENTS.md").write_text(
                agent_entry(legacy_marker=True), encoding="utf-8"
            )
            report = self.collect(root)

        self.assertTrue(self.fails(report))
        self.assertIn(
            "missing-marker:recall_business_truth: project-root-current-logic-docs",
            report["agent_entrypoints"][0]["issues"],
        )

    def test_nonroot_current_document_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / "src" / "logic_readme.md").write_text(
                "# duplicate\n", encoding="utf-8"
            )
            report = self.collect(root)

        self.assertTrue(self.fails(report))

    def test_registered_readme_only_child_document_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            readme_path = root / "logic_readme.md"
            text = readme_path.read_text(encoding="utf-8")
            self.assertIn(INHERITED_APP_ROW, text)
            readme_path.write_text(
                text.replace(INHERITED_APP_ROW, README_ONLY_APP_ROW),
                encoding="utf-8",
            )
            (root / "src" / "logic_readme.md").write_text(
                child_readme(), encoding="utf-8"
            )
            change_path = root / "logic_change.md"
            proposal = change_path.read_text(encoding="utf-8")
            change_path.write_text(
                proposal.replace(
                    "- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)",
                    "- related_modules: MOD-APP",
                ),
                encoding="utf-8",
            )
            report = self.collect(root)

        self.assertNotIn(
            "src/logic_readme.md", report["current_state_nonroot_documents"]
        )
        self.assertFalse(
            [
                issue
                for issue in report["module_routes"]["route_issues"]
                if issue.startswith("mod-app:")
            ]
        )
        self.assertFalse(self.fails(report))

    def test_nonroot_paired_registration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            readme_path = root / "logic_readme.md"
            text = readme_path.read_text(encoding="utf-8")
            readme_path.write_text(
                text.replace(INHERITED_APP_ROW, PAIRED_APP_ROW),
                encoding="utf-8",
            )
            (root / "src" / "logic_readme.md").write_text(
                child_readme(policy="paired"), encoding="utf-8"
            )
            (root / "src" / "logic_change.md").write_text(
                "# module changes\n", encoding="utf-8"
            )
            report = self.collect(root)

        self.assertIn(
            "mod-app:paired-policy-root-only",
            report["module_routes"]["route_issues"],
        )
        self.assertIn(
            "src/logic_change.md", report["current_state_nonroot_documents"]
        )
        self.assertTrue(self.fails(report))

    def test_agent_private_current_document_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            private_root = root / ".agents" / "memory"
            private_root.mkdir(parents=True)
            (private_root / "logic_readme.md").write_text(
                "# stale private truth\n", encoding="utf-8"
            )
            report = self.collect(root)

        self.assertIn(
            ".agents/memory/logic_readme.md",
            report["private_agent_knowledge_files"],
        )
        self.assertFalse(report["static_gate"]["passed"])
        self.assertTrue(self.fails(report))

    def test_other_tool_and_backup_current_documents_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / ".cursor").mkdir()
            (root / ".cursor" / "logic_readme.md").write_text(
                "# stale tool truth\n", encoding="utf-8"
            )
            (root / ".github").mkdir()
            (root / ".github" / "logic_change.md").write_text(
                "# stale hidden truth\n", encoding="utf-8"
            )
            (root / "backup").mkdir()
            (root / "backup" / "logic_change.md").write_text(
                "# stale backup proposal\n", encoding="utf-8"
            )
            report = self.collect(root)

        self.assertIn(
            ".cursor/logic_readme.md",
            report["current_state_nonroot_documents"],
        )
        self.assertIn(
            ".github/logic_change.md",
            report["current_state_nonroot_documents"],
        )
        self.assertIn("backup/logic_change.md", report["current_state_nonroot_documents"])
        self.assertTrue(self.fails(report))

    def test_wrong_root_scope_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / "logic_readme.md").write_text(
                root_readme(full=False, scope_path="src"), encoding="utf-8"
            )
            report = self.collect(root)

        self.assertTrue(self.fails(report))
        self.assertTrue(report["current_integrity"]["document_issues"])

    def test_current_policy_requires_both_rule_and_why(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy = policy.replace(
                "Keep callers stable while implementation changes.",
                "none",
            )
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "logic_readme:current-policy-row-1-needs-rule-and-why",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_key_current_policy_requires_immutable_decision_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy = policy.replace(
                "[VER-20260722-001](logic_version/records/"
                "logic_version-20260722-001-output-contract.md)",
                "[active CHG](logic_change.md#chg-20260722-001)",
            )
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "logic_readme:current-policy-row-1-key-needs-immutable-decision-link",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_active_change_count_and_unique_body_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace("- active_changes: 1", "- active_changes: none")
            proposal += "\n## CHG-20260722-001: Duplicate body\n"
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertIn("duplicate-change-body:CHG-20260722-001", issues)
        self.assertIn("active_changes-count-mismatch:none!=2", issues)
        self.assertTrue(self.fails(report))

    def test_every_change_requires_registered_affected_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, affected_scopes=None)
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:missing-affected-scopes",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_unknown_affected_scope_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, affected_scopes="missing/module")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:affected-scope-not-registered:missing/module",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_primary_and_related_scope_must_be_affected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, affected_scopes=".")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:primary-scope-missing-from-affected-scopes:src",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertIn(
            "CHG-20260722-001:related-module-scope-missing-from-affected-scopes:"
            "mod-app:src",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_related_module_anchor_must_be_in_affected_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            (root / "api").mkdir()
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy = policy.replace(
                "| MOD-APP | src | in-system | module/runtime-code | inherited | "
                "[app policy](logic_readme.md#scope-mod-app) | "
                "[changes](logic_change.md) | self | active |",
                "| MOD-APP | src | in-system | module/runtime-code | inherited | "
                "[app policy](logic_readme.md#scope-mod-app) | "
                "[changes](logic_change.md) | self | active |\n"
                "| MOD-API | api | in-system | module/runtime-code | inherited | "
                "[API](logic_readme.md#scope-api) | "
                "[changes](logic_change.md) | self | active |",
            ).replace(
                "- scope_path: src\n",
                "- scope_path: src\n\n<a id=\"scope-api\"></a>\n"
                "### MOD-API: API\n\n- scope_path: api\n",
            )
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)",
                "- related_modules: [API](logic_readme.md#scope-api)",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:related-module-anchor-scope-missing-from-"
            "affected-scopes:scope-api:api",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_scope_registry_rejects_missing_membership_and_placeholder_owner(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy = policy.replace(
                "| MOD-APP | src | in-system | module/runtime-code | inherited |",
                "| MOD-APP | src |  | module/runtime-code | inherited |",
            ).replace("| self | active |", "| <TEAM> | active |", 1)
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            report = self.collect(root)

        route_issues = report["current_integrity"]["scope_registry_issues"]
        self.assertTrue(
            any("route-row-missing-membership" in issue for issue in route_issues)
        )
        self.assertTrue(any("route-row-missing-owner" in issue for issue in route_issues))
        self.assertTrue(self.fails(report))

    def test_legacy_authority_model_requires_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy += "\n## 决策权限登记\n\n| authority_id | scope_path |\n"
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            change = (root / "logic_change.md").read_text(encoding="utf-8")
            change = change.replace(
                "- semantic_reviewed_at: none",
                "- decision_authority: AUTH-SELF\n"
                "- authority_evidence: self-declared\n"
                "- approved_by: AUTH-SELF\n"
                "- semantic_reviewed_at: none",
            )
            (root / "logic_change.md").write_text(change, encoding="utf-8")
            report = self.collect(root)

        issues = report["current_integrity"]["responsibility_issues"]
        self.assertIn(
            "logic_readme:legacy-decision-authority-registry-must-be-migrated",
            issues,
        )
        self.assertTrue(
            any("legacy-authority-fields-must-be-migrated" in issue for issue in issues)
        )
        self.assertTrue(self.fails(report))

    def test_proposal_path_requires_exact_chg_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, proposal_path="logic_change.md")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:proposal-path-must-target-logic_change-anchor",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_change_records_actual_modifier_without_auth_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, changed_by=None)
            report = self.collect(root)

        self.assertTrue(report["current_integrity"]["responsibility_issues"])
        self.assertTrue(self.fails(report))

    def test_legacy_approved_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, status="approved")
            report = self.collect(root)

        self.assertTrue(
            any(
                "invalid-change-status:approved" in issue
                for issue in report["current_integrity"]["document_issues"]
            )
        )
        self.assertTrue(self.fails(report))

    def test_required_decision_confirmation_must_match_current_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, decision_gate="required")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            (root / "logic_change.md").write_text(
                proposal.replace(
                    "- confirmed_proposal_revision: 1",
                    "- confirmed_proposal_revision: 2",
                ),
                encoding="utf-8",
            )
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:confirmed-proposal-revision-mismatch:2!=1",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_high_route_and_decision_gate_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, recall_route="high")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:high-route-needs-required-decision",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_required_decision_cannot_skip_confirmation_before_implementation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                decision_gate="required",
                decision_state="pending",
            )
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:implementing-needs-confirmed-current-decision",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_semantic_review_result_requires_independent_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            (root / "logic_change.md").write_text(
                proposal.replace(
                    "- semantic_review_state: pending",
                    "- semantic_review_state: passed",
                ),
                encoding="utf-8",
            )
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertIn(
            "CHG-20260722-001:semantic_reviewed_by-required-for-semantic-review",
            issues,
        )
        self.assertIn(
            "CHG-20260722-001:semantic_review_ref-required-for-semantic-review",
            issues,
        )
        self.assertTrue(self.fails(report))

    def test_change_requires_precise_authority_surface_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "- authority_surfaces: RULE-OUTPUT",
                "- authority_surfaces: .",
            ).replace(
                "- based_on: policy: logic_readme.md#rule-output; "
                "code: snapshot:before-change; surfaces: RULE-OUTPUT",
                "- based_on: none",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertIn(
            "CHG-20260722-001:authority-surface-too-broad:.",
            issues,
        )
        self.assertIn("CHG-20260722-001:missing-based-on", issues)
        self.assertTrue(self.fails(report))

    def test_unknown_version_pinned_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                depends_on="CHG-20260722-404@revision-1",
            )
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:dependency-target-not-active:CHG-20260722-404",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_dependency_revision_drift_blocks_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, status="draft", proposal_revision="2")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = append_active_change(
                proposal,
                change_id="CHG-20260722-002",
                status="implementing",
                depends_on="CHG-20260722-001@revision-1",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-002:dependency-revision-drift-needs-block-or-"
            "redecision:CHG-20260722-001@revision-1!=2",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertIn(
            "CHG-20260722-002:active-dependency-needs-block-or-redecision:"
            "CHG-20260722-001",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_dependency_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                status="draft",
                depends_on="CHG-20260722-002@revision-1",
            )
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = append_active_change(
                proposal,
                change_id="CHG-20260722-002",
                depends_on="CHG-20260722-001@revision-1",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "dependency-cycle:CHG-20260722-001,CHG-20260722-002",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_shared_authority_surface_requires_explicit_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, status="draft")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = append_active_change(
                proposal,
                change_id="CHG-20260722-002",
                authority_surfaces="RULE-OUTPUT",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:unmarked-authority-surface-overlap:"
            "CHG-20260722-002:rule-output",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_unresolved_conflict_requires_waiting_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                status="draft",
                conflicts_with="CHG-20260722-002",
                conflict_resolution="unresolved",
            )
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = append_active_change(
                proposal,
                change_id="CHG-20260722-002",
                conflicts_with="CHG-20260722-001",
                conflict_resolution="unresolved",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "CHG-20260722-001:unresolved-conflict-needs-block-or-redecision",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertIn(
            "active-conflict-needs-block-or-redecision:CHG-20260722-001:"
            "CHG-20260722-002",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_sequence_conflict_allows_only_waiting_downstream_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                authority_surfaces="RULE-SHARED",
                conflicts_with="CHG-20260722-002",
                conflict_resolution="sequence-and-revalidate",
            )
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = append_active_change(
                proposal,
                change_id="CHG-20260722-002",
                authority_surfaces="RULE-SHARED",
                depends_on="CHG-20260722-001@revision-1",
                conflicts_with="CHG-20260722-001",
                conflict_resolution="sequence-and-revalidate",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root)

        self.assertFalse(report["current_integrity"]["proposal_issues"])
        self.assertFalse(self.fails(report))

    def test_compact_history_and_guarded_rollout_require_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(
                root,
                history_retention="compact",
                runtime_state="deployed-guarded",
                runtime_environments="production",
            )
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertIn(
            "CHG-20260722-001:retained-history-needs-reserved-version-record",
            issues,
        )
        self.assertIn(
            "CHG-20260722-001:deployed-guarded-needs-feature-flag",
            issues,
        )
        self.assertTrue(self.fails(report))

    def test_effective_immutable_record_requires_confirmed_decision_and_review(
        self,
    ) -> None:
        record = """# VER-20260722-001: Test

- version_id: VER-20260722-001
- version_slug: logic_version-20260722-001-src
- status: effective
- immutable: true
- change_id: CHG-20260722-001
- proposal_commit_or_blob: commit:abc123
- proposal_revision: 1
- decision_record: required
- decision_state: confirmed
- confirmed_proposal_revision: 1
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-07-22
- decision_confirmed_at: 2026-07-22
- semantic_review_state: not-applicable
- semantic_reviewed_by: none
- semantic_review_ref: none
- semantic_reviewed_at: none
- final_proposal_snapshot: embedded
- after_commit: commit:def456
- rollback_or_restore_verified: not-applicable
- temporary_structure_removed: not-applicable
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "logic_version-20260722-001-src.md"
            path.write_text(record, encoding="utf-8")
            issues = AUDIT.semantic_issues(path, "version")

        self.assertIn(
            "effective-decision-record-needs-passed-semantic-review",
            issues,
        )
        self.assertIn("required-decision-record-needs-snapshot_source", issues)
        self.assertIn(
            "required-decision-record-needs-intent_source_refs", issues
        )

    def test_topic_version_requires_shared_context_snapshot(self) -> None:
        record = """# VER-20260722-001: Topic close

- version_id: VER-20260722-001
- version_slug: logic_version-20260722-001-topic-close
- status: cancelled
- immutable: true
- governance_mode: personal
- governance_ref: git:demo
- governance_evidence: git:demo
- governance_verification: recorded
- governance_verified_at: 2026-07-22
- change_id: none
- topic_id: TOPIC-20260722-001
- topic_shared_context: none
- topic_shared_constraints: none
- topic_discussion_refs: none
- topic_final_conclusion: none
- changed_by: none
- proposal_revision: none
- decision_record: not-required
- decision_state: not-required
- confirmed_proposal_revision: none
- decision_confirmed_by: none
- decision_ref: none
- decision_confirmed_at: none
- semantic_review_state: not-applicable
- semantic_reviewed_by: none
- semantic_review_ref: none
- semantic_reviewed_at: none
- final_proposal_snapshot: embedded
- rollback_or_restore_verified: not-applicable
- temporary_structure_removed: not-applicable
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "logic_version-20260722-001-topic-close.md"
            path.write_text(record, encoding="utf-8")
            issues = AUDIT.semantic_issues(path, "version")

        for field in (
            "topic_shared_context",
            "topic_shared_constraints",
            "topic_discussion_refs",
            "topic_final_conclusion",
        ):
            self.assertIn(f"topic-version-needs-{field}", issues)

    def test_retained_change_rejects_malformed_intent_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, decision_gate="required")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "test:tests/test_app.py#output-contract",
                "tests/test_app.py",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        self.assertIn(
            "CHG-20260722-001:invalid-trace-test-ref:tests/test_app.py",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report, formal=True))

    def test_review_freshness_accepts_current_interval_and_rejects_expiry(self) -> None:
        today = AUDIT.date(2026, 7, 24)
        self.assertFalse(
            AUDIT.review_freshness_issues(
                "2026-07-22", "interval:90d; event:release", label="rule", today=today
            )
        )
        self.assertIn(
            "rule:review-interval-expired:2026-04-01",
            AUDIT.review_freshness_issues(
                "2026-01-01", "interval:90d; event:release", label="rule", today=today
            ),
        )
        self.assertIn(
            "rule:review-due-expired:2026-07-01",
            AUDIT.review_freshness_issues(
                "2026-07-22", "due:2026-07-01", label="rule", today=today
            ),
        )

    def test_formal_review_checks_current_evidence_not_history_format(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            records = root / "logic_version" / "records"
            records.mkdir(parents=True, exist_ok=True)
            (records / "logic_version-20260722-001-bad.md").write_text(
                "malformed history\n", encoding="utf-8"
            )
            report = self.collect(root, formal=True)

        self.assertFalse(report["archive"]["scanned"])
        self.assertFalse(report["archive"]["malformed_versions"])
        self.assertFalse(self.fails(report, formal=True))

    def test_formal_review_does_not_inherit_old_v2_readme_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            policy = (root / "logic_readme.md").read_text(encoding="utf-8")
            policy = policy.replace("## 目标与边界\n\nDemo boundary.\n\n", "")
            (root / "logic_readme.md").write_text(policy, encoding="utf-8")
            report = self.collect(root, formal=True)

        root_module = next(
            module for module in report["modules"] if module["path"] == "."
        )
        self.assertFalse(root_module["v2_issues"])
        self.assertFalse(root_module["missing_readme_sections"])
        self.assertTrue(report["static_gate"]["passed"])
        self.assertFalse(self.fails(report, formal=True))

    def test_formal_required_decision_needs_checkpoint_and_three_options(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, decision_gate="required")
            report = self.collect(root, formal=True)

        issues = report["formal_review"]["proposal_issues"]
        self.assertIn(
            "CHG-20260722-001:required-decision-needs-formal-decision_needed_because",
            issues,
        )
        self.assertIn(
            "CHG-20260722-001:required-decision-needs-three-options",
            issues,
        )
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_rejects_invalid_dates_and_version_identity(self) -> None:
        mutations = (
            (
                "- created: 2026-07-22",
                "- created: 2026-99-99",
                "formal-field-must-be-date:created",
            ),
            (
                "- reserved_version_id: none\n- version_slug: none",
                "- reserved_version_id: BANANA\n- version_slug: BANANA",
                "invalid-reserved-version-id:BANANA",
            ),
        )
        for old, new, expected in mutations:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.write_project(root, full=True)
                proposal = (root / "logic_change.md").read_text(encoding="utf-8")
                (root / "logic_change.md").write_text(
                    proposal.replace(old, new), encoding="utf-8"
                )
                report = self.collect(root, formal=True)

            self.assertTrue(
                any(
                    expected in issue
                    for issue in report["formal_review"]["proposal_issues"]
                )
            )
            self.assertFalse(report["static_gate"]["passed"])
            self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_rejects_malformed_decision_and_impact_tables(self) -> None:
        replacements = (
            (
                "| 方案 | 收益 | 风险/坏处 | 复杂度增量 | 状态 |\n"
                "|---|---|---|---|---|\n"
                "| A | minimal change | low | low | selected |",
                "| garbage |\n|---|\n| value |",
                "invalid-formal-table-columns:方案与决策",
            ),
            (
                "| 行为/契约 | artifact_layer | producer | consumer | environment | 影响 | 证据 |\n"
                "|---|---|---|---|---|---|---|\n"
                "| output | runtime-code | app | test | local | preserved | tests/test_app.py |",
                "| garbage |\n|---|\n| value |",
                "invalid-formal-table-columns:消费者与影响",
            ),
        )
        for old, new, expected in replacements:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.write_project(root, full=True)
                proposal = (root / "logic_change.md").read_text(encoding="utf-8")
                (root / "logic_change.md").write_text(
                    proposal.replace(old, new), encoding="utf-8"
                )
                report = self.collect(root, formal=True)

            self.assertTrue(
                any(
                    expected in issue
                    for issue in report["formal_review"]["proposal_issues"]
                )
            )
            self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_rejects_none_only_formal_table_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "| A | minimal change | low | low | selected |",
                "| none | none | none | none | selected |",
            ).replace(
                "| output | runtime-code | app | test | local | preserved | "
                "tests/test_app.py |",
                "| none | runtime-code | none | none | local | none | none |",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        issues = report["formal_review"]["proposal_issues"]
        self.assertTrue(any("formal-table-方案与决策" in issue for issue in issues))
        self.assertTrue(any("formal-table-消费者与影响" in issue for issue in issues))
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_cli_json_fails_invalid_static_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            (root / "logic_change.md").write_text(
                proposal.replace(
                    "- reserved_version_id: none",
                    "- reserved_version_id: BANANA",
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    str(root),
                    "--formal-review",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1, completed.stderr + completed.stdout)
        self.assertFalse(payload["static_gate"]["passed"])
        self.assertFalse(payload["semantic_review"]["performed"])

    def test_formal_review_requires_current_test_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, include_matrix=False)
            report = self.collect(root, formal=True)

        self.assertTrue(report["formal_review"]["test_matrix_issues"])
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_rejects_failed_post_change_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, status="verifying")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "| unit | output contract | python -m unittest | pass | pass | pass |",
                "| unit | output contract | python -m unittest | pass | pass | fail |",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        self.assertTrue(
            any(
                "post-change-failed" in issue
                for issue in report["formal_review"]["test_matrix_issues"]
            )
        )
        self.assertFalse(report["static_gate"]["passed"])
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_rejects_empty_required_evidence_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "- proposer: user",
                "- proposer: none",
            ).replace(
                "- current_behavior: current code behavior verified by tests",
                "- current_behavior: none",
            ).replace(
                "- intent_digest: Preserve the requested output behavior while changing implementation.",
                "- intent_digest: none",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        issues = report["formal_review"]["proposal_issues"]
        self.assertTrue(
            any("formal-field-needs-meaningful-evidence:proposer" in issue for issue in issues)
        )
        self.assertTrue(
            any(
                "formal-field-needs-meaningful-evidence:current_behavior" in issue
                for issue in issues
            )
        )
        self.assertTrue(
            any(
                "formal-field-needs-meaningful-evidence:intent_digest" in issue
                for issue in issues
            )
        )
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_does_not_accept_legacy_authority_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, status="verifying")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "| unit | output contract | python -m unittest | pass | pass | pass | "
                "command: python -m unittest | self + 2026-07-22 |",
                "| unit | output contract | python -m unittest | pass | "
                "pass | not-run: unavailable | risk-accepted: deferred; "
                "authority:self; compensation-owner:self; due:2099-01-01 | "
                "self + 2026-07-22 |",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        self.assertTrue(
            any(
                "post-change-required-for-verifying" in issue
                for issue in report["formal_review"]["test_matrix_issues"]
            )
        )
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_accepts_complete_decision_ref_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True, status="verifying")
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "| unit | output contract | python -m unittest | pass | pass | pass | "
                "command: python -m unittest | self + 2026-07-22 |",
                "| unit | output contract | python -m unittest | pass | "
                "pass | not-run: unavailable | risk-accepted: deferred; "
                "decision-ref:user-confirmed:2026-07-22; compensation-owner:self; "
                "due:2099-01-01 | self + 2026-07-22 |",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        self.assertFalse(report["formal_review"]["test_matrix_issues"])
        self.assertTrue(report["static_gate"]["passed"])
        self.assertFalse(self.fails(report, formal=True))

    def test_formal_review_validates_reviewer_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "self + 2026-07-22",
                "self + 2026-99-99",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        self.assertTrue(
            any(
                "reviewer-needs-date" in issue
                for issue in report["formal_review"]["test_matrix_issues"]
            )
        )
        self.assertTrue(self.fails(report, formal=True))

    def test_formal_review_requires_nonempty_locator_and_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, full=True)
            proposal = (root / "logic_change.md").read_text(encoding="utf-8")
            proposal = proposal.replace(
                "command: python -m unittest",
                "command:",
            ).replace(
                "self + 2026-07-22",
                "2026-07-22",
            )
            (root / "logic_change.md").write_text(proposal, encoding="utf-8")
            report = self.collect(root, formal=True)

        issues = report["formal_review"]["test_matrix_issues"]
        self.assertTrue(any("evidence-needs-locator" in issue for issue in issues))
        self.assertTrue(any("reviewer-needs-date" in issue for issue in issues))
        self.assertTrue(self.fails(report, formal=True))


if __name__ == "__main__":
    unittest.main()
