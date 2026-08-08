# GitHub 发布指南

## 📦 第一步：初始化 Git 仓库

```bash
# 使用 Recall CLI 初始化（推荐）
recall init

# 或手动初始化
git init
git config user.name "你的名字"
git config user.email "your.email@example.com"
```

## 📝 第二步：提交所有文件

```bash
# 查看将要提交的文件
git status

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: Recall decision management system

- Core documentation (SKILL.md, CLAUDE.md, README.md)
- Unified CLI tool (recall command)
- Consistency validation tool
- Git integration scripts
- Decision record templates and examples

Ref: Project initialization"
```

## 🌐 第三步：在 GitHub 创建仓库

### 方法 A：使用 GitHub CLI（推荐）

```bash
# 如果已安装 gh CLI
gh auth login
gh repo create recall --public --source=. --remote=origin --push

# 设置仓库描述
gh repo edit --description "AI-powered decision management: Save design logic, not code snapshots"
gh repo edit --add-topic recall,decision-management,ai-assistant,git-integration
```

### 方法 B：手动创建

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `recall`
   - **Description**: `AI-powered decision management: Save design logic, not code snapshots`
   - **Visibility**: Public（或 Private）
   - **不要**勾选 "Initialize with README"（我们已经有了）
3. 点击 "Create repository"

## 🔗 第四步：关联远程仓库并推送

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/recall.git

# 或使用 SSH（如果配置了 SSH key）
git remote add origin git@github.com:YOUR_USERNAME/recall.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## ✅ 第五步：验证发布

访问你的仓库页面：
```
https://github.com/YOUR_USERNAME/recall
```

检查：
- ✅ README.md 正确显示
- ✅ 文件结构完整
- ✅ LICENSE 文件存在
- ✅ .gitignore 生效（敏感文件未上传）

## 🎨 第六步：优化仓库展示（可选）

### 添加 Topics（标签）

在仓库页面点击齿轮图标，添加标签：
```
recall, decision-management, ai-assistant, git-integration, 
claude-ai, documentation, developer-tools, python
```

### 编辑 About 描述

在仓库页面右侧 "About" 区域：
- **Description**: AI-powered decision management: Save design logic, not code snapshots
- **Website**: 可以添加你的博客或文档站点
- **Topics**: 添加相关标签

### 创建 Release（可选）

```bash
# 标记版本
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release

Features:
- Unified CLI tool
- Consistency validation
- Git integration
- Decision record templates"

# 推送标签
git push origin v1.0.0

# 使用 GitHub CLI 创建 Release
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "First stable release of Recall"
```

## 📊 第七步：添加徽章（可选）

在 README.md 顶部添加状态徽章：

```markdown
# Recall

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**保存设计逻辑，而非代码快照。**
```

## 🔄 后续更新流程

```bash
# 修改文件后
git add .
git commit -m "类型: 描述

详细说明

Ref: logic_version/records/xxx.md"

# 推送到 GitHub
git push origin main
```

## ⚠️ 发布前检查清单

- [ ] 已初始化 Git 仓库
- [ ] .gitignore 已创建
- [ ] LICENSE 文件已添加
- [ ] README.md 描述清晰
- [ ] 没有敏感信息（密钥、密码、个人信息）
- [ ] 所有脚本可执行
- [ ] 文档链接正确
- [ ] Git 用户信息已配置

## 🎯 推荐的仓库设置

### Branch Protection（分支保护）
对于个人项目可以跳过，但如果有协作者：
- Settings → Branches → Add rule
- 保护 `main` 分支
- 可选：要求 PR review

### GitHub Actions（自动化）
可以后续添加：
- 自动运行 `recall validate`
- 自动运行测试
- 自动生成文档

## 📚 参考资源

- [GitHub 快速开始](https://docs.github.com/get-started)
- [GitHub CLI 文档](https://cli.github.com/manual/)
- [语义化版本](https://semver.org/lang/zh-CN/)
