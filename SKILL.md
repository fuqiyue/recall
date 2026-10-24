---
name: recall
description: 在修改、规划、诊断或审查会影响项目逻辑的代码或文档时，恢复现行规则、用户意图与未完任务，按领域读取上下文并完成可验证收尾；普通无逻辑影响的局部编辑无需使用。
metadata:
  version: "2026.10.25"
---

# Recall

Recall 保存设计理由、约束和剩余工作；Git 保存代码历史。现行规则在所属 `logic_readme.md`，新任务正文在 `logic_changes/<任务>/logic_change.md`，根 `logic_change.md` 监督全项目任务，已结束的决定在根 `logic_version/`。

## 定位与读取

先确定本轮要处理的项目。用户指定的路径或项目优先；维护 Recall 自身时使用技能维护源，执行消费项目任务时使用消费项目根。当前工作目录和同名文档只提供定位线索。目标仍有实质歧义时先做只读调查并澄清，确定目标后再写入。

1. 完整读取目标项目根 `logic_readme.md`，恢复现行规则、功能意图和领域目录。缺失时按[项目接入](references/project-onboarding.md)处理，不把代码推断写成已确认意图。
2. 读取根 `logic_change.md`；接手或选择下一项时运行 `recall next [--json]`，再核对相关正文的需求来源、剩余动作和证据时点。
3. 运行 `recall route <任务ID、路径、关键词或 INT-ID>`；任务 ID/路径按声明范围准确找规则，其他相关任务先看摘要，必要时再展开正文（兼容旧领域 change）。CLI 在目标项目根执行；命中清单是阅读范围，不是实施授权。
4. 核对受影响代码、真实消费者、测试与必要运行证据。当前引用、冲突或兼容问题需要时，才按 ID 读取对应 VER/ADR。

本文的 RULE 编号属于 Recall 技能规则。消费项目的业务制度与一次性授权始终由该项目文档承载，不写入通用技能入口。

用户指定的项目文件夹作为根；命令显式设置 cwd，输出使用根相对路径且只拼接一次。目录不清楚先 `recall inventory`；输出前用 `recall path` 核对，临时代码与输出放 `.work/临时-具体功能`（或项目声明的 scratch_root）。详见[工作路径与任务](references/workspace-tasks.md)。

## 需求与实施

授权与需求记录见 RULE-014/017/027；按需操作见[任务上下文](references/task-context.md)。

