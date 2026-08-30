# Recall Skill for Claude

修改、规划、诊断、审查项目逻辑，或解释"为什么这样设计"前：

1. 先读根 `logic_readme.md`（现行制度：规则、代码地图、功能意图/用户流程层），再读 `logic_change.md`（活跃议案），然后读相关代码、测试和必要的运行证据；`logic_version/` 历史仅在现行文档引用或需要追溯时按 ID 读取
2. 动手前先按 `simple` / `medium` / `high` 三通道路由：medium 先给计划、影响范围与验证方式；high 另需消费者与历史决策核查、迁移/回滚对比，并经用户确认后实施
3. 新请求与现行规则、活跃议案或已确认意图实质矛盾，或模糊点会改变范围/语义/兼容/数据安全时：列明新旧来源、矛盾点、选项、影响与建议，经用户裁决后再动受影响部分（可用 `recall conflicts` 辅助检测）
4. 代码改动后更新并运行相关测试，报告结果与 `docs_impact`；现行规则、锚点、契约或验证入口实际变化时在同一变更中更新根 `logic_readme.md`
5. 完整工作流语义在 recall 技能（SKILL.md）；`.claude/` 只放工具配置，不放业务制度、议案、ADR 或历史

首次接入运行 `recall init`（建 Git 管道并默认启用自动同步）；日常命令见 `recall help`，语义权威在 logic_readme.md 的规则行与 SKILL.md（RULE-019）。

## 机器可读标记

- recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md
- recall_change_effective: false
- recall_business_truth: project-root-current-logic-docs
- recall_history_root: <project-root>/logic_version
- recall_agent_config_root: <project-root>/.claude
