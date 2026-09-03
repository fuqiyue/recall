# logic_readme.md 模板

只在项目根使用：本模板是一级文档（宪法），承载全局规则、功能意图与用户流程层、领域目录（范围登记表）、INV 与有效决策索引，用范围登记、稳定锚点和章节组织模块；不是讨论记录、需求池或历史档案。二级文档（部门法）用[领域文档模板](logic-domain-template.md)，且只能是已登记的 `logic_domains/<domain>/` 领域文档（RULE-018）；领域内部的规则行与代码地图行写在领域文档，不在本文件重复。

代码地图负责说明当前结构、边界和验证入口；本文件的规则与决策引用负责说明当前应遵守什么、为什么如此。代码地图不能替代 ADR 或版本记录，决策记录也不能替代当前代码地图。

目录：文档控制与归属；当前制度与代码地图；功能意图与用户流程；代码/数据边界；消费者与兼容；验证与维护。

~~~markdown
# <项目名称> Logic

## 文档控制

- doc_id: LOGIC-<唯一ID>
- module_id: MOD-ROOT
- scope: .
- scope_path: .
- parent: none
- parent_module_id: none
- membership: in-system
- scope_type: root
- layer: runtime-code
- module_doc_policy: paired
- status: active | transitional
- owner: <self/团队/角色；发布态必须明确>
- governance_mode: personal | collaborative
- governance_ref: <实际版本控制/发布/审批控制的稳定引用；personal 也应指向 Git 或外部存档>
- governance_evidence: <可核验的控制证据；例如 branch-protection:<ref>;ci:<ref>;approval:<ref>;git:<ref>>
- governance_verification: verified | recorded | unavailable | not-applicable
- governance_verified_at: YYYY-MM-DD | none
- effective_from: YYYY-MM-DD | event-driven
- last_verified: YYYY-MM-DD
- review_trigger: interval:90d; event:release,api-schema-change,dependency-major
- source_of_truth: <代码、Schema、策略或外部系统的权威位置>
- source_decisions: <有效 ADR/VER ID；根级汇总，无则 none>
- intent_summary: <已确认且长期有效的用户/产品意图摘要；不粘贴原始提示词；未知填 unknown>
- intent_sources: <支持此摘要的有效 VER/ADR；或已声明范围的外部 product/tech/structure 来源；没有填 none>
- decision_validity: valid | under-review | uncertain
- validity_evidence: <最近核验、用户确认或有效 ADR；未知填 unknown>

## 目标与边界

- 负责：<本范围必须解决的问题>
- 不负责：<明确非目标>
- 上级制度：<继承的全局约束>
- 允许的例外：<根制度授权的例外和 ADR；没有填 none>

## 范围登记与归属

- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: <项目内受治理的路径或模式>
- child_policy: inherit
- data_owner: <运行数据/外部系统的负责人；不适用填 none>
- registry_status: registered | pending-review | retired

“范围登记表”是新文件、新文件夹是否属于体系的第一依据，也是本项目的领域目录：每个 `in-system` 且 `doc_policy: paired` 的非根行产生一个领域的 `logic_domains/<domain>/logic_readme.md` + `logic_change.md`（RULE-018，至少一个）；其余行只定位代码和责任边界，不产生二级文档。

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key/ordinary | ... | ... | [VER-...](logic_version/records/logic_version-...md) / [ADR-...](logic_version/decisions/ADR-...md) / none | 用户确认/法规/ADR/VER | code/test/runtime/部署证据 | valid/under-review | YYYY-MM-DD | ... |

只写已生效内容。不写原始提示词、AI 推断、备选方案、开放问题、实施步骤或未来状态。`规则等级` 只能是 `key` 或 `ordinary`：`key` 包括公共契约、跨模块边界、持久化数据/迁移、兼容策略、安全或权限规则、业务不变量，以及引入长期复杂度后的非显然取舍；其 `决策记录` 必须是指向根 `logic_version/records/` 下 `VER-*` 或根 `logic_version/decisions/` 下 ADR 的具体链接。`ordinary` 可写 `none`，但仍须保留可审计的 `why`。`logic_change.md` 只记录活跃变更，关闭后会移除，不能作为已生效关键规则的唯一决策记录。`决策依据` 说明“为什么应当这样”；`验证证据` 说明“当前是否做到了”。测试通过不能单独变成规则的决策依据。

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| path/to/file / symbol-or-route | source/runtime-code | ... | ... | ... | ... | yes/no | ... |