- 区分想法、已决定但未开始的任务和本次实施授权。`code-derived` / `inferred` 保留为待核实来源；只有项目认可的用户来源可驱动实施。
- 已有授权在同一任务内有效。计划获准后直接承接必要拆解并实施；只有实质需求冲突、未决长期选择或新增高风险外部操作，才说明来源、影响、选项与建议并请求裁决。
- 需要 CHG 时先查活跃案，相同/相近需求能统一验收与收尾则合并原正文；保留 `raw_request`、`decomposition`、`fit_analysis`、影响、验证与回滚。当前状态只写在顶部，旧计划精简进[修订记录](references/workspace-tasks.md#多轮修订)；合并方法见该参考，不另建过程正文。承接待办后移除原行。
- 接手或阻塞时记录下一步、依据和真实缺口，不编造来源、日期、确认或验证结果。

## 按影响选择深度

| 通道 | 适用 | 必要工作 |
|---|---|---|
| simple | 局部隔离、意图明确，不触及 public/persisted/security 契约或活跃案 | 直接修改并适度验证；通常不建 CHG/VER，按实际影响同步文档 |
| medium | 触及契约路径但语义不变，或多个相关文件且无未决长期选择 | 按 RULE-014/020 在任务正文记录计划、影响、验证和产物台账；规则/行为变化保留精简 VER |
| high | 改变对外语义、迁移、安全边界或长期结构 | 核真实消费者与必要历史，比较最小修改、结构修改和保持现状；明确迁移/回滚，记录已有授权，未决关键选择先裁决，保留完整 VER |

治理字段按[治理模式](references/governance-modes.md)选择；完整表单和 `formal-review` 仅用于用户明确要求的正式审查。

## 交付与收尾

按 RULE-018/019/020/025 完成同一次交付：核实际 diff → 语义审查与必要验证 → 更新所属 readme、代码地图和验证入口 → 清理并核对本次临时产物 → 将需求与修订记录归入同一 VER 并核索引 → 移除已结束 CHG 并核公报；删除受阻时按[集中待清理](references/workspace-tasks.md#删除受阻的集中待清理)核对能否保全移动，移动也受限则仅在历史索引登记原位待清理；通过归档/身份/指纹核验后退出活跃队列。无 CHG 的 simple 修改沿用简短交付汇报。

提前创建的 VER 是未归档草稿，保留关联 CHG；清理结果写实后才定稿，定稿后只追加。规则正文、活跃正文和历史各保留唯一位置。VER 只追加；人工交付后的新问题另开案，简单修复仍走 simple。静态通过、源码交付和生产启用分别记录，不把未部署或未测环境写成已验收。任何工具都不自动删除用户文件；处置本次产物后在汇报中列明。

每轮处理本轮产物，任务完成后清空本任务临时文件及空目录，加入 `.gitignore` 不算清理。台账区分临时物、运行数据和正式证据，保留项写依据与退出条件。关案前 `recall workspace --closing CHG-ID` 对照实物，分开报告本任务和全局问题；复用代码/必要证据先晋升正式位置。旧 `logic_temp.md` 兼容，新任务只维护正文内台账。

引入兼容层等长期复杂度前，先核真实消费者、退出条件和回滚路径。Git 初始化、同步与推送责任见 RULE-010/011/013。

## 命令与参考

`recall` 代表命令入口；Windows 使用维护源 `recall.bat`，Linux/macOS 使用 `recall.sh`，在目标项目根调用。CLI 需要 Python 3.11+ 与完整 `scripts/`。CLI 不可用时沿用读取顺序，并记录未执行的检查及其影响。

```bash
recall next [--json]          # 当前任务与下一步；只读
recall route <目标>           # 应读领域；只读
recall index                 # 核根公报；差异退出 1
recall index --write         # 显式写入派生公报与根 CHG 计数
recall inventory [目录]       # 有界盘点；--write 更新领域文件地图
recall workspace --task CHG-ID [--round 01] # 本任务/本轮核对，全局问题另列
recall path <相对路径>        # 输出前核路径；拒绝越界/重复根
recall workspace --closing CHG-ID # 按真实文件核对关案条件
recall status                # 行动摘要与项目/Git 状态
recall validate              # 一致性与残留提示
recall audit                 # 现行文档静态门
recall audit --formal-review # 仅正式审查
```

以上只有 `index --write` 与 `inventory --write` 写入派生文档；不推送、不删除。按任务读取下列参考：

| 任务 | 参考 |
|---|---|
| 待办、接手、公报 | [任务上下文](references/task-context.md) |
| 目录盘点、任务文件、临时代码与清理 | [工作路径与任务](references/workspace-tasks.md) |
| CHG 晋升、归档、关案 | [生命周期](references/change-lifecycle.md) |
| 文档创建、拆分、压缩 | [文档模型](references/document-model.md)、[领域模板](references/logic-domain-template.md) |
| 治理字段与长度限制 | [治理模式](references/governance-modes.md)、[字段词汇](references/field-vocabulary.md) |
| 必要记录 | [CHG](references/logic-change-template.md)、[VER](references/logic-version-template.md)、[临时台账](references/logic-temp-template.md) |
| 首次接入、普通变更、中断恢复实例 | [三个操作示例](references/practical-examples.md) |
| 接入项目、Git 同步 | [项目接入](references/project-onboarding.md)、[Git 同步](references/git-sync.md) |
| 对接 Plan/Spec/Steering | [外部工作流](references/workflow-integration.md) |
| 持久解释文档 | [explainers HTML](references/explainers.md)（RULE-026；简单问答无需建页） |
