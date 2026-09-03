# VER-20260903-002: 结构性与上下文成本优化——CLI 胶水修复、按需披露、审计器分包

## 记录控制

- version_id: VER-20260903-002
- version_slug: logic_version-20260903-002-structure-context-cost
- status: effective
- date: 2026-09-03
- change_id: CHG-20260903-002
- before_commit: a75723d
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
用户要求对 recall skill 做一次整体调研。调研发现四类问题：① 两处真实运行故障——`recall status` 在 Windows 中文环境崩溃（scripts/recall.py 的 git 子进程未指定 utf-8，GBK 解码含中文的提交信息时读线程抛异常、stdout 变 None），`recall conflicts` 经 CLI 永远失败（detect_conflicts.main 把 sys.argv[1] 即子命令名 `conflicts` 当项目根）；两者都在 CLI 装配层，而 CI 全绿，因为测试只覆盖纯函数。② 制度自述的缺口——RULE-010 验证证据列承认"推送责任子句当前无自动检测"；行数目标 250 只写在文档里、审计器只查硬上限 400；五份脚本各写一份 find_project_root、七份各写一份编码防护（RULE-012 曾修过的"各用一套"模式重演）。③ 文档漂移——Python 版本口径 3.7/3.8/3.11 三种、CI 检查 `Code Map` 与 CHANGELOG.md 两个早已不存在的对象、代码地图缺 test_validate.py、控制流图仍是"只有高风险归档 VER"的旧语义、样板段落"初始版本无旧行为消费者"。④ 结构与上下文成本——audit_logic_map.py 单文件 6764 行、最大函数 650 行；SKILL.md 每次触发约 6300 token，其中近半是代理极少当场需要的目录模型与 Git 细节。

**用户需求/反馈**：
2026-09-03 会话："请问目前的 recall skill，有什么需要优化的地方吗？请帮我调研和分析" → 报告四节后 "认可你的建议，请你帮我修改。重点优化结构性与上下文成本。按需调用请帮我优化"。

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: 2026-09-03 用户："请问目前的 recall skill，有什么需要优化的地方吗？请帮我调研和分析" → 报告后 "认可你的建议，请你帮我修改。重点优化结构性与上下文成本。按需调用请帮我优化"
- decomposition: ① status 子进程 utf-8 + conflicts 走项目根查找；② 新建 scripts/recall_common.py 统一 find_project_root/run_git/force_utf8_output，六份脚本改用；③ status/validate 增加未推送提交（ahead）提示；④ 审计器 density 增加 250 目标软提示；⑤ SKILL.md 按需披露：文档模型与 Git 同步细节下沉 references/document-model.md、references/git-sync.md；⑥ audit_logic_map.py 拆为 scripts/recall_audit/ 十层包，入口保留为 facade；⑦ CLI 胶水层子进程冒烟测试 + recall_common 单测；⑧ 文档同步：Python 版本口径、CI 死检查、代码地图、控制流图、样板段落、index.md slug
- fit_analysis: 修复 INT-20260816-006（status）与 INT-20260816-009（conflicts）的既有目标，不新增 INT；ahead 提示扩展 INT-20260816-006/008 的输出并补 RULE-010 验证证据；SKILL 按需披露服务 INT-20260816-003（文档三件套阅读）的上下文成本；审计器分包属系统内部结构，不改任何 FLOW；不触碰 UXI-001..006

## 决策过程

**方案 A**：只修两处故障 + 文档同步（优点：风险最低；缺点：重复根查找、巨型审计文件、SKILL 体积原样保留，与用户"重点优化结构性与上下文成本"的要求不符；复杂度：低）

**方案 B**：故障修复 + 公共模块 + 审计器按层分包（facade 保持入口与测试路径不变）+ SKILL 按需下沉（优点：结构与上下文成本一并改善；外部调用路径、`--json` 输出、测试 API 全部不变；缺点：拆包需依赖图无环、只拷贝单个 audit 文件的部署方式失效；复杂度：中）