避免依赖易漂移的行号。生成物、依赖、历史档案和临时目录不作为制度真源，但必须登记其生成来源、消费者和重建/清理方式。

- coverage_policy: governed-boundaries | registry-every-folder
- membership_policy: root-registry-first
- layer_policy: <本项目采用的层分类和边界>
- version_root: logic_version/
- temp_root: logic_version/working/
- 子范围路由：<名称、职责、受影响章节锚点和代码路径>
- unmapped_paths: <尚未纳入治理的路径及原因；没有填 none>

### 范围登记表（根文档必填）

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | ... | active |

| MOD-<NAME> | logic_domains/<domain> | in-system | domain/runtime-code | paired | [<name>](logic_domains/<domain>/logic_readme.md) | [changes](logic_domains/<domain>/logic_change.md) | self | active |
| MOD-... | path/to/module | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-example) | [active changes](logic_change.md) | ... | active |
| EXT-... | path/to/vendor | dependency | dependency | inherited | none | none | ... | active |

`doc_policy` 取值：根行固定 `paired`；领域行（`scope_type/layer: domain/runtime-code`）
也是 `paired`——两列分别链接 `logic_domains/<domain>/logic_readme.md` 与同目录
`logic_change.md`，领域文档字段见[领域文档模板](logic-domain-template.md)（RULE-018）。
不单独成领域的小范围用 `inherited`（正文在根文档或所属领域文档的 `<a id="scope-...">`
锚点小节，`logic_readme` 列链接带锚点）。`readme-only`（子文档 + `logic_change: none`）
仅作存量兼容，工具仍接受但不再推荐，新拆分一律建 paired 领域。`logic_domains/`
下未登记的文档为平行真源违规（INV-001/INV-002）。尚未补全文档的存量模块登记
`status: pending-docs`（见项目接入流程）。

`registry-every-folder` 只要求每个纳入体系的目录在本表中有记录和稳定锚点，不因此产生二级文档（二级文档只来自 paired 领域行）；机器检查该策略时需要完整目录扫描。`governed-boundaries` 只登记有独立职责、契约、数据或风险边界的范围。

新增文件或文件夹时，先更新/核对此表：落在某领域 `owned_paths` 内的，补该领域文档的代码地图；形成新职权边界的，按 RULE-018 先在本表登记领域再建其两份文档，不创建未登记的二级文档。不单独成领域的 in-system 子范围使用显式稳定锚点，例如：

<a id="scope-mod-example"></a>
### MOD-EXAMPLE: <范围名称>

- scope_path: path/to/module
- 适用规则与不变量：<RULE/INV ID>
- 代码地图入口：<路径、符号或路由>

## 功能意图与用户流程

用户视角层，与代码地图（系统视角）互补：记录每个面向用户的功能服务什么目标、位于哪条操作流程的哪一步，以及不可破坏的操作直觉。按条目模块化维护：一个功能一行 `INT-*`，一条流程一个 `FLOW-*` 块，一条直觉约束一行 `UXI-*`；新增、合并或移除功能时只增删对应条目，不重写整节。

### 功能意图登记

| intent_id | 功能入口 | intent（服务的用户目标，一句话） | 流程位置 | 关联规则 | 代码锚点 | last_verified |
|---|---|---|---|---|---|---|
| INT-YYYYMMDD-NNN | <命令/界面/API/文档入口> | ... | FLOW-001#2 | RULE-... | path/to/file; path/to/other | YYYY-MM-DD |

`intent_id` 使用 `INT-YYYYMMDD-NNN` 格式（日期为条目首次登记日），与 `intent_traceability` 的 `INT-*` 共用同一编号空间和格式；需要追溯链的中等/高风险变更直接引用本表条目。不要使用无日期的短编号（如 INT-001），审计与追溯链只识别完整格式。"代码锚点"列填实现该功能的文件路径（多个用 `;` 分隔，可填 none），支撑反向查询 `recall query intent <INT-ID>`；validate 会检查路径存在性，文件改名/移动时同步更新本列。

### 用户流程

- FLOW-001: <流程名（用户要完成的任务）>
  1. <用户动作> → INT-...
  2. <用户动作> → INT-...

