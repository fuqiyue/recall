# Recall

[![Validation](https://github.com/fuqiyue/recall/actions/workflows/validate.yml/badge.svg)](https://github.com/fuqiyue/recall/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**AI 驱动的项目逻辑追溯系统** — 让每次代码修改都能理解当初的设计意图。

Recall 记录 **"系统架构 + 设计原因"**，而不是 **"代码快照"**。代码版本交给 Git，设计逻辑交给 Recall：每个新开启的 AI 会话像新人接手成熟项目，从文档恢复上下文，而不是重扫代码库。

---

## v2026.10.25.1：先核验删除，受限再兜底

清理先核归属、准确路径及归档/文件指纹，再逐项删除文件和已确认的空目录；需要额外权限时走环境提供的正式审批。成功后核实文件消失、正式归档与其他任务未变，并移除对应待清理登记。

仍受限的已归档重复正文，才在执行策略允许下移入 `logic_version/pending_cleanup/`；移动也受限，仅在现有历史索引登记“原位待清理，允许时可删除”。移动仍有清理欠账，不新增过程文档。CLI只读核验，具体操作见[清理步骤](references/workspace-tasks.md#核验后逐项删除)。

## v2026.10.24：任务准确路由、增量地图与分层清理

本版沿用现有任务正文和文件地图，让上下文按任务准确恢复、局部扫描保留已有覆盖、清理结果明确归属。

- **按任务声明找规则**：任务 ID 或路径依据 `scope` / `affected_scopes` 定位领域；其他相关任务先给摘要，按需展开正文，减少漏读与无关上下文。
- **文件地图增量更新**：只替换完整列举的目录范围，未重扫或截断的条目保留旧时间；确认目录消失才移除对应索引。
- **分任务、分轮次核对产物**：支持 `workspace --task` 和 `--round`，全局问题另列；共享临时目录仍归属双方，关案检查不按轮次过滤。
- **相近需求合并维护**：能统一目标、验收和收尾的需求优先并入同一任务，当前状态只维护一处，修订事实随最终决定归档。
- **保留产物写明依据**：台账补充保留依据、退出条件和轮次；每轮处置临时物，任务完成后清理临时文件及空目录。

兼容旧五列台账和旧文件地图，保留原 JSON 字段；筛选检查的退出码对应所选任务或轮次。工具不自动删除文件。详见[工作路径与任务](references/workspace-tasks.md)及[本版发布](https://github.com/fuqiyue/recall/releases/tag/v2026.10.24)。

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
recall workspace --task CHG-ID --round 01 # 核本轮产物；全局遗留另列
recall path <相对路径> # 输出前核对路径，防止越界和重复项目根
recall workspace --closing CHG-ID # 核台账与真实产物，包括被忽略的临时文件
recall new "描述" tag  # 在已定位项目创建草稿；可加 --project <项目根>
recall sync          # 自动保存并同步（未跟踪新文件默认排除，--include-new 纳入）
recall validate      # 验证一致性
recall audit         # 文档审计静态门（默认 --current-state）
recall route <任务ID、路径或关键词> # 任务按声明范围找规则；相关任务先给摘要
recall query file <路径>  # 查询文件的决策历史
recall help          # 完整帮助
```

`init` 完成 Git 管道后，按[项目接入](references/project-onboarding.md)建立或补全项目逻辑文档。维护 Recall 技能使用本仓库；处理业务项目使用业务项目根，不在技能仓库登记业务规则或授权。

最小实践见[三个操作示例](references/practical-examples.md)：首次接入、中等修改与中断接手。

完整命令、台账字段和兼容边界见[工作路径与任务](references/workspace-tasks.md)。

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
