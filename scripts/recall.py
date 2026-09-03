#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 统一命令行工具
整合所有 Recall 功能到一个简洁的 CLI 接口
"""

import re
import sys
import os
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

# 决策记录文件名，与 validate.py / link_ver_git.py / create_ver.py 一致（RULE-009）
RECORD_NAME_RE = re.compile(r'^logic_version-\d{8}-\d{3}-.+\.md$', re.IGNORECASE)


def find_version_records(records_dir):
    """按规范文件名列出决策记录，跳过 README.md 等说明文件。"""
    if not records_dir.exists():
        return []
    return sorted(
        path for path in records_dir.glob("*.md") if RECORD_NAME_RE.match(path.name)
    )

def _force_utf8_when_redirected():
    """重定向到文件/管道时把输出流切成 UTF-8。

    Windows 上重定向后的 stdout 用 ANSI 代码页（如 cp936），
    帮助信息里的 emoji 会触发 UnicodeEncodeError。
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def print_help():
    """显示帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║                   Recall CLI - 统一命令行工具                    ║
╚══════════════════════════════════════════════════════════════╝

📖 使用方法:
  python scripts/recall.py <命令> [参数...]

🔧 可用命令:

  init
    初始化 Recall 项目（配置 Git、启用自动同步）
    示例: recall init

  sync [选项]
    自动保存并同步：默认把工作区变更自动提交，再拉取变基并推送
    示例: recall sync
    示例: recall sync --commit-message "docs: 更新 Recall 规则"
    示例: recall sync --manual    # 切换为手动模式（不自动提交）
    示例: recall sync --auto      # 恢复自动保存（默认）
    示例: recall sync --disable   # 完全关闭自动同步

  new <描述> <短标签>
    创建新的决策记录
    示例: recall new "添加暗色模式" "dark-mode"

  query file <文件路径>
    查询文件的修改历史和相关决策记录
    示例: recall query file src/main.py

  query commit <commit-hash>
    查询 Git 提交的详细信息和相关决策记录
    示例: recall query commit abc123f

  query intent <INT-ID>
    反向查询：从功能意图定位关联规则、决策记录和代码锚点
    （"我要改功能 X，会涉及哪些规则和文件"）
    示例: recall query intent INT-20260816-005

  list [数量]
    列出最近的决策记录（默认 10 条）
    示例: recall list
    示例: recall list 20

  validate
    验证 Recall 系统的一致性
    检查 RULE-ID、CHG-ID、决策记录的完整性
    示例: recall validate

  status
    显示当前 Recall 系统状态
    包括规则数量、活跃变更、最近决策等
    示例: recall status

  conflicts
    检测规则间的潜在冲突
    分析 RULE-* 和 CHG-* 是否存在逻辑矛盾
    示例: recall conflicts

  help
    显示此帮助信息
    示例: recall help

📚 更多信息:
  - 文档: README.md
  - 使用方式与原则: SKILL.md
  - 现行规则与代码地图: logic_readme.md
  - 工作流程: CLAUDE.md

💡 提示:
  所有命令都可以在项目根目录或子目录中执行
  Recall 会自动查找最近的项目根目录
"""
    print(help_text)

def cmd_init(args):
    """初始化命令。参数原样转交 init_recall。"""
    try:
        import init_recall
        return init_recall.main(args)
    except ImportError:
        print("❌ 错误: 找不到 init_recall.py")
        return 1

def cmd_sync(args):
    """同步 Git 远端。"""
    try:
        import git_sync
        return git_sync.main(args)
    except ImportError:
        print("❌ 错误: 找不到 git_sync.py")
        return 1
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return 1

