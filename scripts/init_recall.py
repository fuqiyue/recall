#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 初始化脚本

引导用户配置 Git 并初始化 Recall 项目结构。

支持非交互运行（CI、代理环境、stdin 不可用时）：
    python scripts/init_recall.py --non-interactive --name "张三" --email "z@example.com"

首次初始化默认启用 Git 自动同步；使用 --no-auto-sync 可关闭。
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


class Aborted(Exception):
    """用户中断，或非交互模式下缺少必要输入。"""


def run_git(args, cwd=None):
    """运行 git 命令，返回 (成功, stdout, stderr)。

    参数以列表传入且不经过 shell：多行 commit message、
    含空格或引号的用户名都能原样传递，也不会被 shell 解释。
    """
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, ValueError) as e:
        return False, "", str(e)
    return (
        result.returncode == 0,
        (result.stdout or "").strip(),
        (result.stderr or "").strip(),
    )


def check_git_installed():
    """检查 Git 是否可用"""
    ok, _, _ = run_git(["--version"])
    return ok


def describe_repo_state(project_root):
    """判断 project_root 与 Git 仓库的关系。

    返回 "repo_root" / "nested" / "none"。

    以 `git rev-parse --show-toplevel` 为准，而不是判断 .git 是否存在：
      - 上层目录是仓库时，project_root 本身并不是仓库；
      - 残留或损坏的 .git 会让路径检查误判为"已经是仓库"。
    """
    ok, toplevel, _ = run_git(["rev-parse", "--show-toplevel"], cwd=project_root)
    if not ok or not toplevel:
        return "none"
    try:
        same = Path(toplevel).resolve() == project_root.resolve()
    except OSError:
        same = False
    return "repo_root" if same else "nested"


def init_git_repo(project_root):
    """初始化 Git 仓库"""
    print("\n📦 正在初始化 Git 仓库...")
    ok, _, stderr = run_git(["init"], cwd=project_root)
    if ok:
        print("✅ Git 仓库初始化成功")
        return True
    print(f"❌ Git 仓库初始化失败: {stderr}")
    return False


def read_git_config(project_root):
    """读取生效的 Git 用户配置，返回 (name, email)，缺失为 None"""
    values = []
    for key in ("user.name", "user.email"):
        ok, value, _ = run_git(["config", "--get", key], cwd=project_root)
        values.append(value if ok and value else None)
    return values[0], values[1]


def write_git_config(project_root, name, email, scope):
    """写入 Git 用户配置。scope 为 "global" 或 "local"。"""
    flag = "--global" if scope == "global" else "--local"
    for key, value in (("user.name", name), ("user.email", email)):
        ok, _, stderr = run_git(["config", flag, key, value], cwd=project_root)
        if not ok:
            print(f"❌ 写入 {key} 失败: {stderr}")
            return False
    return True


def prompt_text(label, interactive):
    """读一行输入；非交互模式或 stdin 关闭时抛 Aborted 而不是崩溃"""
    if not interactive:
        raise Aborted(f"非交互模式下缺少必要输入：{label.strip()}")
    try:
        return input(label).strip()
    except (EOFError, KeyboardInterrupt):
        raise Aborted("输入已中断")


def confirm(label, default, ask):
    """确认提示。ask 为 False 时直接返回 default，不读 stdin。

    EOF 按 default 处理，不中断：本函数的每个调用点都有安全默认值，
    读不到输入不构成失败。`sys.stdin.isatty()` 不足以判断 stdin 可用——
    Windows/Git Bash 下 `< /dev/null` 会把 NUL 当字符设备，isatty 返回
    True，但第一次读取就 EOF。真正的判据是读取本身。

    KeyboardInterrupt 仍然中断：那是用户显式打断，不是缺少输入。
    """
    if not ask:
        return default
    suffix = "(Y/n)" if default else "(y/N)"
    try:
        answer = input(f"{label} {suffix}: ").strip().lower()
    except EOFError:
        print("(stdin 不可用，按默认值处理)")
        return default
    except KeyboardInterrupt:
        raise Aborted("输入已中断")
    if not answer:
        return default
    return answer in ("y", "yes")


