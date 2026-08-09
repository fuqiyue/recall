# Recall 常见问题

## 基础概念

### Q: Recall 和 Git 有什么区别？

**简短答案**：Git 记录"改了什么"，Recall 记录"为什么改"。

**详细说明**：

| 维度 | Git | Recall |
|------|-----|--------|
| **记录内容** | 代码差异（diff） | 决策原因、权衡、影响 |
| **回答问题** | "代码如何变化？" | "为什么这样设计？" |
| **存储位置** | `.git/` 目录 | `logic_version/` 目录 |
| **查询方式** | `git log`, `git blame` | `recall query`, 阅读 VER 记录 |
| **目标用户** | 人类开发者 | AI 代理 + 人类 |

### Q: 为什么不直接用 Git commit message？

Commit message 通常很简短，无法承载：
- 详细的权衡分析
- 多个备选方案对比
- 风险评估和影响分析
- 未来维护者需要知道的约束

Recall 的 VER 记录提供结构化的决策文档，而非简单的一行描述。

### Q: 必须用 Git 吗？

**是的**。Recall 依赖 Git 来：
- 追踪代码变化历史
- 通过 commit hash 关联决策和代码
- 提供时间线和版本控制

但你可以在已有的 Git 仓库中添加 Recall，无需创建新仓库。

---

## 使用问题

### Q: 什么时候需要创建 VER 记录？

**遵循"三条通道"原则**：

- **简单修改**（typo、格式）：无需 VER 记录
- **中等修改**（小功能、重构）：可选，推荐在 `logic_change.md` 中记录
- **高风险修改**（架构变更、打破约束）：**必须**创建 VER 记录

**判断标准**：如果 3 个月后有人问"为什么这样做"，你需要解释超过 2 分钟 → 需要 VER 记录。

### Q: 如何为现有项目引入 Recall？

```bash
# 1. 在项目根目录初始化
cd /path/to/your/project
/path/to/recall/recall.sh init

# 2. 创建初始的 Code Map
# 编辑 logic_readme.md，记录当前架构

# 3. 记录重要的历史决策（可选）
# 为过去的关键决策补充 VER 记录

# 4. 从下一次修改开始使用标准流程
```

### Q: 团队协作如何使用？

**推荐工作流**：

1. **共享规则**
   - `logic_readme.md` 作为单一真相源
   - 定期同步（`git pull`）

2. **议案评审**
   - 在 `logic_change.md` 中提出修改议案
   - 通过 PR 让团队评审
   - 达成共识后实施

3. **决策归档**
   - 完成后立即归档到 `logic_version/`
   - 更新 `logic_readme.md`

4. **冲突处理**
   - 如果多人同时修改同一规则，Git 会提示冲突
   - 手动合并，保留最新共识

### Q: Recall CLI 的常用命令是什么？

```bash
# 查看系统状态
recall status

# 验证一致性
recall validate

# 创建新决策记录
recall new "添加用户认证" auth

# 列出最近记录
recall list

# 查询文件历史
recall query file src/auth.py

# 查询提交详情
recall query commit abc123

# 查看帮助
recall help
```

---

## 技术问题

### Q: Windows 上能用吗？

**完全支持**。使用 `recall.bat`：

```cmd
recall status
recall validate
```

如果安装了 Git Bash，也可以用 `recall.sh`。

### Q: 需要安装什么依赖？

**最小依赖**：
- Python 3.11+
- Git 2.x+

**可选**：
- GitHub CLI (`gh`) - 用于自动化 PR 创建等

### Q: 性能如何？大型仓库会慢吗？

Recall 主要操作文本文件，性能瓶颈通常在 Git：

- **小型项目**（< 1000 commits）：几乎无延迟
- **中型项目**（< 10000 commits）：毫秒级
- **大型项目**（> 10000 commits）：主要受 `git log` 影响

优化建议：
- 使用 `recall query file` 而非 `git log --follow`（已优化）
- 定期归档历史记录

### Q: 如何备份 Recall 数据？

Recall 的所有数据都在 Git 仓库中：