**方案 C**：重写审计器（优点：可彻底精简 compliance 专用逻辑；缺点：6764 行语义没有完整规格，回归风险高；复杂度：高）

**落选方案归档**：A 的需求原文即上方 raw_request，否决原因是没有回应"结构性与上下文成本"这一重点；C 否决原因是无规格重写的回归风险与本次"不改对外行为"的约束冲突。

**选中方案与原因**：
选 B。拆包前先用 AST 核实：77 个顶层定义只有 14 处前向引用且全部集中在 `is_within` 与 Markdown 助手，按"常量→解析→文件分类→CHG 检查→单文档语义→路由/议案/静态门→formal→归档/入口/密度→汇总→CLI"十层切分后依赖图无环；测试只经 facade 访问 8 个属性且无 monkeypatch，因此 facade 重新导出即可零改动通过。搬迁由一次性脚本机械完成、不改任何函数体，回归面最小。SKILL 的下沉遵循 RULE-019：语义正文本就只在 logic_readme 规则行，SKILL 里的目录模型与 Git 段落是操作细节，移到 references 后 SKILL 用一张"何时读哪份"的表指向。

## 影响范围

**修改的文件/模块**：
- `scripts/recall_common.py`（新）- `find_project_root(start, fallback=)`、`run_git`/`git_output`（argv + utf-8）、`force_utf8_output`、`unpushed_commit_count`
- `scripts/recall.py` - status 改用 `run_git`（修崩溃）、新增未推送提交提示行 `describe_unpushed`；conflicts 显式传空 argv；删除本地重复实现
- `scripts/detect_conflicts.py` - `main(argv=None)` 经公共根查找定位文档（修永远失败）
- `scripts/validate.py` - 改用公共根查找；新增 `report_unpushed_commits`（RULE-010 非阻断告警）
- `scripts/create_ver.py`、`scripts/link_ver_git.py`、`scripts/git_sync.py` - 删除各自的根查找/run_git/编码防护实现，改为导入（git_sync 保留同名绑定供测试打桩）
- `scripts/audit_logic_map.py` - 6764 行 → 209 行 facade；`scripts/recall_audit/`（新）十个模块 + `__init__.py`
- `scripts/recall_audit/archive.py` `audit_density` - 新增 `notices`（over-target：SKILL 130 / readme 250 / change 150）；`report.py` `print_text` 新增 Density 段（此前 density 结果只进 JSON 计数，文本模式完全不可见）
- `SKILL.md` - 182 行 → 84 行（约 6300 → 3960 token）；新增"按需读取"表；删除"发布态文档模型/Git 自动同步/项目接入/代理入口/治理模式"整节
- `references/document-model.md`（新）、`references/git-sync.md`（新）- 承接下沉内容；`references/field-vocabulary.md` 更新 Density 语义
- `tests/test_recall_common.py`（新，7 例）；`tests/test_recall_cli.py` 新增 `UnpushedHintTests`、`CliGlueSmokeTests`（4 例子进程真跑）；`tests/test_validate.py` 新增 `UnpushedCommitTests`
- `recall.sh`、`recall.bat`（ASCII+CRLF 保持）- Python 版本口径统一为 3.11+
- `.github/workflows/validate.yml` - 死检查 `Code Map` 改为 `## 代码地图` 并升级为阻断；补跑 test_recall_cli/test_validate/test_recall_common 与 audit 静态门；`pr-checks.yml` - CHANGELOG.md 检查改为"脚本变更未触及 logic 文档"提示
- `logic_readme.md` - RULE-010 验证证据列；新增 RULE-021（CLI 基础设施只此一份 + 胶水层冒烟）、RULE-022（按需披露 + 审计器分包 + Density 目标）；代码地图新增 recall_common/recall_audit/test_validate/test_recall_common 行；INT-003/006/009 更新；控制流图改为三通道全流程；旧行为消费者与兼容制度改为真实内容；测试表新增 5 行；当前限制新增 2 条；有效决策索引
- `logic_version/index.md` - 新增本记录行；前两行 version_slug 统一为完整文件名格式

