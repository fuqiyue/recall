# Recall Skill Logic

## 文档控制

- doc_id: LOGIC-RECALL-001
- module_id: MOD-ROOT
- scope: .
- scope_path: .
- parent: none
- parent_module_id: none
- membership: in-system
- scope_type: root
- layer: runtime-code
- module_doc_policy: paired
- status: active
- owner: self
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08
- effective_from: 2026-08-07
- last_verified: 2026-08-16
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: SKILL.md, logic_readme.md
- source_decisions: VER-20260808-001, VER-20260808-002, VER-20260811-001, VER-20260811-002, VER-20260811-003, VER-20260816-001, VER-20260816-002, VER-20260816-003
- intent_summary: 为 AI 提供项目设计逻辑的回忆机制，记录"为什么这么设计"而非代码快照，避免上下文膨胀
- intent_sources: 用户访谈 2026-08-07
- decision_validity: valid
- validity_evidence: 用户确认 2026-08-07

## 目标与边界

- 负责：记录项目设计决策的逻辑推理、关键取舍、影响分析；提供"为什么这么设计"的回忆能力
- 不负责：代码版本管理（由 Git 负责）、完整代码快照、原始对话记录、详细实现细节
- 上级制度：无
- 允许的例外：none

## 范围登记与归属

- canonical_readme: logic_readme.md
- canonical_change: logic_change.md
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_version/, references/, scripts/, tests/, recall.bat, recall.sh, .gitattributes, AGENTS.md, CLAUDE.md, README.md
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why（仅一句可审计摘要） | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key | 逻辑回档而非代码回档 | 避免上下文膨胀，保持文档简洁可读 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | SKILL.md 章节 | valid | 2026-08-08 | self |
| RULE-002 | key | logic_readme.md 只保留最新规则 | 删除已废弃内容，保持单一真相源 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | 当前文档 | valid | 2026-08-08 | self |
| RULE-003 | key | 历史记录保存设计逻辑 | 记录为什么、取舍、影响，不记录代码快照 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | logic_version/ | valid | 2026-08-08 | self |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |
| RULE-005 | key | 批处理入口必须纯 ASCII + CRLF | cmd.exe 按字节偏移定位命令，多字节字符加 LF 换行会错行执行注释片段 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | .gitattributes + recall.bat 实测 | valid | 2026-08-08 | self |
| RULE-006 | key | 脚本调用外部命令必须用 argv 列表，禁止 shell=True | 多行 commit message 会被 shell 截断，用户输入可注入命令 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | init_recall.py / link_ver_git.py 注入测试 | valid | 2026-08-08 | self |
| RULE-007 | key | 嵌套项目根不计入本项目审计 | 自带 `scope: .` 的子目录属于另一个项目，按模块审计会用其 module_id 顶掉真实根文档 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | audit_logic_map.py 静态门 | valid | 2026-08-08 | self |
| RULE-008 | ordinary | CLI 必须可非交互运行，且重定向下不崩 | CI、容器和 AI 代理环境没有 tty；Windows 重定向后 stdout 走 ANSI 代码页 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | 空 stdin 与重定向实测 | valid | 2026-08-08 | self |
| RULE-009 | ordinary | 校验脚本的字段名以 references/ 模板为准 | schema 漂移会让检查静默失效或报假错误 | [VER-20260808-002](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) | 复现验证 | validate.py 记录发现测试 | valid | 2026-08-08 | self |
| RULE-010 | key | `recall init` 默认启用仓库级 Git 自动同步并安装受管理的 post-commit hook | 让已提交的 Recall 逻辑和代码及时进入配置的远端，减少本地历史与远端漂移 | [VER-20260811-001](logic_version/records/logic_version-20260811-001-git-auto-sync.md) | 用户要求 | git_sync.py + hook 集成测试 | valid | 2026-08-11 | self |
| RULE-011 | key | `recall sync` 默认自动保存：脏工作区自动提交后同步（`recall.autoCommit`，`--manual` 切换手动）；提交前列出文件清单并对未跟踪新文件单独提示（排除私人文件用 .gitignore）；post-commit hook 场景绝不自动提交其他脏文件 | 用户要求默认自动保存上传；`git add -A` 会打包一切脏文件，用户必须先看到会上传什么，避免私人文件被推上远端 | [VER-20260816-002](logic_version/records/logic_version-20260816-002-traceability-repair.md) | 用户要求 | git_sync.py 单元测试 | valid | 2026-08-16 | self |
| RULE-012 | key | 决策记录文件名统一为 `logic_version-YYYYMMDD-NNN-*.md`，创建方与所有发现方共用同一正则 | create_ver/status/validate/list 曾各用一套命名，记录对部分工具静默不可见 | [VER-20260811-002](logic_version/records/logic_version-20260811-002-cli-interface-repair.md) | 复现验证 | tests/test_recall_cli.py | valid | 2026-08-11 | self |
| RULE-013 | key | 提交后自动回填决策记录的 after_commit，双通道定位记录：commit message 的 Ref 行 + 本次提交内规范命名的记录文件；识别新旧两种占位符（`- after_commit:`/`- commit:`）且只按整个字段行匹配（叙述文字中引用的占位符不回填）；无法回填时打印警告而非静默跳过；内部提交通过环境变量防止 hook 递归 | 只认 Ref 行时自动保存提交（无 Ref）永不触发回填；裸子串替换曾把记录叙述文字里引用的占位符改成哈希，污染不可变记录正文 | [VER-20260816-002](logic_version/records/logic_version-20260816-002-traceability-repair.md) | 复现验证 | tests/test_git_sync.py（含端到端与字段行锚定） | valid | 2026-08-16 | self |
| RULE-014 | key | logic_readme 维护功能级"功能意图与用户流程"层（INT/FLOW/UXI 按条目模块化，intent_id 统一 `INT-YYYYMMDD-NNN` 完整格式，登记表含代码锚点列支撑反向查询）；medium/high CHG 在实施前记录需求拆解与融入分析（raw_request/decomposition/fit_analysis），归档时三字段原样搬入 VER 记录（需求保全）；plan 模式产出批准后、动代码前按通道落盘 | 功能级产品逻辑此前无处沉淀，AI 每会话从代码反推意图；CHG 归档即删除，三字段不搬入不可变记录则需求拆解只剩 git 考古可查 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md) | 用户确认 | 本文件"功能意图与用户流程"节 + scripts/validate.py | valid | 2026-08-16 | self |
| RULE-015 | ordinary | `recall validate` 覆盖一致性对账：VER 三处登记（records/、index.md、有效决策索引）与撞号、INT/FLOW/UXI 引用有效性与代码锚点存在性、medium/high CHG 三字段、VER 需求保全三字段（change_id != none 时）、字段行占位符未回填、RULE 重复仅按定义行判定；post-commit hook 对"含代码变更但未触及 logic 文档"的提交打印非阻断漂移提醒 | 文档是代码理解的持久缓存，缓存腐烂与登记缺失此前无任何检测，静默失效是本系统反复出现的失败模式 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md) | 复现验证 | scripts/validate.py + tests/test_git_sync.py | valid | 2026-08-16 | self |
| RULE-016 | key | 项目接入采用模块化渐进：接入时只建根骨架（文档控制、范围登记表、代码地图顶层入口、访谈式 INT/FLOW 初稿），存量模块登记 `pending-docs`；此后仅在新项目开始使用时或用户单独要求时补全对应模块；AI 代码扫描产出标 `code-derived`，意图层必须经用户确认后落盘 | `recall init` 只建 Git 管道，文档内容从哪来此前无流程；一次性全量扫描在存量项目不可行，未经确认的 AI 推断意图会污染真源 | [VER-20260816-003](logic_version/records/logic_version-20260816-003-semantic-link.md) | 用户确认 | references/project-onboarding.md + SKILL.md 接入章节 | valid | 2026-08-16 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | 关联测试 |
|---|---|---|---|---|---|---|---|
| SKILL.md | source/runtime-code | Recall skill 主入口，定义核心原则和使用方式 | AI 读取 | 指导 AI 行为 | SKILL.md | yes | none |
| logic_readme.md | source/runtime-code | 当前生效的规则和代码地图（唯一真相源） | AI 读取 | 当前制度 | logic_readme.md | yes | none |
| logic_change.md | source/runtime-code | 活跃的修改记录（未生效） | AI 读取/写入 | 修改议案 | logic_change.md | yes | none |
| logic_version/records/ | source/runtime-code | 历史决策记录（逻辑回档） | AI 按需读取 | 设计逻辑回忆 | VER-*.md | no | none |
| logic_version/index.md | source/runtime-code | 决策记录索引 | AI 按需读取 | VER-* 列表 | logic_version/index.md | yes | none |
| references/ | source/runtime-code | 模板文件和参考文档；字段名的权威来源 | AI 按需读取 | 文档模板 | 模板文件 | yes | none |
| recall.bat | source/runtime-code | Windows CLI 入口；探测 python/py/python3 后转发 | 命令行参数 | 子命令输出与退出码 | recall.bat | yes | none |
| recall.sh | source/runtime-code | Linux/macOS CLI 入口；同上 | 命令行参数 | 子命令输出与退出码 | recall.sh | yes | none |
| .gitattributes | source/runtime-config | 固定 *.bat 为 CRLF、*.sh 为 LF | Git 检出 | 换行符 | .gitattributes | yes | none |
| scripts/recall.py | source/runtime-code | CLI 调度器；转发到各子命令 | 子命令与参数 | 退出码 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/audit_logic_map.py | source/runtime-code | 审计脚本：检查文档结构、唯一性、依赖、密度 | 项目根路径 | 审计报告与静态门退出码 | 脚本文件 | yes | tests/test_audit_logic_map.py |
| scripts/validate.py | source/runtime-code | 一致性校验：RULE/CHG/VER 与 Git 状态 | 项目根路径 | 验证报告 | 脚本文件 | yes | none |
| scripts/init_recall.py | source/runtime-code | 首次初始化：Git 仓库、身份、.gitignore、首次提交 | CLI 参数或环境变量 | 初始化结果 | 脚本文件 | yes | none |
| scripts/git_sync.py | source/runtime-code | 配置 Git 自动同步策略、安装受管理 hook、自动保存提交、回填 after_commit、拉取变基并推送 | CLI 参数、仓库 Git 配置、远端 | 同步结果与退出码 | 脚本文件 | yes | tests/test_git_sync.py |
| scripts/create_ver.py | source/runtime-code | 按模板创建 VER-* 决策记录（规范文件名取号） | 描述与 scope | 记录文件 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/link_ver_git.py | source/runtime-code | 关联查询：文件/提交 ↔ 决策记录；intent 反向查询（意图 → 规则 → 记录 → 代码锚点） | 文件路径、commit 或 INT-ID | 关联报告 | 脚本文件 | yes | tests/test_recall_cli.py |
| scripts/detect_conflicts.py | source/runtime-code | 规则间与议案-规则冲突的启发式检测 | logic_readme/logic_change | 冲突报告与退出码 | 脚本文件 | yes | tests/test_recall_cli.py |
| tests/test_audit_logic_map.py | test/test-fixture | 审计脚本测试套件 | unittest | 测试结果 | 测试文件 | yes | python tests/test_audit_logic_map.py |
| tests/test_git_sync.py | test/test-fixture | Git 自动同步行为测试 | unittest/mock | 同步断言 | 测试文件 | yes | python -m unittest tests.test_git_sync |
| tests/test_recall_cli.py | test/test-fixture | CLI 胶水层接口一致性冒烟测试 | unittest | 接口断言 | 测试文件 | yes | python -m unittest tests.test_recall_cli |
| references/examples/audit-repro-legacy/ | test/test-fixture | 审计复现夹具；自带 `scope: .`，按嵌套项目根排除 | 审计脚本读取 | 复现场景 | 夹具文件 | yes | none |

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code 层
- version_root: logic_version/
- temp_root: logic_version/working/
- 子范围路由：无（单一根文档）
- unmapped_paths: agents/ (Codex 配置), .agents/ (代理私有目录), .claude/ (代理私有目录), logic_version/backups/ (归档快照)

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-TEMPLATES | references/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-templates) | [active changes](logic_change.md) | self | active |
| MOD-HISTORY | logic_version/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md#scope-mod-history) | [active changes](logic_change.md) | self | active |