def configure_git_user(project_root, name, email, scope, interactive):
    """配置 Git 用户信息。name/email 已给出时不再询问。"""
    print("\n👤 配置 Git 用户信息")
    print("这将用于记录每次修改的作者信息")
    scope_label = "全局 (--global)" if scope == "global" else "当前仓库 (--local)"
    print(f"写入范围: {scope_label}\n")

    if not name:
        name = prompt_text("请输入你的名字 (例如: 张三): ", interactive)
    if not email:
        email = prompt_text("请输入你的邮箱 (例如: zhangsan@example.com): ", interactive)

    if not name or not email:
        print("❌ 用户名和邮箱不能为空")
        return False

    if not write_git_config(project_root, name, email, scope):
        return False

    print("\n✅ Git 用户配置完成:")
    print(f"   名字: {name}")
    print(f"   邮箱: {email}")
    return True


GITIGNORE_CONTENT = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.tmp-tests/

# Recall 临时文件
logic_version/working/
*.tmp
*.bak

# 敏感信息
.env
.env.local
secrets/
*.key
*.pem

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# Claude
.claude/settings.local.json
"""


def create_gitignore(project_root):
    """创建 .gitignore 文件（已存在则不改动）"""
    gitignore_path = project_root / ".gitignore"

    if gitignore_path.exists():
        print("✅ .gitignore 已存在")
        return True

    try:
        gitignore_path.write_text(GITIGNORE_CONTENT, encoding="utf-8")
        print("✅ 已创建 .gitignore")
        return True
    except OSError as e:
        print(f"❌ 创建 .gitignore 失败: {e}")
        return False


COMMIT_MESSAGE = """chore: 初始化 Recall 项目

