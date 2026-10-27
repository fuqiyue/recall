# Git 自动同步与推送责任

本文承载 SKILL.md 按需下沉的 Git 同步细节（RULE-022 按需披露）。权威语义是本技能 [Git管道部门法](../logic_domains/git-pipeline/logic_readme.md) 的 RULE-010 / RULE-011 / RULE-013：这些编号属于 Recall 工具自身，与消费项目 `logic_readme.md` 里的同名编号无关。需要初始化管道、排查同步或判断"谁负责推送"时再读。

## 自动同步是默认值，不是保证

`recall init` 默认启用自动同步：安装受管理的 `post-commit` hook，提交后执行 `pull --rebase --autostash` 再 `push`，失败只告警、不阻断本地提交。

提交前核远端、分支、`recall.autoSync` 与实际 hook。hook 开启时普通 `git commit` 也可能连带发布，因此发布授权须在提交前核对。已有“修改并推送”授权直接沿用；仅要求本地修改时先完成可审阅结果，未覆盖的发布再确认。未启用自动同步时，提交方仍完成已授权推送。

核对入口：

- 实际 push 成功回执；`git status -sb` 不带 `ahead` 作为本地交叉核对，单凭该状态不能证明远端实时一致
- `recall status` 输出的"未推送提交"行（本地领先上游的提交数；无上游时不显示）
- `recall validate` 对本地领先上游给出非阻断告警

## 命令实际影响

| 操作 | 写入或外部影响 | 使用前核对 |
|---|---|---|
| `recall init` | 配置 Git、身份、.gitignore 和 hook；新仓库可初次提交，默认立即尝试同步 | 初始化范围与远端；`--no-auto-sync` 关闭自动同步，`--no-commit` 跳过新仓库初次提交；均不生成 Recall 文档正文 |
| `recall sync` | 默认自动提交全部已跟踪变更，再拉取变基并推送；关闭自动保存时仅同步已提交历史 | 全部纳入文件和待推送提交均在授权内；已有暂存的新文件也会提交 |
| `sync --include-new` | 在上述基础上纳入未跟踪新文件 | 新文件逐项核对，不把教材、聊天或私人资料随工具上传 |
| `sync --manual` / `sync --auto` | 只切换仓库自动保存配置并返回；本次不提交或同步 | manual 不关闭 hook 或后续推送；manual 下显式 `--commit-message` 才提交脏文件 |
| `sync --disable` | 关闭自动同步和自动保存，移除 Recall 受管理 hook 段并返回 | 属于持久配置修改；之后显式运行 sync 仍可同步已提交历史 |
| `sync --no-push` / `sync --no-pull` | 分别跳过此次推送/拉取，其余步骤仍执行，包括可能的自动提交与回填 | no-push 不是只读，也不关闭后续 hook |
| 普通 `git commit` | 提交暂存内容；启用的 post-commit hook 可回填、拉取和推送 | 在提交前确认 hook 的实际影响与发布授权 |

`init --no-commit` 仅跳过初次提交步骤，不会关闭随后默认执行的同步；若目标仅为本地配置，应同时按所需影响选择初始化选项。

## 选择文件与同步结果

未跟踪新文件默认排除，仅 `--include-new` 或先 `git add` 纳入；提交前列纳入/排除清单，私人文件加入 .gitignore。工作树混有其他任务的已跟踪改动时，逐项暂存后用普通 Git 提交，不再用默认 sync 扩大范围。post-commit hook 不自动提交其他脏文件（UXI-003）。

无远端时按授权配置 `git remote add origin <url>`；有远端仍须核目标。远端缺失、网络失败或变基冲突保留本地提交，报告具体缺口；本地提交成功不能写成推送成功，推送成功也不代表 CI 或部署完成。

## 决策记录的 after_commit 回填

提交后 hook 双通道定位记录：commit message 的 `Ref:` 行，或本次提交内规范命名的 `logic_version-YYYYMMDD-NNN-*.md` 文件；识别 `- after_commit:` / `- commit:` 两种占位符且只按整个字段行匹配。无法回填时打印警告而非静默跳过；内部提交通过环境变量防止 hook 递归（RULE-013）。

## 项目接入（文档初稿从哪来）

`recall init` 只建 Git 管道，不生成文档内容。文档采用模块化渐进接入：接入时只建根骨架，存量模块登记为 `pending-docs`，此后按触发时机补全；AI 从代码扫描得出的描述标 `code-derived`，与用户确认的条目区分（[文档治理 RULE-016](../logic_domains/document-governance/logic_readme.md)）。步骤见[项目接入流程](project-onboarding.md)。

## 先交付后提交的追加追溯

定稿时尚无实施提交，应诚实写 `after_commit: none` 并保留测试/文件校验等现有证据。它不是hook占位符，后续不能把原不可变记录改成SHA。

真正提交后，先核该commit包含实际交付，再用 `recall new "追加已交付变更的提交关联" "commit-link"` 创建新的勘误记录。填 `status: correction`、`corrects: VER-原记录ID`、`after_commit: 实施提交SHA`，说明核对的文件与验证证据，保留原记录。按正常清理/定稿顺序设immutable:true并登记全量index；无CHG的简单补链将需求三字段填none，有CHG则保全原字段。

`validate` 仅接受已归档且SHA在项目中有效的追加证据；活跃草稿、自指、不存在的目标或无效SHA均不能替代原记录的提交关联。`query commit` 可同时找到勘误及被补链的原决策。尚未提交时保留“未关联Git commit”提示，不把计划提交说成已发生。

需要手动提交时，一次命令同时写标题与Ref，例如：

```bash
git commit -m "feat: 描述本次变更" -m "Ref: logic_version/records/<实际文件名>.md"
```

正常受管理hook仍只一次性回填模板占位符。Git检查失败时，status/validate保留具体原因；先判断仓库路径、工作树、权限或沙箱访问，再决定修复方式。
