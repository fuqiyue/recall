# VER-20260811-001: Git 自动同步

## 记录控制

- version_id: VER-20260811-001
- version_slug: logic_version-20260811-001-git-auto-sync
- status: effective
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: commit:1546710; hook:post-commit; tests:test_git_sync
- governance_verification: recorded
- governance_verified_at: 2026-08-11
- date: 2026-08-11
- scope: Git 初始化、远端同步与 Recall CLI
- affected_scopes: MOD-ROOT/., scripts/, tests/, references/
- authority_surfaces: RULE-010, RULE-011, recall init, recall sync, recall.autoSync
- based_on: policy: logic_readme.md#当前制度; code: commit:7e7f8ab; surfaces: Git 初始化与手动保持同步流程
- changed_layers: runtime-code/runtime-config/test-fixture
- change_id: none
- topic_id: none
- topic_shared_context: none
- topic_shared_constraints: none
- topic_discussion_refs: none
- topic_final_conclusion: none
- changed_by: Codex
- recall_route: medium
- history_retention: compact
- runtime_state: deployed-active
- runtime_environments: local Git repositories with configured remotes
- feature_flag: recall.autoSync=true by default; --no-auto-sync/--disable opt out
- proposal_commit_or_blob: none
- proposal_revision: none
- decision_record: not-required
- decision_state: not-required
- confirmed_proposal_revision: none
- decision_confirmed_by: user
- decision_ref: user-request:2026-08-11
- decision_confirmed_at: 2026-08-11
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: commit:1546710; tests:test_git_sync.py; audit:current-state
- semantic_reviewed_at: 2026-08-11
- before_commit: 7e7f8ab
- after_commit: 1546710
- supersedes: none
- corrects: none

## 来源与意图提炼

- intent_source_refs: user-request:2026-08-11
- intent_digest: 配置 Recall 的 Git 时要求具备自动同步能力，并将实现发布到 GitHub。
- intent_non_goals: 不静默提交未审阅的工作区文件；不保存 GitHub 凭据或替代远端权限控制。
- intent_constraints: 继续遵守 Git 管理代码、Recall 管理设计逻辑；外部命令使用 argv；CLI 支持非交互和重定向。
- intent_acceptance: 初始化默认启用同步；提交后自动拉取变基并推送；提供手动 sync 和关闭入口；同步失败保留本地提交。
- intent_status: confirmed
- intent_distilled_by: Codex
- intent_distilled_at: 2026-08-11
- intent_traceability: INT-20260811-001 -> RULE-010..011 -> test:tests/test_git_sync.py -> VER-20260811-001

## 为什么做这个决策？

Git 负责代码历史，远端同步是保持该历史可追溯的运行要求；自动化应只处理已确认的本地状态，避免静默提交未审阅文件。

## 决策确认与最终议案

- final_proposal_snapshot: embedded
- snapshot_source: user-request:2026-08-11; implementation in scripts/git_sync.py
- decision_confirmation: 采用默认启用、受管理 post-commit hook、手动 sync 和显式脏工作区提交信息的方案。
- current_behavior: 初始化只配置本地 Git 和首次提交；保持同步依赖人工执行 git pull/git push。
- proposed_rule: recall init 默认设置 recall.autoSync=true、pull.rebase=true、fetch.prune=true、push.autoSetupRemote=true，并安装 hook；recall sync 可手动同步或关闭。
- selected_option: A: 受管理 hook + CLI sync
- alternatives_and_tradeoffs: 仅文档提示无法自动同步；仅 Git 配置无法可靠执行 push；自动提交所有脏文件会绕过审阅。选择的方案覆盖自动推送，同时将工作区提交保持为显式动作。
- decision_why: Git 负责代码历史，远端同步是保持该历史可追溯的运行要求；hook 失败不阻断本地提交，降低网络和认证故障的破坏性。
- promoted_rule_ids: RULE-010, RULE-011
- scope_and_consumers: scripts/init_recall.py 和 scripts/git_sync.py 生产同步配置与命令；recall.py、recall.bat、recall.sh、Claude/Codex 入口和用户仓库消费；本地 Git 与配置的远端为运行环境。
- compatibility_and_exit: 新参数默认启用，旧命令仍可用；无远端时只告警；通过 --no-auto-sync 或 recall sync --disable 关闭，移除受管理 hook。
- acceptance_and_rollback: 自动 hook 在提交后执行 pull --rebase/push；脏工作区无显式消息返回保护性状态；git revert 相关提交并关闭 autoSync 可回滚。

