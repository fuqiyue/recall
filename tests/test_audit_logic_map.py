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

# 默认夹具自带的领域行：RULE-018 ④ 要求至少一个领域，否则 current-state 门失败（VER-20260904-005）
CORE_DOMAIN_ROW = "| MOD-CORE | logic_domains/core | in-system | domain/runtime-code | paired | [core](logic_domains/core/logic_readme.md) | [changes](logic_domains/core/logic_change.md) | self | active |"

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
    with_domain: bool = True,
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
{core_row}

<a id="scope-mod-app"></a>
### MOD-APP: Application

- scope_path: src
""".replace("{core_row}", CORE_DOMAIN_ROW if with_domain else "")
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


# RULE-018 一二级拆分法（VER-20260903-004）：非根 paired 行是部门法——
# readme + change 成对；根 logic_change.md 的活跃议案索引是全项目公报，
# 每条领域 CHG 在其中占一行并链接到领域账本的锚点。
DOMAIN_CHANGE_ID = "CHG-20260722-002"

DOMAIN_GAZETTE_ROW = (
    f"| {DOMAIN_CHANGE_ID} | implementing | src | self | domain test | none | "
    f"[{DOMAIN_CHANGE_ID}](src/logic_change.md#{DOMAIN_CHANGE_ID.casefold()}) | 2026-07-22 |"
)


def core_domain_readme() -> str:
    """默认夹具的 core 领域 readme（最小部门法）。"""
    return """# Core Domain Logic

## 文档控制

- module_id: MOD-CORE
- scope: logic_domains/core
- scope_path: logic_domains/core
- parent: ../../logic_readme.md
- parent_module_id: MOD-ROOT
- membership: in-system
- scope_type: domain
- layer: runtime-code
- module_doc_policy: paired
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
- source_of_truth: src/core
- source_decisions: none
- intent_summary: keep the core module logic discoverable
- intent_sources: user-confirmed:2026-07-22
- decision_validity: valid
- validity_evidence: user-confirmed:2026-07-22
- canonical_readme: logic_domains/core/logic_readme.md
- canonical_change: logic_domains/core/logic_change.md
- owned_paths: src/core
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-CORE-STABLE | ordinary | Keep the core entry point stable. | Callers import it directly. | none | user-confirmed:2026-07-22 | src/core | valid | 2026-07-22 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| src/core | source/runtime-code | core | input | output | code | yes | none |

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none
"""


def core_domain_change() -> str:
    """默认夹具的 core 领域空账本。"""
    return """# Core Domain Active Changes

## 文档控制

- scope: logic_domains/core
- scope_path: logic_domains/core
- module_id: MOD-CORE
- current_policy: logic_readme.md
- owner: self
- governance_mode: personal
- governance_ref: git:demo-repository
- governance_evidence: git:demo-repository
- governance_verification: recorded
- governance_verified_at: 2026-07-22
- last_updated: 2026-07-22
- active_changes: none

## 议案规则

- All entries are non-effective until promoted.

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
"""


def domain_readme() -> str:
    """部门法 readme：paired 策略、canonical_* 位于文档控制、scope_type: domain。"""
    text = child_readme(policy="paired")
    text = text.replace("- scope_type: module", "- scope_type: domain")
    text = text.replace(
        "- validity_evidence: user-confirmed:2026-07-22\n",
        "- validity_evidence: user-confirmed:2026-07-22\n"
        "- canonical_readme: src/logic_readme.md\n"
        "- canonical_change: src/logic_change.md\n",
    )
    text = text.replace(
        "- canonical_readme: src/logic_readme.md\n- canonical_change: none\n", ""
    )
    text = text.replace(
        "- 唯一入口：[logic_change.md](../logic_change.md)",
        "- 唯一入口：[logic_change.md](logic_change.md)",
    )
    return text.replace("- 相关 CHG-ID：none", f"- 相关 CHG-ID：{DOMAIN_CHANGE_ID}")


def domain_change(*, affected_scopes: str = "src") -> str:
    """领域账本：镜像根账本结构，scope 绑定到 src，一条一事一议的 CHG。"""
    document = change_document(
        full=False,
        affected_scopes=affected_scopes,
        authority_surfaces="RULE-APP-OUTPUT",
    )
    document = document.replace(
        "- scope: .\n- scope_path: .\n- module_id: MOD-ROOT",
        "- scope: src\n- scope_path: src\n- module_id: MOD-APP",
    )
    document = document.replace("CHG-20260722-001", DOMAIN_CHANGE_ID).replace(
        "chg-20260722-001", DOMAIN_CHANGE_ID.casefold()
    )
    document = document.replace(
        "- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)",
        "- related_modules: MOD-APP",
    )
    return document.replace(
        "policy: logic_readme.md#rule-output",
        "policy: src/logic_readme.md#rule-app-output",
    )



def domain_gazette_row(change_id: str, *, status: str = "draft") -> str:
    """根公报中指向 src 领域账本另一条 CHG 的行。"""
    return (
        f"| {change_id} | {status} | src | self | domain test | none | "
        f"[{change_id}](src/logic_change.md#{change_id.casefold()}) | 2026-07-22 |"
    )


def append_domain_change(
    document: str,
    *,
    change_id: str,
    status: str = "draft",
    authority_surfaces: str = "RULE-APP-OUTPUT",
    conflicts_with: str = "none",
    conflict_resolution: str = "none",
) -> str:
    """向 src 领域账本追加第二条合法 CHG 正文（含本地索引行与 active_changes 计数）。"""
    source = change_document(
        full=False,
        status=status,
        authority_surfaces=authority_surfaces,
        conflicts_with=conflicts_with,
        conflict_resolution=conflict_resolution,
    )
    source_anchor = '<a id="chg-20260722-001"></a>'
    block = source[source.index(source_anchor) :]
    block = block.replace("CHG-20260722-001", change_id).replace(
        "chg-20260722-001", change_id.casefold()
    )
    block = block.replace(
        "- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)",
        "- related_modules: MOD-APP",
    ).replace(
        "policy: logic_readme.md#rule-output",
        "policy: src/logic_readme.md#rule-app-output",
    )
    active_count = len(AUDIT.change_blocks(document))
    document = document.replace(
        f"- active_changes: {active_count}",
        f"- active_changes: {active_count + 1}",
        1,
    )
    index_row = (
        f"| {change_id} | {status} | src | self | domain test | none | "
        f"[{change_id}](logic_change.md#{change_id.casefold()}) | 2026-07-22 |"
    )
    domain_anchor = f'<a id="{DOMAIN_CHANGE_ID.casefold()}"></a>'
    assert document.count("\n\n" + domain_anchor) == 1
    document = document.replace(
        "\n\n" + domain_anchor,
        "\n" + index_row + "\n\n" + domain_anchor,
        1,
    )
    return document + "\n" + block


def rule_change_block(
    change_id: str,
    *,
    authority_surfaces: str | None = "RULE-OUTPUT",
    conflicts_with: str = "none",
    created: str = "2026-07-22",
    last_status_change: str = "2026-07-22",
    proposed_policy: str = "Keep the output contract.",
) -> str:
    """手写的最小 CHG 块：供 cross_ledger_rule_conflicts 直接单测。"""
    authority_line = (
        f"- authority_surfaces: {authority_surfaces}\n"
        if authority_surfaces is not None
        else ""
    )
    return f"""## {change_id}: Test proposal