<a id="scope-mod-templates"></a>
### MOD-TEMPLATES: 模板与参考文档

- scope_path: references/
- 适用规则与不变量：RULE-009, INV-001, INV-002
- 代码地图入口：references/（模板文件是字段名的权威来源）

<a id="scope-mod-history"></a>
### MOD-HISTORY: 历史决策记录

- scope_path: logic_version/
- 适用规则与不变量：RULE-001, RULE-003, INV-003, INV-004
- 代码地图入口：logic_version/records/、logic_version/index.md

## 功能意图与用户流程

用户视角层，与代码地图（系统视角）互补；新增或调整用户可见功能前先对照本节做融入分析（RULE-014）。

### 功能意图登记

| intent_id | 功能入口 | intent（服务的用户目标） | 流程位置 | 关联规则 | 代码锚点 | last_verified |
|---|---|---|---|---|---|---|
| INT-20260816-001 | logic_readme 功能意图与用户流程层 | AI 从文档恢复功能级产品逻辑与用户流程，无需重扫代码库 | FLOW-002#1 | RULE-014 | logic_readme.md | 2026-08-16 |
| INT-20260816-002 | recall init | 一条命令完成 Git + Recall 接入，无需手动配置 | FLOW-001#1 | RULE-010 | scripts/init_recall.py | 2026-08-16 |
| INT-20260816-003 | 文档三件套阅读（SKILL/logic_readme/logic_change） | AI 在修改前恢复设计上下文，不从代码反推意图 | FLOW-002#1 | RULE-001..004 | SKILL.md | 2026-08-16 |
| INT-20260816-004 | recall new | 修改前留下"为什么改"的决策记录骨架 | FLOW-002#3 | RULE-003, RULE-012 | scripts/create_ver.py | 2026-08-16 |
| INT-20260816-005 | recall sync | 一条命令保存并同步全部进度，无需手写 Git 序列 | FLOW-001#3, FLOW-002#5 | RULE-011, RULE-013 | scripts/git_sync.py | 2026-08-16 |
| INT-20260816-006 | recall status / recall list | 快速了解系统当前状态与最近决策 | FLOW-003#1 | RULE-012 | scripts/recall.py; scripts/link_ver_git.py | 2026-08-16 |
| INT-20260816-007 | recall query file/commit/intent | 双向追溯：从代码定位"为什么改"，从功能意图定位"要改哪里" | FLOW-003#2 | RULE-013, RULE-014 | scripts/link_ver_git.py | 2026-08-16 |
| INT-20260816-008 | recall validate | 确认文档、记录与 Git 状态一致 | FLOW-003#3 | RULE-009 | scripts/validate.py | 2026-08-16 |
| INT-20260816-009 | recall conflicts | 新需求与现行规则矛盾时提前暴露，交用户裁决 | FLOW-004#1 | none | scripts/detect_conflicts.py | 2026-08-16 |
| INT-20260816-010 | 项目接入流程（references/project-onboarding.md） | 存量/新项目模块化建立文档初稿：接入时建根骨架，按触发时机逐模块补全 | FLOW-005#2 | RULE-016 | references/project-onboarding.md | 2026-08-16 |

