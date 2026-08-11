# VER-20260811-003: 默认自动保存上传与 after_commit 自动回填

## 记录控制

- version_id: VER-20260811-003
- version_slug: logic_version-20260811-003-auto-save-sync
- status: effective
- immutable: true
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: tests:test_git_sync; audit:current-state
- governance_verification: recorded
- governance_verified_at: 2026-08-11
- date: 2026-08-11
- scope: Git 同步语义（自动保存提交）、决策记录 after_commit 回填、hook 递归防护
- affected_scopes: MOD-ROOT/., scripts/, tests/
- authority_surfaces: RULE-011, RULE-013, recall sync, recall init, post-commit hook
- based_on: policy: logic_readme.md#当前制度; code: commit:5afe9bb; surfaces: 用户对同步语义的新决定
- changed_layers: runtime-code/test-fixture
- change_id: none
- topic_id: none
- topic_shared_context: none
- topic_shared_constraints: none
- topic_discussion_refs: none
- topic_final_conclusion: none
- changed_by: Claude (Fable 5)
- recall_route: high
- history_retention: compact
- runtime_state: implemented-unmerged
- runtime_environments: local
- feature_flag: recall.autoCommit（仓库级 Git 配置，默认 true）
- proposal_commit_or_blob: none
- proposal_revision: none
- decision_record: not-required
- decision_state: not-required
- confirmed_proposal_revision: none
- decision_confirmed_by: user
- decision_ref: user-request:2026-08-11（"skill 默认是自动保存上传，如果用户选择手动上传的话，则修改为手动上传"；"after_commit 由 AI/自动化回填，请提交"）
- decision_confirmed_at: 2026-08-11
- semantic_review_state: passed
- semantic_reviewed_by: self
- semantic_review_ref: tests:test_git_sync.py（12 tests）；runtime:提交本记录时 hook 实测回填
- semantic_reviewed_at: 2026-08-11
- before_commit: 5afe9bb
- after_commit: _待填写_
- supersedes: none
- corrects: none

## 来源与意图提炼

- intent_source_refs: user-request:2026-08-11
- intent_digest: 用户改动保存后无需手动上传：sync 默认自动提交并推送，可切换手动；决策记录的 after_commit 不再依赖手工回填。
- intent_non_goals: 不实现文件系统监听守护进程（保存即提交仍需触发 recall sync 或 git commit）；不改变 pull --rebase --autostash 的同步策略。
- intent_constraints: post-commit hook 绝不把其他脏文件卷入提交（保护部分提交工作流）；内部提交必须防 hook 递归；继续遵守 RULE-005..009。
- intent_acceptance: 脏工作区下 recall sync 自动提交并推送；--manual 后恢复旧的显式提交语义；带 Ref 行的提交后记录 after_commit 被自动填为提交哈希；测试全绿。
- intent_status: confirmed
- intent_distilled_by: Claude (Fable 5)
- intent_distilled_at: 2026-08-11
- intent_traceability: INT-20260811-003 -> RULE-011, RULE-013 -> test:tests/test_git_sync.py -> VER-20260811-003

## 为什么做这个决策？

原 RULE-011 规定脏工作区绝不被自动提交，导致"已修改未提交"的窗口期没有任何
保护：此时意外删除或覆盖文件无法从 Git 恢复。用户明确决定把默认语义反转为
自动保存上传（用户不想手动触发上传），保留手动模式作为可选项。同时，决策
记录的 after_commit 此前靠人工回填，容易遗忘，记录到提交方向的追溯链会静默
断裂——这与 Recall "commit hash 关联 what/why" 的核心承诺矛盾。

## 决策过程

**方案 A**：保持手动语义，只加提醒（提示用户运行 --commit-message）——不满足
用户"默认自动"的明确要求。

**方案 B**：文件系统监听守护进程，保存即提交——真正的"保存即上传"，但引入
常驻进程、平台差异和噪音提交，远超当前单人 + AI 场景的需要（原则 8：无真实
消费者不引入临时复杂度）。

**方案 C**：`recall sync` 默认自动提交脏工作区（`recall.autoCommit`，init 默认
写 true，未设置视为 true），`--manual`/`--auto` 切换；post-commit hook 场景
绝不自动提交其他脏文件；同步流程顺带解析 HEAD 的 Ref 行回填 after_commit，
回填以内部提交落盘并用环境变量 RECALL_INTERNAL_COMMIT 防 hook 递归。

**选中方案与原因**：方案 C。在不引入常驻进程的前提下满足"默认自动、可切手动"；
hook 侧不提交是刻意保留的安全边界——否则任何一次部分提交都会把无关脏文件
卷进历史。局限性如实记录：自动保存的触发点是 recall sync 或 git commit，
不是编辑器保存事件。

## 影响范围

**修改的文件/模块**：
- `scripts/git_sync.py` - 自动保存提交（_autocommit_enabled + 默认开启）、
  backfill_after_commit（解析 Ref 行、只 add 被回填文件）、--auto/--manual 开关、
  内部提交递归防护、--disable 同时关闭 autoCommit
- `scripts/init_recall.py` - 初始同步注释更新（自动保存语义）
- `scripts/recall.py` - sync 帮助文本更新
- `tests/test_git_sync.py` - 6 -> 12 tests：自动保存、手动模式、hook 不提交、
  递归防护、回填与幂等
- `CLAUDE.md` / `SKILL.md` - 自动同步章节改写为自动保存语义；标准流程加第 5 步

**破坏性变更**：语义反转（用户确认）。此前脏工作区在 `recall sync` 下只告警不
提交；现在默认提交（消息 `chore(recall): 自动保存本地修改`）。旧行为通过
`recall sync --manual` 完整保留。post-commit hook 行为不变：仍然只同步已提交
历史，另加 after_commit 回填。

## 验证方式

`python -m unittest tests.test_git_sync tests.test_recall_cli`（20 tests OK）；
`python tests/test_audit_logic_map.py`（62 tests OK）；
`python scripts/audit_logic_map.py . --current-state` Static gate PASS；
提交本记录的 commit 带 Ref 行，hook 实测把本记录 after_commit 回填为提交哈希。

## 回滚方式

`git revert` 本次提交即可整体回退（连同 RULE-011 表述还原为 VER-20260811-002
版本）。仅想恢复手动语义而保留回填：运行 `recall sync --manual`（配置级回退，
无需改代码）。仅回退回填：删除 sync_repository 中 backfill_after_commit 调用
及对应测试。

## 经验与教训

默认值就是产品语义：`recall.autoCommit` 未设置时视为 true 是用户决定的一部分，
必须写进规则表而不是只藏在代码里。由自动化产生的提交（自动保存、回填）必须
有递归防护和最小暂存范围（绝不 add -A 回填文件之外的内容），否则 hook 链会
自我触发或把无关文件卷入历史。

## 关联

- current_logic: RULE-011, RULE-013
- proposal_id: none
- former_proposal_path: none
- immutable_record: VER-20260811-003
- decision_record_path: logic_version/records/logic_version-20260811-003-auto-save-sync.md
- related_adr: none
- code/tests: scripts/git_sync.py; scripts/init_recall.py; scripts/recall.py; tests/test_git_sync.py
- issue/commit/release: before commit:5afe9bb
