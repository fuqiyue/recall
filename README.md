# Recall

**AI 驱动的项目逻辑追溯系统** — 让每次代码修改都能理解当初的设计意图。

Recall 回答"为什么这样设计"，而不是"代码长什么样"。代码版本交给 Git，设计逻辑交给 Recall。

---

## 这是什么？

在 AI 辅助开发中，代理常常因为缺乏上下文而：
- 🔄 重复踩坑（不知道为什么要避开某个方案）
- 💥 破坏性修改（不知道这个设计保护了什么）
- 🤷 过度兼容（不知道 V1 已经没有真实用户）

Recall 通过记录 **决策原因、权衡、影响分析**，让 AI 代理能够：
- 📝 理解历史约束，避免重复错误
- 🔍 追溯设计意图，做出知情决策
- ⚖️ 评估风险等级，选择合适的修改通道

---

## 快速开始

### 1. 初始化

```bash
# 推荐：使用统一 CLI
recall init

# 或直接调用脚本
python scripts/init_recall.py
```

这会：
- ✅ 检查/初始化 Git 仓库
- ✅ 配置 Git 用户信息
- ✅ 创建必要的文档结构
- ✅ 完成初始提交

**非交互模式**（CI/容器环境）：

```bash
recall init --non-interactive --name "张三" --email "zhangsan@example.com"
```

### 2. 日常使用

修改代码前的标准流程：

```bash
# 1. 查看当前规则
recall status

# 2. 阅读相关决策历史
cat logic_readme.md        # 当前生效规则
cat logic_change.md        # 活跃修改议案

# 3. 查询特定文件的历史
recall query file <path>

# 4. 修改代码并记录决策
recall new "描述" tag      # 创建决策记录
git commit -m "..."        # 提交代码变化
```

### 3. 完整工作流

```
需求 → 记录议案（logic_change.md）
    ↓
实施 → 提交代码（git commit）
    ↓
归档 → 保存决策（logic_version/）
    ↓
更新 → 现行规则（logic_readme.md）
```

---

## 核心理念

### Git vs Recall 职责分工

| 维度 | Git 负责 | Recall 负责 |
|------|----------|-------------|
| **回答** | "改了什么" | "为什么改" |
| **存储** | 代码快照、diff | 原因、背景、权衡 |
| **工具** | `git log`, `git show` | logic_version/*.md |
| **关联** | commit hash | 文档中引用 commit |

### 文档结构

```
logic_readme.md          # 📗 当前生效规则（唯一真相源）
logic_change.md          # 📙 活跃修改记录（临时）
logic_version/           # 📚 历史决策归档（只读）
  ├── records/           #    已完成的决策记录
  └── index.md           #    快速索引
```

**单一真相源原则**：
- ✅ `logic_readme.md` 是当前唯一权威
- ✅ `logic_change.md` 只记录进行中的修改
- ✅ `logic_version/` 只在需要追溯时查询

---

## 三条变更通道

Recall 根据风险等级提供三条通道，避免过度流程化：

| 通道 | 适用场景 | 流程深度 |
|------|----------|----------|
| **简单修复** | 局部 Bug、UI 调整、单文件改动 | 快速修复，无需创建记录 |
| **中等变更** | 添加功能、多文件修改、架构调整 | 先给计划，可选创建 CHG |
| **高风险变更** | API 修改、数据迁移、破坏性变更 | 完整 Recall 流程，必须记录 |

详见 [SKILL.md](SKILL.md#三条变更通道)。

---

## 避免常见陷阱

### ❌ 错误方式
```
收到 Bug → 直接让 AI 修复 → AI 只看当前代码 → 实施修改
→ Bug 修复了，但破坏了其他功能
```

### ✅ 正确方式（Recall）
```
收到 Bug → 读取 logic_readme.md → 高风险？
→ Recall 历史决策 → "为什么这么设计？"
→ 分析影响范围 → 提供方案对比 → 用户决策
→ 实施修改 → 更新文档
→ Bug 修复且不破坏设计
```

---

## CLI 工具

所有功能已整合到 `recall` 命令：

```bash
recall status          # 查看系统状态
recall validate        # 验证一致性
recall new "描述" tag  # 创建决策记录
recall list            # 列出最近记录
recall query file <路径>    # 查询文件历史
recall query commit <hash>  # 查询提交详情
recall help            # 查看完整帮助
```

---

## 文档

- **[SKILL.md](SKILL.md)** — 完整使用指南（核心原则、三条通道、调用模式）
- **[CLAUDE.md](CLAUDE.md)** — Claude AI 集成说明
- **[docs/RECALL_FLOW_GUIDE.md](docs/RECALL_FLOW_GUIDE.md)** — 详细流程指南（含实战案例）
- **[logic_readme.md](logic_readme.md)** — 当前生效规则与代码地图
- **[logic_change.md](logic_change.md)** — 活跃修改议案
- **[references/](references/)** — 模板与参考文档

---

## 与其他工具兼容

Recall 可与现有工具组合使用：

- **Kiro Steering** — 提供长期背景（product.md / tech.md）
- **Spec Kit** — 提供具体规格和需求
- **Recall** — 记录"为什么这么实现"的决策逻辑
- **Codex Plan** — 提供一次性实施计划

每个工具负责自己的领域，通过 `logic_readme.md` 作为集成点。

---

## 设计原则

- ✅ 记录决策原因，不记录代码快照
- ✅ 单一真相源（logic_readme.md）
- ✅ 风险相称的流程深度（三条通道）
- ✅ 按需回忆，不强制加载全部历史
- ✅ 模块化兼容，可接入其他工具

---

## 许可

本项目使用 MIT 许可证。