编号使用 `INT-YYYYMMDD-NNN`，与 CHG/VER 的 `intent_traceability` 链共用同一编号空间与格式（登记日期为条目首次登记日）。"代码锚点"列支撑反向查询 `recall query intent <INT-ID>`（意图 → 规则 → 决策记录 → 文件）；validate 检查锚点路径存在性。

### 用户流程

- FLOW-001 首次接入：1. recall init → INT-20260816-002；2. 配置远端（可选）；3. recall sync → INT-20260816-005
- FLOW-002 日常修改：1. 读文档 → INT-20260816-001, INT-20260816-003；2. 判定通道并修改代码；3. recall new（medium/high）→ INT-20260816-004；4. git commit（带 Ref 行）；5. recall sync（hook 回填 after_commit）→ INT-20260816-005
- FLOW-003 追溯审查：1. recall status/list → INT-20260816-006；2. recall query → INT-20260816-007；3. recall validate → INT-20260816-008
- FLOW-004 冲突澄清：1. recall conflicts → INT-20260816-009；2. 在 logic_change.md 标注；3. 用户裁决后按通道实施
- FLOW-005 项目接入（文档初稿）：1. recall init → INT-20260816-002；2. 建根骨架 + 意图访谈（存量模块登记 pending-docs）→ INT-20260816-010；3. 按触发时机（新项目使用时/用户单独要求时）逐模块补全 → INT-20260816-010