**破坏性变更**：否（对外）。命令行、退出码、`--json` 结构、模板字段名、记录文件名均不变。部署形态变化：`audit_logic_map.py` 不再能单文件拷贝使用，必须与 `recall_audit/` 同目录；已知消费者只有指向本仓库的技能目录符号链接，无迁移动作。

## 验证方式

- `python tests/test_audit_logic_map.py` → 69 OK（拆包前后一致）
- `python -m unittest tests.test_git_sync tests.test_recall_cli tests.test_validate tests.test_recall_common` → 59 OK（基线 45 + 新增 14）
- `python scripts/audit_logic_map.py . --current-state` → Static gate PASS；Density 段出现 `logic_readme.md:over-target:3xx>250` advisory；`--formal-review` 与 `--json --current-state` 正常
- `python scripts/recall.py status`（本仓库、中文提交信息、Windows cp936）→ 退出 0，输出最近提交/未提交/未跟踪/未推送四类信息
- `python scripts/recall.py conflicts` 与 `cd scripts && python detect_conflicts.py ..` → 读到 22 条规则，退出 0/2，不再报"未找到 logic_readme.md"
- `python scripts/validate.py` → 无错误
- 代码差异：`git show <after_commit>`

## 回滚方式

`git revert <after_commit>`。纯代码搬迁 + 文档；无数据、无运行时依赖。回滚后 audit 单文件恢复、SKILL 恢复 182 行版本；recall_common 消失但各脚本旧实现随之恢复。

## 经验与教训

- 胶水层故障与 CI 全绿可以长期共存：纯函数测试不能替代"以子进程真跑一遍"的冒烟测试，后者成本极低（4 例 < 3 秒）。
- 制度自述的缺口（RULE-010 的"当前无自动检测"）就是最便宜的待办清单；写进验证证据列的坦白应该定期被回收。
- 拆分巨型文件前先用 AST 算依赖图与前向引用，机械搬迁 + facade 重导出可以把回归风险压到"测试零改动通过"。
- "按需披露"的判据是"代理在当场需要它的概率"：目录模型、Git 命令细节、代理入口模板在 90% 的会话里不需要，一张"何时读哪份"的表比整段正文更省 token 也更好维护。
- 审计器只把 density 放进 JSON 计数、文本模式不打印，是"检查存在但不可见"的又一实例；新增任何检查都应确认它在默认输出模式下有落点。

## 兼容、迁移与回滚

- compatibility: 向后兼容；`recall_audit` 包为新增依赖目录，整目录部署即满足
- migration: none（单文件拷贝消费者不存在）
- rollback: git revert
- logic_temp_cleanup: logic_version/working/logic_version-20260903-002-structure-context-cost/ 于 2026-09-03 删除；台账 10 项（keep 6：recall_common.py、recall_audit/、document-model.md、git-sync.md、本记录、test_recall_common.py；delete 4：scratchpad 内四个一次性改写脚本）全部处置

## 关联

- current_logic: logic_readme.md#RULE-021；RULE-022；RULE-010（验证证据列更新）
- proposal_id: CHG-20260903-002（本记录创建后关闭）
- intent_traceability: INT-20260816-006 -> RULE-021 -> test:tests/test_recall_cli.py#CliGlueSmokeTests -> VER-20260903-002; INT-20260816-009 -> RULE-021 -> test:tests/test_recall_cli.py#CliGlueSmokeTests -> VER-20260903-002; INT-20260816-003 -> RULE-022 -> test:tests/test_audit_logic_map.py -> VER-20260903-002
- code/tests: scripts/recall_common.py; scripts/recall.py; scripts/detect_conflicts.py; scripts/validate.py; scripts/audit_logic_map.py; scripts/recall_audit/; SKILL.md; references/document-model.md; references/git-sync.md; tests/test_recall_common.py; tests/test_recall_cli.py; tests/test_validate.py
