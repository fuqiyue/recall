# Recall

[![Validation](https://github.com/fuqiyue/recall/actions/workflows/validate.yml/badge.svg)](https://github.com/fuqiyue/recall/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**为 AI 编程保留项目记忆，让每次接手都理解设计意图。**

Recall 将项目的现行规则、功能意图、任务进度和设计决策保存在仓库中。AI 会话开始时，先从文档恢复上下文，再按任务读取相关代码与测试，帮助你持续推进项目。

Git 保存代码版本，Recall 连接“为什么这样设计”和“接下来做什么”。适合个人与小团队在持续迭代、会话切换和项目交接中使用。

## 能帮你做什么

- **延续上下文**：从现行文档和任务进度接手，减少反复解释项目背景。
- **按需读取**：根据任务、路径或关键词定位相关领域，集中阅读本次需要的规则。
- **保留设计依据**：把需求、取舍和验证结果与 Git 提交关联，方便追溯。
- **完成任务交付**：持续维护同一任务的计划、进度与产物，支持验证、归档和收尾。

## 快速开始

准备 Python 3.11+ 和 Git，然后克隆完整仓库：

```bash
git clone https://github.com/fuqiyue/recall.git
```

在**要接入的项目根目录**调用 Recall。以下假设仓库位于 `D:\tools\recall` 或 `~/tools/recall`，请替换为你的实际路径。

Windows（PowerShell）：

```powershell
& 'D:\tools\recall\recall.bat' init
```

Linux / macOS：

```bash
bash ~/tools/recall/recall.sh init
```

`init` 配置 Git 仓库、身份、`.gitignore` 和首次提交，并默认启用提交后的自动同步；使用 `--no-auto-sync` 可选择手动同步。随后让 AI 按 [SKILL.md](SKILL.md) 和[项目接入流程](references/project-onboarding.md)建立根文档、首个领域与功能意图初稿。

下文用 `recall` 代表上述入口；实际调用时继续使用对应路径，或将命令入口加入你的环境。首次接入、中途修改和会话恢复可直接参考[三个操作示例](references/practical-examples.md)。

## 日常使用

| 你想做什么 | 命令 |
|---|---|
| 接手当前任务，查看下一步 | `recall next` |
| 找到本次应读的文档 | `recall route <任务ID、路径或关键词>` |
| 查看项目与 Git 状态 | `recall status` |
| 核对文档一致性 | `recall validate` / `recall audit` |
| 查询文件的设计决策 | `recall query file <路径>` |
| 保存并同步进度 | `recall sync` |
| 查看完整命令 | `recall help` |

`sync` 默认自动提交已跟踪文件的变更，再拉取变基并推送。新文件由你先 `git add` 选入，或用 `--include-new` 一并纳入；提交前会列出文件清单。配置与说明见 [Git 同步](references/git-sync.md)。

需要维护任务公报、文件地图或核对任务产物时，参阅[工作路径与任务](references/workspace-tasks.md)，了解 `index`、`inventory`、`path` 和 `workspace`。

## 文档如何协作

根文档提供全局上下文，领域文档承载具体规则，任务文件保存当前工作，历史记录用于追溯。

| 位置 | 内容 |
|---|---|
| `logic_readme.md` | 全局现行规则、功能意图与领域目录 |
| `logic_change.md` | 全项目活跃任务公报与正文链接 |
| `logic_domains/<domain>/` | 领域现行规则、代码地图与验证入口 |
| `logic_changes/<task>/logic_change.md` | 同一任务的需求、计划、进度与产物台账 |
| `logic_version/` | 已完成变更的设计依据、影响与验证记录 |
| `explainers/` | 便于阅读的 HTML 流程与架构说明 |

读取、实施与交付步骤见 [SKILL.md](SKILL.md)；目录与模板说明见[文档模型](references/document-model.md)。

## 按需阅读

| 你关心的内容 | 入口 |
|---|---|
| 第一次使用或接入已有项目 | [项目接入](references/project-onboarding.md) · [操作示例](references/practical-examples.md) |
| AI 如何读取上下文、修改和交付 | [技能入口](SKILL.md) · [变更生命周期](references/change-lifecycle.md) |
| Recall 自身的现行设计与领域导航 | [现行规则](logic_readme.md) |
| 任务恢复、目录盘点与产物管理 | [任务上下文](references/task-context.md) · [工作路径与任务](references/workspace-tasks.md) |
| 模板与参考材料 | [references/](references/) |
| 版本更新 | [GitHub Releases](https://github.com/fuqiyue/recall/releases) |
| 参与贡献与安全使用 | [贡献指南](CONTRIBUTING.md) · [安全说明](SECURITY.md) |

## 运行环境

- Windows / Linux / macOS，Python 3.11+ 与 Git；Python 部分使用标准库。
- 保留完整 `scripts/` 目录，CLI 脚本共享其中的模块。
- 提供 [Codex 代理入口](AGENTS.md)和 [Claude Code 代理入口](CLAUDE.md)。

## 许可

[MIT](LICENSE)