### 操作直觉约束

- UXI-001: 用户不手写 commit message，sync 自动保存；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-002: 一条命令完成一个用户目标，不要求用户记忆多步 Git 序列；来源：用户确认 2026-08-07；影响：INT-20260816-002, INT-20260816-005
- UXI-003: hook 与自动化绝不提交用户未提交的其他文件；自动保存提交前列出文件清单，未跟踪文件单独提示；来源：VER-20260811-003；影响：INT-20260816-005
- UXI-004: 全部 CLI 在非交互与重定向环境可用；来源：VER-20260808-002；影响：全部 INT 条目

## 责任记录约定

- 本项目为个人项目，使用 `governance_mode: personal`
- `owner: self` 表示维护责任
- `changed_by` 记录实际修改人或 AI 代理
- `decision_confirmed_by` 记录用户确认
- `semantic_reviewed_by` 记录代码语义审查（个人项目允许 self）
- Git 作为外部治理控制，保证历史追溯

## 代码、生成物与运行数据边界

| path/pattern | artifact_class | layer | read/write | environment | source_of_truth | safe_to_edit | safe_to_rebuild | retention/sensitivity |
|---|---|---|---|---|---|---|---|---|
| SKILL.md | source | runtime-code | read/write | local | SKILL.md | yes | N/A | permanent |
| logic_readme.md | source | runtime-code | read/write | local | logic_readme.md | yes | N/A | permanent |
| logic_change.md | source | runtime-code | read/write | local | logic_change.md | yes | N/A | temporary |
| logic_version/records/ | source | runtime-code | read-only | local | VER-*.md | no | N/A | permanent |
| references/ | source | runtime-code | read/write | local | 模板文件 | yes | N/A | permanent |

