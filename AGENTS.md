# Recall Skill for Codex

修改、规划、诊断、审查项目逻辑，或解释"为什么这样设计"前：

1. 先读根 `logic_readme.md`（宪法：全局规则、领域目录与功能意图/用户流程层）
2. 再读根 `logic_change.md`（修宪议案 + 全项目活跃议案索引）
3. 运行 `recall route <任务ID、目标路径或关键词>`，先读命中领域的现行 `logic_readme.md`，再读相关任务的 `logic_change.md`（兼容旧领域账本）
4. 然后读相关代码、测试和必要的运行证据；历史仅在任务明确要求查阅时按 ID 读取（RULE-003）

代理自审按自身能力执行，但先以上述上下文校验设计意图。

不要把业务制度、议案、ADR 或历史记录复制到 `.agents/` 目录。

## 机器可读标记

- recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md
- recall_change_effective: false
- recall_business_truth: project-root-current-logic-docs
- recall_history_root: <project-root>/logic_version
- recall_agent_config_root: <project-root>/.agents
