# Recall 项目 Git 集成优化总结

## 优化概述

**优化日期**: 2026-08-08  
**目标**: 将 Git 版本控制集成到 Recall 系统，实现代码变化和决策记录的完整追溯  
**原则**: 保持现有架构，Git 管理代码，Recall 管理决策

## 核心架构

### 三层结构（保持不变）

```
recall/
├── logic_readme.md          # 现行法规（当前生效的规则）
├── logic_change.md          # 修改预案（待讨论的提案）
├── logic_version/           # 修改记录（历史存档）
│   ├── records/            # 决策记录（为什么改）
│   │   └── ver-*.md       # 文字说明：原因、背景、决策
│   └── index.md           # 索引
└── .git/                    # 代码历史（Git 管理）
```

### 职责分离

| 维度 | Git 负责 | Recall 负责 |
|------|----------|-------------|
| **存储内容** | 代码快照、diff | 决策原因、背景、权衡 |
| **回答问题** | 改了什么？(What) | 为什么改？(Why) |
| **查询工具** | `git log`, `git show` | 阅读 `logic_version/*.md` |
| **关联方式** | Commit hash | 文档中引用 commit hash |

## 新增功能

### 1. 初始化脚本 (`scripts/init_recall.py`)

**功能**：
- ✅ 检查 Git 是否已安装
- ✅ 初始化 Git 仓库（如未初始化）
- ✅ 引导用户配置 Git 用户信息
- ✅ 创建 .gitignore 文件
- ✅ 创建初始提交

**使用方法**：
```bash
python scripts/init_recall.py
```

**何时使用**：
- 首次使用 Recall 时
- 新项目初始化时
- 需要重新配置 Git 时

### 2. 决策记录创建工具 (`scripts/create_ver.py`)

**功能**：
- 自动生成版本号（VER-YYYYMMDD-NNN）
- 使用 Git 集成模板创建记录
- 自动填充日期和基本信息

**使用方法**：
```bash
python scripts/create_ver.py "添加暗色模式" "dark-mode"
```

**输出**：
```
logic_version/records/ver-20260808-001-dark-mode.md
```

### 3. 关联查询工具 (`scripts/link_ver_git.py`)

**功能**：
- 查询文件的 Git 历史和决策记录
- 查询提交的详情和关联决策
- 列出最近的决策记录

**使用方法**：
```bash
# 查询文件
python scripts/link_ver_git.py file logic_readme.md

# 查询提交
python scripts/link_ver_git.py commit abc123d

# 列出最近决策
python scripts/link_ver_git.py list
```

### 4. Git 集成模板 (`references/logic-version-git-template.md`)

**特点**：
- 简化字段（10-15 个必填/可选字段）
- 强调 Git 关联（commit hash）
- 提供快速模板和完整指南
- 包含 Git 命令示例

**与完整模板的差异**：

| 维度 | 完整模板 | Git 集成版 |
|------|----------|------------|
| 字段数量 | 50+ | 10-15 |
| 适用场景 | 大型团队/正式审计 | 个人/小团队 |
| 代码管理 | 可能需要快照 | 完全交给 Git |
| 决策流程 | 多阶段审批 | 简化流程 |

### 5. 工作流文档 (`references/git-workflow-integration.md`)

**内容**：
- 完整工作流（预案→执行→归档→更新）
- Commit message 规范
- 查询和追溯方法
- Git hooks 示例
- 分支策略
- 最佳实践
- 故障排查

### 6. 更新的文档

**CLAUDE.md**：
- 添加初始化指引
- 说明为什么需要 Git
- 提供快速命令参考

**README.md**：
- 添加"首次使用"章节
- 说明 Git 集成概念
- 提供辅助工具使用方法

## 标准工作流

### 完整流程

```
1. 提出修改（预案阶段）
   ↓
   logic_change.md（记录 CHG-ID）

2. 实施修改（执行阶段）
   ↓
   修改代码 + git commit（记录代码变化）
   ↓
   获取 commit hash

3. 归档决策（存档阶段）
   ↓
   logic_version/records/（创建 VER-ID，填入 commit hash）
   ↓
   记录原因、背景、决策过程

4. 更新现行（生效阶段）
   ↓
   logic_readme.md（更新 RULE-ID）
   ↓
   清理 logic_change.md
```

### 关联方式

```
logic_change.md
    ↓
  CHG-20260808-001
    ↓
[实施修改]
    ↓
  git commit
    ↓
  abc123def456 ← commit hash
    ↓
logic_version/records/ver-20260808-001-xxx.md
    ↓
  引用 commit: abc123def456
    ↓
logic_readme.md
    ↓
  RULE-001 → 链接 VER-20260808-001
```

### 双向追溯

**从代码到决策**：
```bash
git log                           # 查看提交历史
git show abc123d                  # 查看具体提交
# 在 commit message 中找到 Ref: logic_version/...
cat logic_version/records/ver-*.md  # 阅读决策记录
```

**从决策到代码**：
```bash
cat logic_version/records/ver-*.md  # 阅读决策记录
# 找到 "关联 Commit: abc123d"
git show abc123d                    # 查看代码变化
```

## Commit Message 规范

### 格式

```
<type>(<scope>): <简短描述>

<详细说明>

Ref: logic_version/records/<filename>.md
Closes: #<issue-number>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `docs`: 文档
- `test`: 测试
- `chore`: 构建/工具

### 示例

```bash
git commit -m "feat: 添加暗色模式支持

- 使用 CSS 变量实现主题切换
- 添加主题切换按钮
- 默认跟随系统主题

