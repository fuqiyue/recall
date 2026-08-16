# 贡献指南

感谢你考虑为 Recall 做贡献！🎉

## 如何贡献

### 报告 Bug

发现问题？请在 [Issues](https://github.com/fuqiyue/recall/issues) 中报告：

- **清晰的标题**：简短描述问题
- **复现步骤**：详细说明如何触发问题
- **预期行为**：你期望发生什么
- **实际行为**：实际发生了什么
- **环境信息**：
  - OS: Windows/Linux/macOS
  - Python 版本
  - Git 版本
  - Recall 版本

### 提交功能请求

有好点子？我们很乐意听到：

1. 先在 Issues 中搜索，避免重复
2. 创建新 Issue，选择 "Feature Request" 标签
3. 说明：
   - **为什么需要这个功能**（解决什么问题）
   - **期望的行为**（如何使用）
   - **可能的实现方案**（可选）

### 提交代码

#### 开发流程

1. **Fork 仓库**

2. **克隆到本地**
   ```bash
   git clone https://github.com/你的用户名/recall.git
   cd recall
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **进行修改**
   - 遵循 Recall 自己的工作流！
   - 先记录议案到 `logic_change.md`
   - 实施修改
   - 归档决策到 `logic_version/records/`
   - 更新 `logic_readme.md`

5. **测试**
   ```bash
   # 运行验证
   ./recall.sh validate
   
   # 手动测试相关功能
   ./recall.sh status
   ./recall.sh query file <path>
   ```

6. **提交**
   ```bash
   git add .
   git commit -m "feat: 添加某功能

   详细说明修改内容和原因
   
   Ref: logic_version/records/VER-YYYYMMDD-HHMM-description.md"
   ```

7. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <简短描述>

<详细说明>

Ref: logic_version/records/<record-file>.md
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档修改
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（不是新功能也不是修复）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

#### 代码风格

- **Python**: 遵循 PEP 8
- **文档**: 简洁清晰，中文优先
- **注释**: 解释"为什么"，而不是"做什么"

#### Pull Request 检查清单

在提交 PR 前，确保：

- [ ] 代码通过 `recall validate` 验证
- [ ] 更新了相关文档（README, CLAUDE.md 等）
- [ ] 添加/更新了测试（如适用）
- [ ] Commit messages 遵循规范
- [ ] 创建了对应的 VER 记录（重要修改；历史索引见 logic_version/index.md）
- [ ] PR 描述清楚说明了：
  - 做了什么修改
  - 为什么需要这个修改
  - 如何测试

### 文档贡献

改进文档同样重要！

- 修正错误、改进表述
- 添加示例和使用场景
- 翻译文档（如需要）

直接编辑 Markdown 文件并提交 PR 即可。

## 开发环境设置

```bash
# 1. 安装 Python 3.11+
python --version

# 2. 初始化 Recall（如果是新克隆）
./recall.sh init

# 3. 验证环境
./recall.sh status
```

## 项目结构

```
recall/
├── recall.bat / recall.sh      # CLI 入口
├── scripts/                    # Python 脚本
│   ├── cli.py                 # 命令解析
│   ├── validator.py           # 验证逻辑
│   ├── query.py               # 查询功能
│   └── record.py              # 记录功能
├── logic_readme.md            # 当前规则
├── logic_change.md            # 活跃议案
├── logic_version/             # 历史记录
│   ├── records/              # VER 记录
│   └── index.md              # 索引
└── docs/                      # 文档
```

## 测试

目前主要通过手动测试和 `recall validate` 验证。

计划添加：
- 单元测试（pytest）
- 集成测试
- 端到端测试

欢迎贡献测试框架！

## 行为准则

- **尊重**：友善对待每个人
- **建设性**：提供有价值的反馈
- **协作**：一起让 Recall 更好

## 需要帮助？

- 查看 [Issues](https://github.com/fuqiyue/recall/issues) 中标记为 `good first issue` 的任务
- 在 [Discussions](https://github.com/fuqiyue/recall/discussions) 提问
- 阅读 [CLAUDE.md](CLAUDE.md) 了解项目设计理念

---

再次感谢你的贡献！每一个 PR、Issue 和建议都让 Recall 变得更好。❤️