### 元数据

- status: draft
- effective: false
- created: {created}
- last_status_change: {last_status_change}
{authority_line}- conflicts_with: {conflicts_with}
- conflict_resolution: none

### 拟议制度

{proposed_policy}

### 兼容、迁移与回滚

Rollback the code change.
"""


class ProjectFixtureMixin:
    """根宪法 / 领域夹具与审计调用助手；子类只带自己的用例，避免重复跑整套 RootOnlyAuditTests。"""

    def write_project(
        self,
        root: Path,
        *,
        full: bool = False,
        write_agent: bool = True,
        governance_mode: str = "personal",
        governance_ref: str = "git:demo-repository",
        with_domain: bool = True,
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
                with_domain=with_domain,
            ),
            encoding="utf-8",
        )
        if with_domain:
            core = root / "logic_domains" / "core"
            core.mkdir(parents=True)
            (core / "logic_readme.md").write_text(core_domain_readme(), encoding="utf-8")
            (core / "logic_change.md").write_text(core_domain_change(), encoding="utf-8")
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

    def write_domain_project(
        self,
        root: Path,
        *,
        registry_row: str = PAIRED_APP_ROW,
        affected_scopes: str = "src",
        gazette_row: str | None = DOMAIN_GAZETTE_ROW,
    ) -> None:
        """根宪法 + src 部门法（readme/change 成对）+ 根公报行。"""
        self.write_project(root)
        readme_path = root / "logic_readme.md"
        text = readme_path.read_text(encoding="utf-8")
        self.assertIn(INHERITED_APP_ROW, text)
        readme_path.write_text(
            text.replace(INHERITED_APP_ROW, registry_row), encoding="utf-8"
        )
        (root / "src" / "logic_readme.md").write_text(
            domain_readme(), encoding="utf-8"
        )
        (root / "src" / "logic_change.md").write_text(
            domain_change(affected_scopes=affected_scopes), encoding="utf-8"
        )
        change_path = root / "logic_change.md"
        proposal = change_path.read_text(encoding="utf-8").replace(
            "- related_modules: [MOD-APP](logic_readme.md#scope-mod-app)",
            "- related_modules: MOD-APP",
        )
        if gazette_row is not None:
            proposal = proposal.replace(
                '\n\n<a id="chg-20260722-001"></a>',
                "\n" + gazette_row + '\n\n<a id="chg-20260722-001"></a>',
                1,
            )
        change_path.write_text(proposal, encoding="utf-8")


class RootOnlyAuditTests(ProjectFixtureMixin, unittest.TestCase):
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

    def test_registered_paired_domain_passes(self) -> None:
        """RULE-018：已登记的部门法（readme + change）与根公报行一起通过现状门。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            report = self.collect(root)

        self.assertNotIn(
            "src/logic_readme.md", report["current_state_nonroot_documents"]
        )
        self.assertNotIn(
            "src/logic_change.md", report["current_state_nonroot_documents"]
        )
        self.assertFalse(
            [
                issue
                for issue in report["module_routes"]["route_issues"]
                if issue.startswith("mod-app:")
            ],
            report["module_routes"]["route_issues"],
        )
        self.assertNotIn(
            "mod-app:paired-policy-root-only",
            report["module_routes"]["route_issues"],
        )
        integrity = report["current_integrity"]
        self.assertFalse(integrity["proposal_issues"], integrity["proposal_issues"])
        self.assertFalse(integrity["document_issues"], integrity["document_issues"])
        self.assertFalse(self.fails(report))

    def test_unregistered_domain_directory_is_rejected(self) -> None:
        """未登记的 logic_domains/<x>/ readme + change 仍是平行真源。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            rogue = root / "logic_domains" / "billing"
            rogue.mkdir(parents=True)
            (rogue / "logic_readme.md").write_text("# rogue\n", encoding="utf-8")
            (rogue / "logic_change.md").write_text("# rogue\n", encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "logic_domains/billing/logic_readme.md",
            report["current_state_nonroot_documents"],
        )
        self.assertIn(
            "logic_domains/billing/logic_change.md",
            report["current_state_nonroot_documents"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_change_touching_root_scope_is_constitution_amendment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root, affected_scopes=".")
            report = self.collect(root)

        self.assertIn(
            f"{DOMAIN_CHANGE_ID}:constitution-amendment-must-live-in-root-change",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_change_must_include_own_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root, affected_scopes=".")
            report = self.collect(root)

        self.assertIn(
            f"{DOMAIN_CHANGE_ID}:domain-proposal-must-include-own-scope:src",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_change_missing_from_root_gazette_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root, gazette_row=None)
            report = self.collect(root)

        self.assertIn(
            f"{DOMAIN_CHANGE_ID}:domain-change-missing-from-root-index:src",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_root_gazette_row_must_link_domain_change_anchor(self) -> None:
        wrong_anchor = DOMAIN_GAZETTE_ROW.replace(
            f"#{DOMAIN_CHANGE_ID.casefold()})", "#chg-20260722-999)"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root, gazette_row=wrong_anchor)
            report = self.collect(root)

        self.assertIn(
            f"{DOMAIN_CHANGE_ID}:root-index-must-link-domain-change:src/logic_change.md",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_root_gazette_rows_are_not_counted_as_root_bodies(self) -> None:
        """公报行指向领域账本，不参与根正文<->索引比对，也不能指向不存在的正文。"""
        orphan = DOMAIN_GAZETTE_ROW.replace(
            DOMAIN_CHANGE_ID, "CHG-20260722-003"
        ).replace(DOMAIN_CHANGE_ID.casefold(), "chg-20260722-003")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(
                root, gazette_row=DOMAIN_GAZETTE_ROW + "\n" + orphan
            )
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertFalse(
            [issue for issue in issues if issue.startswith("index-ids-without-body")],
            issues,
        )
        self.assertIn(
            "CHG-20260722-003:root-index-target-body-not-found:src/logic_change.md",
            issues,
        )
        self.assertTrue(self.fails(report))

    def test_out_of_system_paired_row_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(
                root,
                registry_row=PAIRED_APP_ROW.replace(
                    "| in-system |", "| out-of-system |"
                ),
            )
            report = self.collect(root)

        self.assertIn(
            "mod-app:paired-policy-needs-in-system",
            report["module_routes"]["route_issues"],
        )
        self.assertNotIn(
            "mod-app:paired-policy-root-only",
            report["module_routes"]["route_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_readme_tables_are_checked_like_root(self) -> None:
        """规则行搬进部门法后不能降级：列/等级/决策链接同受根表检查。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            readme_path = root / "src" / "logic_readme.md"
            text = readme_path.read_text(encoding="utf-8").replace(
                "| RULE-APP-OUTPUT | ordinary |", "| RULE-APP-OUTPUT | key |"
            )
            readme_path.write_text(text, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "src/logic_readme:current-policy-row-1-key-needs-immutable-decision-link",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_ledger_active_changes_count_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            change_path = root / "src" / "logic_change.md"
            text = change_path.read_text(encoding="utf-8").replace(
                "- active_changes: 1", "- active_changes: 2"
            )
            change_path.write_text(text, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            "src/logic_change:active_changes-count-mismatch:2!=1",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def _with_contract_class(self, readme_path: Path, value: str) -> None:
        text = readme_path.read_text(encoding="utf-8")
        header = "| 路径/稳定锚点 | artifact_class/layer | 职责 |"
        row = "| src/app.py | source/runtime-code | "
        self.assertIn(header, text)
        self.assertIn(row, text)
        text = text.replace(
            header, "| 路径/稳定锚点 | artifact_class/layer | contract_class | 职责 |"
        ).replace(
            "|---|---|---|---|---|---|---|---|\n| src/app.py",
            "|---|---|---|---|---|---|---|---|---|\n| src/app.py",
        ).replace(row, f"| src/app.py | source/runtime-code | {value} | ")
        readme_path.write_text(text, encoding="utf-8")

    def test_code_map_accepts_optional_contract_class_column(self) -> None:
        """SKILL"路由一问"的靶子列：写了就校验取值，不写不报（旧文档兼容）。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            self._with_contract_class(root / "src" / "logic_readme.md", "public")
            report = self.collect(root)
        issues = report["current_integrity"]["document_issues"]
        self.assertFalse(
            [issue for issue in issues if "code-map" in issue], issues
        )

    def test_code_map_rejects_unknown_contract_class_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            self._with_contract_class(root / "src" / "logic_readme.md", "bogus")
            report = self.collect(root)
        self.assertIn(
            "src/logic_readme:code-map-row-1-invalid-contract-class:bogus",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_constitution_without_domains_fails_gate_unless_advisory_only(self) -> None:
        """RULE-018 ④（VER-20260904-005）：宪法未登记任何领域时静态门失败；--advisory-only 只提示。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root, with_domain=False)
            plain = self.collect(root)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            layered = self.collect(root)

        self.assertTrue(
            any(
                issue.startswith("logic_readme.md:constitution-without-domains")
                for issue in plain["density"]["issues"]
            ),
            plain["density"]["issues"],
        )
        self.assertFalse(
            any("constitution-without-domains" in item for item in layered["density"]["issues"] + layered["density"]["notices"]),
            layered["density"],
        )
        self.assertTrue(self.fails(plain))
        self.assertFalse(
            AUDIT.strict_failure(plain, current_state=True, advisory_only=True)
        )
        self.assertFalse(self.fails(layered))

    def test_hard_limit_violation_fails_gate_unless_advisory_only(self) -> None:
        """RULE-022 ③（VER-20260904-005）：越过硬上限使静态门失败；越过目标值仍只是提示。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            readme_path = root / "logic_readme.md"
            base = readme_path.read_text(encoding="utf-8")
            readme_path.write_text(base + "\n" + "note\n" * 160, encoding="utf-8")
            over_target = self.collect(root)
            readme_path.write_text(base + "\n" + "note\n" * 260, encoding="utf-8")
            over_limit = self.collect(root)

        self.assertTrue(
            any(n.startswith("logic_readme.md:over-target:") for n in over_target["density"]["notices"]),
            over_target["density"],
        )
        self.assertFalse(self.fails(over_target))
        self.assertTrue(
            any(i.startswith("logic_readme.md:exceeds-hard-limit:") for i in over_limit["density"]["issues"]),
            over_limit["density"],
        )
        self.assertTrue(self.fails(over_limit))
        self.assertFalse(
            AUDIT.strict_failure(over_limit, current_state=True, advisory_only=True)
        )

    def test_domain_chg_block_density_is_measured(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            change_path = root / "src" / "logic_change.md"
            change_path.write_text(
                change_path.read_text(encoding="utf-8") + "\n" + "filler\n" * 60,
                encoding="utf-8",
            )
            report = self.collect(root)

        self.assertTrue(
            any(
                issue.startswith(f"{DOMAIN_CHANGE_ID}:exceeds-chg-limit:")
                for issue in report["density"]["notices"]
            ),
            report["density"]["notices"],
        )

    # ------------------------------------------------------------------
    # 一法多议案（VER-20260904-001）：跨账本目标规则冲突、旧议案基线失效、
    # 领域账本整本协调检查
    # ------------------------------------------------------------------

    def _retarget_root_change(self, root: Path, rule_id: str) -> None:
        """让根 CHG 的 authority_surfaces/based_on 指向指定规则。"""
        change_path = root / "logic_change.md"
        text = change_path.read_text(encoding="utf-8")
        self.assertIn("- authority_surfaces: RULE-OUTPUT", text)
        text = text.replace(
            "- authority_surfaces: RULE-OUTPUT", f"- authority_surfaces: {rule_id}"
        ).replace("surfaces: RULE-OUTPUT", f"surfaces: {rule_id}")
        change_path.write_text(text, encoding="utf-8")

    def test_cross_ledger_shared_rule_target_requires_explicit_conflict(self) -> None:
        """根 CHG 与领域 CHG 同指 RULE-APP-OUTPUT 却未互写 conflicts_with → 现状门失败。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            self._retarget_root_change(root, "RULE-APP-OUTPUT")
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertEqual(
            issues,
            [
                "CHG-20260722-001:shared-rule-target-needs-explicit-conflict:"
                f"{DOMAIN_CHANGE_ID}:RULE-APP-OUTPUT"
            ],
        )
        self.assertTrue(self.fails(report))

    def test_cross_ledger_reciprocal_conflict_passes_gate(self) -> None:
        """互写 conflicts_with + 同一 conflict_resolution + 单向 depends_on 后，门应当通过。

        这是一法多议案的规定解法（RULE-023）：根议案与领域议案的目标可以跨账本
        解析，不得被账本边界打成 conflict-target-not-active / dependency-target-not-active。
        """
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            self._retarget_root_change(root, "RULE-APP-OUTPUT")
            root_change = root / "logic_change.md"
            text = root_change.read_text(encoding="utf-8")
            text = text.replace(
                "- conflicts_with: none", f"- conflicts_with: {DOMAIN_CHANGE_ID}"
            ).replace(
                "- conflict_resolution: none",
                "- conflict_resolution: sequence-and-revalidate",
            )
            root_change.write_text(text, encoding="utf-8")
            domain_change_path = root / "src" / "logic_change.md"
            text = domain_change_path.read_text(encoding="utf-8")
            text = text.replace(
                "- conflicts_with: none", "- conflicts_with: CHG-20260722-001"
            ).replace(
                "- conflict_resolution: none",
                "- conflict_resolution: sequence-and-revalidate",
            ).replace(
                "- depends_on: none",
                "- depends_on: CHG-20260722-001@revision-1\n"
                "- unblock_condition: CHG-20260722-001 closes, then re-verify the output contract",
            )
            # 依赖活跃议案的一方须处于 verifying + unblock_condition（联合验收等待），
            # 否则审计按规则报 active-dependency-needs-block-or-redecision
            text = text.replace("implementing", "verifying")
            domain_change_path.write_text(text, encoding="utf-8")
            text = root_change.read_text(encoding="utf-8")
            root_change.write_text(
                text.replace(f"| {DOMAIN_CHANGE_ID} | implementing |", f"| {DOMAIN_CHANGE_ID} | verifying |"),
                encoding="utf-8",
            )
            report = self.collect(root)

        issues = report["current_integrity"]["proposal_issues"]
        self.assertEqual(issues, [])
        self.assertTrue(report["static_gate"]["passed"], report["static_gate"])

    def test_rule_reviewed_after_proposal_is_reported_through_gate(self) -> None:
        """规则 last_reviewed（2026-07-22）晚于 CHG created/last_status_change（2026-07-01）。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            change_path = root / "logic_change.md"
            text = change_path.read_text(encoding="utf-8")
            text = text.replace("- created: 2026-07-22", "- created: 2026-07-01").replace(
                "- last_status_change: 2026-07-22", "- last_status_change: 2026-07-01"
            )
            change_path.write_text(text, encoding="utf-8")
            report = self.collect(root)

        self.assertEqual(
            report["current_integrity"]["proposal_issues"],
            ["CHG-20260722-001:rule-changed-after-proposal:RULE-OUTPUT:2026-07-22>2026-07-01"],
        )
        self.assertTrue(self.fails(report))

    def test_domain_rule_reviewed_after_domain_proposal_is_reported(self) -> None:
        """领域 readme 当前制度行的 last_reviewed 也进入规则日期表。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            domain_change_path = root / "src" / "logic_change.md"
            text = domain_change_path.read_text(encoding="utf-8")
            text = text.replace("- created: 2026-07-22", "- created: 2026-07-01").replace(
                "- last_status_change: 2026-07-22", "- last_status_change: 2026-07-10"
            )
            domain_change_path.write_text(text, encoding="utf-8")
            report = self.collect(root)

        self.assertIn(
            f"{DOMAIN_CHANGE_ID}:rule-changed-after-proposal:RULE-APP-OUTPUT:2026-07-22>2026-07-10",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))

    def test_same_domain_ledger_overlap_is_checked_as_whole_ledger(self) -> None:
        """同一领域账本内两条 CHG 共享 authority_surfaces → unmarked-authority-surface-overlap。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            domain_change_path = root / "src" / "logic_change.md"
            domain_change_path.write_text(
                append_domain_change(
                    domain_change_path.read_text(encoding="utf-8"),
                    change_id="CHG-20260722-003",
                    authority_surfaces="RULE-APP-OUTPUT",
                ),
                encoding="utf-8",
            )
            root_change = root / "logic_change.md"
            text = root_change.read_text(encoding="utf-8")
            self.assertIn(DOMAIN_GAZETTE_ROW, text)
            text = text.replace(
                DOMAIN_GAZETTE_ROW,
                DOMAIN_GAZETTE_ROW + "\n" + domain_gazette_row("CHG-20260722-003"),
                1,
            )
            root_change.write_text(text, encoding="utf-8")
            report = self.collect(root)

        self.assertEqual(
            report["current_integrity"]["proposal_issues"],
            [
                f"{DOMAIN_CHANGE_ID}:unmarked-authority-surface-overlap:"
                "CHG-20260722-003:rule-app-output"
            ],
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


REGISTRY_HEADER = (
    "| module_id | scope_path | membership | scope_type/layer | doc_policy "
    "| logic_readme | logic_change | owner | status |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)


class RootDocCoverageTests(unittest.TestCase):
    """RULE-019：git 跟踪的顶层 Markdown 入口必须被 owned/unmapped 登记覆盖。"""

    @staticmethod
    def _init_repo(root: Path) -> None:
        for args in (
            ["init"],
            ["config", "user.email", "test@example.invalid"],
            ["config", "user.name", "Recall Test"],
        ):
            subprocess.run(
                ["git", *args], cwd=root, capture_output=True, text=True
            )

    @staticmethod
    def _readme(owned: str, unmapped: str | None = None) -> str:
        unmapped_line = f"- unmapped_paths: {unmapped}\n" if unmapped else ""
        return (
            "# Root\n\n## 范围登记与归属\n\n"
            f"- owned_paths: {owned}\n{unmapped_line}"
        )

    def test_unregistered_top_level_markdown_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_repo(root)
            (root / "logic_readme.md").write_text(
                self._readme("logic_readme.md, references/"), encoding="utf-8"
            )
            (root / "SUMMARY_COPY.md").write_text("# stale\n", encoding="utf-8")
            (root / "references").mkdir()
            (root / "references" / "tpl.md").write_text("# tpl\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "--", "."], cwd=root, capture_output=True
            )
            result = AUDIT.audit_root_doc_coverage(root)

        self.assertTrue(result["checked"])
        self.assertIn("SUMMARY_COPY.md", result["unregistered"])
        self.assertNotIn("references", result["unregistered"])
        self.assertNotIn("logic_readme.md", result["unregistered"])

    def test_unmapped_registration_and_annotations_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_repo(root)
            (root / "logic_readme.md").write_text(
                self._readme(
                    "logic_readme.md",
                    "docs/ (教学材料、非真源), CONTRIBUTING.md (社区文档)",
                ),
                encoding="utf-8",
            )
            (root / "docs").mkdir()
            (root / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("# c\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "--", "."], cwd=root, capture_output=True
            )
            result = AUDIT.audit_root_doc_coverage(root)

        self.assertTrue(result["checked"])
        self.assertEqual(result["unregistered"], [])

    def test_without_git_or_owned_paths_check_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "logic_readme.md").write_text(
                "# Root without owned_paths\n", encoding="utf-8"
            )
            result = AUDIT.audit_root_doc_coverage(root)

        self.assertFalse(result["checked"])
        self.assertEqual(result["unregistered"], [])


class ChildReadmeDensityTests(unittest.TestCase):
    """RULE-018：宪法 150/250、部门法 250/400；旧式 readme-only 子文档按部门法阈值。"""

    @staticmethod
    def _write_registry(root: Path, row: str) -> None:
        (root / "logic_readme.md").write_text(
            "# Root\n\n### 范围登记表\n\n" + REGISTRY_HEADER + row + "\n",
            encoding="utf-8",
        )

    def test_registered_child_document_paths_cover_paired_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_registry(root, PAIRED_APP_ROW)
            paired = AUDIT.registered_child_document_paths(root)
            self._write_registry(root, README_ONLY_APP_ROW)
            readme_only = AUDIT.registered_child_document_paths(root)
            self.assertEqual(readme_only, AUDIT.registered_child_readme_paths(root))

        self.assertEqual(paired, {"src/logic_readme.md", "src/logic_change.md"})
        self.assertEqual(readme_only, {"src/logic_readme.md"})

    def test_constitution_thresholds_are_150_and_250(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_registry(root, PAIRED_APP_ROW)
            base = (root / "logic_readme.md").read_text(encoding="utf-8")
            (root / "logic_readme.md").write_text(
                base + "line\n" * 160, encoding="utf-8"
            )
            over_target = AUDIT.audit_density(root, [])
            (root / "logic_readme.md").write_text(
                base + "line\n" * 260, encoding="utf-8"
            )
            over_limit = AUDIT.audit_density(root, [])

        self.assertTrue(
            any(n.startswith("logic_readme.md:over-target:") for n in over_target["notices"]),
            over_target["notices"],
        )
        self.assertFalse(
            [i for i in over_target["issues"] if i.startswith("logic_readme.md:")],
            over_target["issues"],
        )
        self.assertTrue(
            any(
                i.startswith("logic_readme.md:exceeds-hard-limit:")
                for i in over_limit["issues"]
            ),
            over_limit["issues"],
        )

    def test_domain_readme_over_target_suggests_splitting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_registry(root, PAIRED_APP_ROW)
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text(
                "line\n" * 300, encoding="utf-8"
            )
            (root / "src" / "logic_change.md").write_text("# c\n", encoding="utf-8")
            result = AUDIT.audit_density(root, [])

        notice = next(
            (n for n in result["notices"] if n.startswith("src/logic_readme.md:over-target:")),
            None,
        )
        self.assertIsNotNone(notice, result["notices"])
        self.assertIn("大部门拆小部门", notice)
        self.assertFalse(
            [i for i in result["issues"] if i.startswith("src/logic_readme.md")],
            result["issues"],
        )
        self.assertFalse(
            any(n.startswith("logic_readme.md:constitution-without-domains") for n in result["notices"]),
            result["notices"],
        )

    def test_domain_readme_over_hard_limit_is_an_issue(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_registry(root, PAIRED_APP_ROW)
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text(
                "line\n" * 450, encoding="utf-8"
            )
            result = AUDIT.audit_density(root, [])

        self.assertTrue(
            any(
                i.startswith("src/logic_readme.md:exceeds-hard-limit:")
                for i in result["issues"]
            ),
            result["issues"],
        )

    def test_oversized_registered_child_readme_reports_issue(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "logic_readme.md").write_text(
                "# Root\n\n### 范围登记表\n\n"
                + REGISTRY_HEADER
                + README_ONLY_APP_ROW
                + "\n",
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text(
                "line\n" * 450, encoding="utf-8"
            )
            issues = AUDIT.audit_density(root, [])["issues"]

        self.assertTrue(
            any(
                issue.startswith("src/logic_readme.md:exceeds-hard-limit")
                for issue in issues
            ),
            issues,
        )

    def test_child_readme_within_limit_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "logic_readme.md").write_text(
                "# Root\n\n### 范围登记表\n\n"
                + REGISTRY_HEADER
                + README_ONLY_APP_ROW
                + "\n",
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text(
                "line\n" * 100, encoding="utf-8"
            )
            issues = AUDIT.audit_density(root, [])["issues"]

        self.assertFalse(
            [issue for issue in issues if issue.startswith("src/logic_readme.md")]
        )


PERSONAL_LEDGER_HEAD = """# Demo Active Changes

