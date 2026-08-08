# Git 工作流集成指南

本文档说明 Recall 如何与 Git 集成，实现代码变化和决策记录的完整追溯。

## 核心理念

**职责分离**：
- **Git** - 管理代码的"是什么"（What changed）
  - 代码快照和差异
  - 完整的修改历史
  - 文件级别的版本控制
  
- **Recall** - 管理决策的"为什么"（Why changed）
  - 修改的原因和背景
  - 决策过程和权衡
  - 影响范围和注意事项

**关联方式**：通过 **commit hash** 双向链接

```
logic_version/ver-xxx.md  ←→  Git Commit
     (为什么改)                  (改了什么)
```

## 完整工作流

### 阶段 1: 提出修改（预案）

在 `logic_change.md` 中记录修改议案：

```markdown
## CHG-20260808-001: 添加暗色模式支持

- status: draft
- proposal_revision: 1

### 目标
用户反馈长时间使用眼睛疲劳，需要暗色模式支持

### 理由
...

### 影响范围
...
```

### 阶段 2: 实施修改（执行）

```bash
# 1. 修改代码
vim src/styles.css
vim src/components/ThemeToggle.tsx

# 2. 测试验证
npm test

# 3. Git 提交
git add src/styles.css src/components/ThemeToggle.tsx
git commit -m "feat: 添加暗色模式支持

- 使用 CSS 变量实现主题切换
- 添加主题切换按钮组件
- 默认跟随系统主题

Ref: logic_change.md#CHG-20260808-001"

# 4. 记录 commit hash
git rev-parse HEAD
# 输出: abc123def456789...
```

### 阶段 3: 归档决策（存档）

```bash
# 1. 创建决策记录
python scripts/create_ver.py "添加暗色模式支持" "dark-mode"
# 创建: logic_version/records/ver-20260808-001-dark-mode.md

# 2. 编辑决策记录，填入 commit hash
vim logic_version/records/ver-20260808-001-dark-mode.md
```

在决策记录中：

```markdown
## 版本信息
- **关联 Commit**: `abc123def456`

## Git 追溯
```bash
git show abc123def456
```

## 修改原因
用户反馈长时间使用白色背景眼睛疲劳...

## 决策过程
考虑了三种方案：
- 方案A: CSS 变量（选择）
- 方案B: 完全重写样式
- 方案C: 引入 UI 库

选择方案A因为...
```

### 阶段 4: 更新现行规则

```bash
# 1. 更新 logic_readme.md（如规则变化）
vim logic_readme.md

# 2. 从 logic_change.md 删除已完成的 CHG
vim logic_change.md

# 3. 提交文档更新
git add logic_readme.md logic_change.md logic_version/records/
git commit -m "docs: 归档暗色模式决策记录

- 更新现行规则
- 归档 CHG-20260808-001
- 创建 VER-20260808-001

Ref: logic_version/records/ver-20260808-001-dark-mode.md"
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

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat: 添加用户认证 |
| `fix` | Bug 修复 | fix: 修复登录超时问题 |
| `refactor` | 重构 | refactor: 优化数据库查询 |
| `docs` | 文档 | docs: 更新 API 文档 |
| `test` | 测试 | test: 添加单元测试 |
| `chore` | 构建/工具 | chore: 更新依赖 |
| `style` | 代码格式 | style: 格式化代码 |
| `perf` | 性能优化 | perf: 优化渲染性能 |

### Scope（可选）

指明修改的范围：`auth`, `ui`, `api`, `db` 等

### 示例

```bash
# 简单修改
git commit -m "fix: 修复用户名验证正则表达式"

# 中等修改
git commit -m "feat(auth): 添加 OAuth 登录支持

- 集成 Google OAuth 2.0
- 添加用户信息同步
- 更新认证流程文档

Ref: logic_change.md#CHG-20260808-002"

# 高风险修改（需要决策记录）
git commit -m "refactor(db): 迁移到新的数据库架构

破坏性变更：
- 用户表结构改变
- 需要运行迁移脚本

迁移步骤见决策记录

Ref: logic_version/records/ver-20260808-003-db-migration.md
BREAKING CHANGE: 需要手动运行 migrate.sql"
```

## 查询和追溯

### 从文件追溯到决策

```bash
# 查看某个文件的完整上下文
python scripts/link_ver_git.py file src/styles.css

# 输出:
# - Git 提交历史
# - 最近一次修改详情
# - 相关决策记录
```

### 从提交追溯到决策

```bash
# 查看某个提交的完整上下文
python scripts/link_ver_git.py commit abc123d

