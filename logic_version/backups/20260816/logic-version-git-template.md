# logic_version 决策记录模板（Git 集成版）

本模板是 `logic-version-template.md` 的简化版，强调 Git 集成和实用性。
适用于个人项目或小团队，专注于记录"为什么"而非"是什么"。

**核心原则**：
- **代码变化交给 Git** - 不在此记录代码快照
- **文字说明记录原因** - 为什么改、背景、决策过程
- **通过 commit hash 关联** - 文档 ↔ 代码双向追溯

---

## 快速模板

控制字段名（`version_id`/`date`/`status` 等）以 `logic-version-template.md` 为准；
`validate.py` 按这些字段名校验，改名会让校验静默失效（RULE-009）。
本块内不要嵌套 ``` 代码围栏：`scripts/create_ver.py` 以第一个独立的 ``` 行为块结束标记。

```markdown
# VER-YYYYMMDD-NNN: <变更标题>

## 记录控制

- version_id: VER-YYYYMMDD-NNN
- version_slug: logic_version-YYYYMMDD-NNN-<scope>
- status: effective
- date: YYYY-MM-DD
- change_id: none
- before_commit: <before-commit-hash>
- after_commit: _待填写_

## 为什么做这个决策？

**背景**：
<为什么需要这次修改？遇到了什么问题？>

**用户需求/反馈**：
<来自用户的具体诉求，引用原话或 issue>

**需求拆解（归档时从 CHG 原样搬入；无 CHG 的记录填 none）**：
- raw_request: <用户原始请求的稳定引用或一句忠实转述>
- decomposition: <拆解出的功能点/工作项>
- fit_analysis: <复用/替代/新增哪个 INT-*，插入哪条 FLOW-* 的哪一步，是否触碰 UXI-*>

## 决策过程

**方案 A**：<描述>（优点 / 缺点 / 复杂度：低-中-高）

**方案 B**：<描述>（优点 / 缺点 / 复杂度：低-中-高）

**选中方案与原因**：
<为什么选这个方案？权衡了什么？>

## 影响范围

**修改的文件/模块**：
- `path/to/file1.py` - 修改了什么

**破坏性变更**：是/否（如是，说明向后兼容策略）

## 验证方式

<如何验证这次修改成功？测试命令与结果。
代码差异用 git 查看：git show <commit>；git log --follow -- <file-path>>

## 回滚方式

<如何撤销：git revert <commit>，或说明配置回退步骤与回滚风险>

## 经验与教训

<可复用的原则与注意事项；没有填 none>

## 关联

- current_logic: logic_readme.md#RULE-XXX
- proposal_id: none
- code/tests: <相关文件>
```

---

## 使用指南

### 1. 创建决策记录

```bash
# 推荐：用 CLI 自动取号并按模板生成
recall new "添加暗色模式支持" "add-dark-mode"

# 生成 logic_version/records/logic_version-20260808-001-add-dark-mode.md
```

### 2. 实施代码修改

```bash
# 修改代码
git add .

# 提交时在 commit message 中引用决策记录
git commit -m "feat: 添加暗色模式支持

实现 CSS 变量驱动的主题切换系统

Ref: logic_version/records/logic_version-20260808-001-add-dark-mode.md"
```

### 3. 更新决策记录

提交后无需手动操作：post-commit hook 解析 commit message 的 Ref 行，
把记录中的 `- after_commit: _待填写_` 占位符自动回填为提交哈希（RULE-013）。
记录文件与代码在同一提交中时，即使没有 Ref 行也会按提交文件清单回填。
`before_commit` 由 `recall new` 在创建时填入当时的 HEAD。

```bash
# 仅在 hook 未启用时才需要手动回填：
git rev-parse --short HEAD   # 填入 - after_commit: <hash>
```

### 4. 归档议案

```bash
# 先把 CHG 的 raw_request/decomposition/fit_analysis 搬入本记录（需求保全，
# 否则删除 CHG 后需求拆解只剩 git 考古可查），再从 logic_change.md 移除该 CHG
# 同议题落选方案：把其需求原文与否决原因并入本记录"决策过程"的方案分析；
# 曾独立立案的落选 CHG 另建 status: rejected 的精简 VER 并同样搬运三字段
# 更新 logic_readme.md（如规则变化）
# 在 logic_version/index.md 中添加索引行
```

---

## 字段说明（最小集）

### 必填字段

| 字段 | 说明 | 示例 |
|------|------|------|
| version_id | VER-YYYYMMDD-NNN 格式 | VER-20260808-001 |
| date | 归档日期 | 2026-08-08 |
| status | effective/rejected/cancelled | effective |
| before_commit | 变更前基线 commit（recall new 自动填入） | b8db894 |
| after_commit | 实施提交的 hash（hook 自动回填 `_待填写_` 占位符） | beb24d6 |
| ## 为什么做这个决策？ | 为什么要改 | 用户反馈... |
| raw_request / decomposition / fit_analysis | 需求拆解三字段；有 CHG（change_id != none）时必须在归档时从 CHG 原样搬入，无 CHG 填 none | 见 logic-change-template.md |
| ## 影响范围 | 改了什么文件/功能 | 修改了样式系统 |
| ## 验证方式 | 如何验证修改成功 | 测试命令与结果 |
| ## 回滚方式 | 如何撤销 | git revert ... |

### 可选字段

| 字段 | 说明 | 何时使用 |
|------|------|----------|
| change_id | 原始议案 ID | 高风险修改 |
| 决策过程 | 考虑了哪些方案，为什么选这个 | 有多个候选方案时 |
| 破坏性变更 | 是否不兼容 | API/数据结构变化 |
| 迁移步骤 | 如何升级 | 需要用户操作时 |
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

实现见 `scripts/create_ver.py`（即 `recall new` 命令）。此处不再内嵌副本：
模板里的示例代码无法随实现更新，曾因此出现文件命名漂移（ver-* vs logic_version-*）。

```bash
recall new "添加暗色模式" "dark-mode"
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
