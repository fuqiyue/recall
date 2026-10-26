# 根规则精简与领域归属

<a id="chg-20261026-002"></a>
## CHG-20261026-002: 精简根现行规则并同步 GitHub
- governance_mode: personal
- status: promoting
- effective: false
- proposal_revision: 1
- recall_route: medium
- owner: self
- changed_by: Codex
- scope: .
- affected_scopes: .; logic_domains/toolchain; logic_domains/git-pipeline; logic_domains/document-governance; logic_domains/task-workflow
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-26
- created: 2026-10-26
- last_status_change: 2026-10-26
- raw_request: 请继续优化根 logic_readme.md 的简洁程度，把适合下放的内容放到对应的 logic_domains，减少每次必读的内容，同时保证现行规则完整、避免重复。然后更新github。
- decomposition: 按职责迁移领域规则并保留原编号和证据链接；压缩根导航与重复说明；同步规则指针和路径/意图路由；验证唯一性、完整性与阅读成本；归档关案并提交推送 GitHub。
- fit_analysis: 复用 INT-20260816-003、INT-20260816-011 与 INT-20260903-002，落实 FLOW-002#1/4/5 及 FLOW-005#4；保留 INT/FLOW/UXI 根层入口，不改变 CLI 行为或业务授权边界。
- authority_surfaces: RULE-016; RULE-018; RULE-020; RULE-022; RULE-025; RULE-026; RULE-027; RULE-029
- based_on: policy: logic_readme.md; code: 0e38394bf6ce3abafbff2d54175b222630e5b90d; surfaces: RULE-016; RULE-018; RULE-020; RULE-022; RULE-025; RULE-026; RULE-027; RULE-029
- history_retention: compact
- reserved_version_id: VER-20261026-002
- version_slug: logic_version-20261026-002-root-domain-slim
- intent_traceability: INT-20260816-011 -> RULE-018 -> test:tests/test_recall_cli.py -> VER-20261026-002
- task_temp_dirs: none
- current_result: 29条规则唯一且正文/理由保全；根140行约5715 token；audit零问题、skill校验通过、全量353测试通过（1项符号链接环境跳过）；路径/RULE/INT/任务ID路由核验通过。
- next_action: 提交已验证实现，给留档绑定真实提交；完成清理、定稿/关案，再推送并核对远端与CI。

### 目标与依据
根文档必须每次完整读取，但包含任务收尾和目录治理的细节；现有路由支持 readme-only 领域、owned_paths 和 INT 关联规则，无需改 CLI。当前工作区另有前轮技能更新及已归档的审计提示汇总修改；发布时核对并纳入已准备的相关交付，未跟踪备份保持原位。

### 拟议制度
选用两个领域：文档治理承接 RULE-016/022/026；任务交付承接 RULE-020/025/027/029。根保留全局规则、INT/FLOW/UXI、领域目录与验证入口。迁移规则原编号、语义和留档反链不变；根仅给条件导航，不保留第二份规则摘要。
仅压缩措辞不足以去掉无关必读内容；把全部细节塞进工具链会扩大无关路由；选用有独立文档职责的两个领域。用户本轮请求已授权整理和 GitHub 更新。

### 验证与回滚
逐行核迁移规则与原定义；静态审计、validate、公报一致性；按路径、RULE、INT 与任务 ID 检查路由；skill quick_validate；全量现有测试（含待发布代码）。保全历史文件指纹与本轮未编辑代码。失败修正后复验；提交后可用 git revert 撤销本轮结构变化，不改历史事实。

### 修订记录
| 轮次 | 日期 | 方案版本 | 原因与修改 | 涉及文件 | 结果/验证 |
|---|---|---|---|---|---|
| 01 | 2026-10-26 | 1 | 审查必读成本与领域边界，选择保留规则编号的迁移 | 根及领域readme、references、SKILL | route基线已确认，远端基线一致 |
| 02 | 2026-10-26 | 1 | 迁移七条规则，更新导航/范围/引用与领域职权 | 根和四个领域、相关references、SKILL | 根读取成本约降36%，两类路径路由正确；完整回归见第03轮 |

| 03 | 2026-10-26 | 1 | 核规则保全、路由及发布回归 | 全部现行readme、路由、既有测试 | 29条规则无重复/缺失/语义丢失；353测试OK（1环境跳过）；audit零问题；skill有效 |

### 晋升与归档
生效规则写入唯一所属 readme；核临时产物后把需求三字段、修订表和验证结论归入同一 VER，更新索引，移除本任务并核根公报。发布保留真实 Git/CI 结果。

### 工作区产物台账
| path | artifact_kind | disposition | reason | cleaned_at | retention_basis | exit_condition | round |
|---|---|---|---|---|---|---|---|