步骤按用户实际操作顺序排列；一个功能可出现在多条流程中。

### 操作直觉约束

- UXI-001: <不可破坏的操作直觉>；来源：<VER/ADR/用户确认>；影响：INT-...

维护规则：新增用户可见功能前，必须能用本节说明它属于哪条流程的哪一步、与相邻功能的关系（复用/替代/新增哪个 INT），以及是否触碰 UXI 条目；说不清位置视为会改变方案的模糊点，按核心原则 5 向用户澄清。该分析的产出写入对应 CHG 的"需求拆解与融入分析"。

## 责任记录约定

- 范围登记表的 `owner` 表示当前维护责任，不表示操作系统、Git、分支或部署权限。
- `logic_change.md` 的 `owner` 表示 CHG 协调责任，`changed_by` 表示实际修改人或代理。
- `decision_confirmed_by` 与 `decision_ref` 记录用户/决策方确认的具体议案版本；`semantic_reviewed_by` 与 `semantic_review_ref` 记录实施后的代码语义审查。两者都不等于权限授予。
- `governance_mode: personal` 是单人或低并发小团队默认模式：允许 `semantic_reviewed_by: self`，但 `governance_ref` 必须能追溯到 Git、发布记录或外部存档；`immutable: true` 只声明追加式历史规则，真正的防改写来自该外部控制。
- `governance_evidence`、`governance_verification` 和 `governance_verified_at` 是对外部治理控制的可审计核验记录；`verified` 表示责任人已在该日期检查引用，不能证明平台权限永远有效。`governance_mode: collaborative` 仅在需要真实分工时使用，必须提供 PR/CI、分支保护、CODEOWNERS 或外部审批证据；高风险 CHG 的通过性语义审查人不得等于 `changed_by`，也不得写 `self`。
- 个人项目不需要先建立审批角色或 `AUTH-*` 登记；确认来源可以是自己、用户、issue 或稳定会话引用，但必须绑定 `proposal_revision`。这里的“自己”只指具备项目决策权的人明确作出的选择，当前执行代理不能把自己的建议记为用户确认。多人项目如需组织级权限、并行队列或审批留存，应使用外部系统；Recall 只保存可审计引用。

`coverage_policy`、`membership_policy`、`layer_policy`、`version_root`、`temp_root`、完整范围登记表和责任记录约定只在本文件维护。

文档策略约束：

- `paired` 用于项目根与已登记领域：根行两条链接指向根 `logic_readme.md` 与根 `logic_change.md`，领域行指向 `logic_domains/<domain>/` 下的两份文件；每个项目至少一个领域行。
- 其余子范围标为 `inherited`，不得有本地 `logic_readme.md` 或 `logic_change.md`；其制度和议案入口是所属领域文档或根文件。external/generated/dependency 可写 none。

## 代码、生成物与运行数据边界

| path/pattern | artifact_class | layer | read/write | environment | source_of_truth | safe_to_edit | safe_to_rebuild | retention/sensitivity |
|---|---|---|---|---|---|---|---|---|
| ... | source/config/test-fixture/generated/runtime-data | ... | ... | local/staging/prod | ... | yes/no | yes/no | ... |

运行代码、前期处理、生成物和运行数据必须分栏；不能因为文件扩展名相同就把数据目录当成代码模块。数据库、缓存、日志和上传物只记录 schema、路径、校验值和恢复流程，不把大文件嵌入本文件。

## 数据与控制流

<用简短步骤或 Mermaid 描述当前关键流向，标出读写边界和失败路径。>

## 消费者与公共契约

| 契约/数据 | 生产者 | 真实消费者 | 环境 | 当前兼容要求 | 证据 |
|---|---|---|---|---|---|
| ... | ... | ... | local/staging/prod | ... | code/test/runtime/... |

### 旧行为消费者

| 旧行为/版本 | 仍在消费的调用方或数据 | 环境 | 证据 | 退出条件/负责人 |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

没有已确认的旧行为消费者时写 `none + 证据`，不要凭空假设 V1 必须兼容。

## 不可破坏约束

- INV-001: <约束>；来源：<ADR/测试/用户确认>；验证：<测试或检查>

## 兼容与迁移制度