## 数据与控制流

```
用户请求修改
    ↓
AI 读取 logic_readme.md（当前规则）
    ↓
AI 读取 logic_change.md（活跃修改）
    ↓
判断通道：简单/中等/高风险
    ↓
[高风险] AI 读取 logic_version/records/（Recall 历史决策）
    ↓
AI 给出方案和影响分析
    ↓
用户确认
    ↓
AI 实施修改
    ↓
AI 更新 logic_readme.md（如规则变化）
    ↓
[高风险] AI 归档到 logic_version/records/
    ↓
[高风险] AI 关闭 logic_change.md 记录
```

## 消费者与公共契约

| 契约/数据 | 生产者 | 真实消费者 | 环境 | 当前兼容要求 | 证据 |
|---|---|---|---|---|---|
| SKILL.md | Recall 项目 | Claude Code, Codex | local | 向后兼容 | 文档格式 |
| logic_readme.md | Recall 项目 | AI（读取当前规则） | local | 稳定格式 | 表格结构 |
| logic_change.md | Recall 项目 | AI（读写修改记录） | local | 稳定格式 | CHG-ID 格式 |
| VER-* 记录 | Recall 项目 | AI（回忆历史） | local | 只读，不修改 | 记录格式 |

### 旧行为消费者

当前项目为初始版本，无旧行为消费者。

证据：首次建立 Recall 体系，2026-08-07。

