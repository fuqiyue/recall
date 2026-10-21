# Recall

[![Validation](https://github.com/fuqiyue/recall/actions/workflows/validate.yml/badge.svg)](https://github.com/fuqiyue/recall/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**AI 驱动的项目逻辑追溯系统** — 让每次代码修改都能理解当初的设计意图。

Recall 记录 **"系统架构 + 设计原因"**，而不是 **"代码快照"**。代码版本交给 Git，设计逻辑交给 Recall：每个新开启的 AI 会话像新人接手成熟项目，从文档恢复上下文，而不是重扫代码库。

---

## v2026.10.21：工作路径与任务修订

本版把项目目录、任务过程和历史归档接起来，减少重复计划、交接正文和临时文件遗留。

- **先定位再写入**：以用户指定的项目文件夹为根，检查根相对路径，拒绝越界、链接和重复项目根。
- **按实际目录找文件**：有界扫描生成领域文件地图；数据目录只看上层，注明扫描范围，描述仍需核实。
- **一个任务一份正文**：根 `logic_change.md` 提供索引，`logic_changes/<任务>/logic_change.md` 集中计划、进度、修订表和产物台账；领域文档保存现行规则。
- **区分轮次与方案版本**：同一任务持续修订，记录原因、涉及文件和验证结果；普通修复不强制提升方案版本。
- **凭实际清理关案**：临时代码集中到 `.work/临时-具体功能/`，核对台账与真实文件，删除非交付物及空目录；修订表随需求归入同一份 VER 后再移除活跃正文。

沿用旧领域账本；存量任务按需迁移。工具不会自动搬移或删除文件，修订内容的完整性仍由代理核对。详见[工作路径与任务](references/workspace-tasks.md)及[本版发布](https://github.com/fuqiyue/recall/releases/tag/v2026.10.21)。

## 快速开始

```bash
# 在需要接入的项目根运行（recall 代表已配置的命令入口）
# 初始化 Git、同步 hook、.gitignore 和首次提交；逻辑文档接入见下方说明
recall init          # Windows 使用维护源 recall.bat；其他平台使用 recall.sh

# 日常命令
recall status        # 查看系统状态
recall next          # 当前任务、下一步与阻塞上下文
recall index         # 生成并核对根公报；加 --write 显式更新
recall inventory     # 有界盘点真实目录；--write 更新领域文件地图
recall path <相对路径> # 输出前核对路径，防止越界和重复项目根
recall workspace --closing CHG-ID # 核台账与真实产物，包括被忽略的临时文件
recall new "描述" tag  # 在已定位项目创建草稿；可加 --project <项目根>
recall sync          # 自动保存并同步（未跟踪新文件默认排除，--include-new 纳入）
recall validate      # 验证一致性
recall audit         # 文档审计静态门（默认 --current-state）
recall route <路径或关键词>  # 打印本任务应读的领域文档（按需导入）
recall query file <路径>  # 查询文件的决策历史
recall help          # 完整帮助
```

`init` 完成 Git 管道后，按[项目接入](references/project-onboarding.md)建立或补全项目逻辑文档。维护 Recall 技能使用本仓库；处理业务项目使用业务项目根，不在技能仓库登记业务规则或授权。

最小实践见[三个操作示例](references/practical-examples.md)：首次接入、中等修改与中断接手。

## 工作方式

两级文档承载全部项目逻辑（一二级拆分法）：

| 文档 | 角色 |
|---|---|
| `logic_readme.md` | 宪法：全局规则、功能意图与领域目录，每个任务必读 |
| `logic_change.md` | 全项目活跃任务索引 |
| `logic_changes/<task>/logic_change.md` | 同任务唯一正文：需求、计划、进度、修改与产物台账 |
| `logic_domains/<domain>/` | 领域现行规则与可重建文件地图，按需导入（`recall route`） |
| `.work/临时-具体功能/` | 临时代码和输出，完成后删除；忽略规则不代替清理 |
| `explainers/` | 可直接打开的 HTML 解释快照（非制度真源） |
| `logic_version/` | 不可变决策记录：为什么改、方案取舍、如何回滚 |

代码变化由 Git 管理，决策记录通过 commit hash 与代码双向关联。

## 文档

规则语义与使用方式的权威来源（本 README 只是入口，不重述规章）：

- **[SKILL.md](SKILL.md)** — 核心原则、变更通道与使用方式
- **[logic_readme.md](logic_readme.md)** — 当前生效规则与代码地图
- **[AI 交付流程说明](explainers/ai-delivery-closure-20260907.html)** — AI 审查、关案与人工反馈的关系
- **[references/](references/)** — 模板、生命周期与项目接入流程

## 兼容性

- Windows / Linux / macOS，Python 3.11+，仅依赖标准库
- `scripts/` 须整目录部署（`audit_logic_map.py` 是 `recall_audit/` 分层包的入口，`recall_common.py` 为各脚本共用）
- 与 Claude Code（CLAUDE.md）和 Codex（AGENTS.md）代理入口兼容

## 许可

MIT — 见 [LICENSE](LICENSE)。
