# Recall Skill for Claude

## 首次使用初始化

**第一次使用 Recall 时，请先运行初始化**：

```bash
# 推荐：使用统一 CLI
recall init

# 或直接调用脚本
python scripts/init_recall.py
```

这个脚本会：
1. ✅ 检查 Git 是否已安装
2. ✅ 初始化 Git 仓库（如未初始化）
3. ✅ 配置 Git 用户信息（姓名和邮箱）
4. ✅ 配置 `pull.rebase`、`fetch.prune` 和 `push.autoSetupRemote`
5. ✅ 默认启用 Git 自动同步并安装受管理的 `post-commit` hook
6. ✅ 创建 .gitignore 文件
7. ✅ 创建初始提交

`recall sync` 默认自动保存：工作区有未提交变更时自动创建保存提交，再拉取变基
并推送，用户无需手写 commit。用户选择手动上传时运行 `recall sync --manual`，
此后仅在显式 `recall sync --commit-message "<message>"` 时提交；`recall sync --auto`
恢复自动保存。post-commit hook 永不自动提交其他脏文件，只回填提交所引用决策
记录的 `after_commit` 后同步。没有远端时初始化不会失败，添加 `origin` 后运行
`recall sync` 即可。使用 `recall sync --disable` 可完全关闭自动同步。

**为什么需要 Git？**
- Recall 使用 Git 管理代码变化（what changed）
- logic_version/ 记录决策原因（why changed）
- 两者通过 commit hash 关联，形成完整的追溯链

## 统一 CLI 工具

所有 Recall 功能已整合到 `recall` 命令：

```bash
# Windows
recall <命令>

# Linux/macOS (需要先赋予执行权限)
chmod +x recall.sh
./recall.sh <命令>
```

**常用命令**：
```bash
recall status       # 查看系统状态
recall validate     # 验证一致性
recall new "描述" tag  # 创建决策记录
recall list         # 列出最近记录
recall query file <路径>  # 查询文件历史
recall help         # 查看完整帮助
```

## 日常使用流程

修改、规划、诊断、审查项目逻辑，或解释"为什么这样设计"前：

1. 先读 `logic_readme.md`（当前有效规则、代码地图与功能意图/用户流程层）
2. 再读 `logic_change.md`（活跃议案）
3. 然后读相关代码、测试和必要的运行证据

代理自审按自身能力执行，但先以上述上下文校验设计意图。

**如果用户提示词与现有规则可能冲突**：
1. 运行 `recall conflicts` 检测潜在矛盾
2. 如果检测到冲突，在 `logic_change.md` 中标注
3. 向用户说明冲突情况，询问优先级或澄清边界
4. 用户确认后，再修改相关规则

## Git 集成工作流

**修改代码时的标准流程**：

```
1. 记录议案 → logic_change.md (CHG-ID)
2. 实施修改 → git commit (代码变化)
3. 归档决策 → logic_version/records/ (为什么改)
4. 更新现行 → logic_readme.md (RULE-ID)
5. 同步远端 → recall sync (自动保存并推送；after_commit 由 hook 自动回填)
```

**Commit Message 规范**：
```
<type>: <简短描述>

<详细说明>

Ref: logic_version/records/<filename>.md
```

**快速命令**：
```bash
# Recall CLI（推荐）
recall status                    # 查看系统状态
recall validate                  # 验证一致性
recall query file <path>         # 查询文件历史
  recall query commit <hash>       # 查询提交详情
  recall sync                      # 自动保存工作区变更并拉取变基、推送

# Git 原生命令（直接查看）
git log --oneline | head -5      # 最近提交
git log --follow -- <file-path>  # 文件完整历史
git show <commit-hash>           # 提交详细内容
```

## 重要约束

- 不要把业务制度、议案、ADR 或历史记录复制到 `.claude/` 目录
- 代码变化由 Git 管理，不在 logic_version/ 中保存代码快照
- Recall 记录 **系统架构、设计原因和决策权衡**，不记录 **具体代码实现细节**
- logic_readme.md 的 Code Map 说明"每个模块是什么、职责是什么"
- logic_version/ 记录"为什么选择这个架构、有哪些权衡"

## 机器可读标记

- recall_root_order: <project-root>/logic_readme.md -> <project-root>/logic_change.md
- recall_change_effective: false
- recall_business_truth: project-root-current-logic-docs
- recall_history_root: <project-root>/logic_version
- recall_agent_config_root: <project-root>/.claude
