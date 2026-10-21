# VER-20261020-001: 工作路径、文件地图与任务产物治理

## 记录控制
- version_id: VER-20261020-001
- version_slug: logic_version-20261020-001-workspace-task-governance
- status: effective
- immutable: true
- date: 2026-10-20
- change_id: CHG-20261020-001
- proposal_revision: 1
- changed_by: Codex
- recall_route: high
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: 本机实际测试与目录只读盘点
- governance_verification: recorded
- governance_verified_at: 2026-10-20
- before_commit: f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-20
- decision_ref: user:2026-10-20 本轮五项认可及任务监督需求
- proposal_commit_or_blob: user:2026-10-20 本轮请求；需求原文及拆解保存在下节

## 为什么做这个决策？
项目根定位不约束输出路径，旧残留提示跳过Git忽略文件；按领域分散的任务正文和独立过程资料难以监督临时产物。
- raw_request: 用户认可将当前项目文件夹作为根目录并建立工作路径约定；明确加入.gitignore不等于清理、非交付物删除；过程资料简洁集中；临时代码单独保存在“临时-具体功能”文件夹；核对台账与实际文件。算法识别content等功能目录和资产库等数据目录，在logic_domains中提供目录/文件简明说明；logic_change独立任务文件夹，同任务修改更新同一文件，监督任务和临时文件，logic_domains记录现行规则，并防止教材/vscode3/教材/.work式嵌套目录。
- decomposition: 增加受限目录盘点、项目相对路径校验、独立任务账本发现与路由、任务内产物台账和实际文件核对；同步技能/模板/规则及兼容测试；以教材只读盘点验证。
- fit_analysis: 扩展INT-20260816-006/008/010与INT-20260903-001/002；复用领域owned_paths、共享账本发现、next/index/audit/validate与历史记录；新任务使用独立正文，兼容旧账本，不移动消费项目既有文件。

## 决策过程
| 方案 | 收益与代价 | 决定 |
|---|---|---|
| 复用领域登记/公报/共享发现，增加任务文件与有界实物核对 | 保持旧任务可读，新增正文不重复；路径检查需调用方使用 | selected |
| 只加文字规则或把所有旧文件移入.work | 无法验证忽略文件是否删除，仍可能重复正文 | rejected |
| 全库扫描、立即迁移全部旧任务并自动删除 | 大数据项目成本高且无法仅凭目录名判断所有权 | rejected |

## 影响范围
新任务一文件，根公报与next/status/route/validate/audit共享发现；旧根/领域任务和旧logic_temp兼容。新领域readme-only，规则与任务职责分离。inventory只按真实名称、类型与owned_paths生成可重建文件地图，数据目录限制深度。path核项目相对路径，workspace核任务台账与实际临时文件，包含忽略文件、空目录及预算边界，不自动删除。

## 验证方式
最终329项unittest：328通过、1项因本机符号链接权限跳过；另有模拟junction保护用例通过。覆盖真实CLI、published个人模板、新readme-only领域、旧logic_temp兼容、任务索引/路由/正式审查、Git忽略产物与空目录、虚假清理和扫描预算。audit、validate、index、workspace关案核对、UTF-8技能格式及git diff --check通过；validate仍报告既有未提交/未跟踪文件和历史commit缺失，未伪造关联。

教材项目只读盘点content和资产库共3项（content/test-fixtures和两个学制目录），归属缺口明确标待登记，不读取全量素材。本次复查旧vscode3/教材嵌套路径已不存在，本轮未删除它；同类故障保留测试。Recall自身生成3份可重建文件地图。消费者为完整scripts部署及技能入口；未执行远端CI、消费项目迁移或业务运行操作。
- semantic_review_state: passed
- semantic_review_ref: 本机真实CLI与unittest输出；自审核路径边界、所有账本消费者、忽略文件处理和清理顺序

## 回滚方式
仅撤销本轮新增模块/测试与各调用方、文档增量，保留开始时已有的未提交修改。已迁移的活跃任务如需回退，移动正文回原账本并重建根公报；不复制为两份，不改已归档历史。

## 临时产物
- logic_temp_cleanup: 2026-10-20；启动时旧working台账1个文件及其任务目录已删除，5个新模块/测试pyc已删除；测试夹具由TemporaryDirectory清理。本轮未创建运行临时代码目录。workspace --closing CHG-20261020-001核对findings为空。保留源码/测试/参考/3份文件地图和本决策；未动开始时已有未提交改动及旧产物。

## 关联
- current_logic: logic_readme.md#当前制度; logic_domains/toolchain/logic_readme.md
- proposal_id: CHG-20261020-001
- code/tests: scripts/workspace_paths.py; scripts/workspace_inventory.py; scripts/workspace_check.py; tests/test_workspace.py
