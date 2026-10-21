# 文档模型

权威语义见根 RULE-018/019/020/029；本文说明职责和目录，操作见[工作路径与任务](workspace-tasks.md)。

```text
<project-root>/
|-- logic_readme.md                      # 全局现行规则、意图、领域与工作路径约定
|-- logic_change.md                      # 全项目任务公报，可选待办
|-- logic_domains/<domain>/logic_readme.md # 领域现行规则、代码地图、测试入口
|-- logic_domains/<domain>/file_map.md     # 可重建的真实文件名索引
|-- logic_changes/<task>/logic_change.md   # 同任务唯一正文：需求、计划、进度、修改、产物
|-- .work/临时-具体功能/                  # 临时代码和输出，完成后删除
|-- explainers/                          # 用户需要的可重建HTML说明
|-- AGENTS.md / CLAUDE.md                 # 短阅读入口
`-- logic_version/
    |-- index.md                         # 历史索引
    |-- records/                         # 已结束的不可变决策记录
    |-- decisions/                       # 可选ADR
    |-- working/<version_slug>/          # 仅兼容旧logic_temp；关案删除
    `-- backups/                         # 确有交付用途的受控证据
```

根目录是用户指定的当前项目文件夹；现有功能和数据目录保持原位。至少登记一个领域，小项目可只有 core。新领域用 `readme-only`；旧 `paired` 文档继续可读，不为迁移机械生成或复制文件。

## 现行规则

根 `logic_readme.md` 保存跨领域规则、INT/FLOW/UXI、范围登记表、不变量、工作路径约定及最近有效决策入口。领域 readme 保存 `owned_paths` 内的现行规则、稳定代码锚点和验证入口。意图来源只能来自真实用户或已确认依据；文件扫描的描述标为推断。

规则正文只在所属 readme；RULE/INT 编号全项目唯一。每条规则保留一句why、决策链接与复核日期。根有效索引只留最近3条，全量在 `logic_version/index.md`；移出最近索引前保留规则反链。未实施方案不写成现行行为。

文件地图通过 `recall inventory --write` 生成，记录文件/目录、简要类型与领域归属；数据目录只列上层，明确预算和未深入范围。它不是制度，也不能把算法猜测变成业务事实。每次只对相关目录更新，阅读时按需打开。

模板：[根readme](logic-readme-template.md)、[领域文档](logic-domain-template.md)。

## 任务监督

根 `logic_change.md` 是项目负责人视图，以 `proposal_path` 指向任务文件；`recall index --write` 派生公报。新任务无论是否跨领域都写到 `logic_changes/<任务>/logic_change.md`；一个文件一个CHG，正文用scope/affected_scopes关联规则范围，不在任务目录另建readme制度。

同任务持续更新同一文件，以[修订表](workspace-tasks.md#多轮修订)区分执行轮次与方案版本，保留变化原因和当前下一步。计划、进度、交接及产物台账合并；不再创建PLAN2、STATUS、HANDOFF_CURRENT等重复正文。正式交付报告按用户需要生成并登记用途。

medium/high按[CHG模板](logic-change-template.md)保全需求三字段、验证/回滚及产物台账。simple通常无需CHG。所有活跃任务effective:false；完成后按[生命周期](change-lifecycle.md)更新规则、对照真实文件清理、定稿历史，再移除正文和公报。

旧根和领域账本继续识别。迁移某任务时保留CHG-ID，将唯一正文移入任务文件并更新公报、依赖及草稿回链；不要双写。旧logic_temp沿用到迁移或关闭，新的任务只在正文维护一张产物台账。

## 读取、历史与代理入口

读取顺序：根readme → 根change → `recall route`命中的领域与任务 → 相关代码/测试/运行证据；仅需要时按ID读取历史。

`logic_version/records/`保留为什么、取舍、影响、验证、清理事实，以及从任务搬入的简短修订表；不保存代码快照、逐轮全文或整套任务副本。历史只追加，后续纠正另建记录。模板见[VER](logic-version-template.md)。

AGENTS/CLAUDE只给短阅读路由；.agents/.claude只存代理配置，不放业务规则或任务历史。根规则优先于领域；当前系统、开发者和用户指令优先。

文档长度目标与硬上限见[字段词汇](field-vocabulary.md)；explainers是用户需要的展示层，操作见[解释文档](explainers.md)。
