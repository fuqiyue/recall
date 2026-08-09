#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 统一命令行工具
整合所有 Recall 功能到一个简洁的 CLI 接口
"""

import sys
import os
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

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
    初始化 Recall 项目（配置 Git、创建目录结构）
    示例: recall init

  new <描述> <短标签>
    创建新的决策记录
    示例: recall new "添加暗色模式" "dark-mode"

  query file <文件路径>
    查询文件的修改历史和相关决策记录
    示例: recall query file src/main.py

  query commit <commit-hash>
    查询 Git 提交的详细信息和相关决策记录
    示例: recall query commit abc123f

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
  - Git 集成: references/git-workflow-integration.md
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

def cmd_new(args):
    """创建新决策记录"""
    if len(args) < 2:
        print("❌ 错误: 缺少参数")
        print("用法: recall new <描述> <短标签>")
        print("示例: recall new \"添加暗色模式\" \"dark-mode\"")
        return 1

    title = args[0]
    short_desc = args[1]

    try:
        import create_ver

        # 查找项目根目录
        root = create_ver.find_project_root()
        template_path = root / "references" / "logic-version-git-template.md"
        output_dir = root / "logic_version" / "records"

        if not template_path.exists():
            print(f"❌ 错误: 模板文件不存在 {template_path}")
            return 1

        output_dir.mkdir(parents=True, exist_ok=True)

        return create_ver.create_ver_record(title, short_desc, template_path, output_dir)
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
        print("用法: recall query <file|commit> <参数>")
        print("示例: recall query file src/main.py")
        print("示例: recall query commit abc123f")
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

        else:
            print(f"❌ 错误: 未知的查询类型 '{query_type}'")
            print("支持的类型: file, commit")
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
            records = list(records_dir.glob("ver-*.md"))
            print(f"📚 决策记录: {len(records)} 个文件")

            # 显示最近 3 条
            if records:
                sorted_records = sorted(records, key=lambda x: x.stat().st_mtime, reverse=True)
                print(f"\n   最近的决策记录:")
                for record in sorted_records[:3]:
                    mtime = record.stat().st_mtime
                    from datetime import datetime
                    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                    print(f"   • {record.name} ({date_str})")
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
                uncommitted = status_result.stdout.strip()
                if uncommitted:
                    lines = uncommitted.split('\n')
                    print(f"⚠️  未提交变更: {len(lines)} 个文件")
                else:
                    print(f"✅ 工作区状态: 干净")
        except:
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