## 文档控制

- scope: .
- scope_path: .
- module_id: MOD-ROOT
- current_policy: logic_readme.md
- owner: self
- governance_mode: {mode}
- governance_ref: git:demo-repository
- governance_evidence: git:demo-repository
- governance_verification: recorded
- governance_verified_at: 2026-09-03
- last_updated: 2026-09-03
- active_changes: 1

## 议案规则

- All entries are non-effective until promoted.

## 讨论主题索引

| topic_id | 同类议题/共享问题 | coordinator | discussion_refs | related_changes | status |
|---|---|---|---|---|---|

## 活跃议案索引

| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |
|---|---|---|---|---|---|---|---|
| CHG-20260903-001 | {status} | src | self | slim | none | logic_change.md#chg-20260903-001 | 2026-09-03 |

<a id="chg-20260903-001"></a>
## CHG-20260903-001: Slim personal proposal

### 元数据

- status: {status}
- effective: false
- proposal_revision: 1
- recall_route: medium
- owner: self
- changed_by: agent
- scope: src
{confirmation}
### 目标

Keep the output contract.
"""


def personal_ledger(*, mode: str = "personal", status: str = "implementing", confirmed: bool = True) -> str:
    confirmation = (
        "- decision_confirmed_by: user\n- decision_confirmed_at: 2026-09-03\n"
        if confirmed
        else ""
    )
    return PERSONAL_LEDGER_HEAD.format(mode=mode, status=status, confirmation=confirmation)


class GovernanceTierTests(unittest.TestCase):
    """RULE-023：CHG 字段要求按治理模式分档——personal 缺则不查、写则照查。"""

    def test_personal_slim_block_has_no_missing_field_issues(self) -> None:
        text = personal_ledger()
        semantic = AUDIT.change_block_semantic_issues(text, root_index=True)
        coordination = AUDIT.change_coordination_issues(
            AUDIT.change_blocks(text), ledger_mode="personal"
        )
        self.assertEqual(semantic, [])
        self.assertEqual(coordination, [])

    def test_same_block_under_collaborative_still_requires_full_fields(self) -> None:
        text = personal_ledger(mode="collaborative")
        semantic = AUDIT.change_block_semantic_issues(text, root_index=True)
        coordination = AUDIT.change_coordination_issues(
            AUDIT.change_blocks(text), ledger_mode="collaborative"
        )
        self.assertIn("CHG-20260903-001:topic-id-must-appear-once:0", semantic)
        self.assertIn("CHG-20260903-001:decision_gate-must-appear-once:0", semantic)
        self.assertIn("CHG-20260903-001:missing-authority-surfaces", coordination)
        self.assertIn("CHG-20260903-001:based_on-must-appear-once:0", coordination)

    def test_unknown_mode_keeps_full_requirements(self) -> None:
        """账本与块都没声明模式时按 full 处理，不替未声明模式的项目降门槛。"""
        blocks = AUDIT.change_blocks(personal_ledger())
        self.assertIn(
            "CHG-20260903-001:missing-authority-surfaces",
            AUDIT.change_coordination_issues(blocks),
        )

    def test_personal_implementation_still_needs_confirmation(self) -> None:
        text = personal_ledger(confirmed=False)
        issues = AUDIT.change_block_semantic_issues(text, root_index=True)
        self.assertIn(
            "CHG-20260903-001:implementation-needs-decision-confirmation", issues
        )
        self.assertIn("CHG-20260903-001:decision_confirmed_at-must-be-date", issues)
        draft = AUDIT.change_block_semantic_issues(
            personal_ledger(status="draft", confirmed=False), root_index=True
        )
        self.assertNotIn(
            "CHG-20260903-001:implementation-needs-decision-confirmation", draft
        )

    def test_personal_written_optional_fields_are_still_validated(self) -> None:
        text = personal_ledger().replace(
            "- scope: src\n",
            "- scope: src\n- conflicts_with: CHG-20260903-009\n- runtime_state: bogus\n",
        )
        coordination = AUDIT.change_coordination_issues(
            AUDIT.change_blocks(text), ledger_mode="personal"
        )
        self.assertIn("CHG-20260903-001:conflicts-need-resolution", coordination)
        self.assertIn("CHG-20260903-001:invalid-runtime-state:bogus", coordination)


def coordination_block(
    change_id: str,
    *,
    status: str = "awaiting-decision",
    conflicts_with: str = "none",
    conflict_resolution: str = "none",
    depends_on: str = "none",
) -> str:
    """最小协调块（personal 档）：供 change_coordination_issues 跨账本目标解析单测。"""
    return f"""## {change_id}: Coordination probe

