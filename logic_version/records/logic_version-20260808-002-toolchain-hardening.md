# VER-20260808-002: 工具链与自审一致性加固

## 版本控制

- version_id: VER-20260808-002
- version_slug: toolchain-hardening
- change_id: CHG-20260808-002
- date: 2026-08-08
- status: effective
- affected_scopes: ., scripts/, references/, logic_version/
- linked_rule_ids: RULE-005, RULE-006, RULE-007, RULE-008, RULE-009
- confirmed_revision: 1
- immutable: true
- recall_route: high
- history_retention: full
- changed_by: Claude Opus 5 (AI)
- based_on: policy: logic_readme.md#当前制度; code: commit:578cd5e; surfaces: RULE-005, RULE-006, RULE-007, RULE-008, RULE-009
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:https://github.com/fuqiyue/recall@main
- governance_verification: recorded
- governance_verified_at: 2026-08-08

## 为什么做这个决策？

用户报告两个 CLI 缺陷。修复时发现它们不是孤立 bug，而是同一个结构性问题的表现：
**Recall 的自审只检查文档形式，不检查工具链行为，也不检查脚本与模板的 schema 是否一致。**
于是工具链里的失效可以长期存在而不被任何检查发现。

具体发现的失效，按"是否会被现有检查发现"分类：

**用户可见、但无检查覆盖：**

1. `recall.bat` 每次运行都先打印一行 `'LI' is not recognized`。根因不是引号转义
   （最初的猜测），而是 cmd.exe 按**字节偏移**定位下一条命令、却按控制台代码页
   解码行内容；UTF-8 中文注释 + LF-only 换行使两者错开，解释器从 `CLI` 的 `L`
   处重新开始，把注释片段当成命令执行。
2. `init_recall.py` 以 `.git` 路径是否存在判断仓库，双向误判：残留或损坏的 `.git`
   报"已经是仓库"；在真实仓库的子目录里报"不是仓库"，并会创建嵌套仓库。
3. 同一脚本只能交互运行，stdin 不可用时抛 `EOFError` 崩栈，CI、容器和 AI 代理
   环境无法使用。
3b. 修复第 3 项时引入的后续缺陷：用 `sys.stdin.isatty()` 判断 stdin 是否可用是
   不充分的。Windows/Git Bash 下 `< /dev/null` 把 NUL 当字符设备，`isatty()`
   返回 True，于是可选确认项仍去读 stdin、第一次读取即 EOF，退出 130。管道
   （`echo "" |`）返回 False 因而正常降级——两种"无输入"形式行为不一致。
   真正的判据是读取本身：可选确认遇 EOF 应取安全默认值，只有必填输入才中断。
4. Windows 上重定向输出即崩：重定向后 stdout 用 ANSI 代码页（cp936），
   报告里的 emoji 触发 `UnicodeEncodeError`。

**静默失效，连使用者都看不出来：**

5. `validate.py` 用 `glob("ver-*.md")` 查找决策记录，而实际文件名是
   `logic_version-*.md`——永远返回空列表。其后的必填字段检查、commit hash
   校验全是死代码，"验证通过"是假的。
6. 同一脚本的必填字段名（`版本号`、`关联 Commit`、`修改原因`、`决策过程`）
   与 `references/logic-version-template.md` 的真实 schema（`version_id`、`date`、
   `## 为什么做这个决策？`）完全不匹配。只修 glob 会让每条记录都报假缺失。
7. `link_ver_git.py` 按 `- **日期**:` / `- **关联 Commit**:` 粗体格式提取字段，
   真实记录用的是 `- date:` 控制字段，列表里日期和 commit 永远显示
   `Unknown` / `_待填写_`。它还把 `README.md` 当成决策记录列出。

**安全性缺陷：**

8. `init_recall.py` 和 `link_ver_git.py` 都用 `shell=True` + f-string 拼接命令。
   两个后果：多行 commit message 被 shell 截断（只有首行进入提交）；用户提供的
   姓名、邮箱和命令行传入的 commit 值可以注入命令执行。

**自审自身失效：**

