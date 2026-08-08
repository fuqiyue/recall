# logic_version 决策记录模板（Git 集成版）

本模板是 `logic-version-template.md` 的简化版，强调 Git 集成和实用性。
适用于个人项目或小团队，专注于记录"为什么"而非"是什么"。

**核心原则**：
- **代码变化交给 Git** - 不在此记录代码快照
- **文字说明记录原因** - 为什么改、背景、决策过程
- **通过 commit hash 关联** - 文档 ↔ 代码双向追溯

---

## 快速模板

```markdown
# VER-YYYYMMDD-NNN: <变更标题>

## 版本信息
- **版本号**: VER-YYYYMMDD-NNN
- **日期**: YYYY-MM-DD
- **状态**: effective | rejected | cancelled
- **关联 Commit**: `<git-commit-hash>`
- **关联 CHG**: CHG-YYYYMMDD-NNN (或 none)

## Git 追溯
```bash
# 查看这次变更的代码
git show <commit-hash>

# 查看相关文件的完整历史
git log --follow -- <file-path>

# 查看代码差异
git diff <before-commit> <after-commit>
```

## 修改原因

**背景**：
<为什么需要这次修改？遇到了什么问题？>

**用户需求/反馈**：
<来自用户的具体诉求，引用原话或 issue>

**痛点**：
<当前实现的问题是什么？>

## 决策过程

### 考虑的方案

**方案 A**：<描述>
- ✅ 优点：
- ❌ 缺点：
- 复杂度：低/中/高

**方案 B**：<描述>
- ✅ 优点：
- ❌ 缺点：
- 复杂度：低/中/高

### 最终选择

**选中方案**：方案 X

**选择原因**：
<为什么选这个方案？权衡了什么？>

## 影响范围

**修改的文件/模块**：
- `path/to/file1.py` - 修改了什么
- `path/to/file2.ts` - 添加了什么
- `path/to/file3.md` - 删除了什么

**影响的功能**：
<列出受影响的用户可见功能>

**破坏性变更**：
- 是/否
- 如果是，说明向后兼容策略

## 实施记录

**修改前状态**：
<简述修改前的行为>

**修改后状态**：
<简述修改后的行为>

**迁移步骤**（如需要）：
1. ...
2. ...

## 验证

**测试方法**：
<如何验证这次修改是成功的？>

**测试结果**：
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

**运行证据**：
<测试输出、截图、日志等>

## 回滚计划

**如何回滚**：
```bash
git revert <commit-hash>
# 或
git checkout <before-commit> -- <file-path>
```

**回滚风险**：
<回滚会导致什么问题？>

## 经验与教训

**可复用的原则**：
<这次决策中有什么可以在未来类似情况下复用的原则？>

**注意事项**：
<未来修改这块代码需要注意什么？>

## 关联

- **当前规则**: logic_readme.md#RULE-XXX
- **原始议案**: logic_change.md#CHG-YYYYMMDD-NNN
- **相关 Issue**: #123 (如有)
- **相关 PR**: #456 (如有)
- **文档更新**: README.md, CHANGELOG.md (如有)
```

---

## 使用指南

### 1. 创建决策记录

```bash
# 在 logic_version/records/ 创建新文件
touch logic_version/records/ver-20260808-001-add-dark-mode.md

# 使用模板填写
```

### 2. 实施代码修改

```bash
# 修改代码
git add .

# 提交时在 commit message 中引用决策记录
git commit -m "feat: 添加暗色模式支持

实现 CSS 变量驱动的主题切换系统

Ref: logic_version/records/ver-20260808-001-add-dark-mode.md"
```

### 3. 更新决策记录

```bash
# 获取刚才的 commit hash
COMMIT=$(git rev-parse HEAD)

# 在决策记录中填入 commit hash
# 编辑 ver-20260808-001-add-dark-mode.md
# - **关联 Commit**: `$COMMIT`
```

### 4. 归档议案

```bash
# 从 logic_change.md 移除已完成的 CHG
# 更新 logic_readme.md（如规则变化）
# 在 logic_version/index.md 中添加索引行
```

---

## 字段说明（最小集）

### 必填字段

| 字段 | 说明 | 示例 |
|------|------|------|
| 版本号 | VER-YYYYMMDD-NNN 格式 | VER-20260808-001 |
| 日期 | 归档日期 | 2026-08-08 |
| 状态 | effective/rejected/cancelled | effective |
| 关联 Commit | Git commit hash（完整或短版） | abc123def456 |
| 修改原因 | 为什么要改 | 用户反馈... |
| 决策过程 | 考虑了哪些方案，为什么选这个 | 方案A vs 方案B... |
| 影响范围 | 改了什么文件/功能 | 修改了样式系统 |