```bash
# 备份整个仓库（包括 Recall）
git clone --mirror <repo-url> backup/

# 或只备份 Recall 相关文件
tar -czf recall-backup.tar.gz logic_readme.md logic_change.md logic_version/
```

---

## 概念澄清

### Q: Code Map 是什么？

**Code Map（代码地图）** 是 `logic_readme.md` 中的一个部分，记录：

- **路径**：文件/目录位置
- **职责**：这个组件做什么
- **依赖**：依赖哪些其他组件

示例：
```markdown
## Code Map

| 路径 | 职责 | 依赖 |
|------|------|------|
| scripts/cli.py | CLI 命令解析 | validator.py, query.py |
| scripts/validator.py | 验证 Recall 一致性 | - |
```

**用途**：让 AI 代理快速理解项目结构。

### Q: CHG-ID 和 RULE-ID 是什么？

- **CHG-ID**：Change ID，议案追踪标识符
  - 格式：`CHG-YYYYMMDD-HHMM-description`
  - 位置：`logic_change.md`
  - 状态：未生效的提案

- **RULE-ID**：Rule ID，生效规则标识符
  - 格式：`RULE-category-brief-name`
  - 位置：`logic_readme.md`
  - 状态：当前生效的规则

**关系**：CHG-ID 完成后，会生成对应的 RULE-ID 并移到 `logic_readme.md`。

### Q: VER 记录的格式是什么？

```markdown
---
ver_id: VER-20260808-1430-add-auth
date: 2026-08-08T14:30:00+08:00
author: 张三
commit: abc123def456
related_files:
  - src/auth.py
  - config/auth.config
tags: [security, authentication]
---

# 添加用户认证系统

## 决策背景
（为什么需要这个修改）

## 方案对比
（考虑过哪些方案）

## 最终决策
（选择了什么，为什么）

## 影响分析
（对系统的影响）

## 实施记录
（如何实现的）
```

---

## 故障排查

### Q: `recall validate` 失败怎么办？

**常见原因**：

1. **缺少必要文件**
   ```bash
   # 检查是否存在
   ls logic_readme.md logic_change.md logic_version/
   
   # 如果缺失，重新初始化
   recall init
   ```

2. **Git 用户未配置**
   ```bash
   git config user.name "你的名字"
   git config user.email "your@email.com"
   ```

3. **格式错误**
   - 检查 VER 记录的 YAML frontmatter
   - 确保日期格式正确

### Q: Git push 失败

**检查清单**：

```bash
# 1. 确认远程仓库配置
git remote -v

# 2. 确认有推送权限
git push origin main

# 3. 如果是新分支
git push -u origin <branch-name>

# 4. 查看详细错误
GIT_TRACE=1 git push origin main
```

### Q: 中文显示乱码

**Windows**：
```cmd
# 设置 Git 编码
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commitencoding utf-8

# 设置终端代码页
chcp 65001
```

**Linux/macOS**：
```bash
# 设置 locale
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

---

## 进阶使用

### Q: 如何与 CI/CD 集成？

参考 `.github/workflows/validate.yml`：

```yaml
- name: 验证 Recall
  run: |
    chmod +x recall.sh
    ./recall.sh validate
```

### Q: 如何在 IDE 中使用？

**VS Code**：
1. 安装 Markdown 预览插件
2. 打开 `logic_readme.md`
3. 使用 "Markdown: Open Preview" 查看

**JetBrains IDE**：
1. 内置 Markdown 支持
2. 右键 → "Open in Browser"

### Q: 能否自动生成 VER 记录？

**部分可以**：

```bash
# 使用 recall CLI（计划中的功能）
recall new "修改描述" tag1 tag2

# 或使用模板
cp logic_version/template.md logic_version/records/VER-$(date +%Y%m%d-%H%M)-my-change.md
```

---

## 更多问题？

- 查看 [GitHub Issues](https://github.com/fuqiyue/recall/issues)
- 阅读 [CLAUDE.md](CLAUDE.md) 了解设计理念
- 查看 [示例流程图](docs/RECALL_FLOW_DIAGRAMS.md)