9. `audit_logic_map.py` 对本项目静态门 FAIL，20 项问题。其中两类不是文档写错：
   - `references/examples/audit-repro-legacy/` 是审计的复现夹具，自带完整治理
     文档且声明 `module_id: MOD-ROOT` + `scope: .`。审计按 `module_id` 建索引，
     夹具把真正的根文档顶掉，于是根范围被报 `no-governance-parent`；夹具同时
     被算作未登记治理目录。五个独立扫描器都有同样问题。
   - `canonical_readme`、`canonical_change`、`registry_status` 三个字段：
     `references/logic-readme-template.md` 定义在 `## 范围登记与归属`，审计却只从
     `## 文档控制` 读取。两份独立文档（真实根文档和夹具）都按模板写、都失败——
     是审计与自己的模板矛盾，不是文档错。

**文档与实现漂移：**

10. `logic_readme.md` 的代码地图只登记 7 个条目，缺 5 个脚本和 2 个 CLI 入口；
    `governance_ref` 仍是占位符 `[your-repo]`；测试表登记 `pytest tests/`，但
    环境里没有 pytest（实际可用命令是 `python tests/test_audit_logic_map.py`）。
11. `init_recall.py` 生成的 `.gitignore` 含 `# Claude` 块，本仓库自己的
    `.gitignore` 没有——该文件仅靠用户全局 ignore 屏蔽，克隆者会看到未跟踪噪音。

问题的根源：Recall 把"检查"等同于"检查文档字段是否齐全"。工具脚本、脚本与模板
的一致性、以及跨平台执行行为都在检查范围之外，所以第 5、6、7 项可以长期通过
"验证通过"的假象存在。

## 考虑过哪些方案？

### 方案 A：全面加固工具链，并把工具链行为纳入自审（选择此方案）

- 修复全部 11 项失效
- 新增 RULE-005..009，把"批处理必须 ASCII+CRLF""禁止 shell=True"
  "嵌套项目根不计入审计""CLI 必须可非交互""脚本字段名以模板为准"写入现行制度
- 用 `.gitattributes` 固定换行符，让修复不因克隆配置而回退
- 测试表改为可执行命令，每条规则对应真实验证入口

### 方案 B：只修用户报告的两个缺陷

- 只处理 `recall.bat` 错行和仓库误判
- **缺点**：第 5、6、7 项静默失效仍在，"验证通过"继续是假的；
  没有强制点，同类问题会再次出现

### 方案 C：重写工具链

- 用统一的 CLI 框架重写全部脚本
- **缺点**：现有脚本的逻辑基本正确，失效集中在边界处理和 schema 对齐；
  重写会丢掉已验证的行为，且无法解释为什么原来会错

## 为什么选择方案 A？

1. 静默失效比可见 bug 更危险：第 5 项让 `validate.py` 长期给出虚假的通过结论，
   必须连同它的成因（schema 漂移无检查）一起修
2. 夹具污染和模板矛盾是审计脚本自身的缺陷，不修就无法用静态门守护其余规则
3. 换行符和 `shell=True` 都需要**强制点**而非一次性修复，否则必然回退
4. 每条新规则都能对应一条可执行验证命令，避免再次出现"只有形式、没有验证"的规则

## 影响范围

### 修改的文件

- `recall.bat`：改为纯 ASCII + CRLF；增加 python/py/python3 探测链与退出码传递
- `recall.sh`：增加 python3/python 回退
- `.gitattributes`（新建）：固定 `*.bat` 为 CRLF、`*.sh` 为 LF
- `scripts/init_recall.py`：仓库判定改用 `git rev-parse --show-toplevel`；
  全部 git 调用改 argv 列表；增加非交互参数与环境变量；`Aborted` 替代 `EOFError`
- `scripts/recall.py`：`cmd_init` 转发参数；重定向时切 UTF-8
- `scripts/validate.py`：修 glob；字段名对齐模板；重定向时切 UTF-8；
  `exit()` 改 `sys.exit()`；裸 `except` 改具体异常
- `scripts/link_ver_git.py`：`shell=True` 改 argv 列表；三处重复解析合并为
  `_parse_record`；字段名对齐模板；按记录名过滤而非 `*.md`
- `scripts/audit_logic_map.py`：新增 `is_nested_project_root` 与 `is_foreign_subtree`，
  六个扫描器统一剪枝；三个字段改为 `文档控制` 优先、`范围登记与归属` 回退
- `logic_readme.md`：新增 RULE-005..009；代码地图补全 18 条；测试表改为可执行
  命令；`governance_ref` 换成真实仓库地址；补 MOD-TEMPLATES/MOD-HISTORY 锚点
