# Recall Skill for Codex

修改、规划、诊断、审查项目逻辑，或解释"为什么这样设计"前：

1. 先读根 `logic_readme.md`（宪法：全局规则、领域目录与功能意图/用户流程层）
2. 再读根 `logic_change.md`（修宪议案 + 全项目活跃议案索引）
3. 运行 `recall route <目标路径或关键词>`，只读命中领域的 `logic_domains/<domain>/logic_readme.md` + `logic_change.md`
4. 然后读相关代码、测试和必要的运行证据

代理自审按自身能力执行，但先以上述上下文校验设计意图。

不要把业务制度、议案、ADR 或历史记录复制到 `.agents/` 目录。

## 机器可读标记

- recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md
- recall_change_effective: false
- recall_business_truth: project-root-current-logic-docs
- recall_history_root: <project-root>/logic_version
- recall_agent_config_root: <project-root>/.agents
