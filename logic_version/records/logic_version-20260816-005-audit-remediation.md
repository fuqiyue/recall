# VER-20260816-005: 审查整改：五项漏洞修复与重复脱管清理

## 记录控制

- version_id: VER-20260816-005
- version_slug: logic_version-20260816-005-audit-remediation
- status: effective
- date: 2026-08-16
- change_id: CHG-20260816-004
- before_commit: 8b5b0fb
- after_commit: _待填写_
- recall_route: high
- history_retention: full
- decision_confirmed_by: user
- decision_ref: user-confirmed:2026-08-16（"请你解决漏洞……同时帮我解决你的ABCDE发现"）
- changed_by: Claude (Fable 5)
- intent_traceability: INT-20260816-005 -> RULE-011 -> test:tests/test_git_sync.py -> VER-20260816-005; INT-20260816-008 -> RULE-015 -> test:tests/test_validate.py -> VER-20260816-005; INT-20260816-011 -> RULE-018 -> test:tests/test_audit_logic_map.py -> VER-20260816-005

## 为什么做这个决策？

**背景**：
对开发逻辑的整体审查发现五项漏洞与五项重复/脱管问题。漏洞：(1) RULE-014 的
rejected 记录与 validate 三处对账矛盾——被否决方案会被迫登记为"有效决策"；
(2) 自动保存的文件清单警告与 `git add -A` 上传在同一次不可中断运行内完成，
非交互环境下警告读到时私人文件已上远端；(3) INV-003"不可修改"与 RULE-013
回填 hook 事实矛盾，对应测试矩阵验证命令必然失败；(4) validate 与行数上限
只看根文档，RULE-018 拆分后的子文档进入无检查区；(5) 漂移哨兵非阻断且无累积
度量。重复/脱管：(A) 根目录与 docs/ 下 8 份脱管文档重述规章（README 重述三条
通道正是 VER-20260808-001 清理过的失败模式复发），且平行真源检测只认
logic_readme/logic_change 命名，对改名副本全盲；(B) 双 VER 模板权威分裂
（create_ver 用 git 版、validate 注释指 full 版）；(C) 515 行孤儿文档
git-workflow-integration.md 语义停留在 4 个 VER 之前；(D) 三组规范语义各散布
5 处，每次更新 N 连改；(E) references/ 四份模板未列入 SKILL 参考列表。

**用户需求/反馈**：
"可以，请你解决漏洞。认可漏洞2你的解决办法，这个是自动化处理的程序，除非
用户明确要求。同时帮我解决你的ABCDE发现，你做的不错"

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 用户 2026-08-16："可以，请你解决漏洞。认可漏洞2你的解决办法，这个是自动化处理的程序，除非用户明确要求。同时帮我解决你的ABCDE发现，你做的不错"（承接同日审查报告的五项漏洞与 A-E 五项发现）
- decomposition: 1) validate 豁免 rejected/cancelled/rolled-back 记录的有效决策索引检查；2) 自动保存默认排除未跟踪新文件，新增 --include-new；3) INV-003 改写为"语义不可改，占位符回填是唯一合法变更"；4) validate 与行数上限覆盖已登记子文档、RULE/INT 编号空间全项目唯一入 RULE-018；5) validate 漂移度量（自上次触及 logic 文档以来的提交数）；A) 脱管文档归档 + 审计新增根目录 md 覆盖对账；B) 合并双 VER 模板为 logic-version-template.md；C) 归档 git-workflow-integration.md 并修正指针；D) 新增 RULE-019 文档引用纪律并收敛三组五连抄；E) SKILL 参考列表补齐
- fit_analysis: 强化 INT-20260816-005（sync）与 INT-20260816-008（validate）；UXI-003 语义从"事后透明"升级为"事前排除"，UXI-001/002 不变；不新增 INT；审计对账扩展 INV-001 的机器验证面

## 决策过程

**漏洞2 方案**：A. 维持事后警告（零改动，但对非交互环境无拦截力，否决）；
B. 交互式确认（破坏 UXI-004 非交互约束，否决）；C（选中）. 未跟踪新文件默认
排除、`--include-new` 或先 `git add` 才纳入——用户裁决"自动化处理的程序，
除非用户明确要求"，默认从"新文件默认公开"翻转为"新文件默认本地"（复杂度：低）。