- `logic_change.md`：`governance_ref` 对齐；补讨论主题索引表头
- `AGENTS.md`、`CLAUDE.md`：补五个机器可读标记
- `.gitignore`：补 `# Claude` 块，与 `init_recall.py` 的产物一致
- `README.md`：补非交互运行参数说明

### 消费者影响

- **Recall 的消费者项目**：
  - `recall.bat` 不再打印伪错误行；无 Python 时给出可操作提示而非静默失败
  - `recall init` 可在 CI、容器和 AI 代理环境运行
  - `validate.py` 开始真正检查决策记录（此前是空检查）
  - 审计对 vendored 或示例项目不再误报
- **破坏性变更**：无。新增参数都有默认值，字段位置改为"两处都接受"而非迁移

### 已知偏差

VER-20260808-001 的"注意"段落写着"本仓库 `.git` 目录为空，无 Git 历史"。该事实
在 2026-08-08 发布到 GitHub 后不再成立（当前 `git:https://github.com/fuqiyue/recall@main`，
初始提交 `578cd5e`）。VER-* 不可变（INV-003），因此不修改原记录，在此声明其被
本记录取代。

## 验证方式

1. **批处理不错行**：`recall status` / `help` / `validate` / `list` 四个子命令输出中
   不含 `is not recognized`；退出码 0/0/0/1（未知命令）
2. **仓库判定**：四场景探针——真实仓库根、空目录、残留 `.git`、真实仓库子目录，
   分别得到 `repo_root` / `none` / `none` / `nested`（旧逻辑在第 3、4 项均错）
3. **非交互**：`recall init` 在三种形式下都退出 0——`< /dev/null`（isatty 为 True，
   靠 EOF 取默认值）、`echo "" |`（isatty 为 False，走非交互分支）、
   `--non-interactive`（显式）。此前分别为 130 / 0 / 0
4. **注入防护**：作者名 `Te"st & Na|me` 原样进入 author 字段；
   `link_ver_git.py commit 'abc; echo PWNED'` 不产生 `PWNED` 输出
5. **多行提交**：5 行 commit message 完整往返，不被截断
6. **重定向**：`recall help > out.txt` 无 `UnicodeEncodeError`，emoji 保留
7. **记录发现**：`validate.py` 找到 1 条决策记录、0 个假缺失字段
8. **静态门**：`python scripts/audit_logic_map.py . --current-state` 通过，
   夹具不出现在 Non-root current documents，无 agent-entry 问题
9. **回归**：`python tests/test_audit_logic_map.py` 62 tests OK
10. **换行符固定**：`git check-attr text eol -- recall.bat recall.sh` 得到
    `recall.bat: eol: crlf`、`recall.sh: eol: lf`

## 回滚方式

1. 用 Git 回退本次提交：`git revert <commit>`
2. 单项回滚：各文件互相独立，可按需回退单个文件
3. 若只需恢复审计旧行为：移除 `is_nested_project_root` / `is_foreign_subtree`
   的调用点，六个扫描器改回 `is_dependency_tree_root`
4. 从 `logic_readme.md` 移除 RULE-005..009，从本目录删除本记录，
   并从 `logic_version/index.md` 移除对应索引行

**注意**：`.gitattributes` 回滚后，`recall.bat` 的 CRLF 会在下次克隆时
按用户 `core.autocrlf` 设置变化，第 1 项缺陷可能复现。

## 实施记录

- 实施者：Claude Opus 5 (AI)
- 实施日期：2026-08-08
- 确认者：user（确认"按 CLAUDE.md 流程走一遍"并要求继续优化）
- 确认日期：2026-08-08
- 语义审查：self（个人模式）
- 审查日期：2026-08-08
- 审查证据：上述 10 项验证全部执行并通过；每项缺陷在修复前先用探针复现，
  确认根因后再改，未依赖推测（第 1 项的初始猜测"引号转义"经字节转储否证）

## 关联

- change_id: CHG-20260808-002
- 取代：VER-20260808-001 中关于"无 Git 历史"的事实陈述
- 意图来源：用户报告的两个 CLI 缺陷 + 用户要求"继续优化"
- 规则新增：RULE-005, RULE-006, RULE-007, RULE-008, RULE-009
