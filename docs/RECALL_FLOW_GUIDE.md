# Recall 工作流详解

> **让 AI 记住"为什么这样设计"，而不是"代码长什么样"**

Recall 是一套为 AI 代理设计的项目逻辑追溯系统，让每次修改都能理解当初的设计意图，避免重复踩坑或破坏已有约束。

---

## 核心理念

**代码版本交给 Git，设计逻辑交给 Recall。**

| Git 负责 | Recall 负责 |
|---------|-----------|
| 代码的"是什么" | 决策的"为什么" |
| 代码快照、diff | 原因、背景、权衡 |
| `git log`, `git show` | logic_version/*.md |
| commit hash | 文档中引用 commit |

这样做的好处：
- ✅ **避免上下文爆炸** — 不把完整代码历史塞进文档
- ✅ **防止设计退化** — 修改前能看到"当初为什么这么做"
- ✅ **保持文档简洁** — 只记录决策逻辑，不记录代码快照

---

## 文档结构

```
<项目根>/
├── logic_readme.md              # 当前有效规则（唯一真相源）
├── logic_change.md              # 活跃修改议案（未生效）
├── logic_version/               # 历史决策记录（不可变）
│   ├── index.md                 # 决策记录索引
│   └── records/                 # VER-* 决策文档
│       └── logic_version-YYYYMMDD-NNN-<scope>.md
├── references/                  # 模板与参考文档
└── CLAUDE.md / AGENTS.md        # AI 代理入口
```

### 三个核心文档

| 文档 | 作用 | 特征 | 何时修改 |
|-----|------|------|---------|
| **logic_readme.md** | 当前生效的规则、代码地图、验证入口 | 唯一真相源 | 代码行为实际改变时 |
| **logic_change.md** | 尚未生效的修改议案 | 协调工具 | 需要跨会话追踪时 |
| **logic_version/records/** | 已关闭变更的决策记录 | 不可变历史 | 高风险变更完成后 |

---

## 标准工作流

### 完整流程图

```
┌─────────────────┐
│  用户提出需求    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ 1. 读取当前上下文             │
│  • logic_readme.md（规则）   │
│  • logic_change.md（议案）   │
│  • 相关代码、测试、运行证据   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 2. 判断变更风险等级          │
│  • 简单修复 → 直接修改       │
│  • 中等变更 → 给出计划       │
│  • 高风险 → 创建议案         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3. 记录议案（可选）           │
│  logic_change.md + CHG-ID   │
│  • 修改意图、影响范围        │
│  • 方案选择、验证方式        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4. 实施修改                  │
│  git commit（代码变化）      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 5. 归档决策（高风险）         │
│  logic_version/records/     │
│  • 为什么这样做              │
│  • 考虑过哪些方案            │
│  • 如何验证和回滚            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 6. 更新现行规则              │
│  logic_readme.md            │
│  • RULE-ID 生效              │
│  • 代码地图更新              │
│  • 验证入口更新              │
└─────────────────────────────┘
```

---

## 三条变更通道

根据**风险等级**选择不同的流程深度，避免过度流程化：

### 🟢 简单修复

**条件**：
- 局部、隔离
- 不影响公共契约、持久化数据、安全边界
- 意图和测试直接明确

**流程**：
```
读规则 → 修改代码 → git commit → 更新文档（如需要）
```

**示例**：修复拼写错误、调整内部实现、优化性能

---

### 🟡 中等变更

**条件**：
- 涉及多个相关文件
- 对外语义不变，但内部结构调整
- 无未确认的长期设计选择

**流程**：
```
读规则 → 给出计划 → 修改代码 → git commit 
      → 更新规则 → 保留 VER-*（可选）
```

**示例**：重构函数、添加新功能、修改配置

---

### 🔴 高风险变更

**条件**：
- 改变对外语义
- 涉及数据迁移、权限边界
- 需要引入适配层、全局开关、双读写

**流程**：
```
读规则 → 找消费者 → 分析历史决策 → 创建 CHG-ID
      → 用户确认 → 实施修改 → git commit
      → 创建 VER-* → 更新 logic_readme.md → 关闭 CHG
```

**示例**：API 破坏性变更、数据库迁移、权限模型调整

---

## 实战示例

### 场景 1：简单修复（拼写错误）

```bash
# 1. 读取上下文（快速浏览规则）
cat logic_readme.md

# 2. 修改代码
# 修复 typo: getUserName → getUsername

# 3. 提交
git commit -m "fix: 修正函数名拼写 getUserName → getUsername"

# 4. 文档影响
# docs_impact: none（内部实现，无契约变化）
```

---

### 场景 2：中等变更（添加功能）

```bash
# 1. 读取上下文
cat logic_readme.md
cat logic_change.md

# 2. 给出计划
# "添加用户头像上传功能"
# - 新增 /upload endpoint
# - 文件大小限制 5MB
# - 支持 jpg/png
# - 存储到 S3

# 3. 实施修改
# （编写代码、测试）

# 4. 提交
git commit -m "feat: 添加用户头像上传功能

- 新增 POST /api/upload endpoint
- 支持 jpg/png，最大 5MB
- 存储到 S3 bucket
"

# 5. 更新 logic_readme.md
# 在代码地图中新增 upload.ts 条目
# 在规则表中添加 RULE-010（头像限制）

# 6. 可选：创建 VER-*（如涉及安全策略）
```

---

### 场景 3：高风险变更（API 破坏性变更）

```bash
# 1. 读取上下文
cat logic_readme.md
cat logic_change.md
git log --follow -- api/users.ts

# 2. 创建议案
# logic_change.md 中添加 CHG-001
# - 意图：将 API 响应从 camelCase 改为 snake_case
# - 影响：所有客户端需要更新
# - 方案：双格式支持 3 个月 + 废弃警告

# 3. 用户确认方案

# 4. 实施修改
# （添加格式适配层、废弃警告、测试）

# 5. 提交
git commit -m "feat: API 响应格式迁移到 snake_case

添加 Accept-Format header 支持：
- application/json (新默认，snake_case)
- application/json+camelCase (兼容，3 个月后移除)

Breaking change: 默认响应格式变更
Ref: logic_version/records/logic_version-20260808-003-api-format.md
"

# 6. 创建 VER-* 决策记录
python scripts/create_ver.py "API 格式迁移" "api-format"

# 编辑 logic_version/records/logic_version-20260808-003-api-format.md：
# - 为什么改：客户端团队统一要求 snake_case
# - 考虑的方案：
#   A. 立即切换（被拒，破坏现有客户端）
#   B. 双格式永久支持（被拒，维护成本高）
#   C. 双格式 + 3 个月废弃期（✓ 采纳）
# - 影响：iOS/Android/Web 客户端需要迁移
# - 验证：集成测试 + 客户端确认
# - 回滚：恢复 camelCase 为默认，保留 header 选项

# 7. 更新 logic_readme.md
# - 新增 RULE-011：API 响应格式为 snake_case
# - 更新代码地图中 api/formatters.ts 条目
# - 添加废弃期验证入口

# 8. 关闭议案
# logic_change.md 中标记 CHG-001 状态为 promoting
# 3 个月后完全移除兼容代码，再标记为 closed
```

---

## Git 集成

### Commit Message 规范

```
<type>: <简短描述>

<详细说明>

Ref: logic_version/records/<filename>.md
```

**Type 类型**：
- `feat`: 新功能
- `fix`: 修复 bug
- `refactor`: 重构
- `docs`: 文档更新
- `test`: 测试
- `chore`: 构建/工具链

### 关联查询

```bash
# 查询文件的完整历史和决策记录
python scripts/link_ver_git.py file logic_readme.md

# 查询某个提交的详情
python scripts/link_ver_git.py commit abc123d

# 列出最近的决策记录
python scripts/link_ver_git.py list

# Git 原生命令
git log --follow -- <file-path>  # 文件完整历史
git show <commit-hash>            # 提交详细内容
```

---

## 历史记录保存什么？

### ✅ 应该保存

- **为什么做这个决策**
- **考虑过哪些方案**（A/B/C）
- **为什么选择当前方案**
- **影响了谁**（消费者、依赖方）
- **如何验证和回滚**

### ❌ 不应该保存

- 完整代码快照（Git 已有）
- 逐行 diff（Git 已有）
- 详细实现细节（代码注释更合适）
- 原始对话记录（过于冗长）
- 思维推理过程（非决策依据）

---

## VER 记录模板

```markdown
---
version_id: VER-20260808-003
scope: api-format
date: 2026-08-08
status: active
related_commits: abc123d, def456e
supersedes: none
---

## 为什么做这个决策？

客户端团队统一要求使用 snake_case，现有 camelCase 导致转换层重复实现。

## 考虑过哪些方案？

| 方案 | 优点 | 缺点 | 结果 |
|-----|------|------|------|
| A. 立即切换 | 简单直接 | 破坏现有客户端 | ❌ 拒绝 |
| B. 双格式永久支持 | 无破坏性 | 维护成本高 | ❌ 拒绝 |
| C. 双格式 + 3 个月废弃期 | 平衡迁移成本 | 需要临时兼容代码 | ✅ 采纳 |

## 影响了谁？

- iOS 客户端：需要更新网络层
- Android 客户端：需要更新网络层
- Web 前端：需要更新 API 客户端

## 如何验证？

- 集成测试覆盖两种格式
- 客户端团队确认迁移完成
- 3 个月后检查无 camelCase header 请求

## 如何回滚？

恢复 camelCase 为默认格式，保留 header 选项继续支持 snake_case。
```

---

## 统一 CLI 工具

所有功能整合到 `recall` 命令（Windows）或 `./recall.sh`（Linux/macOS）：

```bash
# 查看系统状态
recall status

# 验证一致性
recall validate

# 创建决策记录
recall new "描述" tag

# 列出最近记录
recall list

# 查询文件历史
recall query file <路径>

# 查询提交详情
recall query commit <hash>

# 查看帮助
recall help
```

---

## 初始化新项目

**首次使用 Recall**：

```bash
# 交互式初始化
python scripts/init_recall.py

# 非交互式（CI/容器环境）
python scripts/init_recall.py --non-interactive \
    --name "张三" --email "zhangsan@example.com"
```

这个脚本会：
1. ✅ 检查 Git 是否已安装
2. ✅ 初始化 Git 仓库（如未初始化）
3. ✅ 配置 Git 用户信息（姓名和邮箱）
4. ✅ 创建 .gitignore 文件
5. ✅ 创建初始提交

---

## 最佳实践

### 1. 分离状态

- `logic_readme.md` — 已生效
- `logic_change.md` — 未生效
- `logic_version/` — 已结束

**绝对不要**：
- ❌ 创建 `logic_readme-v2.md`
- ❌ 在 `logic_readme.md` 中写未生效方案
- ❌ 在 `logic_change.md` 中保留已关闭议案

### 2. 单一真相源

每个语义关注点指定一处权威位置：
- 产品需求 → Spec Kit
- 技术约束 → Steering 文档
- 当前运行逻辑 → logic_readme.md
- 活跃决策 → logic_change.md
- 历史原因 → logic_version/

### 3. 按需读取历史

**不要**每次修改都读完整历史，**只在**以下情况读取 `logic_version/`：
- 当前文档直接引用某个 VER-ID
- 发生冲突，需要理解历史约束
- 追溯兼容性策略

### 4. 风险相称的流程

- 简单修复 → 不创建 CHG/VER
- 中等变更 → 可选创建 VER-*
- 高风险 → 必须创建 CHG → VER → 更新 RULE

**不要为了"符合流程"强行制造文档。**

---

## 治理模式

根据团队规模选择：

| 模式 | 适用场景 | 字段数 | 审查要求 |
|-----|---------|-------|---------|
| **personal** | 单人或单人+AI | 8 | 自审即可 |
| **collaborative** | 小团队有分工 | +9 | PR/CI 审查 |
| **compliance** | 正式审计留存 | +13 | 完整 Brief |

---

## 常见问题

### Q: 为什么不直接用 Git log？

A: Git log 记录"代码变成什么样"，Recall 记录"为什么这样改"。两者互补，不是替代。

### Q: 每次修改都要创建 VER-* 吗？

A: **不需要**。简单修复直接提交即可，只有高风险变更才需要完整 VER 记录。

### Q: logic_change.md 什么时候清空？

A: 议案完成后立即移除。它只保留**活跃**的未生效议案。

### Q: 如何处理多人协作？

A: 升级到 `collaborative` 模式，配合 PR/CI/CODEOWNERS 使用。Recall 记录决策，Git 平台控制权限。

### Q: 历史记录会不会越来越大？

A: 不会。只保存关键决策的提炼，不保存完整代码。常规项目一年大约 10-30 条 VER 记录。

---

## 更多资源

- **[SKILL.md](../SKILL.md)** — 完整使用指南
- **[CLAUDE.md](../CLAUDE.md)** — Claude AI 使用说明
- **[logic_readme.md](../logic_readme.md)** — 当前有效规则
- **[references/](../references/)** — 模板与参考文档

---

**记住**：Recall 的目标是让 AI 能够回忆"当初为什么这么设计"，而不是把每次开发变成文书流程。保持简洁，风险相称，按需记录。
