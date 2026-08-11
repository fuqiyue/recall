# VER-20260811-002: CLI 胶水层接口修复

## 记录控制

- version_id: VER-20260811-002
- version_slug: logic_version-20260811-002-cli-interface-repair
- status: effective
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: tests:test_recall_cli, test_git_sync; audit:current-state
- governance_verification: recorded
- governance_verified_at: 2026-08-11
- date: 2026-08-11
- scope: Recall CLI 胶水层（recall.py 与子模块的接口）、决策记录命名、自动同步语义
- affected_scopes: MOD-ROOT/., scripts/, tests/, references/
- authority_surfaces: RULE-011, RULE-012, recall new, recall status, recall conflicts, recall sync
- based_on: policy: logic_readme.md#当前制度; code: commit:60aea3f; surfaces: 代码审查发现的接口断裂清单
- changed_layers: runtime-code/test-fixture
- change_id: none
- topic_id: none
- topic_shared_context: none
- topic_shared_constraints: none
- topic_discussion_refs: none
- topic_final_conclusion: none
- changed_by: Claude (Fable 5)
- recall_route: medium
- history_retention: compact
- runtime_state: implemented-unmerged
- runtime_environments: local
- feature_flag: none
- proposal_commit_or_blob: none
- proposal_revision: none
- decision_record: not-required
- decision_state: not-required
- confirmed_proposal_revision: none
- decision_confirmed_by: user
- decision_ref: user-request:2026-08-11（审查后要求"帮我修复这些内容"）
- decision_confirmed_at: 2026-08-11
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: tests:test_recall_cli.py, test_git_sync.py; runtime:recall status/new/list 实测
- semantic_reviewed_at: 2026-08-11
- before_commit: 60aea3f
- after_commit: 5afe9bb
- supersedes: none
- corrects: none

## 来源与意图提炼

- intent_source_refs: user-request:2026-08-11
- intent_digest: 修复代码审查发现的 CLI 胶水层缺陷，使 recall new/status/conflicts/list 与文档承诺一致。
- intent_non_goals: 不重构 audit_logic_map.py；不改变治理模式和记录 schema 本身。
- intent_constraints: 继续遵守 RULE-005..009（argv、非交互、schema 以 references/ 为准）；VER-* 记录不可改写。
- intent_acceptance: recall new 可创建能被 validate/status/list 发现的记录；status 正确统计；conflicts 能提取标准 CHG 标题；脏工作区不再阻断已提交历史同步；新增冒烟测试全绿。
- intent_status: confirmed
- intent_distilled_by: Claude (Fable 5)
- intent_distilled_at: 2026-08-11
- intent_traceability: INT-20260811-002 -> RULE-011..012 -> test:tests/test_recall_cli.py -> VER-20260811-002

## 为什么做这个决策？

审查发现被测试覆盖的核心模块质量良好，而无测试的 CLI 胶水层存在多处接口漂移：
recall.py 调用 create_ver 中不存在的函数且参数个数不符（recall new 完全不可用）；
决策记录文件名有三套（create_ver 生成 ver-*、status 统计 ver-*、validate/list 认
logic_version-*），导致 status 显示 0 条记录、新建记录对校验工具不可见——这正是
RULE-009 声称防范却只修了一半的 schema 漂移；detect_conflicts 的正则匹配不到标准
`## CHG-...:` 标题，议案冲突检测一直返回空；git_sync 在脏工作区时连已提交历史也
拒绝同步，比 RULE-011 的字面承诺更保守，使部分提交场景下 hook 永远推不出去。

## 决策过程

**方案 A**：只修断裂点（补函数、改正则），不加测试、不统一命名——最小改动，
但漂移已复发过一次，没有回归防线还会再犯。

**方案 B**：修复 + 用规范名 `logic_version-YYYYMMDD-NNN-<scope>.md` 统一创建方与
所有发现方 + 增加 CLI 冒烟测试 + 把命名约定固化为 RULE-012。多改一层，但把
"接口约定"从隐式变为受测试保护的显式规则。

**选中方案与原因**：方案 B。断裂的共同根因是接口约定只存在于口头，选 B 消除
根因而不只是症状。脏工作区语义按文档字面（"只处理已提交的变更"）对齐实现，
pull 侧由 `--autostash` 保护。

## 影响范围

**修改的文件/模块**：
- `scripts/create_ver.py` - 补 find_project_root；生成规范文件名；返回退出码；模板解析只取围栏内内容
- `scripts/recall.py` - cmd_new 接口对齐；status 用规范名统计；收窄裸 except
- `scripts/detect_conflicts.py` - CHG 标题正则接受 `## CHG-...:`；UTF-8 处理加防护
- `scripts/git_sync.py` - 脏工作区不阻断已提交历史同步；--post-commit 软性跳过返回 0
- `scripts/link_ver_git.py` - 记录目录改为向上查找项目根
- `references/logic-version-git-template.md` - 快速模板字段对齐 validate schema；移除内嵌过期示例代码
- `references/git-workflow-integration.md` - 示例文件名改为规范命名
- `tests/test_git_sync.py`、`tests/test_recall_cli.py` - 更新与新增测试

**破坏性变更**：否。旧命名 ver-*.md 的既有文件不被改名；create_ver 取号时新旧
命名的序号都计入，避免撞号。行为变化仅有：脏工作区时 sync 从"拒绝（返回 2）"
变为"仅同步已提交历史（返回 0）"。

## 验证方式

`python -m unittest tests.test_git_sync tests.test_recall_cli`（14 tests OK）；
`python tests/test_audit_logic_map.py`（62 tests OK）；`recall status` 正确显示
3 条记录；子目录中 `recall list` 可发现记录；`recall new` 在临时项目中生成的
记录通过 validate 必填字段检查；`python scripts/validate.py` 无错误。

## 回滚方式

`git revert` 本次修复提交即可整体回退；如仅需恢复旧的脏工作区阻断行为，改回
`git_sync.sync_repository` 中 `_is_dirty` 分支为 `return 2`，并同步还原
RULE-011 表述与 `tests/test_git_sync.py` 对应断言。

## 经验与教训

跨文件的接口约定（函数签名、文件命名、根目录查找）必须有一个可执行的权威来源：
要么共享常量/函数，要么用接口级测试钉住；只写在注释和文档里的约定会在独立修改
中静默漂移。模板中不要内嵌实现代码副本——它无法随实现更新，本次命名漂移的
复发源正是模板里的过期示例脚本。

## 关联

- current_logic: RULE-011, RULE-012
- proposal_id: none
- former_proposal_path: none
- immutable_record: VER-20260811-002
- decision_record_path: logic_version/records/logic_version-20260811-002-cli-interface-repair.md
- related_adr: none
- code/tests: scripts/recall.py; scripts/create_ver.py; scripts/detect_conflicts.py; scripts/git_sync.py; scripts/link_ver_git.py; tests/test_recall_cli.py; tests/test_git_sync.py
- issue/commit/release: before commit:60aea3f