**发现A 防复发方案**：A. 仅清理文件（复发无感知，否决）；B（选中）. 清理 +
审计新增"git 跟踪的顶层 Markdown ⊆ owned_paths ∪ unmapped_paths"对账并纳入
静态门——登记表继续作为唯一合法性来源，与 RULE-018 的白名单思路一致；只查
.md 限定噪音面（复杂度：中）。C. 全文件类型对账（误报多：LICENSE、CI 配置等，
否决）。

**发现B 方案**：保留实际生成源（git 版正文）但落在多数指针已指向的文件名
`logic-version-template.md`，full 版 schema 降级为文内"扩展 schema"章节，
旧 git 版文件归档（选中）；反向合并需改动 create_ver 提取逻辑，否决。

**选中方案与原因**：见上。共同原则：合法性由机器可检的登记定义，默认值偏向
安全（不上传、不放行、要登记）。

## 影响范围

**修改的文件/模块**：
- `scripts/git_sync.py` - 自动保存默认 `git add -u`，未跟踪文件排除清单与 `--include-new`
- `scripts/validate.py` - rejected 豁免与反向告警、readme-only 子文档纳入 RULE/INT 检查、漂移度量
- `scripts/audit_logic_map.py` - audit_root_doc_coverage 覆盖对账入静态门、子文档行数上限
- `scripts/create_ver.py`、`scripts/recall.py` - 模板与帮助指针更新
- `logic_readme.md` - RULE-011/015/018 改写、新增 RULE-019、INV-001/003 与 UXI-003 改写、unmapped_paths 补登记
- `SKILL.md`、`CLAUDE.md`、`logic_change.md` 底部、`logic_version/index.md` - 重复语义收敛为指针（RULE-019）
- `references/logic-version-template.md` - 成为唯一决策记录模板（含扩展 schema）
- `logic_version/backups/20260816/` - 10 份脱管/被替代文档归档（MANIFEST 列明原因与现行真源）
- `README.md` - 瘦身为入口，不再重述规章；`CONTRIBUTING.md`、`.github/ISSUE_TEMPLATE` 失链修复
- `tests/` - test_git_sync +2、test_audit_logic_map +5、新增 test_validate（7 用例）

**破坏性变更**：`recall sync` 对未跟踪新文件的行为变化（不再自动上传）；
`--include-new` 恢复旧行为，属安全默认值翻转而非能力移除。其余向后兼容。

## 验证方式

`python tests/test_audit_logic_map.py`（69 OK，含覆盖对账三用例与子文档行数
双向用例）；`python -m unittest tests.test_validate tests.test_git_sync
tests.test_recall_cli`（40 OK）；`python scripts/audit_logic_map.py .
--current-state` 静态门 PASS（新对账检查实测先抓出本仓库 9 个脱管条目，
清理登记后放行）；`python scripts/validate.py` 零错误。

## 回滚方式

`git revert` 本次提交整体回退；归档文件 `git mv` 回原路径即可（backups/20260816/
MANIFEST.md 列明原路径）。`recall sync --include-new` 可临时恢复旧上传行为，
无需回滚。

## 经验与教训

自动化的安全默认值必须假设"无人在看输出"：事后警告在非交互环境等于没有警告，
拦截必须发生在动作之前。检查体系每放宽一个约束（rejected 记录、子文档拆分），
必须同步给豁免路径建检查，否则放宽点就是下一个无检查区。平行真源会以改名换姓
的形式复发，命名模式检测不够，需要"登记表 ⊆ 对账"式的全集检查。

## 关联

- current_logic: logic_readme.md#RULE-011, RULE-015, RULE-018, RULE-019
- proposal_id: CHG-20260816-004（已归档移除）
- code/tests: scripts/git_sync.py; scripts/validate.py; scripts/audit_logic_map.py; tests/test_validate.py; logic_version/backups/20260816/MANIFEST.md
