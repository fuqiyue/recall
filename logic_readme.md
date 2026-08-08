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
- governance_ref: git:https://github.com/[your-repo]/recall
- governance_evidence: git:main-branch
- governance_verification: recorded
- governance_verified_at: 2026-08-07
- effective_from: 2026-08-07
- last_verified: 2026-08-08
- review_trigger: interval:90d; event:major-refactor
- source_of_truth: SKILL.md, logic_readme.md
- source_decisions: none
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
- owned_paths: SKILL.md, logic_readme.md, logic_change.md, logic_version/, references/, scripts/, tests/
- child_policy: inherit
- data_owner: none
- registry_status: registered

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |
|---|---|---|---|---|---|---|---|---|---|
| RULE-001 | key | 逻辑回档而非代码回档 | 避免上下文膨胀，保持文档简洁可读 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | SKILL.md 章节 | valid | 2026-08-08 | self |
| RULE-002 | key | logic_readme.md 只保留最新规则 | 删除已废弃内容，保持单一真相源 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | 当前文档 | valid | 2026-08-08 | self |
| RULE-003 | key | 历史记录保存设计逻辑 | 记录为什么、取舍、影响，不记录代码快照 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 用户确认 | logic_version/ | valid | 2026-08-08 | self |
| RULE-004 | ordinary | 三条通道分流修改 | 简单/中等/高风险，避免过度流程化 | [VER-20260808-001](logic_version/records/logic_version-20260808-001-recall-restructure.md) | 最佳实践 | SKILL.md | valid | 2026-08-08 | self |

## 代码地图

| 路径/稳定锚点 | artifact_class/layer | 职责 | 输入 | 输出 | 权威来源 | 可直接编辑 | contract_class | 关联测试 |
|---|---|---|---|---|---|---|---|---|
| SKILL.md | source/runtime-code | Recall skill 主入口，定义核心原则和使用方式 | AI 读取 | 指导 AI 行为 | SKILL.md | yes | internal | none |
| logic_readme.md | source/runtime-code | 当前生效的规则和代码地图（唯一真相源） | AI 读取 | 当前制度 | logic_readme.md | yes | internal | none |
| logic_change.md | source/runtime-code | 活跃的修改记录（未生效） | AI 读取/写入 | 修改议案 | logic_change.md | yes | internal | none |
| logic_version/records/ | source/runtime-code | 历史决策记录（逻辑回档） | AI 按需读取 | 设计逻辑回忆 | VER-*.md | no | internal | none |
| references/ | source/runtime-code | 模板文件和参考文档 | AI 按需读取 | 文档模板 | 模板文件 | yes | internal | none |
| scripts/audit_logic_map.py | source/runtime-code | 审计脚本：检查文档结构、唯一性、依赖、密度 | 项目根路径 | 审计报告 | 脚本文件 | yes | internal | tests/test_audit_logic_map.py |
| tests/ | source/runtime-code | 审计脚本测试套件 | pytest | 测试结果 | 测试文件 | yes | internal | pytest tests/ |

- coverage_policy: governed-boundaries
- membership_policy: root-registry-first
- layer_policy: 所有 Recall 文档为 source/runtime-code 层
- version_root: logic_version/
- temp_root: logic_version/working/
- 子范围路由：无（单一根文档）
- unmapped_paths: .tmp-tests/ (临时测试), agents/ (配置文件), .agents/ (空目录), .claude/ (配置文件)

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [logic_readme.md](logic_readme.md) | [logic_change.md](logic_change.md) | self | active |
| MOD-TEMPLATES | references/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md) | [active changes](logic_change.md) | self | active |
| MOD-HISTORY | logic_version/ | in-system | module/runtime-code | inherited | [root policy](logic_readme.md) | none | self | active |

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

## 测试与验证

| test_level | 规则/不变量 | 当前验证命令/检查 | expected | authoritative_evidence |
|---|---|---|---|---|
| manual | INV-001 单一 logic_readme.md | 文件系统检查 | 只有一个 logic_readme.md | 目录列表 |
| manual | INV-002 单一 logic_change.md | 文件系统检查 | 只有一个 logic_change.md | 目录列表 |
| manual | INV-003 VER-* 不可变 | Git 历史检查 | 已发布的 VER-* 无修改 | Git log |
| manual | INV-004 逻辑回档原则 | VER-* 内容审查 | 无代码快照 | 人工审查 |

## 有效决策索引

当前无历史决策记录。

## 活跃议案入口

- 唯一入口：[logic_change.md](logic_change.md)
- 相关 CHG-ID：none

## 当前限制

- 仅支持个人或小团队使用（low-concurrency）
- 不提供实际权限控制（依赖 Git）
- 历史记录为手动归档，无自动化工具

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
