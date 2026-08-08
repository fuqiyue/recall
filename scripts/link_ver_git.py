#!/usr/bin/env python3
"""
查询 Git 历史和决策记录的关联
用于追溯某个文件或提交的完整上下文
"""

import subprocess
import sys
from pathlib import Path
import re


def run_git_command(cmd):
    """运行 Git 命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def find_decision_records_for_file(file_path):
    """查找与某个文件相关的决策记录"""
    records_dir = Path("logic_version/records")
    if not records_dir.exists():
        return []

    results = []
    for record_file in records_dir.glob("*.md"):
        try:
            content = record_file.read_text(encoding="utf-8")
            # 查找文件路径引用
            if file_path in content or Path(file_path).name in content:
                # 提取版本号
                match = re.search(r'VER-\d{8}-\d{3}', content)
                ver_id = match.group(0) if match else "Unknown"

                # 提取标题
                lines = content.split('\n')
                title = "Unknown"
                for line in lines[:10]:
                    if line.startswith('# VER-'):
                        title = line.split(':', 1)[1].strip() if ':' in line else line
                        break

                results.append({
                    'file': record_file.name,
                    'ver_id': ver_id,
                    'title': title,
                    'path': record_file
                })
        except Exception:
            continue

    return results


def find_decision_records_for_commit(commit_hash):
    """查找与某个提交相关的决策记录"""
    records_dir = Path("logic_version/records")
    if not records_dir.exists():
        return []

    results = []
    for record_file in records_dir.glob("*.md"):
        try:
            content = record_file.read_text(encoding="utf-8")
            # 查找提交哈希引用
            if commit_hash in content:
                # 提取版本号
                match = re.search(r'VER-\d{8}-\d{3}', content)
                ver_id = match.group(0) if match else "Unknown"

                # 提取标题
                lines = content.split('\n')
                title = "Unknown"
                for line in lines[:10]:
                    if line.startswith('# VER-'):
                        title = line.split(':', 1)[1].strip() if ':' in line else line
                        break

                results.append({
                    'file': record_file.name,
                    'ver_id': ver_id,
                    'title': title,
                    'path': record_file
                })
        except Exception:
            continue

    return results


def query_file_history(file_path):
    """查询文件的 Git 历史和决策记录"""
    print(f"\n{'='*70}")
    print(f"📁 文件: {file_path}")
    print(f"{'='*70}\n")

    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"⚠️  文件不存在: {file_path}")
        return

    # 1. Git 历史
    print("📊 Git 提交历史 (最近10次):\n")
    git_log = run_git_command(f'git log --oneline --follow -10 -- "{file_path}"')

    if git_log:
        for line in git_log.split('\n'):
            print(f"  {line}")
    else:
        print("  (无提交历史)")

    # 2. 最近一次修改详情
    print("\n📝 最近一次修改:\n")
    last_commit = run_git_command(f'git log -1 --format="%H|%an|%ad|%s" --date=short -- "{file_path}"')

    if last_commit:
        parts = last_commit.split('|')
        if len(parts) >= 4:
            commit_hash, author, date, subject = parts[0], parts[1], parts[2], '|'.join(parts[3:])
            print(f"  Commit:  {commit_hash[:8]}")
            print(f"  作者:    {author}")
            print(f"  日期:    {date}")
            print(f"  说明:    {subject}")

            # 查找该提交的决策记录
            records = find_decision_records_for_commit(commit_hash[:8])
            if records:
                print(f"\n  关联决策记录:")
                for rec in records:
                    print(f"    - {rec['ver_id']}: {rec['title']}")
                    print(f"      文件: {rec['file']}")
    else:
        print("  (无提交记录)")

    # 3. 相关决策记录
    print("\n📚 相关决策记录:\n")
    records = find_decision_records_for_file(file_path)

    if records:
        for rec in records:
            print(f"  • {rec['ver_id']}: {rec['title']}")
            print(f"    文件: {rec['file']}")
    else:
        print("  (未找到相关决策记录)")

    print(f"\n{'='*70}\n")


def query_commit_details(commit_hash):
    """查询提交的详情和决策记录"""
    print(f"\n{'='*70}")
    print(f"🔖 Commit: {commit_hash}")
    print(f"{'='*70}\n")

    # 1. 提交详情
    print("📝 提交信息:\n")
    commit_info = run_git_command(f'git show --stat --format="%an|%ad|%s|%b" --date=short {commit_hash}')

    if commit_info:
        lines = commit_info.split('\n')
        if lines:
            parts = lines[0].split('|')
            if len(parts) >= 3:
                author, date, subject = parts[0], parts[1], '|'.join(parts[2:])
                print(f"  作者:    {author}")
                print(f"  日期:    {date}")
                print(f"  说明:    {subject}")

                # 打印提交正文（如果有）
                body_started = False
                for line in lines[1:]:
                    if line.strip() and not line.startswith(' ') and not '|' in line:
                        if not body_started:
                            print(f"\n  正文:")
                            body_started = True
                        print(f"    {line}")
    else:
        print(f"  ❌ 找不到提交: {commit_hash}")
        return

    # 2. 修改的文件
    print("\n📂 修改的文件:\n")
    files = run_git_command(f'git diff-tree --no-commit-id --name-status -r {commit_hash}')

    if files:
        for line in files.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  (无文件修改)")

    # 3. 相关决策记录
    print("\n📚 相关决策记录:\n")
    records = find_decision_records_for_commit(commit_hash)

    if records:
        for rec in records:
            print(f"  • {rec['ver_id']}: {rec['title']}")
            print(f"    文件: {rec['file']}")
            print(f"    路径: {rec['path']}")
    else:
        print("  (未找到相关决策记录)")

    print(f"\n{'='*70}\n")


def list_recent_decisions():
    """列出最近的决策记录"""
    print(f"\n{'='*70}")
    print(f"📚 最近的决策记录")
    print(f"{'='*70}\n")

    records_dir = Path("logic_version/records")
    if not records_dir.exists():
        print("  (没有决策记录)")
        return

    # 获取所有记录并按修改时间排序
    records = sorted(records_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not records:
        print("  (没有决策记录)")
        return

    for record_file in records[:10]:  # 只显示最近10条
        try:
            content = record_file.read_text(encoding="utf-8")

            # 提取版本号
            match = re.search(r'VER-\d{8}-\d{3}', content)
            ver_id = match.group(0) if match else "Unknown"

            # 提取标题
            lines = content.split('\n')
            title = "Unknown"
            for line in lines[:10]:
                if line.startswith('# VER-'):
                    title = line.split(':', 1)[1].strip() if ':' in line else line
                    break

            # 提取日期
            date_match = re.search(r'- \*\*日期\*\*: (\d{4}-\d{2}-\d{2})', content)
            record_date = date_match.group(1) if date_match else "Unknown"

            # 提取 commit hash
            commit_match = re.search(r'- \*\*关联 Commit\*\*: `([a-f0-9]+)`', content)
            commit_hash = commit_match.group(1) if commit_match else "_待填写_"

            print(f"  • {ver_id} ({record_date})")
            print(f"    {title}")
            print(f"    Commit: {commit_hash}")
            print(f"    文件: {record_file.name}")
            print()
        except Exception:
            continue

    print(f"{'='*70}\n")


def show_usage():
    """显示使用说明"""
    print("""
使用方法:
  python scripts/link_ver_git.py <模式> <参数>

模式:
  file <文件路径>     - 查询某个文件的 Git 历史和决策记录
  commit <提交哈希>   - 查询某个提交的详情和决策记录
  list                - 列出最近的决策记录

示例:
  python scripts/link_ver_git.py file logic_readme.md
  python scripts/link_ver_git.py commit abc123d
  python scripts/link_ver_git.py list
""")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "file":
        if len(sys.argv) < 3:
            print("❌ 请指定文件路径")
            show_usage()
            sys.exit(1)
        query_file_history(sys.argv[2])

    elif mode == "commit":
        if len(sys.argv) < 3:
            print("❌ 请指定提交哈希")
            show_usage()
            sys.exit(1)
        query_commit_details(sys.argv[2])

    elif mode == "list":
        list_recent_decisions()

    else:
        print(f"❌ 未知模式: {mode}")
        show_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