## 不可破坏约束

- INV-001: logic_readme.md 必须唯一，禁止创建 logic_readme-v2.md；来源：SKILL.md 核心原则；验证：文件系统检查
- INV-002: logic_change.md 必须唯一，禁止创建副本；来源：SKILL.md 核心原则；验证：文件系统检查
- INV-003: logic_version/records/ 中的 VER-* 记录不可修改，只能追加；来源：不可变决策记录原则；验证：Git 历史
- INV-004: 历史记录不保存代码快照，只保存设计逻辑；来源：逻辑回档原则；验证：VER-* 内容审查

## 兼容与迁移制度

- 对象：无（首次建立）
- 当前版本关系：V1（初始版本）
- 持久化状态：文件系统（Markdown 文档）
- 当前策略：N/A
- 旧行为消费者与移除条件：none
- transitional 结束条件：N/A
- 回滚能力：Git 版本控制

## 安全、性能与运维

- 权限/隐私：本地文件，无特殊权限要求
- 性能/并发：单用户读写，无并发问题
- 部署/配置：无需部署，直接使用
- 日志/监控/告警：通过 Git 历史追踪
- 自动同步：仓库级 `recall.autoSync=true` 控制受管理的 `post-commit` hook；`recall.autoCommit=true`（默认）时 `recall sync` 自动提交脏工作区；远端缺失、网络失败或变基冲突只告警，不丢弃本地提交

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| unit | 审计脚本行为（含 INV-001/INV-002 平行真源检测） | `python tests/test_audit_logic_map.py` | 62 tests OK | unittest 输出 |
| contract | INV-001/INV-002 单一现行文档 | `python scripts/audit_logic_map.py . --current-state` | 无 parallel-current 或 nonroot-current 报告 | 审计报告 + 退出码 |
| contract | RULE-007 嵌套项目根不计入审计 | `python scripts/audit_logic_map.py . --current-state` | 夹具不出现在 Non-root current documents | 审计报告 |
| integration | RULE-009 校验字段名与模板一致 | `python scripts/validate.py` | 决策记录被发现且无假缺失字段 | 验证报告 |
| integration | INV-003 VER-* 不可变 | `git log --follow -- logic_version/records/` | 已发布 VER-* 只有创建提交 | Git log |
| runtime | RULE-005 批处理入口不错行 | `recall status` / `recall help` | 无 `is not recognized` 输出 | 终端输出 |
| runtime | RULE-008 非交互可用（三种无输入形式） | `recall init < /dev/null`；`echo "" \| recall init`；`recall init --non-interactive` | 三者均退出 0 | 终端输出 |
| runtime | RULE-008 重定向不崩 | `recall help > out.txt`；`recall status > out.txt` | 退出码 0，无 UnicodeEncodeError | 输出文件 |
| unit | RULE-009 决策记录字段名与模板一致 | `python tests/test_audit_logic_map.py` | 记录 schema 检查通过 | unittest 输出 |
| unit | RULE-010/RULE-011/RULE-013 自动同步、自动保存与回填 | `python -m unittest tests.test_git_sync` | 18 tests OK；配置、hook、pull/push、自动保存提交、手动模式、hook 不提交脏文件、递归防护、回填双通道（Ref 行/提交内记录）、旧占位符兼容、占位符字段行锚定（叙述文字不回填）、无占位符警告、漂移哨兵、recall new 端到端回填 | unittest 输出 |
| integration | RULE-015 validate 一致性对账 | `python scripts/validate.py` | 三处登记对账、撞号、意图层引用、CHG 三字段、占位符检查出现且无假错误 | 验证报告 |
| unit | RULE-012/RULE-014 CLI 胶水层接口一致性与反向查询（new/status/conflicts/query intent/记录发现） | `python -m unittest tests.test_recall_cli` | 13 tests OK；记录命名、必填字段、CHG 标题提取、项目根查找、query intent 解析、需求保全与锚点检查通过 | unittest 输出 |
| runtime | RULE-010 自动同步 CLI 可发现 | `python scripts/recall.py help`; `python scripts/git_sync.py --help` | 帮助包含 `sync`、`--auto`、`--manual`、`--no-auto-sync` 和 `--disable` | 终端输出 |

