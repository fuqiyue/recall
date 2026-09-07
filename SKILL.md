---
name: recall
description: 在修改、规划、诊断或审查项目逻辑时，恢复当前规则、用户意图与未完任务；按领域读取关键上下文，保留决策理由并完成交付收尾。
---

# Recall

帮助有能力的模型理解需求、现状和剩余工作。优先记录会影响下一步判断的事实、来源、约束与验证结果；分析方法和实现步骤由模型按任务选择。代码历史由 Git 保存，Recall 保存设计理由。

## 先恢复上下文

1. 读项目根 `logic_readme.md` 全文（宪法：当前规则、用户意图、领域目录）。
2. 读根 `logic_change.md`（待办、修宪议案、全项目公报）。需要接手或选择下一项时运行 `recall next`，再读相关正文；视图不代表授权。
3. 运行 `recall route <路径或关键词>`，只读命中领域的 `logic_readme.md` 和 `logic_change.md`。
4. 核对相关代码、消费者、测试和运行证据。历史仅按当前引用、冲突或兼容问题读取对应 VER/ADR。

项目尚未接入时见 [接入流程](references/project-onboarding.md)。文档缺失不能冒充已恢复设计原因。

## 记录需求与任务

执行语义见项目宪法 RULE-014/017/018/027；操作见 [任务上下文](references/task-context.md)。

- 想法和已决定但尚未开始的任务，按需写在所属账本的待办区；保留需求来源和重要上下文。讨论意向与本次实施授权分别理解。
- 开始实施时按下面的变更通道工作；已有授权直接沿用。需要 CHG 时承接待办的来源与完成条件，再移除待办行，避免双写。
- 大目标按能单独验证价值的成果组织；必须一起保持不变量的修改留在同一 CHG，用步骤清单拆解。
- 接手最需要的是剩余动作与依据；阻塞时补充原因、解除动作、执行者与日期或事件复查时机。缺信息据实说明，不为填满字段编造事实。

## 按影响选择深度

| 通道 | 适用 | 必要工作 |
|---|---|---|
| simple | 局部隔离、不触及 public/persisted/security 契约或活跃案，意图明确 | 直接修改与适度验证；通常无需 CHG/VER，文档实际变化时同步更新 |
| medium | 触及契约路径但语义不变，或多个相关文件且无未决长期选择 | 简述计划、影响和验证；按 RULE-014/020 记录 CHG 需求拆解与收尾台账，行为/规则变化保留精简 VER |
| high | 对外语义、迁移、安全边界或长期结构选择 | 核实真实消费者与相关历史，比较最小修改/结构修改/保持现状，说明迁移回滚；记录当前方案的已有用户授权，未决关键选择再咨询，保留完整 VER |

风险决定分析和验证深度。普通开发不使用完整表单；`formal-review` 仅在用户明确要求正式审查时使用。计划获准后、动代码前，将必要的需求拆解落入 CHG；无需让用户重复批准已经明确的决定。

## 保留的关键边界

- 当前规则只在所属 readme；待办与活跃议案只在所属 change；历史 VER 只追加。规则正文不复制到入口、模板或代理私有目录（RULE-018/019）。
- 用户来源与模型推断分清；实质性需求冲突或未获决定的长期选择，说明来源、选项和建议后再请求裁决（RULE-014）。工具静态通过不能替代语义审查或真实授权。
- 根据实际 diff 判断文档影响，在同一交付更新相关规则、地图与验证入口。引入兼容层等长期复杂度前核实真实消费者、退出条件和回滚。
- 按 RULE-025 完成 AI 语义审查与必要验证，通过后继续晋升、归档和关案；生产未验证据实注明。后续人工反馈另开案，简单修复仍走简单通道。
- 按 RULE-020 清理本次临时产物并报告处置；工具不自动删除用户文件。

## 常用工具

```bash
recall next [--json]       # 当前任务、下一步与阻塞上下文；只读
recall index               # 从 CHG 正文生成并核对根公报，差异退出 1
recall index --write       # 显式更新根公报表与根 CHG 正文计数
recall route <目标>         # 按领域导入上下文
recall status              # 行动摘要 + 项目/Git 状态
recall validate            # 一致性与残留提示
recall audit               # 当前状态静态检查
recall audit --formal-review # 明确要求时才用完整审查
```

CLI 需要 Python 3.11+ 与完整 `scripts/` 目录；只读命令不推送、不删除。Git 初始化、同步与推送责任见 RULE-010/011/013 和下表。

## 按需读取

| 任务 | 参考 |
|---|---|
| 待办、下一步、公报自动生成 | [任务上下文](references/task-context.md) |
| CHG 状态、交付、归档 | [生命周期](references/change-lifecycle.md) |
| 文档创建或拆分 | [文档模型](references/document-model.md)、[领域模板](references/logic-domain-template.md) |
| personal 与协作/正式审查字段 | [治理模式](references/governance-modes.md)、[字段词汇](references/field-vocabulary.md) |
| 填写必要记录 | [CHG](references/logic-change-template.md)、[VER](references/logic-version-template.md)、[临时台账](references/logic-temp-template.md) |
| 接入项目或 Git 同步 | [项目接入](references/project-onboarding.md)、[Git 同步](references/git-sync.md) |
| 对接 Plan/Spec/Steering | [外部工作流](references/workflow-integration.md) |
| 需要持久解释文档 | [explainers HTML](references/explainers.md)（RULE-026；简单问答无需建页） |
