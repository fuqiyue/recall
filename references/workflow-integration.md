# 外部工作流适配

Recall 管理的是“当前代码应遵守什么、为何如此、变更尚未生效时如何协调、关闭后如何追溯”。它可以组合其他工具的工作流，但不复制其全部内容。

## 角色边界

| 工件 | 最适合承载 | Recall 如何使用 | 不应承担 |
|---|---|---|---|
| Codex Plan | 当前任务的实施步骤、影响范围和验证计划 | 在 `intent_source_refs` 引用；采纳的结论提炼到 CHG | 当前生效规则或永久决策记录 |
| Spec Kit / Kiro Specs | 需求、设计、任务分解及验收设计 | 保留完整 Spec；CHG 引用它并记录本次采纳的意图、约束和取舍 | 与 `logic_readme.md` 平行的当前代码逻辑副本 |
| Kiro Steering（product/tech/structure 等） | 长期产品背景、技术约束、结构导航 | 在根 `logic_readme.md` 声明其负责的范围后作为外部来源读取 | 未声明范围内的自动业务真源 |
| `logic_readme.md` | 当前已生效的代码行为、契约、代码地图和验证义务 | 只保留已生效的提炼结论及 VER/ADR 链接 | 活跃讨论、完整规格或原始请求 |
| `logic_change.md` | 未生效 CHG 的协调、意图提炼和方案选择 | 引用上游工件，记录当前提案版本 | 永久历史或第二份完整 Spec |
| `VER-*` / ADR | 已关闭变更的可追溯理由和长期约束 | 固化最终采纳的提炼、方案和证据 | 原始聊天、自动记忆或逐步思考 |
| Agent memory | 发现可能相关的历史、偏好或来源 | 当作线索，回到可验证来源 | 业务规则或决策权威 |

## 单一权威规则

对每个语义关注点指定一处权威位置，而不是要求所有内容都塞进一个文件：

- 产品需求/设计任务若由 Spec 管理，Spec 是该关注点的完整正文；Recall 只留引用和与运行逻辑有关的提炼。
- 长期产品或技术约束若由 Steering 管理，根 `logic_readme.md` 必须写明它的路径、负责范围和优先级；相同约束不再重复成两段正文。
- 当前运行逻辑、公共契约、代码锚点和验证义务仍由 `logic_readme.md` 管理。
- 活跃决策仍由 `logic_change.md` 管理；关闭后的原因由 `VER-*`/ADR 管理。

“一个关注点一处权威”不等于“整个项目只有一个文件”。它避免的是同一规则在 Plan、Spec、Steering 和 Recall 中分别被悄悄改写。

## 并发与治理边界

Recall 的根文档模型默认适合单人或低并发小团队。`logic_change.md` 可用 `TOPIC-ID` 把同类讨论和多个 CHG 集中管理，但主题不替代每个 CHG 的独立发布、验收和回滚边界。

- `personal`：允许同一人协调、实现和审查；用 Git/发布/外部存档引用保留可追溯性，不把文档字段当成权限控制。
- `collaborative`：需要真实分工时，根 `logic_readme.md` 与 `logic_change.md` 声明同一个 `governance_mode` 和 `governance_ref`。高风险 CHG 的通过性语义审查人与实施者分离，实际 PR/CI、分支保护、CODEOWNERS 或审批规则仍在外部系统执行。
- 协作模式用 `governance_evidence`、`governance_verification: verified`、`governance_verified_at` 记录责任人的控制核验；高风险 CHG 进入验证时再用 `governance_execution_ref` 指向本次 PR/CI/审批。Recall 只核对类型、日期和责任分离，不声称证明平台权限持续生效。
- 若多个作者频繁同时写账本、需要跨团队排队或组织级留痕，完整讨论和审批应由 Issue、Spec、PR 或变更系统承担；Recall 只引用它们，并保存当前 CHG 的可审计提炼。

## 接入步骤

1. 在 CHG 的 `intent_source_refs` 指向外部 Plan、Spec、Steering 或任务来源。
2. 写 `intent_digest`、`intent_non_goals`、`intent_constraints`、`intent_acceptance`，并标明 `intent_status`。没有给出的信息写 `not-specified`，不要猜测补全。
3. 若外部工件与当前 `logic_readme.md` 冲突，先核对已声明的权威范围和优先级。若更高优先级当前指令或该精确影响面的唯一权威没有直接给出唯一结论，就向当前用户或授权决策方列出新旧来源、具体矛盾、可行选项、主要影响和建议，取得明确选择后再更新同一 CHG 的 `proposal_revision`；代理不得自行选择哪一处覆盖另一处。可由代码、Schema 或运行证据客观核实的事实先调查。
4. 代码生效时，把当前规则更新到 `logic_readme.md`；把最终来源引用和提炼固化到 `VER-*`，需要长期跨范围约束时再创建 ADR。
5. 外部 Spec/Steering 后续变更不会回写旧 VER。它若影响当前规则，创建或更新新的 CHG 并重新核对基线。
6. 对需要保留历史的中等/高风险变更，为采纳的意图分配 `INT-*`，并维护 `INT -> RULE -> test:<path#anchor> -> VER` 链；简单修复不为格式强行建链。
7. `TOPIC-ID` 结束时，在最后一个相关 CHG 的 `VER-*` 保存共享背景、约束、讨论引用和最终结论，再从活跃账本移除主题。
8. 外部来源或依赖更新属于事件复查信号；同时用 `interval`/`due` 让规则具备可计算的新鲜度。只有真实重新核验后才更新 `last_verified`，不得靠编辑动作续期。

## Plan 模式对接

各家代理的计划模式（Claude Code plan mode、Codex plan 等）共同特征：只读探索 → 产出计划 → 用户批准 → 执行，计划本身是一次性产物，会话结束即丢。Recall 是计划的输入源和产出归宿：

| Plan 模式环节 | Recall 对应物 |
|---|---|
| 规划前的只读探索 | 默认上下文读取：`logic_readme.md`（含功能意图与用户流程）→ `logic_change.md` → `recall route` 命中的领域文档 → 代码/测试 |
| 计划中的需求拆解与影响范围 | 中等/高风险通道要求的修改计划；CHG 的 `raw_request` / `decomposition` / `fit_analysis` |
| 用户批准计划 | 该 CHG 当前 `proposal_revision` 的决策确认（`decision_ref: plan-approved:YYYY-MM-DD`） |
| 计划执行完成 | 更新 `logic_readme.md` 受影响章节；`compact`/`full` 固化 `VER-*` |

时序约束：规划阶段只读，不写 `logic_change.md`；批准后、动代码前，按通道落盘——`simple` 直接实施不留痕，`medium`/`high` 先把计划的拆解结论写入 CHG 再实施。批准的 plan 是决策确认的载体，不是当前制度；会话结束后能追溯的只有 CHG/VER 中的提炼。

## 典型组合

```text
用户任务 / Codex Plan / Spec / Steering
             |  stable reference
             v
CHG: intent digest + impact + proposal revision
             |  accepted and verified
             +--> logic_readme: current effective behavior
             +--> VER / ADR: immutable rationale and source digest
```

对简单隔离修复，不必制造 CHG 或外部链接；只读取相关规则、代码和测试，并在交付中说明 `docs_impact`。当请求、约束或方案需要跨会话复用、协调或审计时，才建立上述关联。
