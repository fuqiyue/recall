# 变更与决策生命周期

只有真正需要决策的变更才走完整流程。简单、局部且没有实质方案选择的修复不必创建 CHG 或历史记录。

**一旦创建了需要决策的 CHG，确认和不可变记录不能省略。**

## 状态机

```
draft → awaiting-decision → implementing → verifying → promoting → [关闭]
  ↓            ↓                 ↓            ↓           ↓
blocked ←────┴─────────────────┴────────────┴───────────┘
```

任何阶段发现基线失效、依赖改版/阻塞/关闭、冲突未解决，都转 `blocked` 或回到 `awaiting-decision`。

简单修复或无决策门槛修改可跳过 `awaiting-decision`：`draft -> implementing -> verifying -> promoting -> [关闭]`。

### 状态含义

| 状态 | 含义 |
|---|---|
| `draft` | 草稿，方案尚未定稿 |
| `awaiting-decision` | 等待用户或授权决策方选择当前 `proposal_revision` |
| `implementing` | 确认已获得且基线有效，正在实施 |
| `verifying` | 代码已写，正在核对语义、测试、消费者 |
| `promoting` | 验收通过，正在晋升：写所属 `logic_readme.md`（宪法或领域）、创建 `VER-*`、更新索引、关闭 CHG。这是合法的过渡状态 |
| `blocked` | 依赖失效、冲突未解决、外部阻塞，或发现基线已变 |

## 晋升窗口（promoting 状态）

系统实际上已经 `deployed-active`，但 CHG 还没关闭 — 这个间隙可能因会话中断、上下文压缩而停留。

`promoting` 状态记录这个过渡期。它不是长期稳定态，而是用于支持中断恢复的合法工作态。

### 晋升检查清单

CHG 进入 `promoting` 时建立以下清单：

- [ ] 目标环境已启用
- [ ] 所属 `logic_readme.md`（宪法或领域）最终规则已写入，旧规则已删除
- [ ] `VER-*` / ADR 已创建
- [ ] `logic_version/index.md` 索引行已添加
- [ ] 关键规则已链接到 `VER-*` / ADR
- [ ] `logic_temp.md` 工作区产物台账已清零（`delete` 项均已删除、无 `pending`），随后整个 working 目录已删除（RULE-020）
- [ ] 可以从所属账本移除 CHG 条目，并删除根账本公报中的对应行

全部完成后执行关闭动作：从所属 `logic_change.md` 移除该 CHG，并删除根账本公报行。

### 中断恢复

会话恢复时若发现 CHG 停在 `promoting`，读取其清单，继续未完成项。

## 完整生命周期（9 步）

### 1. 写议案

在所属账本（领域事项写该领域的 `logic_domains/<domain>/logic_change.md`，修宪案写根 `logic_change.md`；RULE-018）同一 `CHG-ID` 内写出，并在根账本的全项目活跃议案索引加一行（领域 CHG 的 `proposal_path` 指向领域账本锚点）：

- `proposal_revision`
- 当前事实、方案取舍
- 精确 `authority_surfaces`、`based_on`
- 依赖/冲突、运行暴露、历史保留级别、`docs_impact`

`governance_mode: personal` 只强制前两项加 `recall_route`/`changed_by`，其余字段缺则不查、写则照查（RULE-023；最小块见 references/logic-change-template.md）。实质性修改方案、影响面、基线或协调关系时递增版本。

### 2. 获得确认

用户或授权决策方确认该版本，记录：

- `decision_confirmed_by`
- 确认日期
- 来源
- `confirmed_proposal_revision`

版本不一致时确认失效，回到 `awaiting-decision`。

### 3. 重新核对基线

实施前以及晋升前重新核对：

- `based_on`
- 依赖版本
- 冲突解决
- 同一影响面的并行 CHG

任何不一致都使确认失效，转为 `awaiting-decision` 或 `blocked`。

确认不是代码审查，也不代表已生效。

### 4. 实施

实施已确认且基线仍有效的方案，记录实际运行环境与开关暴露。

### 5. 代码语义审查

对实施后的当前代码做语义审查，独立记录：

- 审查人
- 证据
- 结果

它核对当前代码、调用方、Schema、测试结果和运行证据是否支持已确认方案。

不能用用户确认、测试文件存在或静态审计通过替代。

失败或关键未知项回到议案处理，不得晋升。

### 6. 进入晋升（promoting）

CHG 转为 `promoting` 状态，建立晋升检查清单。

### 7. 创建历史记录

对使用决策检查点或 `history_retention: full` 的 CHG 创建完整 `logic_version/records/logic_version-YYYYMMDD-NNN-<scope>.md`；对 `history_retention: compact` 的中等行为/规则变更创建精简记录。

两者都更新 `logic_version/index.md`，长期跨范围约束按需创建 ADR。

创建记录时复制最终 `intent_traceability`，并把 CHG 的 `raw_request`/`decomposition`/`fit_analysis` 原样搬入记录（需求保全：CHG 关闭后即删除，需求拆解必须落在不可变记录中，否则只剩 git 考古可查）；若关闭的是主题最后一个 CHG，同时固化四个 `topic_*` 共享快照字段。同议题多方案竞争时，落选方案的需求原文与否决原因随胜出记录的方案分析归档；曾独立立案的落选 CHG 创建 `status: rejected` 的精简 `VER-*` 并同样搬运三字段。

协作治理还要记录已核验的控制证据和本次执行引用。

### 8. 更新现行制度

审查和验收通过后，在启用目标环境前或同一受控发布变更中：

- 把实际规则写入所属 `logic_readme.md`（全局规则、INT 层、登记表、INV 入宪法；领域规则、代码地图、测试入该领域文档）
- 删除被替代的规则
- 让每条生效关键规则直接链接到其 `VER-*` 或 ADR——这是生效 VER 在现行文档中的长期落点；宪法"有效决策索引"只滚动保留最近 3 条（RULE-002），把最旧的一行挤出去前确认它已被某条规则行链接

不能把 `deployed-active` 留给未关闭 CHG。

### 9. 关闭 CHG

最后从所属账本移除已结束条目，并删除根账本公报中的对应行。移除前先核对 `logic_temp.md` 的工作区产物台账已清零（RULE-020：`delete` 项全部执行、无 `pending`），再删除整个 working 目录，并把结果写入 `VER-*` 的 `logic_temp_cleanup`。

回滚时先让所属 `logic_readme.md` 反映实际恢复状态，再记录回滚结论和后续限制。

## CHG 边界

CHG 表达可独立确认、验收、发布和回滚的原子决策边界。

若两个改动必须一起实施才能保持同一不变量，合并为同一 CHG；独立 CHG 才允许并行。

不要用相互依赖的条目模拟一个变更。

## TOPIC-ID

`TOPIC-ID` 只在活跃期组织共享讨论。

关闭主题最后一个相关 CHG 时，把主题共享背景、共享约束、稳定讨论引用和最终结论写入该 CHG 的 `VER-*`；不能只保留 `topic_id`，否则主题从 `logic_change.md` 移除后会失去共同理由。

主题可集中同类改动的来源、共享约束和开放问题，不产生第二份规则或替代 CHG 的原子边界。
