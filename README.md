# Recall

[![Validation](https://github.com/fuqiyue/recall/actions/workflows/validate.yml/badge.svg)](https://github.com/fuqiyue/recall/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**AI 驱动的项目逻辑追溯系统** — 让每次代码修改都能理解当初的设计意图。

Recall 记录 **"系统架构 + 设计原因"**，而不是 **"代码快照"**。代码版本交给 Git，设计逻辑交给 Recall：每个新开启的 AI 会话像新人接手成熟项目，从文档恢复上下文，而不是重扫代码库。

---

## 快速开始

```bash
# 初始化（配置 Git、自动同步 hook、.gitignore、首次提交）
recall init          # Windows；Linux/macOS 用 ./recall.sh init

# 日常命令
recall status        # 查看系统状态
recall new "描述" tag  # 创建决策记录
recall sync          # 自动保存并同步（未跟踪新文件默认排除，--include-new 纳入）
recall validate      # 验证一致性
recall route <路径或关键词>  # 打印本任务应读的领域文档（按需导入）
recall query file <路径>  # 查询文件的决策历史
recall help          # 完整帮助
```

## 工作方式

两级文档承载全部项目逻辑（一二级拆分法）：

| 文档 | 角色 |
|---|---|
| `logic_readme.md` | 宪法：全局规则、功能意图与领域目录，每个任务必读 |
| `logic_change.md` | 修宪议案 + 全项目活跃议案索引 |
| `logic_domains/<domain>/` | 部门法：领域规则、代码地图与其议案账本，按需导入（`recall route`） |
| `logic_version/` | 不可变决策记录：为什么改、方案取舍、如何回滚 |

代码变化由 Git 管理，决策记录通过 commit hash 与代码双向关联。

## 文档

规则语义与使用方式的权威来源（本 README 只是入口，不重述规章）：

- **[SKILL.md](SKILL.md)** — 核心原则、变更通道与使用方式
- **[logic_readme.md](logic_readme.md)** — 当前生效规则与代码地图
- **[references/](references/)** — 模板、生命周期与项目接入流程

## 兼容性

- Windows / Linux / macOS，Python 3.11+，仅依赖标准库
- `scripts/` 须整目录部署（`audit_logic_map.py` 是 `recall_audit/` 分层包的入口，`recall_common.py` 为各脚本共用）
- 与 Claude Code（CLAUDE.md）和 Codex（AGENTS.md）代理入口兼容

## 许可

MIT — 见 [LICENSE](LICENSE)。