def cmd_new(args):
    """创建新决策记录"""
    if len(args) < 2:
        print("❌ 错误: 缺少参数")
        print("用法: recall new <描述> <短标签>")
        print("示例: recall new \"添加暗色模式\" \"dark-mode\"")
        return 1

    title = args[0]
    scope = args[1]

    try:
        import create_ver

        # 路径解析（项目根、模板、输出目录）由 create_ver 内部完成
        return create_ver.create_ver_record(title, scope)
    except ImportError:
        print("❌ 错误: 找不到 create_ver.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def cmd_query(args):
    """查询命令"""
    if len(args) < 1:
        print("❌ 错误: 缺少查询类型")
        print("用法: recall query <file|commit|intent> <参数>")
        print("示例: recall query file src/main.py")
        print("示例: recall query commit abc123f")
        print("示例: recall query intent INT-20260816-005")
        return 1

    query_type = args[0].lower()

    try:
        import link_ver_git

        if query_type == "file":
            if len(args) < 2:
                print("❌ 错误: 缺少文件路径")
                print("用法: recall query file <文件路径>")
                return 1
            return link_ver_git.query_file_history(args[1])

        elif query_type == "commit":
            if len(args) < 2:
                print("❌ 错误: 缺少 commit hash")
                print("用法: recall query commit <commit-hash>")
                return 1
            return link_ver_git.query_commit_details(args[1])

        elif query_type == "intent":
            if len(args) < 2:
                print("❌ 错误: 缺少意图编号")
                print("用法: recall query intent <INT-YYYYMMDD-NNN>")
                return 1
            return link_ver_git.query_intent(args[1])

        else:
            print(f"❌ 错误: 未知的查询类型 '{query_type}'")
            print("支持的类型: file, commit, intent")
            return 1

    except ImportError:
        print("❌ 错误: 找不到 link_ver_git.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def cmd_list(args):
    """列出决策记录"""
    limit = 10
    if len(args) > 0:
        try:
            limit = int(args[0])
        except ValueError:
            print(f"❌ 错误: 无效的数量 '{args[0]}'")
            return 1

    try:
        import link_ver_git
        return link_ver_git.list_recent_decisions(limit)
    except ImportError:
        print("❌ 错误: 找不到 link_ver_git.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def cmd_validate():
    """验证一致性"""
    try:
        import validate
        return validate.main()
    except ImportError:
        print("❌ 错误: 找不到 validate.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def classify_porcelain(porcelain_output):
    """把 ``git status --porcelain`` 输出分成已跟踪变更与未跟踪文件两组路径。

    RULE-020（收尾归零）：未跟踪文件是 AI 解题过程残留（探针脚本、临时
    测试、草稿）的主要形态，而 RULE-011 让它们默认不进自动保存提交，
    因此必须单列提示，不能与已跟踪修改混成一个"未提交变更"计数。
    只分类、不删除。
    """
    tracked = []
    untracked = []
    for raw_line in (porcelain_output or "").splitlines():
        if not raw_line.strip():
            continue
        code = raw_line[:2]
        path = raw_line[3:].strip() if len(raw_line) > 3 else raw_line.strip()
        if " -> " in path:  # 重命名：只关心新路径
            path = path.split(" -> ", 1)[1]
        if code == "??":
            untracked.append(path)
        else:
            tracked.append(path)
    return tracked, untracked


def cmd_status():
    """显示系统状态"""
    try:
        import re
        from pathlib import Path

        # 查找项目根目录
        def find_project_root():
            current = Path.cwd()
            while current != current.parent:
                if (current / "logic_readme.md").exists():
                    return current
                current = current.parent
            return Path.cwd()

        root = find_project_root()

        print("\n" + "=" * 60)
        print("📊 Recall 系统状态")
        print("=" * 60 + "\n")

        # 检查 logic_readme.md
        readme_path = root / "logic_readme.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                rules = re.findall(r'\bRULE-\d{3}\b', content)
                unique_rules = set(rules)
                print(f"📋 现行规则: {len(unique_rules)} 个 RULE-ID")
        else:
            print("📋 现行规则: ⚠️  logic_readme.md 不存在")

        # 检查 logic_change.md
        change_path = root / "logic_change.md"
        if change_path.exists():
            with open(change_path, 'r', encoding='utf-8') as f:
                content = f.read()
                changes = re.findall(r'\bCHG-\d{8}-\d{3}\b', content)
                unique_changes = set(changes)
                print(f"🔄 活跃变更: {len(unique_changes)} 个 CHG-ID")
        else:
            print("🔄 活跃变更: ⚠️  logic_change.md 不存在")

        # 检查决策记录
        records_dir = root / "logic_version" / "records"
        if records_dir.exists():
            records = find_version_records(records_dir)
            print(f"📚 决策记录: {len(records)} 个文件")

            # 显示最近 3 条：文件名自带日期和序号，按名字倒序比 mtime 稳定
            if records:
                print(f"\n   最近的决策记录:")
                for record in sorted(records, key=lambda x: x.name, reverse=True)[:3]:
                    print(f"   • {record.name}")
        else:
            print("📚 决策记录: ⚠️  logic_version/records/ 不存在")

        # 检查 Git 状态
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%h %s'],
                capture_output=True,
                text=True,
                cwd=root,
                timeout=5
            )
            if result.returncode == 0:
                last_commit = result.stdout.strip()
                print(f"\n🔖 最近提交: {last_commit}")
            else:
                print(f"\n🔖 最近提交: ⚠️  无法读取")

            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=root,
                timeout=5
            )
            if status_result.returncode == 0:
                tracked, untracked = classify_porcelain(status_result.stdout)
                if tracked:
                    print(f"⚠️  未提交变更: {len(tracked)} 个已跟踪文件")
                if untracked:
                    # RULE-020：未跟踪文件单列，只提示不删除
                    print(f"🧹 未跟踪文件（待处置候选，RULE-020 收尾归零）: {len(untracked)} 个")
                    shown = untracked[:10]
                    for path in shown:
                        print(f"   • {path}")
                    if len(untracked) > len(shown):
                        print(f"   … 另 {len(untracked) - len(shown)} 个")
                    print("   交付物请 git add；非交付物请删除或加入 .gitignore")
                if not tracked and not untracked:
                    print(f"✅ 工作区状态: 干净")
        except (OSError, subprocess.SubprocessError):
            print(f"\n🔖 Git: ⚠️  未安装或不可用")

        print("\n" + "=" * 60)
        print("💡 提示: 运行 'recall validate' 检查系统一致性")
        print("=" * 60 + "\n")

        return 0

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def cmd_conflicts():
    """检测规则冲突"""
    try:
        import detect_conflicts
        return detect_conflicts.main()
    except ImportError:
        print("❌ 错误: 找不到 detect_conflicts.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def main():
    """主入口"""
    _force_utf8_when_redirected()

    if len(sys.argv) < 2:
        print_help()
        return 0

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        'init': lambda: cmd_init(args),
        'sync': lambda: cmd_sync(args),
        'new': lambda: cmd_new(args),
        'query': lambda: cmd_query(args),
        'list': lambda: cmd_list(args),
        'validate': lambda: cmd_validate(),
        'status': lambda: cmd_status(),
        'conflicts': lambda: cmd_conflicts(),
        'help': lambda: print_help() or 0,
        '--help': lambda: print_help() or 0,
        '-h': lambda: print_help() or 0,
    }

    if command in commands:
        try:
            return commands[command]()
        except Exception as e:
            print(f"\n❌ 执行命令时出错: {e}")
            return 1
    else:
        print(f"❌ 错误: 未知命令 '{command}'")
        print("运行 'recall help' 查看可用命令")
        return 1

if __name__ == "__main__":
    sys.exit(main())
