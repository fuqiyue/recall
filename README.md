# Recall

**保存设计逻辑，而非代码快照。**

Recall 让 AI 能够回忆"当初为什么这么设计"，而不是"当初代码长什么样"。代码版本交给 Git，Recall 负责设计推理、关键取舍和影响分析。

## 快速开始

### 首次使用

**第一次使用 Recall 时，请先运行初始化脚本**：

```bash
python scripts/init_recall.py
```

这个脚本会引导你：
- ✅ 检查并初始化 Git 仓库
- ✅ 配置 Git 用户信息（姓名和邮箱）
- ✅ 创建必要的配置文件
- ✅ 完成初始提交

### 日常使用

对任何可能改变行为或需要审查既有设计的任务：

1. 读 `logic_readme.md`（当前有效规则）
2. 读 `logic_change.md`（活跃议案）
3. 读相关代码、测试和运行证据
4. 只在需要解释冲突或追溯兼容性时，按 ID 读取 `logic_version/records/` 中的历史记录

### 标准工作流

```
用户需求 → logic_change.md（记录议案）
         ↓
    实施修改 → git commit（代码变化）
         ↓
    归档决策 → logic_version/records/（为什么改）
         ↓
    更新规则 → logic_readme.md（现行规则）
```

## 文档

- **[SKILL.md](SKILL.md)** — 完整使用指南（核心原则、三条通道、调用模式）
- **[CLAUDE.md](CLAUDE.md)** — Claude AI 使用说明（含初始化指引）
- **[logic_readme.md](logic_readme.md)** — 当前有效规则与代码地图
- **[logic_change.md](logic_change.md)** — 活跃修改议案
- **[references/](references/)** — 模板与参考文档

## Git 集成

Recall 使用 **Git 管理代码变化**，**文档管理决策原因**：

| 维度 | Git 负责 | Recall 负责 |
|------|----------|-------------|
| **内容** | 代码的"是什么" | 决策的"为什么" |
| **存储** | 代码快照、diff | 原因、背景、权衡 |
| **工具** | `git log`, `git show` | logic_version/*.md |
| **关联** | commit hash | 文档中引用 commit |

**快速命令**：

```bash
# 创建新的决策记录
python scripts/create_ver.py "添加功能X" "feature-x"

# 查询文件的历史和决策记录
python scripts/link_ver_git.py file logic_readme.md

# 查询某个提交的详情
python scripts/link_ver_git.py commit abc123d

# 列出最近的决策记录
python scripts/link_ver_git.py list
```

## 核心理念

**历史记录保存什么？**

✅ 为什么做这个决策、考虑过哪些方案（A/B/C）、为什么选择当前方案、影响了谁、如何验证和回滚

❌ 完整代码快照、逐行 diff、详细实现细节、原始对话记录、思维推理过程

**为什么这样设计？**

1. 避免上下文爆炸 — 完整历史代码会让文档迅速膨胀
2. Git 已经负责代码版本 — Recall 只负责"为什么"
3. 重点是防止设计退化 — 修改时需要知道"当初为什么这么做"

详见 [逻辑回档 vs 代码回档](references/logic-vs-code-recall.md)。

## 三条变更通道

| 通道 | 典型条件 |
|---|---|
| 简单修复 | 局部、隔离、无公共契约/持久化/兼容影响 |
| 中等变更 | 涉及多个相关文件，但无未确认长期设计选择 |
| 高风险变更 | 公共契约、跨模块、权限、安全、持久化数据、迁移 |

详见 [SKILL.md](SKILL.md#三条变更通道)。

## 许可

本项目使用 MIT 许可证。