- 对象：<数据库/API/文件/URL/用户行为/内部接口>
- 当前版本关系：<说明实际对象，不只写 V1/V2>
- 持久化状态：<数据库/文件/缓存/浏览器存储>
- 当前策略：<replace/migrate/dual-read/dual-write/adapter/deprecate>
- 旧行为消费者与移除条件：<链接上表或写 none；包含负责人和最晚复查/移除日期>
- transitional 结束条件：<仅 status=transitional 时填写>
- 回滚能力：<当前可用的恢复路径>

## 安全、性能与运维

- 权限/隐私：...
- 性能/并发：...
- 部署/配置：...
- 日志/监控/告警：...

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | ... | ... | ... | test path/CI policy |

每行只填一个 `test_level`：unit、component、contract、integration、e2e、migration 或 runtime；同一规则需要多个级别时拆成多行。这里只保留当前仍适用的验证义务、入口和权威证据位置。变更前/后对比和一次性结果放 `logic_change.md`、`logic_temp.md` 或最终 version 摘要；存在测试文件不等于测试通过，未执行必须写原因。

## 有效决策索引

| decision_ref | 类型 | 状态 | 关联规则/范围 | 摘要 | last_verified |
|---|---|---|---|---|---|
| [VER-...](logic_version/records/logic_version-...md) | VER | effective | RULE-... / ... | ... | YYYY-MM-DD |
| [ADR-...](logic_version/decisions/ADR-...md) | ADR | active/transitional | RULE-... / ... | ... | YYYY-MM-DD |

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：<none 或 CHG-...；修宪议案正文在根账本，领域议案正文在所属领域账本，根账本公报每项一行>

这里只放链接和 CHG-ID，不复制议案正文。

## 当前限制

- <已经确认且仍然存在的限制；不确定项放 logic_change.md 或 Recall Brief>

## 修改检查清单

- [ ] 是否触及上游/下游契约？
- [ ] 是否触及持久化数据或已部署行为？
- [ ] 是否仍满足所有 INV 条目？
- [ ] 是否需要议案、ADR、迁移、回滚或弃用计划？
- [ ] 新增或修改的关键规则是否已经链接到具体 ADR/VER，而不是只留下 why 或活跃 CHG？
- [ ] 是否已更新根范围登记、关联代码地图、测试和历史索引？
- [ ] 是否先完成代码逻辑、数据边界和现有实现可并入性分析？
- [ ] 是否在修改后生成/补齐测试案例并审核前后结果？
- [ ] 是否存在未被更高优先级指令或精确唯一权威直接裁定的新旧需求矛盾，或会改变方案的未知项；如有，是否已向用户/授权决策方列明来源、冲突、选项和影响并记录答案？
~~~

维护规则：

- 仅保留已经生效的当前知识；尚未生效的内容进入所属账本（修宪案入根 logic_change.md，领域事项入领域账本），已结束内容进入 `logic_version/records/`。`intent_summary` 只保留长期有效的提炼结果，并经 `intent_sources` 追溯；不要复制原始聊天、Plan 或 Spec。
- 功能对目标环境实际启用时，在同一受控发布变更中更新本文件、必要的 `VER-*` 和索引，再从 `logic_change.md` 关闭对应 CHG；不能让已激活行为长期只留在议案中。
- 一句 why 用于理解规则目的，不等同于过程性思考；关键规则的完整取舍链接具体 ADR 或 VER。变更期间先在 `logic_change.md` 记录，关闭前再固化为 VER，不能让已关闭 CHG 成为唯一依据。
- last_verified 表示已对照代码、测试或运行环境核实，不能仅因编辑文档而更新。`review_trigger` 必须包含 `interval:<Nd|Nw|Nm|Ny>` 或 `due:YYYY-MM-DD`；审计器会将 `last_verified` 与每条规则的 `last_reviewed` 视为到期基线，并在过期时报告漂移。
- 发现新请求与旧需求、现行制度、活跃议案或已确认意图冲突时，先报告漂移并建立议案；若没有更高优先级指令或该精确影响面的唯一权威直接裁定，就列明新旧来源、具体矛盾、选项、影响和建议，向用户或授权决策方取得明确选择。代理不得自行决定哪一方覆盖另一方，也不要把猜测直接写成现行规则。
- `scope_path` 为 `.`，`canonical_readme` 和 `canonical_change` 必须指向根文件；目录移动只更新范围登记和代码锚点。
