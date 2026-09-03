# Git 自动同步与推送责任

本文承载 SKILL.md 按需下沉的 Git 同步细节（RULE-022 按需披露）。权威语义是本技能目录 `logic_readme.md` 的 RULE-010 / RULE-011 / RULE-013：这些编号属于 Recall 工具自身，与消费项目 `logic_readme.md` 里的同名编号无关。需要初始化管道、排查同步或判断"谁负责推送"时再读。

## 自动同步是默认值，不是保证

`recall init` 默认启用自动同步：安装受管理的 `post-commit` hook，提交后执行 `pull --rebase --autostash` 再 `push`，失败只告警、不阻断本地提交。

自动同步只在跑过 `recall init` 的仓库里生效。只接入了文档、没接管道的项目（`git config --get recall.autoSync` 为空或 `.git/hooks/post-commit` 不存在）不会自动推送，提交后必须自己推：`recall sync` 或 `git push`。一批提交只推前几个，会让远端停在实现未进的中间提交上（2026-09-02 消费项目实例：7 个提交只推 1 个，CI 18 项失败）。

核对入口：

- `git status -sb` 首行不带 `ahead`
- `recall status` 输出的"未推送提交"行（本地领先上游的提交数；无上游时不显示）
- `recall validate` 对本地领先上游给出非阻断告警

## recall sync 的行为

`recall sync` 默认自动保存**已跟踪文件**的变更后拉取变基并推送。**未跟踪的新文件默认排除**，仅 `recall sync --include-new` 或用户先 `git add` 时纳入（自动化不上传用户未明确要求的文件；私人文件加入 .gitignore）。提交前列出纳入清单与被排除清单。

- `--manual`：切手动模式（仅 `--commit-message` 时提交）
- `--auto`：恢复自动保存（默认）
- `--disable`：完全关闭自动同步
- 无远端时先 `git remote add origin <url>`

post-commit hook 场景绝不自动提交其他脏文件（UXI-003）。

## 决策记录的 after_commit 回填

提交后 hook 双通道定位记录：commit message 的 `Ref:` 行，或本次提交内规范命名的 `logic_version-YYYYMMDD-NNN-*.md` 文件；识别 `- after_commit:` / `- commit:` 两种占位符且只按整个字段行匹配。无法回填时打印警告而非静默跳过；内部提交通过环境变量防止 hook 递归（RULE-013）。

## 项目接入（文档初稿从哪来）

`recall init` 只建 Git 管道，不生成文档内容。文档采用模块化渐进接入：接入时只建根骨架，存量模块登记为 `pending-docs`，此后按触发时机补全；AI 从代码扫描得出的描述标 `code-derived`，与用户确认的条目区分（RULE-016）。步骤见[项目接入流程](project-onboarding.md)。