- 初始化项目结构
- 配置 Git 版本控制
- Recall 系统用于记录需求和决策逻辑
"""


def create_initial_commit(project_root):
    """创建初始提交"""
    print("\n📝 创建初始提交...")

    ok, _, stderr = run_git(["add", "."], cwd=project_root)
    if not ok:
        print(f"❌ 添加文件失败: {stderr}")
        return False

    # message 作为独立 argv 传入，多行内容不会被 shell 截断
    ok, stdout, stderr = run_git(
        ["commit", "-m", COMMIT_MESSAGE], cwd=project_root
    )

    if ok:
        print("✅ 初始提交完成")
        return True

    combined = f"{stdout}\n{stderr}"
    if "nothing to commit" in combined or "nothing added to commit" in combined:
        print("ℹ️  没有需要提交的更改")
        return True

    print(f"❌ 提交失败: {stderr or stdout}")
    return False


def show_git_status(project_root):
    """显示当前 Git 状态"""
    print("\n📊 当前 Git 状态:")
    ok, stdout, _ = run_git(["status", "--short"], cwd=project_root)
    if ok and stdout:
        print(stdout)
    elif ok:
        print("  (工作目录干净)")
    else:
        print("  ⚠️  无法读取 Git 状态")


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


def build_parser():
    parser = argparse.ArgumentParser(
        prog="recall init",
        description="初始化 Recall 项目（配置 Git、创建 .gitignore、可选初始提交）",
    )
    parser.add_argument("--name", help="Git user.name，跳过交互提问")
    parser.add_argument("--email", help="Git user.email，跳过交互提问")
    parser.add_argument(
        "--scope",
        choices=("global", "local"),
        default="global",
        help="用户配置写入范围，默认 global",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="从不读取 stdin；缺少必要输入时报错退出",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="所有确认项按默认值处理，不提问",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="即使是新仓库也不创建初始提交",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="自动同步使用的 Git 远端名称，默认 origin",
    )
    parser.add_argument(
        "--no-auto-sync",
        action="store_true",
        help="不启用 Git 自动同步（默认启用）",
    )
    return parser


def _run(argv):
    args = build_parser().parse_args(argv)

    # stdin 不可用时自动降级为非交互，不再抛 EOFError
    stdin_usable = bool(sys.stdin) and sys.stdin.isatty()
    interactive = stdin_usable and not args.non_interactive
    ask = interactive and not args.yes

    name = args.name or os.environ.get("RECALL_GIT_NAME") or os.environ.get("GIT_AUTHOR_NAME")
    email = args.email or os.environ.get("RECALL_GIT_EMAIL") or os.environ.get("GIT_AUTHOR_EMAIL")

    show_welcome_message()

    project_root = Path(__file__).parent.parent.resolve()
    print(f"📁 项目路径: {project_root}")
    if not interactive:
        print("🤖 非交互模式：确认项按默认值处理\n")
    else:
        print()

    # 1. Git 是否安装
    print("🔍 检查 Git 安装状态...")
    if not check_git_installed():
        print("❌ 未检测到 Git，请先安装 Git")
        print("   下载地址: https://git-scm.com/downloads")
        return 1
    print("✅ Git 已安装")

    # 2. 仓库状态
    state = describe_repo_state(project_root)
    created_repo = False
    if state == "repo_root":
        print("✅ 已经是 Git 仓库")
    elif state == "nested":
        print("⚠️  当前目录位于另一个 Git 仓库内部，本身不是仓库根目录")
        if confirm("是否在此目录单独初始化仓库？", False, ask):
            if not init_git_repo(project_root):
                return 1
            created_repo = True
        else:
            print("ℹ️  跳过初始化，继续使用上层仓库")
    else:
        if not init_git_repo(project_root):
            return 1
        created_repo = True

    # 3. 用户配置
    print("\n🔍 检查 Git 用户配置...")
    current_name, current_email = read_git_config(project_root)
    explicit = bool(name or email)

    if current_name and current_email and not explicit:
        print("✅ Git 用户已配置:")
        print(f"   名字: {current_name}")
        print(f"   邮箱: {current_email}")
        if confirm("\n是否重新配置？", False, ask):
            if not configure_git_user(project_root, None, None, args.scope, interactive):
                return 1
    else:
        if not current_name or not current_email:
            print("⚠️  Git 用户信息未配置")
        if not configure_git_user(
            project_root,
            name or current_name,
            email or current_email,
            args.scope,
            interactive,
        ):
            return 1

    # 4. .gitignore
    print("\n🔍 检查 .gitignore...")
    create_gitignore(project_root)

    # 5. Git 自动同步配置
    print("\n🔍 配置 Git 自动同步...")
    try:
        import git_sync

        auto_sync = not args.no_auto_sync
        if not git_sync.configure_git_sync(project_root, enabled=auto_sync, remote=args.remote):
            return 1
    except ImportError:
        print("❌ 错误: 找不到 git_sync.py")
        return 1

    # 6. 状态
    show_git_status(project_root)

    # 7. 初始提交（仅新建仓库时）
    if created_repo and not args.no_commit:
        if confirm("\n是否创建初始提交？", True, ask):
            create_initial_commit(project_root)

    # 8. 配置完成后立即同步；自动保存默认开启（recall.autoCommit），
    #    脏工作区会作为一次自动保存提交进入同步。
    if not args.no_auto_sync:
        try:
            sync_status = git_sync.sync_repository(project_root)
            if sync_status == 2:
                print("ℹ️  初始同步暂未完成；可配置远端后运行 recall sync")
        except Exception as e:
            print(f"⚠️  初始同步失败（本地配置不受影响）: {e}")

    # 9. 完成
    show_completion_message()

    print("\n💡 快速开始:")
    print("   - 查看文档: README.md")
    print("   - 查看当前规则: logic_readme.md")
    print("   - 记录修改预案: 编辑 logic_change.md")
    print("   - 查看 Git 历史: git log --oneline")
    print("   - 手动同步远端: recall sync")
    print()
    return 0


def main(argv=None):
    """入口。返回退出码，供 recall.py 直接使用。"""
    try:
        return _run(sys.argv[1:] if argv is None else list(argv))
    except Aborted as e:
        print(f"\n⚠️  {e}")
        print("   提示: 用 --name/--email 传入，或设置 RECALL_GIT_NAME / RECALL_GIT_EMAIL")
        return 130


if __name__ == "__main__":
    sys.exit(main())