Ref: logic_version/records/ver-20260808-001-dark-mode.md"
```

## 文件清单

### 新增文件

```
scripts/
├── init_recall.py              # 初始化脚本
├── create_ver.py              # 创建决策记录工具
└── link_ver_git.py            # 关联查询工具

references/
├── logic-version-git-template.md    # Git 集成模板
└── git-workflow-integration.md      # 工作流文档
```

### 更新文件

```
CLAUDE.md                      # 添加初始化和 Git 集成说明
README.md                      # 添加快速开始和 Git 集成章节
```

## 使用场景

### 场景 1: 新项目初始化

```bash
# 1. 初始化项目
python scripts/init_recall.py

# 2. 开始第一个功能
# 在 logic_change.md 记录议案
# 实施修改
git commit -m "feat: 初始功能"

# 3. 归档决策（如需要）
python scripts/create_ver.py "初始功能" "initial-feature"
```

### 场景 2: 添加新功能

```bash
# 1. 记录议案
# 编辑 logic_change.md

# 2. 创建决策记录
python scripts/create_ver.py "添加用户认证" "auth"

# 3. 实施修改
# 修改代码...
git commit -m "feat(auth): 添加用户认证

Ref: logic_version/records/ver-20260808-002-auth.md"

# 4. 获取 commit hash 并更新决策记录
COMMIT=$(git rev-parse HEAD)
echo "Commit: $COMMIT"
# 编辑决策记录，填入 commit hash

# 5. 更新现行规则
# 编辑 logic_readme.md
git commit -m "docs: 更新认证规则"
```

### 场景 3: 追溯历史

```bash
# 查询某个文件为什么这么设计
python scripts/link_ver_git.py file src/auth.ts

# 查询某个提交的背景
python scripts/link_ver_git.py commit abc123d

# 浏览最近的决策
python scripts/link_ver_git.py list
```

## 最佳实践

### 1. 决策记录先行

高风险修改前先创建决策记录草稿，讨论和确认方案后再实施。

### 2. 小步提交

一个决策对应一个或少数几个 commit，保持原子性。

### 3. Commit 引用记录

每次重要提交都在 message 中引用对应的决策记录。

### 4. 定期整理

每周回顾 logic_change.md，及时归档完成的议案。

### 5. 保持简洁

文字说明专注于"为什么"，不重复 Git 能提供的信息。

## 关键约束

### 不可破坏约束（从 logic_readme.md 继承）

- INV-001: logic_readme.md 必须唯一
- INV-002: logic_change.md 必须唯一
- INV-003: logic_version/records/ 中的记录不可修改，只能追加
- INV-004: 历史记录不保存代码快照，只保存设计逻辑

### Git 集成新增约束

- **INV-005**: 高风险修改必须创建决策记录（VER-*）
- **INV-006**: 决策记录必须引用至少一个 Git commit hash
- **INV-007**: 重要 Git commit 必须在 message 中引用决策记录
- **INV-008**: 代码快照完全由 Git 管理，不在 logic_version/ 中保存

## 与其他系统的边界

### Recall 负责

- ✅ 记录需求和决策逻辑
- ✅ 管理"为什么"的文档
- ✅ 提供回溯和追踪
- ✅ 确保执行手册（各平台的 harness）是干净高效的

### Recall 不负责

- ❌ 具体的执行细节（交给各平台的 harness）
- ❌ 代码版本管理（交给 Git）
- ❌ 项目构建和部署（交给 CI/CD）
- ❌ 测试执行（交给测试框架）

### 类比

```
Recall = 部门法规（简洁明确的需求和决策）
Harness = 执行手册（具体的工具和实现）
Git = 档案室（代码的完整历史）
```

## 技术细节

### Python 脚本兼容性

- Python 3.6+
- 跨平台（Windows, macOS, Linux）
- 使用标准库，无外部依赖

### Git 要求

- Git 2.0+
- 支持基本命令：`log`, `show`, `commit`, `rev-parse`

### 文件编码

- 所有 Markdown 文件使用 UTF-8 编码
- 支持中英文混合

## 后续改进方向

### 短期（1-2 周）

- [ ] 添加 Git hooks 示例和安装脚本
- [ ] 创建 VS Code 扩展或快捷命令
- [ ] 添加更多示例和模板

### 中期（1-2 月）

- [ ] 开发 Web UI 可视化工具
- [ ] 支持更复杂的查询（按日期、作者、标签）
- [ ] 集成到 CI/CD 流程

### 长期（3-6 月）

- [ ] 支持多仓库关联
- [ ] 生成决策报告和图表
- [ ] AI 辅助决策记录生成

## 总结

**核心成果**：

1. ✅ **保持了原有架构** - 三层结构（readme/change/version）不变
2. ✅ **集成了 Git 管理** - 代码变化由 Git 负责
3. ✅ **建立了关联机制** - 通过 commit hash 双向追溯
4. ✅ **提供了辅助工具** - 初始化、创建、查询三个脚本
5. ✅ **完善了文档** - 模板、工作流、使用指南

**核心理念实现**：

> Recall 专注于用户是否能够清晰表达以及记录前因后果，
> 就像部门办事一样，法规是简洁的，
> 把用户的需求当做法规一样管理，
> 确保执行手册是干净高效的。

- **法规（需求）** → logic_readme.md
- **修改预案** → logic_change.md
- **修改记录** → logic_version/records/
- **代码历史** → Git
- **执行手册** → 各平台的 harness（不在 Recall 管理范围内）

这个架构实现了：
- 简洁的需求表达
- 完整的前因后果记录
- 清晰的版本控制
- 灵活的回档能力

**用户可以**：
- 随时回到任何历史版本（Git）
- 理解当时为什么这么做（决策记录）
- 追溯完整的变化链条（双向关联）
- 保持文档的简洁性（职责分离）
