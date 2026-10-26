# Recall Skill for Claude

修改、规划、诊断、审查项目逻辑，或解释"为什么这样设计"前：

1. 先读根 `logic_readme.md`（宪法：全局规则、领域目录、功能意图/用户流程层），再读根 `logic_change.md`（修宪议案 + 全项目活跃议案索引），然后 `recall route <任务ID、目标路径或关键词>` 先读命中领域的现行 `logic_readme.md`，再读相关任务的 `logic_change.md`（兼容旧领域账本）及相关代码、测试和必要的运行证据；历史仅在任务明确要求查阅时按 ID 读取（RULE-003）
2. 动手前先按 `simple` / `medium` / `high` 三通道路由：medium 先给计划、影响范围与验证方式；high 另核真实消费者与跨域契约、比较迁移/回滚；记录已有授权，只有未决关键选择才请求裁决
3. 新请求与现行规则、活跃议案或已确认意图实质矛盾，或模糊点会改变范围/语义/兼容/数据安全时：列明新旧来源、矛盾点、选项、影响与建议，经用户裁决后再动受影响部分（可用 `recall conflicts` 辅助检测）
4. 代码改动后更新并运行相关测试，报告结果与 `docs_impact`；现行规则、锚点、契约或验证入口实际变化时，在同一变更中增量更新所属 `logic_readme.md` 并保持完整现行表述（领域规则改领域文档，全局规则/意图层/登记表改宪法）
5. 完整工作流语义在 recall 技能（SKILL.md）；`.claude/` 只放工具配置，不放业务制度、议案、ADR 或历史

首次接入运行 `recall init`（建 Git 管道并默认启用自动同步）；自动同步未启用的仓库，提交后须自行推送、不得让本地长期领先远端（RULE-010）。日常命令见 `recall help`，语义权威在 logic_readme.md 的规则行与 SKILL.md（RULE-019）。

## 机器可读标记

- recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md
- recall_change_effective: false
- recall_business_truth: project-root-current-logic-docs
- recall_history_root: <project-root>/logic_version
- recall_agent_config_root: <project-root>/.claude
