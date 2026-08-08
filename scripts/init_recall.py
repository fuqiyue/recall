#!/usr/bin/env python3
"""
Recall 初始化脚本
用于引导用户配置 Git 并初始化 Recall 项目结构
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_git_installed():
    """检查 Git 是否已安装"""
    success, _, _ = run_command("git --version", check=False)
    return success


def check_git_repo(project_root):
    """检查是否已经是 Git 仓库"""
    git_dir = project_root / ".git"
    return git_dir.exists()


def init_git_repo(project_root):
    """初始化 Git 仓库"""
    print("\n📦 正在初始化 Git 仓库...")
    success, stdout, stderr = run_command("git init", cwd=project_root)

    if success:
        print("✅ Git 仓库初始化成功")
        return True
    else:
        print(f"❌ Git 仓库初始化失败: {stderr}")
        return False


def check_git_config():
    """检查 Git 用户配置"""
    success_name, name, _ = run_command("git config user.name", check=False)
    success_email, email, _ = run_command("git config user.email", check=False)

    return success_name and success_email, name, email


def configure_git_user():
    """配置 Git 用户信息"""
    print("\n👤 配置 Git 用户信息")
    print("这将用于记录每次修改的作者信息\n")

    name = input("请输入你的名字 (例如: 张三): ").strip()
    email = input("请输入你的邮箱 (例如: zhangsan@example.com): ").strip()

    if not name or not email:
        print("❌ 用户名和邮箱不能为空")
        return False

    # 配置用户信息（全局）
    run_command(f'git config --global user.name "{name}"')
    run_command(f'git config --global user.email "{email}"')

    print(f"\n✅ Git 用户配置完成:")
    print(f"   名字: {name}")
    print(f"   邮箱: {email}")
    return True


def create_gitignore(project_root):
    """创建 .gitignore 文件"""
    gitignore_path = project_root / ".gitignore"

    if gitignore_path.exists():
        print("✅ .gitignore 已存在")
        return True

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Recall temporary
.tmp-tests/
logic_version/working/

# Claude
.claude/settings.local.json
"""

    try:
        gitignore_path.write_text(gitignore_content, encoding="utf-8")
        print("✅ 已创建 .gitignore")
        return True
    except Exception as e:
        print(f"❌ 创建 .gitignore 失败: {e}")
        return False


def create_initial_commit(project_root):
    """创建初始提交"""
    print("\n📝 创建初始提交...")

    # 添加所有文件
    run_command("git add .", cwd=project_root)

    # 创建初始提交
    commit_msg = """chore: 初始化 Recall 项目

- 初始化项目结构
- 配置 Git 版本控制
- Recall 系统用于记录需求和决策逻辑
"""

    success, stdout, stderr = run_command(
        f'git commit -m "{commit_msg}"',
        cwd=project_root,
        check=False
    )

    if success:
        print("✅ 初始提交完成")
        return True
    else:
        if "nothing to commit" in stderr:
            print("ℹ️  没有需要提交的更改")
            return True
        print(f"❌ 提交失败: {stderr}")
        return False


def show_git_status(project_root):
    """显示当前 Git 状态"""
    print("\n📊 当前 Git 状态:")
    success, stdout, _ = run_command("git status --short", cwd=project_root)
    if stdout:
        print(stdout)
    else:
        print("  (工作目录干净)")


def show_welcome_message():
    """显示欢迎信息"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           欢迎使用 Recall 需求管理系统                    ║
║                                                           ║
║  Recall 专注于记录"为什么"，而不是"怎么做"                ║
║  代码变化由 Git 管理，决策逻辑由 Recall 记录              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def show_completion_message():
    """显示完成信息"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  🎉 初始化完成！                          ║
║                                                           ║
║  接下来你可以：                                           ║
║  1. 在 logic_change.md 中记录修改预案                    ║
║  2. 实施修改并用 git commit 记录代码变化                 ║
║  3. 在 logic_version/ 中归档决策说明                     ║
║                                                           ║
║  提示：每次 git commit 时，记得关联 logic_version 说明   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def main():
    """主函数"""
    show_welcome_message()

    # 确定项目根目录
    project_root = Path(__file__).parent.parent.resolve()
    print(f"📁 项目路径: {project_root}\n")

    # 1. 检查 Git 是否安装
    print("🔍 检查 Git 安装状态...")
    if not check_git_installed():
        print("❌ 未检测到 Git，请先安装 Git")
        print("   下载地址: https://git-scm.com/downloads")
        sys.exit(1)
    print("✅ Git 已安装")

    # 2. 检查是否已经是 Git 仓库
    is_git_repo = check_git_repo(project_root)
    if is_git_repo:
        print("✅ 已经是 Git 仓库")
    else:
        # 初始化 Git 仓库
        if not init_git_repo(project_root):
            sys.exit(1)

    # 3. 检查 Git 用户配置
    print("\n🔍 检查 Git 用户配置...")
    has_config, name, email = check_git_config()

    if has_config:
        print(f"✅ Git 用户已配置:")
        print(f"   名字: {name}")
        print(f"   邮箱: {email}")

        reconfigure = input("\n是否重新配置？(y/N): ").strip().lower()
        if reconfigure == 'y':
            if not configure_git_user():
                sys.exit(1)
    else:
        print("⚠️  Git 用户信息未配置")
        if not configure_git_user():
            sys.exit(1)

    # 4. 创建 .gitignore
    print("\n🔍 检查 .gitignore...")
    create_gitignore(project_root)

    # 5. 显示当前状态
    show_git_status(project_root)

    # 6. 询问是否创建初始提交
    if not is_git_repo:
        create_initial = input("\n是否创建初始提交？(Y/n): ").strip().lower()
        if create_initial != 'n':
            create_initial_commit(project_root)

    # 7. 完成
    show_completion_message()

    print("\n💡 快速开始:")
    print("   - 查看文档: cat README.md")
    print("   - 查看当前规则: cat logic_readme.md")
    print("   - 记录修改预案: 编辑 logic_change.md")
    print("   - 查看 Git 历史: git log --oneline")
    print()


if __name__ == "__main__":
    main()