# 输出:
# - 提交信息和作者
# - 修改的文件列表
# - 相关决策记录
```

### 从决策追溯到代码

```bash
# 在决策记录中查找 commit hash
grep "关联 Commit" logic_version/records/*.md

# 查看代码变化
git show abc123def456
```

### 列出最近决策

```bash
python scripts/link_ver_git.py list

# 输出最近10条决策记录及其关联的 commit
```

## Git Hooks（可选增强）

### Pre-commit Hook

检查代码质量和测试：

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "🔍 运行预提交检查..."

# 运行测试
npm test
if [ $? -ne 0 ]; then
  echo "❌ 测试失败，请修复后再提交"
  exit 1
fi

# 运行 lint
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ 代码格式检查失败"
  exit 1
fi

echo "✅ 预提交检查通过"
exit 0
```

### Commit-msg Hook

检查 commit message 格式：

```bash
# .git/hooks/commit-msg
#!/bin/bash

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# 检查是否符合规范
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|refactor|docs|test|chore|style|perf)(\(.+\))?:"; then
  echo "❌ Commit message 格式不正确"
  echo ""
  echo "正确格式："
  echo "  <type>(<scope>): <描述>"
  echo ""
  echo "示例："
  echo "  feat: 添加新功能"
  echo "  fix(auth): 修复登录问题"
  exit 1
fi

# 高风险修改提示添加决策记录引用
if echo "$COMMIT_MSG" | grep -qE "^(feat|fix|refactor):"; then
  if ! echo "$COMMIT_MSG" | grep -q "Ref: logic_version/records/"; then
    echo "⚠️  建议添加决策记录引用："
    echo "   Ref: logic_version/records/<filename>.md"
    echo ""
    echo "是否继续？(y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
fi

exit 0
```

安装 hooks：

```bash
# 使 hooks 可执行
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
```

## 分支策略

### 简单项目（个人）

```
main（生产）
 ↓
feature-branches（功能分支）
```

工作流：
```bash
# 创建功能分支
git checkout -b feature/dark-mode

# 开发和提交
git commit -m "feat: 添加暗色模式"

# 合并到 main
git checkout main
git merge feature/dark-mode

# 删除功能分支
git branch -d feature/dark-mode
```

### 团队项目

```
main（生产）
 ↓
develop（开发）
 ↓
feature-branches（功能分支）
```

工作流：
```bash
# 从 develop 创建功能分支
git checkout develop
git checkout -b feature/dark-mode

# 开发和提交
git commit -m "feat: 添加暗色模式"

# 合并到 develop
git checkout develop
git merge feature/dark-mode

# 定期从 develop 发布到 main
git checkout main
git merge develop --no-ff
git tag v1.1.0
```

## 最佳实践

### 1. 小步提交

```bash
# ❌ 不好：一次提交太多东西
git commit -m "添加暗色模式、修复Bug、重构代码"

# ✅ 好：分成多个小提交
git commit -m "feat: 添加 CSS 变量定义"
git commit -m "feat: 添加主题切换组件"
git commit -m "feat: 实现主题持久化"
```

### 2. 原子性提交

每个提交应该是一个完整的、可工作的变更：

```bash
# ✅ 好：功能完整
git add src/ThemeToggle.tsx src/styles.css
git commit -m "feat: 添加主题切换功能"

# ❌ 不好：功能不完整
git add src/ThemeToggle.tsx
git commit -m "feat: 部分主题功能"
```

### 3. 决策记录先行

高风险修改前先创建决策记录草稿：

```bash
# 1. 创建决策记录草稿
python scripts/create_ver.py "数据库架构迁移" "db-migration"

# 2. 讨论和确认方案
# 编辑决策记录，填写方案 A/B/C 和权衡

# 3. 实施修改
# 代码修改...

# 4. 提交时引用决策记录
git commit -m "refactor(db): 迁移到新架构

Ref: logic_version/records/ver-20260808-003-db-migration.md"

# 5. 在决策记录中填入 commit hash
```

### 4. 定期整理

每周检查和归档：

```bash
# 检查未归档的提交
git log --oneline --since="1 week ago"

# 检查活跃议案
cat logic_change.md

# 归档完成的议案
# 将 CHG 转为 VER 记录
```

### 5. 保持同步

```bash
# 提交前拉取最新代码
git pull --rebase

# 解决冲突
# ...

# 推送
git push
```

## 故障排查

### 问题：找不到相关决策记录

**解决**：
```bash
# 1. 确认记录确实存在
ls logic_version/records/

# 2. 检查记录中是否包含正确的关键词
grep -r "文件名或commit" logic_version/records/

# 3. 手动查看 Git 历史
git log --all --grep="关键词"
```

### 问题：Commit 和决策记录对不上

**解决**：
```bash
# 1. 查看提交的完整信息
git show <commit-hash>

# 2. 在决策记录中搜索 commit hash
grep -r "<commit-hash>" logic_version/records/

# 3. 如果找不到，补充决策记录
```

### 问题：决策记录中的 commit hash 是旧的

**原因**：代码被修改但决策记录未更新

**解决**：
```bash
# 1. 查看文件的最新提交
git log -1 --format="%H" -- <file-path>

# 2. 更新决策记录中的 commit hash
# 编辑 logic_version/records/ver-xxx.md

# 3. 提交更新
git commit -m "docs: 更新决策记录中的 commit hash"
```

## 总结

**记住三个关键点**：

1. **Git 管理代码** - 用 `git commit` 记录代码变化
2. **Recall 管理决策** - 用 `logic_version/` 记录为什么改
3. **Commit hash 关联** - 通过 commit hash 双向追溯

遵循这个流程，你就能建立起完整的需求→决策→代码的追溯链。
