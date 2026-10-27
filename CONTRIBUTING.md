# 贡献指南

欢迎通过问题反馈、功能建议、文档和代码改进参与 Recall。

## 反馈问题与建议

在 [Issues](https://github.com/fuqiyue/recall/issues) 中查看相关讨论，再选择对应模板：

- **问题反馈**：提供复现步骤、预期与实际行为，以及操作系统、Python、Git 版本和 Recall 提交号。
- **功能建议**：说明使用场景、期望的操作方式和希望达到的结果；实现思路可选。
- **安全问题**：使用[安全说明](SECURITY.md)中的私密报告渠道。

## 准备开发环境

安装 Python 3.11+ 和 Git，Fork 仓库后克隆到本地：

```bash
git clone https://github.com/你的用户名/recall.git
cd recall
git switch -c docs/your-change
python scripts/recall.py status
```

CLI 和测试使用 Python 标准库。开发代码功能时可使用 `feat/` 或 `fix/` 等描述性分支名。

## 修改流程

1. 按 [SKILL.md](SKILL.md)读取根现行文档、根任务公报，再运行 `python scripts/recall.py route <目标路径或关键词>`，读取相关领域规则与任务正文。
2. 按影响选择变更深度。局部文案、排版等 simple 修改通常直接编辑；需要 CHG 的任务按[任务模板](references/logic-change-template.md)在 `logic_changes/<task>/logic_change.md` 保留计划与进度，并更新根公报。
3. 实施修改，按实际影响同步所属现行文档，并完成必要验证。
4. 按[变更生命周期](references/change-lifecycle.md)完成所需归档与产物清理，再提交 PR。

完整分流标准以 [SKILL.md](SKILL.md)为准。文档贡献可以从修正表述、补充操作示例或校正链接开始。

## 验证修改

在仓库根目录运行文档检查：

```bash
python scripts/recall.py validate
python scripts/recall.py audit
python scripts/recall.py index
git diff --check
```

修改代码时，运行与改动相关的测试；完整测试入口为：

```bash
python -m unittest discover -s tests
```

现有自动化测试覆盖 CLI、Git 同步、文档审计与验证、任务上下文和工作区管理等功能。[GitHub Actions](.github/workflows/validate.yml)在 Ubuntu 与 Windows 上运行验证、测试和审计。

验证结果请记录具体命令、结果和环境，便于复核。

## 提交与 Pull Request

提交前用 `git diff` 和 `git status` 核对内容，再选择本次修改的文件加入暂存区。提交信息使用 Conventional Commits 格式：

```text
docs: 梳理项目快速开始与文档导航
```

常用类型包括 `feat`、`fix`、`docs`、`style`、`refactor`、`test` 和 `chore`。有对应 VER 的变更，在提交正文中补充实际记录路径：

```text
Ref: logic_version/records/<实际记录文件名>.md
```

推送你的分支并创建 PR，在描述中说明：

- 修改解决的具体问题及结果。
- 涉及的范围、文档和必要的兼容说明。
- 执行过的验证及其结果。

## 代码与文档风格

- Python 遵循 PEP 8，沿用相关模块的组织方式。
- 文档中文优先，使用简洁、具体的表述，示例与当前 CLI 保持一致。
- 注释说明设计依据；现行规则由所属 `logic_readme.md` 维护，操作说明通过链接引用。
- 对已归档记录的补充或纠正使用新的记录，保留原始内容以便追溯。

## 项目结构

```text
recall/
├── recall.bat / recall.sh      # 平台命令入口
├── SKILL.md                    # AI 操作入口
├── scripts/
│   ├── recall.py              # CLI 入口与命令分发
│   ├── recall_common.py       # 共享能力
│   ├── recall_audit/          # 文档审计模块
│   └── ...                   # Git、路由、验证与工作区工具
├── tests/                     # unittest 自动化测试
├── logic_readme.md            # 全局现行规则与领域导航
├── logic_change.md            # 全项目任务公报
├── logic_domains/             # 领域规则与文件地图
├── logic_changes/             # 活跃任务正文（按需创建）
├── logic_version/             # 变更归档与索引
├── references/                # 操作指引与模板
├── explainers/                # HTML 解释文档
└── .github/                   # CI 与社区模板
```

## 协作交流

反馈尽量附上具体场景与证据，讨论时尊重彼此的经验与判断。需要选择贡献方向时，可以从 [Issues](https://github.com/fuqiyue/recall/issues) 和 [README 文档导航](README.md#按需阅读)开始。