INV-004（VER-* 不含代码快照）不在此表：它是内容判断，只能人工审查，列在“不可破坏约束”里。此表只登记可执行的验证命令。

## 有效决策索引

| version_id | 决策摘要 | 关联规则 | 记录 |
|---|---|---|---|
| VER-20260808-001 | Recall 系统结构重组：账本完整性、平行真源、反膨胀强制点、状态机补全 | RULE-001..004 | [记录](logic_version/records/logic_version-20260808-001-recall-restructure.md) |
| VER-20260808-002 | 工具链与自审一致性加固：跨平台入口、schema 对齐、嵌套项目根排除 | RULE-005..009 | [记录](logic_version/records/logic_version-20260808-002-toolchain-hardening.md) |
| VER-20260811-001 | Git 自动同步：初始化默认配置、提交后 hook、显式脏工作区提交与手动 sync | RULE-010..011 | [记录](logic_version/records/logic_version-20260811-001-git-auto-sync.md) |
| VER-20260811-002 | CLI 胶水层接口修复：recall new 断裂、记录命名统一、冲突检测失灵、脏工作区不阻断同步 | RULE-011..012 | [记录](logic_version/records/logic_version-20260811-002-cli-interface-repair.md) |
| VER-20260811-003 | 默认自动保存上传（--manual 可切手动）与 after_commit 自动回填 | RULE-011, RULE-013 | [记录](logic_version/records/logic_version-20260811-003-auto-save-sync.md) |
| VER-20260816-001 | 功能级"功能意图与用户流程"层（INT/FLOW/UXI）、CHG 需求拆解字段与 plan 模式落盘约定 | RULE-014 | [记录](logic_version/records/logic_version-20260816-001-feature-intent-layer.md) |
| VER-20260816-002 | 追溯链断裂修复：recall new 回填链路、自动保存文件清单与回填双通道、INT 编号统一、validate 对账与漂移哨兵 | RULE-011, RULE-013..015 | [记录](logic_version/records/logic_version-20260816-002-traceability-repair.md) |
| VER-20260816-003 | 需求↔架构语义链路补全：模块化项目接入流程、CHG 三字段归档搬入 VER（需求保全）、INT 代码锚点与 query intent 反向查询 | RULE-014..016 | [记录](logic_version/records/logic_version-20260816-003-semantic-link.md) |

完整索引见 [logic_version/index.md](logic_version/index.md)。

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none

## 当前限制

- 仅支持个人或小团队使用（low-concurrency）
- 不提供实际权限控制（依赖 Git）
- 归档需人工判断：`scripts/create_ver.py` 按模板生成记录骨架，但"为什么"必须手写
- 静态门只检查文档结构与工具链约定，不能证明代码语义、消费者或运行行为
- 功能意图层随功能数线性增长：接近行数上限（目标 250 / 硬 400）时按 scope 锚点压缩 FLOW 描述、合并同类 UXI，禁止另建第二现行文档（INV-001/002）
- 自动保存提交（"自动保存本地修改"）无 Ref 行、不承载 why：积累过多会稀释追溯链，medium/high 变更应使用带 Ref 行的语义提交；`recall conflicts` 为关键词级启发式，语义冲突仍需人工澄清

## 修改检查清单

- [ ] 是否触及上游/下游契约？
- [ ] 是否触及持久化数据或已部署行为？
- [ ] 是否仍满足所有 INV 条目？
- [ ] 是否需要议案、ADR、迁移、回滚或弃用计划？
- [ ] 新增或修改的关键规则是否已经链接到具体 ADR/VER？
- [ ] 是否已更新根范围登记、关联代码地图、测试和历史索引？
- [ ] 是否先完成代码逻辑、数据边界和现有实现可并入性分析？
- [ ] 是否在修改后生成/补齐测试案例并审核前后结果？
- [ ] 是否存在未被更高优先级指令裁定的新旧需求矛盾？
