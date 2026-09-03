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

from recall_common import (  # noqa: E402  RULE-021：根查找/Git 调用/编码防护只此一份
    change_ledgers,
    classify_porcelain,
    find_project_root,
    registered_domains,
    force_utf8_output,
    run_git,
    unpushed_commit_count,
)

# 决策记录文件名，与 validate.py / link_ver_git.py / create_ver.py 一致（RULE-009）
RECORD_NAME_RE = re.compile(r'^logic_version-\d{8}-\d{3}-.+\.md$', re.IGNORECASE)


def find_version_records(records_dir):
    """按规范文件名列出决策记录，跳过 README.md 等说明文件。"""
    if not records_dir.exists():
        return []
    return sorted(
        path for path in records_dir.glob("*.md") if RECORD_NAME_RE.match(path.name)
    )

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
    包括规则数量、活跃变更、最近决策、未提交/未跟踪/未推送提示
    示例: recall status

  conflicts
    检测规则间的潜在冲突
    分析 RULE-* 和 CHG-* 是否存在逻辑矛盾（宪法 + 全部领域）
    示例: recall conflicts

  route [路径或关键词 ...] [--json]
    按需导入：列出本次任务应读的文档（宪法必读 + 命中领域的 readme/change）
    并给出行数与估算 token；不给参数时列出全部领域
    示例: recall route scripts/git_sync.py
    示例: recall route 同步 --json

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

# classify_porcelain 的实现在 recall_common（RULE-021：porcelain 解析只此一份，
# git_sync 的提交清单与这里的 status 分类共用）；名字保留在本模块供测试访问。


def describe_unpushed(count):
    """把 ``unpushed_commit_count`` 的结果变成一行提示；None 表示不提示。

    RULE-010：自动同步只是默认值不是保证，半接入项目会静默退化成"只提交
    不推送"。这里只报数字，不推送、不改仓库状态。
    """
    if count is None or count <= 0:
        return None
    return (
        f"⬆️  未推送提交: 本地领先上游 {count} 个"
        "（RULE-010：请 recall sync 或 git push，勿让本地长期领先远端）"
    )


def cmd_status():
    """显示系统状态"""
    try:
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

        # 一二级拆分法（RULE-018）：宪法 + 已登记领域（部门法）
        domains = registered_domains(root)
        if readme_path.exists():
            if domains:
                print(f"🏛️  领域（部门法）: {len(domains)} 个 —— " + ", ".join(d.module_id for d in domains))
            else:
                print("🏛️  领域（部门法）: 0 个 ⚠️  宪法未分层（RULE-018 要求至少一个 logic_domains/<domain>/）")

        # 活跃议案：根账本（修宪议案）+ 每个领域账本，按 CHG 标题计数
        ledgers = change_ledgers(root)
        if ledgers:
            total = 0
            parts = []
            for label, ledger_path in ledgers:
                content = ledger_path.read_text(encoding='utf-8', errors='replace')
                ids = set(re.findall(r'^##\s+(CHG-[A-Za-z0-9][A-Za-z0-9-]*)', content, re.MULTILINE))
                total += len(ids)
                parts.append(f"{label} {len(ids)}")
            print(f"🔄 活跃变更: {total} 个 CHG 正文（" + "；".join(parts) + "）")
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

        # 检查 Git 状态（run_git 固定 utf-8：中文提交信息在 GBK 下曾让本命令崩溃）
        ok_log, last_commit, log_err = run_git(['log', '-1', '--format=%h %s'], cwd=root, timeout=5)
        git_missing = not ok_log and any(
            marker in log_err for marker in ('not recognized', 'No such file', 'WinError 2', 'Errno 2')
        )
        if git_missing:
            print(f"\n🔖 Git: ⚠️  未安装或不可用")
        else:
            if ok_log:
                print(f"\n🔖 最近提交: {last_commit}")
            else:
                print(f"\n🔖 最近提交: ⚠️  无法读取")

            ok_status, porcelain, _ = run_git(['status', '--porcelain'], cwd=root, timeout=5)
            if ok_status:
                tracked, untracked = classify_porcelain(porcelain)
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
            unpushed_line = describe_unpushed(unpushed_commit_count(root))
            if unpushed_line:
                print(unpushed_line)

        print("\n" + "=" * 60)
        print("💡 提示: 运行 'recall validate' 检查系统一致性")
        print("=" * 60 + "\n")

        return 0

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def cmd_route(args):
    """按目标路径/关键词给出读取清单（RULE-018 一二级拆分法按需导入）"""
    try:
        import route_docs
        return route_docs.main(args)
    except ImportError:
        print("❌ 错误: 找不到 route_docs.py")
        return 1


def cmd_conflicts():
    """检测规则冲突"""
    try:
        import detect_conflicts
        # 显式传空 argv：否则子模块会把 sys.argv[1]（子命令名）当项目根
        return detect_conflicts.main([])
    except ImportError:
        print("❌ 错误: 找不到 detect_conflicts.py")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

def main():
    """主入口"""
    force_utf8_output()

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
        'route': lambda: cmd_route(args),
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
