# VER-20260907-001: AI 自主审查后完成开发交付

## 记录控制

- version_id: VER-20260907-001
- version_slug: logic_version-20260907-001-ai-delivery-closure
- status: effective
- date: 2026-09-07
- change_id: CHG-20260907-001
- before_commit: d681d75b6853031c12a3e0a97cd52083164b945b
- after_commit: 714e147
- decision_ref: user:2026-09-07 本任务
- confirmed_proposal_revision: 1

## 为什么做这个决策？

个人模式允许自审，但旧清单把晋升绑定到目标环境启用；EduAI 样例还混入真人体验等待。本机技能入口是旧版。

- raw_request: user:2026-09-07 本任务：AI 自主审核后完成并进入 logic_readme，人工交付后发现问题另开议案。
- decomposition: 明确 AI 验证与自动晋升；区分交付和上线；取消默认人工验收等待；同步技能入口。
- fit_analysis: 新增 INT-20260907-001，补充 FLOW-002 的验证与收尾，保留必要测试和真实发布证据。

## 决策过程

明确 AI 验证后主动晋升关案、交付与实际上线分开陈述，人工后测发现问题新开 CHG。

维持旧流程会继续产生人工等待；新增状态或自动关案脚本无法证明真实审查通过且增加复杂度。采用最小文档修订，复用既有状态与机器校验；本机安装入口指向维护源，避免再次漂移。

## 影响范围

SKILL.md、根制度、生命周期、治理模式、readme/change 模板；本机 C:/Users/fu/.agents/skills/recall/SKILL.md 入口。

不修改 EduAI 的业务代码、议案状态或原始 HTML。它的 52 条活跃项只是本次诊断来源，未逐案核实或批量关案。

## 验证方式

AI 对入口、规则和模板做语义核对，确认用户当前授权覆盖本次选择。复用已有审计器，没有新增状态枚举或改动 Python 实现。

2026-09-07：源码技能与本机安装入口均通过 quick_validate.py（使用 Python UTF-8 模式及临时 PyYAML）；recall audit --json 的 Static gate PASS，current_integrity 为 0；validate 无错误，仍提示本次未提交/未跟踪交付物和 after_commit 待回填。HTML 静态检查确认 8 个来源/导航链接可达且 ID 唯一。浏览器 URL 策略拒绝本地 HTML，桌面/窄屏视觉核验未完成。

用户已于 2026-09-07 明确授权删除本次工作目录（含临时校验依赖），但自动审批系统仍以执行策略阻止删除。用户随后要求发布到 GitHub 并同步本机技能；发布按当前成果进行，清理继续作为独立未完成项如实保留。

## 回滚方式

按本次文件差异恢复文档；已发布的本记录用新 correction 说明回退，不静默改写。若迁移本机维护源，同步修正安装入口绝对路径。

## 经验与教训

状态或 HTML 只描述证据，不能代替证据；通过后必须由 AI 执行剩余收尾，不能只汇报“可关案”。

## 关联

- current_logic: logic_readme.md
- linked_rule_ids: RULE-025
- intent_traceability: INT-20260907-001 -> RULE-025 -> references/change-lifecycle.md -> VER-20260907-001
- logic_temp_cleanup: pending；用户已授权删除，执行策略仍阻止；待限制解除或手动清理，CHG 暂留 promoting
