# VER-20260907-002: 解释文档统一交付 explainers HTML

## 记录控制

- version_id: VER-20260907-002
- version_slug: logic_version-20260907-002-html-explainers
- status: effective
- date: 2026-09-07
- change_id: CHG-20260907-002
- before_commit: d681d75b6853031c12a3e0a97cd52083164b945b
- after_commit: _待填写_
- decision_ref: user:2026-09-07 本任务
- confirmed_proposal_revision: 1

## 为什么做这个决策？

EduAI 已用独立 HTML 解释产品与项目状态，Recall 缺少统一的按需输出约定。

- raw_request: user:2026-09-07 本任务：参照 EduAI explainers，需要解释性文档时在 explainers 生成对应 HTML 查看。
- decomposition: 增加按需 HTML 产物约定、来源和快照语义、交付链接与查看要求，并制作本次流程说明。
- fit_analysis: 新增 INT-20260907-002，补充 FLOW-003 的面向用户解释输出，不创建平行制度。

## 决策过程

需要解释性文档时在当前项目 explainers 交付可直接打开的 HTML，简单问答不强制建页。

只写聊天难以复看；引入生成平台/构建依赖超出需求。选择单文件 HTML、来源链接与快照边界，复用当前项目样式；状态页从声明的同一账本范围重算，历史示例标注为示例。

## 影响范围

SKILL.md、根制度、references/explainers.md、document-model/readme 模板、README.md、explainers/ai-delivery-closure-20260907.html。

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
- linked_rule_ids: RULE-026
- intent_traceability: INT-20260907-002 -> RULE-026 -> references/explainers.md -> VER-20260907-002
- logic_temp_cleanup: pending；用户已授权删除，执行策略仍阻止；待限制解除或手动清理，CHG 暂留 promoting