### 可选字段

| 字段 | 说明 | 何时使用 |
|------|------|----------|
| 关联 CHG | 原始议案 ID | 高风险修改 |
| 破坏性变更 | 是否不兼容 | API/数据结构变化 |
| 迁移步骤 | 如何升级 | 需要用户操作时 |
| 验证 | 测试证据 | 关键功能修改 |
| 回滚计划 | 如何撤销 | 高风险修改 |
| 经验与教训 | 可复用的知识 | 有通用价值时 |

---

## Git 工作流集成

### 标准流程

```
用户需求
  ↓
logic_change.md（记录议案）
  ↓
实施修改 + git commit（代码变化）
  ↓
logic_version/records/（归档原因）
  ↓
logic_readme.md（更新现行规则）
```

### Commit Message 规范

```
<type>: <简短描述>

<详细说明>

Ref: logic_version/records/<filename>.md
Closes: #<issue-number>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `docs`: 文档
- `test`: 测试
- `chore`: 构建/工具

### Git Hooks 集成（可选）

在 `.git/hooks/commit-msg` 中检查是否引用了决策记录：

```bash
#!/bin/bash
# 检查高风险提交是否引用了决策记录

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# 检查是否包含 Ref: logic_version/records/
if echo "$COMMIT_MSG" | grep -q "Ref: logic_version/records/"; then
  exit 0
fi

# 如果是 feat/fix/refactor，提示添加引用
if echo "$COMMIT_MSG" | grep -qE "^(feat|fix|refactor):"; then
  echo "⚠️  建议添加决策记录引用："
  echo "   Ref: logic_version/records/<filename>.md"
  echo ""
  echo "是否继续？(y/N)"
  read -r response
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

exit 0
```

---

## 辅助工具

### 快速创建决策记录

```python
# scripts/create_ver.py
import sys
from datetime import date
from pathlib import Path

def create_ver(title, scope):
    today = date.today().strftime("%Y%m%d")
    
    # 查找下一个序号
    records_dir = Path("logic_version/records")
    existing = list(records_dir.glob(f"ver-{today}-*.md"))
    next_num = len(existing) + 1
    
    # 生成文件名
    ver_id = f"VER-{today}-{next_num:03d}"
    filename = f"ver-{today}-{next_num:03d}-{scope}.md"
    filepath = records_dir / filename
    
    # 读取模板
    template = Path("references/logic-version-git-template.md").read_text()
    
    # 替换占位符
    content = template.replace("YYYYMMDD-NNN", f"{today}-{next_num:03d}")
    content = content.replace("<变更标题>", title)
    content = content.replace("YYYY-MM-DD", date.today().isoformat())
    
    # 写入文件
    filepath.write_text(content, encoding="utf-8")
    
    print(f"✅ 已创建决策记录: {filepath}")
    print(f"   版本号: {ver_id}")
    print(f"   请编辑文件并填写详细内容")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python scripts/create_ver.py <标题> <范围>")
        print("示例: python scripts/create_ver.py '添加暗色模式' 'dark-mode'")
        sys.exit(1)
    
    create_ver(sys.argv[1], sys.argv[2])
```

### 关联查询

```bash
# scripts/link_ver_git.sh
# 查询某个文件的决策记录和 Git 历史

FILE=$1

echo "📁 文件: $FILE"
echo ""

echo "📊 Git 历史:"
git log --oneline --follow -- "$FILE" | head -10
echo ""

echo "📝 相关决策记录:"
grep -r "path/to/$FILE" logic_version/records/ || echo "  (未找到)"
```

---

## 最佳实践

1. **决策记录先行** - 高风险修改前先写决策记录草稿
2. **Commit 引用记录** - 每次 commit 都引用对应的决策记录
3. **小步提交** - 一个决策记录对应一个或少数几个 commit
4. **定期整理** - 每周回顾 logic_change.md，及时归档
5. **保持简洁** - 文字说明专注于"为什么"，不重复 Git 能提供的信息

---

## 与完整模板的差异

| 维度 | 完整模板 | Git 集成版 |
|------|----------|------------|
| 字段数量 | 50+ | 10-15 |
| 适用场景 | 大型团队/正式审计 | 个人/小团队 |
| 治理模式 | collaborative | personal |
| 代码管理 | 可能需要快照 | 完全交给 Git |
| 决策流程 | 多阶段审批 | 简化流程 |
| 必填字段 | 严格 | 灵活 |

**何时升级到完整模板**：
- 团队规模 > 5 人
- 需要正式审计追溯
- 多环境部署（staging/prod）
- 有合规要求