### 元数据

- status: {status}
- effective: false
- proposal_revision: 1
- authority_surfaces: RULE-OUTPUT
- depends_on: {depends_on}
- conflicts_with: {conflicts_with}
- conflict_resolution: {conflict_resolution}

### 拟议制度

Keep the output contract.
"""


class CrossLedgerCoordinationTests(unittest.TestCase):
    """RULE-018/023：depends_on / conflicts_with / blocked_by 的目标可落在其他账本。"""

    ROOT_ID = "CHG-20260901-001"
    DOMAIN_ID = "CHG-20260901-002"

    def _ledgers(self, *, domain_conflicts: str, domain_resolution: str = "supersede"):
        root_blocks = {
            self.ROOT_ID: coordination_block(
                self.ROOT_ID, conflicts_with=self.DOMAIN_ID, conflict_resolution="supersede"
            )
        }
        domain_blocks = {
            self.DOMAIN_ID: coordination_block(
                self.DOMAIN_ID,
                conflicts_with=domain_conflicts,
                conflict_resolution=domain_resolution,
            )
        }
        return root_blocks, domain_blocks

    def test_reciprocal_conflict_resolves_across_ledgers(self) -> None:
        root_blocks, domain_blocks = self._ledgers(domain_conflicts=self.ROOT_ID)
        for own, other in ((root_blocks, domain_blocks), (domain_blocks, root_blocks)):
            self.assertEqual(
                AUDIT.change_coordination_issues(
                    own, ledger_mode="personal", other_ledgers={"other": other}
                ),
                [],
            )

    def test_without_other_ledgers_target_is_still_not_active(self) -> None:
        """未提供其他账本时保持旧语义：目标不在本账本即报 not-active。"""
        root_blocks, _ = self._ledgers(domain_conflicts=self.ROOT_ID)
        self.assertEqual(
            AUDIT.change_coordination_issues(root_blocks, ledger_mode="personal"),
            [f"{self.ROOT_ID}:conflict-target-not-active:{self.DOMAIN_ID}"],
        )

    def test_one_way_conflict_across_ledgers_is_not_reciprocal(self) -> None:
        root_blocks, domain_blocks = self._ledgers(
            domain_conflicts="none", domain_resolution="none"
        )
        self.assertEqual(
            AUDIT.change_coordination_issues(
                root_blocks, ledger_mode="personal", other_ledgers={"src": domain_blocks}
            ),
            [f"{self.ROOT_ID}:conflict-not-reciprocal:{self.DOMAIN_ID}"],
        )

    def test_dependency_target_in_other_ledger_is_active(self) -> None:
        root_blocks = {
            self.ROOT_ID: coordination_block(self.ROOT_ID, status="draft")
        }
        domain_blocks = {
            self.DOMAIN_ID: coordination_block(
                self.DOMAIN_ID, status="draft", depends_on=f"{self.ROOT_ID}@revision-1"
            )
        }
        self.assertEqual(
            AUDIT.change_coordination_issues(
                domain_blocks, ledger_mode="personal", other_ledgers={"root": root_blocks}
            ),
            [],
        )
        self.assertEqual(
            AUDIT.change_coordination_issues(domain_blocks, ledger_mode="personal"),
            [f"{self.DOMAIN_ID}:dependency-target-not-active:{self.ROOT_ID}"],
        )

    def test_cross_ledger_dependency_cycle_reported_once(self) -> None:
        root_blocks = {
            self.ROOT_ID: coordination_block(
                self.ROOT_ID, status="draft", depends_on=f"{self.DOMAIN_ID}@revision-1"
            )
        }
        domain_blocks = {
            self.DOMAIN_ID: coordination_block(
                self.DOMAIN_ID, status="draft", depends_on=f"{self.ROOT_ID}@revision-1"
            )
        }
        cycle = f"dependency-cycle:{self.ROOT_ID},{self.DOMAIN_ID}"
        self.assertIn(
            cycle,
            AUDIT.change_coordination_issues(
                root_blocks, ledger_mode="personal", other_ledgers={"src": domain_blocks}
            ),
        )
        self.assertNotIn(
            cycle,
            AUDIT.change_coordination_issues(
                domain_blocks, ledger_mode="personal", other_ledgers={"root": root_blocks}
            ),
        )


class CrossLedgerRuleConflictTests(unittest.TestCase):
    """一法多议案（VER-20260904-001）：cross_ledger_rule_conflicts 直接单测。"""

    ROOT = "logic_change.md"
    DOMAIN = "src/logic_change.md"

    def test_shared_target_across_ledgers_without_reciprocal_conflict(self) -> None:
        issues = AUDIT.cross_ledger_rule_conflicts(
            {
                self.ROOT: {"CHG-20260901-001": rule_change_block("CHG-20260901-001")},
                self.DOMAIN: {"CHG-20260901-002": rule_change_block("CHG-20260901-002")},
            },
            {},
        )
        self.assertEqual(
            issues,
            [
                "CHG-20260901-001:shared-rule-target-needs-explicit-conflict:"
                "CHG-20260901-002:RULE-OUTPUT"
            ],
        )

    def test_one_way_conflict_declaration_is_still_reported(self) -> None:
        issues = AUDIT.cross_ledger_rule_conflicts(
            {
                self.ROOT: {
                    "CHG-20260901-001": rule_change_block(
                        "CHG-20260901-001", conflicts_with="CHG-20260901-002"
                    )
                },
                self.DOMAIN: {"CHG-20260901-002": rule_change_block("CHG-20260901-002")},
            },
            {},
        )
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("shared-rule-target-needs-explicit-conflict", issues[0])

    def test_reciprocal_conflict_declaration_clears_shared_target(self) -> None:
        issues = AUDIT.cross_ledger_rule_conflicts(
            {
                self.ROOT: {
                    "CHG-20260901-001": rule_change_block(
                        "CHG-20260901-001", conflicts_with="CHG-20260901-002"
                    )
                },
                self.DOMAIN: {
                    "CHG-20260901-002": rule_change_block(
                        "CHG-20260901-002", conflicts_with="`CHG-20260901-001`"
                    )
                },
            },
            {},
        )
        self.assertEqual(issues, [])

    def test_same_ledger_overlap_is_left_to_coordination_check(self) -> None:
        """同账本重叠由 change_coordination_issues 报 unmarked-authority-surface-overlap。"""
        blocks = {
            "CHG-20260901-001": rule_change_block("CHG-20260901-001"),
            "CHG-20260901-002": rule_change_block("CHG-20260901-002"),
        }
        self.assertEqual(AUDIT.cross_ledger_rule_conflicts({self.ROOT: blocks}, {}), [])
        self.assertIn(
            "CHG-20260901-001:unmarked-authority-surface-overlap:CHG-20260901-002:rule-output",
            AUDIT.change_coordination_issues(blocks, ledger_mode="personal"),
        )

    def test_multiple_shared_targets_are_listed_sorted_and_uppercased(self) -> None:
        issues = AUDIT.cross_ledger_rule_conflicts(
            {
                self.ROOT: {
                    "CHG-20260901-001": rule_change_block(
                        "CHG-20260901-001", authority_surfaces="rule-output; RULE-INPUT"
                    )
                },
                self.DOMAIN: {
                    "CHG-20260901-002": rule_change_block(
                        "CHG-20260901-002",
                        authority_surfaces="RULE-INPUT, RULE-OUTPUT, RULE-OTHER",
                    )
                },
            },
            {},
        )
        self.assertEqual(
            issues,
            [
                "CHG-20260901-001:shared-rule-target-needs-explicit-conflict:"
                "CHG-20260901-002:RULE-INPUT,RULE-OUTPUT"
            ],
        )

    def test_rule_changed_after_proposal_uses_latest_change_date(self) -> None:
        block = rule_change_block(
            "CHG-20260901-001", created="2026-07-01", last_status_change="2026-07-10"
        )
        stale = AUDIT.cross_ledger_rule_conflicts(
            {self.ROOT: {"CHG-20260901-001": block}}, {"RULE-OUTPUT": "2026-08-01"}
        )
        self.assertEqual(
            stale,
            ["CHG-20260901-001:rule-changed-after-proposal:RULE-OUTPUT:2026-08-01>2026-07-10"],
        )
        same_day = AUDIT.cross_ledger_rule_conflicts(
            {self.ROOT: {"CHG-20260901-001": block}}, {"RULE-OUTPUT": "2026-07-10"}
        )
        self.assertEqual(same_day, [])
        older = AUDIT.cross_ledger_rule_conflicts(
            {self.ROOT: {"CHG-20260901-001": block}}, {"RULE-OUTPUT": "2026-06-30"}
        )
        self.assertEqual(older, [])

    def test_rule_date_check_ignores_unrelated_rules_and_undated_blocks(self) -> None:
        undated = rule_change_block(
            "CHG-20260901-001", created="event-driven", last_status_change="none"
        )
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts(
                {self.ROOT: {"CHG-20260901-001": undated}}, {"RULE-OUTPUT": "2026-08-01"}
            ),
            [],
        )
        dated = rule_change_block("CHG-20260901-001", created="2026-07-01")
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts(
                {self.ROOT: {"CHG-20260901-001": dated}},
                {"RULE-INPUT": "2026-08-01", "RULE-OUTPUT": "not-a-date"},
            ),
            [],
        )

    def test_mentioning_rule_without_authority_surfaces_is_reported(self) -> None:
        block = rule_change_block(
            "CHG-20260901-001",
            authority_surfaces="none",
            proposed_policy="Tighten rule-output and RULE-INPUT; RULE-OUTPUT again.",
        )
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts({self.ROOT: {"CHG-20260901-001": block}}, {}),
            ["CHG-20260901-001:mentions-rule-without-authority-surfaces:RULE-INPUT,RULE-OUTPUT"],
        )
        missing_field = rule_change_block(
            "CHG-20260901-001",
            authority_surfaces=None,
            proposed_policy="Rewrite RULE-OUTPUT.",
        )
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts({self.ROOT: {"CHG-20260901-001": missing_field}}, {}),
            ["CHG-20260901-001:mentions-rule-without-authority-surfaces:RULE-OUTPUT"],
        )

    def test_declared_authority_surfaces_suppress_mention_issue(self) -> None:
        block = rule_change_block(
            "CHG-20260901-001",
            authority_surfaces="RULE-OUTPUT",
            proposed_policy="Also touches RULE-INPUT in passing.",
        )
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts({self.ROOT: {"CHG-20260901-001": block}}, {}),
            [],
        )

    def test_mentions_outside_proposed_policy_section_are_ignored(self) -> None:
        block = rule_change_block(
            "CHG-20260901-001", authority_surfaces="none", proposed_policy="No rule ids here."
        ) + "\n### 开放问题与用户澄清\n\n- questions_for_user: does RULE-OUTPUT apply?\n"
        self.assertEqual(
            AUDIT.cross_ledger_rule_conflicts({self.ROOT: {"CHG-20260901-001": block}}, {}),
            [],
        )



class PlaceholderDetectionTests(unittest.TestCase):
    """占位符识别只用 textutil `contains_angle_placeholder`（RULE-021 ③）。

    2026-09-03 eduai：规则正文里的 `>128` 与 `<meta>` 被 current-state 门当作模板
    占位符，规则行搬进部门法后静态门才爆；用户被迫写 HTML 实体绕过。
    """

    def test_comparisons_arrows_and_inline_code_are_not_placeholders(self) -> None:
        for text in (
            "Reject payloads >128 KB",
            "a < b means retry",
            "INT-001 -> RULE-001 -> test",
            "Strip `<meta>` tags before storing",
        ):
            self.assertFalse(AUDIT.contains_angle_placeholder(text), text)

    def test_template_placeholder_is_still_detected(self) -> None:
        for text in ("<规则正文>", "Use <path> here", "<one-line why>"):
            self.assertTrue(AUDIT.contains_angle_placeholder(text), text)


class DomainRuleTextPlaceholderTests(ProjectFixtureMixin, unittest.TestCase):
    """规则/why 单元格里的比较符与行内代码不算占位符，模板尖括号仍然拒绝。"""

    def _report_with_rule_text(self, rule_text: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            readme_path = root / "src" / "logic_readme.md"
            text = readme_path.read_text(encoding="utf-8").replace(
                "Keep the module output stable.", rule_text
            )
            readme_path.write_text(text, encoding="utf-8")
            return self.collect(root)

    def test_comparison_and_inline_code_in_rule_text_pass(self) -> None:
        report = self._report_with_rule_text(
            "Reject payloads >128 KB and strip `<meta>` tags."
        )
        self.assertNotIn(
            "src/logic_readme:current-policy-row-1-needs-rule-and-why",
            report["current_integrity"]["document_issues"],
        )
        self.assertFalse(self.fails(report))

    def test_angle_placeholder_in_rule_text_still_fails(self) -> None:
        report = self._report_with_rule_text("<fill in the rule>")
        self.assertIn(
            "src/logic_readme:current-policy-row-1-needs-rule-and-why",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))


class CodeSegmentLinkTests(unittest.TestCase):
    """链接可达性只查代码段之外的链接（RULE-021 ③，VER-20260904-004）。

    2026-09-04 消费项目：规则正文里示意性的 `[ID](path)` 被 `audit_links` 当作
    真实链接、报坏链，用户被迫把措辞改成"指向记录的 Markdown 链接"。
    """

    def test_strip_code_segments_removes_fences_and_spans(self) -> None:
        text = (
            "keep `[ID](path)` here\n"
            "```markdown\n[t](missing.md)\n```\n"
            "~~~\n[q](also-missing.md)\n~~~\n"
            "tail [k](v.md)"
        )
        stripped = AUDIT.strip_code_segments(text)
        self.assertNotIn("[ID](path)", stripped)
        self.assertNotIn("missing.md", stripped)
        self.assertIn("[k](v.md)", stripped)

    def test_audit_links_ignores_code_and_link_titles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "real.md").write_text("x", encoding="utf-8")
            document = root / "logic_readme.md"
            text = (
                "| RULE-001 | key | index accepts `[ID](path)` links | why |\n"
                "```\n[example](nowhere/example.md)\n```\n"
                "see [real](real.md \"Title\") and [bad](missing.md)\n"
            )
            document.write_text(text, encoding="utf-8")
            self.assertEqual(
                AUDIT.audit_links(document, text, root), ["missing.md"]
            )

    def test_empty_ledger_count_accepts_none_and_zero(self) -> None:
        for value in ("none", "None", "0", " 0 "):
            self.assertTrue(AUDIT.is_empty_ledger_count(value), value)
        for value in ("1", "", "n/a"):
            self.assertFalse(AUDIT.is_empty_ledger_count(value), value)


class DomainRuleTextLinkTests(ProjectFixtureMixin, unittest.TestCase):
    """规则单元格里反引号包裹的链接示例不算坏链；裸坏链仍使静态门失败并带 broken-link 前缀。"""

    def _report_with_rule_text(self, rule_text: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root)
            readme_path = root / "src" / "logic_readme.md"
            text = readme_path.read_text(encoding="utf-8").replace(
                "Keep the module output stable.", rule_text
            )
            readme_path.write_text(text, encoding="utf-8")
            return self.collect(root)

    def test_inline_code_link_example_passes(self) -> None:
        report = self._report_with_rule_text(
            "Index first column accepts bare IDs or `[ID](path)` links."
        )
        self.assertFalse(
            [
                issue
                for issue in report["current_integrity"]["document_issues"]
                if "broken-link" in issue
            ]
        )
        self.assertFalse(self.fails(report))

    def test_bare_broken_link_still_fails_with_prefix(self) -> None:
        report = self._report_with_rule_text("See [spec](nowhere/spec.md).")
        self.assertIn(
            "src:logic_readme:broken-link:nowhere/spec.md",
            report["current_integrity"]["document_issues"],
        )
        self.assertTrue(self.fails(report))


class EmptyLedgerCountTests(ProjectFixtureMixin, unittest.TestCase):
    """空账本 `active_changes` 写 `0` 与模板的 `none` 同义；有正文时 `0` 仍报不匹配。"""

    def test_domain_ledger_zero_without_bodies_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_domain_project(root, gazette_row=None)
            change_path = root / "src" / "logic_change.md"
            text = change_path.read_text(encoding="utf-8")
            row_start = text.index(f"| {DOMAIN_CHANGE_ID} | implementing")
            text = text[:row_start].replace("- active_changes: 1", "- active_changes: 0")
            change_path.write_text(text, encoding="utf-8")
            readme_path = root / "src" / "logic_readme.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    f"- 相关 CHG-ID：{DOMAIN_CHANGE_ID}", "- 相关 CHG-ID：none"
                ),
                encoding="utf-8",
            )
            report = self.collect(root)

        issues = (
            report["current_integrity"]["proposal_issues"]
            + report["current_integrity"]["document_issues"]
        )
        self.assertFalse([issue for issue in issues if "active_changes" in issue], issues)
        self.assertFalse(
            [issue for issue in issues if "missing-effective-marker" in issue], issues
        )
        self.assertFalse(self.fails(report))

    def test_zero_with_bodies_still_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            change_path = root / "logic_change.md"
            change_path.write_text(
                change_path.read_text(encoding="utf-8").replace(
                    "- active_changes: 1", "- active_changes: 0"
                ),
                encoding="utf-8",
            )
            report = self.collect(root)

        self.assertIn(
            "active_changes-count-mismatch:0!=1",
            report["current_integrity"]["proposal_issues"],
        )
        self.assertTrue(self.fails(report))


if __name__ == "__main__":
    unittest.main()