## 影响范围

影响 Recall 初始化、统一 CLI、Git hook、仓库级 Git 配置、用户远端和自动化测试；不改变 logic_version 的数据格式或 Git 凭据管理。

## 变更摘要

- before: Recall 初始化配置 Git，但同步远端依赖手工命令。
- after: Recall 初始化默认配置自动同步；提交后 hook 自动同步已提交历史，recall sync 提供手动入口。
- why: 减少本地与远端历史漂移，同时避免静默提交未审阅文件。
- result: 生效并已发布到 origin/main。

## 验证方式

通过单元测试、Python 编译检查、当前态逻辑地图审计、CLI 帮助输出和本仓库 post-commit 实际同步验证。

## 影响与消费者

| impact_surface/artifact_layer | 生产者 | 消费者 | 环境 | 最终影响 | 证据 |
|---|---|---|---|---|---|
| scripts/runtime-code | init_recall.py, git_sync.py | Recall CLI 与 Git hook | local | 配置同步、拉取变基、推送 | commit:1546710 |
| docs/runtime-code | SKILL.md, README.md, CLAUDE.md, references/ | AI 代理与用户 | local | 工作流要求与退出方式明确 | commit:b56fd1b |
| tests/test-fixture | test_git_sync.py | CI/维护者 | local/CI | 同步策略和保护行为可回归 | tests:test_git_sync.py |

## 兼容、迁移与回滚

- compatibility: 旧项目不自动改动，运行 recall init 后才写入仓库级配置；已有自定义 hook 会保留，Recall 只更新自身标记区块。
- migration: 运行 recall init；没有远端时先 git remote add origin <url>，再 recall sync。
- runtime_data_evidence: none
- backup_reference: none
- rollback: `recall sync --disable`，必要时回退 commit:1546710 和 commit:b56fd1b。
- rollback_or_restore_verified: not-applicable; reversible through Git and config
- temporary_structure_removed: yes
- logic_temp_cleanup: none
- remaining_deprecation_end: none

## 测试与审核

| test_level | case/command | baseline | post-change | result | evidence | reviewer/date |
|---|---|---|---|---|---|---|
| unit | `python -m unittest tests.test_git_sync -v` | no sync module | 5 tests pass | pass | unittest output | self/2026-08-11 |
| unit | `python -m py_compile scripts/git_sync.py scripts/init_recall.py scripts/recall.py` | n/a | compile succeeds | pass | command output | self/2026-08-11 |
| contract | `python scripts/audit_logic_map.py . --current-state` | broken new link before record | no current integrity issue after record commit | pass | audit output | self/2026-08-11 |
| runtime | `python scripts/recall.py help`; `python scripts/git_sync.py --help` | no sync command | sync options discoverable | pass | CLI output | self/2026-08-11 |

- semantic_review_conclusion: 实现使用 argv 调用 Git；自动 hook 只同步已提交历史；脏工作区必须显式给出提交信息；同步失败不会影响本地提交；关闭操作只移除 Recall 管理的 hook 区块。
- runtime_observation: 本仓库的 post-commit hook 已成功同步到 origin/main。
- known_gaps: 远端认证、网络连通性和变基冲突仍依赖用户环境；未在真实冲突仓库中做端到端演练。

## 决策结论与经验

- selected_or_rejected_reason: 采用自动推送已提交历史、显式提交脏工作区的组合，在减少远端漂移和避免未审阅提交之间取得可回滚平衡。
- reusable_principle: 自动化发布动作应默认只处理已确认的本地状态，并把网络失败降级为可见警告；适用于个人或低并发 Git 工作流。

## 关联

- current_logic: RULE-010, RULE-011
- proposal_id: none
- former_proposal_path: none
- immutable_record: VER-20260811-001
- decision_record_path: logic_version/records/logic_version-20260811-001-git-auto-sync.md
- related_adr: none
- code/tests: scripts/git_sync.py; scripts/init_recall.py; scripts/recall.py; tests/test_git_sync.py
- issue/commit/release: commit:1546710; origin/main

## 回滚方式

运行 `recall sync --disable` 关闭自动同步；必要时用 Git 回退 commit:1546710 和 commit:b56fd1b，并恢复 `logic_readme.md` 中 RULE-010..011。
