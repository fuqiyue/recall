#!/usr/bin/env python3
"""
查询 Git 历史和决策记录的关联
用于追溯某个文件或提交的完整上下文
"""

import subprocess
import sys
from pathlib import Path
import re


# 决策记录文件名：logic_version-YYYYMMDD-NNN-<scope>.md
RECORD_NAME_RE = re.compile(r'^logic_version-\d{8}-\d{3}-.+\.md$', re.IGNORECASE)

# commit 关联的几种写法，与 validate.py 的 COMMIT_PATTERNS 保持一致。
# after_commit 必须排最前：新 schema 记录同时有 before_commit（基线）和
# after_commit（实施提交），列表展示应优先取实施提交。
COMMIT_PATTERNS = (
    r'^\s*-\s*after_commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
    r'关联\s*Commit\*{0,2}\s*[：:]\s*`?([0-9a-f]{7,40})`?',
    r'\bcode\s*:\s*commit\s*:\s*`?([0-9a-f]{7,40})`?',
    r'^\s*-\s*commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
)

# 功能意图登记（logic_readme.md）：反向查询 intent → 规则 → 记录 → 代码锚点
INT_ID_RE = re.compile(r'^INT-\d{8}-\d{3}$', re.IGNORECASE)
RULE_ID_RE = re.compile(r'\bRULE-\d{3}\b')
VER_ID_RE = re.compile(r'\bVER-\d{8}-\d{3}\b')

def find_project_root(start=None):
    """向上查找包含 logic_readme.md 的目录，找不到时退回当前目录。

    旧代码用相对 cwd 的常量路径，在子目录中运行 query/list 会
    静默找不到任何记录，与 CLI 帮助承诺的"子目录可执行"不符。
    """
    current = (start or Path.cwd()).resolve()
    while current != current.parent:
        if (current / "logic_readme.md").exists():
            return current
        current = current.parent
    return (start or Path.cwd()).resolve()


def _records_dir():
    return find_project_root() / "logic_version" / "records"


def run_git(args):
    """运行 Git 命令并返回 stdout，失败返回 None。

    参数以列表传入且不经过 shell：路径里的空格、引号，以及命令行
    传入的 commit 值都原样传递，不会被 shell 解释执行。
    """
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (result.stdout or "").strip()


def _parse_record(record_file):
    """解析一条决策记录的元数据，读不出来返回 None。

    字段名以 references/logic-version-template.md 为准（`- version_id:`、
    `- date:`）。旧代码找的是 `- **日期**:` 和 `- **关联 Commit**:` 粗体
    写法，对实际记录永远匹配不到，列表里的日期和 commit 一直显示
    Unknown / _待填写_。这里两种写法都接受。
    """
    try:
        content = record_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    match = re.search(r'VER-\d{8}-\d{3}', content)
    ver_id = match.group(0) if match else "Unknown"

    title = "Unknown"
    for line in content.split('\n')[:10]:
        if line.startswith('# VER-'):
            title = line.split(':', 1)[1].strip() if ':' in line else line
            break

    date_match = re.search(
        r'^\s*-\s*(?:date|\*\*日期\*\*)\s*[：:]\s*(\d{4}-\d{2}-\d{2})',
        content,
        re.MULTILINE | re.IGNORECASE,
    )
    record_date = date_match.group(1) if date_match else "Unknown"

    commit_hash = "_待填写_"
    for pattern in COMMIT_PATTERNS:
        commit_match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if commit_match:
            commit_hash = commit_match.group(1)
            break

    return {
        'file': record_file.name,
        'ver_id': ver_id,
        'title': title,
        'date': record_date,
        'commit': commit_hash,
        'path': record_file,
        'content': content,
    }


def _iter_records():
    """按文件名规则遍历决策记录，跳过 README.md 等说明文件。"""
    records_dir = _records_dir()
    if not records_dir.exists():
        return
    for record_file in sorted(records_dir.glob("*.md")):
        if not RECORD_NAME_RE.match(record_file.name):
            continue
        record = _parse_record(record_file)
        if record is not None:
            yield record


def find_decision_records_for_file(file_path):
    """查找与某个文件相关的决策记录"""
    name = Path(file_path).name
    return [
        record
        for record in _iter_records()
        if file_path in record['content'] or name in record['content']
    ]


def find_decision_records_for_commit(commit_hash):
    """查找与某个提交相关的决策记录"""
    if not commit_hash:
        return []
    return [
        record for record in _iter_records() if commit_hash in record['content']
    ]


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
    git_log = run_git(["log", "--oneline", "--follow", "-10", "--", file_path])

    if git_log:
        for line in git_log.split('\n'):
            print(f"  {line}")
    else:
        print("  (无提交历史)")

    # 2. 最近一次修改详情
    print("\n📝 最近一次修改:\n")
    last_commit = run_git(
        ["log", "-1", "--format=%H|%an|%ad|%s", "--date=short", "--", file_path]
    )

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
    commit_info = run_git(
        ["show", "--stat", "--format=%an|%ad|%s|%b", "--date=short", commit_hash]
    )

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
    files = run_git(
        ["diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash]
    )

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


def _split_table_row(line):
    """把 Markdown 表格行拆成去除首尾空白的单元格列表。"""
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def query_intent(intent_id):
    """反向查询：从功能意图（INT-ID）定位规则、决策记录和代码锚点。

    正向查询（file/commit）回答"这段代码当初为什么改"；本模式回答开发中
    最高频的反问题——"我要改功能 X，会涉及哪些规则和文件"。数据来源是
    logic_readme.md 功能意图登记表 + 当前制度表 + logic_version/records/。
    返回退出码：找到 0，找不到 1。
    """
    intent_id = intent_id.strip().upper()
    if not INT_ID_RE.match(intent_id):
        print(f"❌ 无效的意图编号: {intent_id}（格式: INT-YYYYMMDD-NNN）")
        return 1

    root = find_project_root()
    readme_path = root / "logic_readme.md"
    if not readme_path.exists():
        print("❌ 未找到 logic_readme.md")
        return 1
    content = readme_path.read_text(encoding="utf-8")

    # 功能意图登记表：| intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 | last_verified |
    int_row = None
    for line in content.splitlines():
        if line.strip().upper().startswith(f"| {intent_id} |".upper()):
            int_row = _split_table_row(line)
            break

    print(f"\n{'='*70}")
    print(f"🎯 功能意图: {intent_id}")
    print(f"{'='*70}\n")

    if int_row is None:
        print(f"❌ 功能意图登记表中没有 {intent_id}")
        registered = sorted(set(
            m.group(0) for m in re.finditer(r'^\|\s*(INT-\d{8}-\d{3})\s*\|', content, re.MULTILINE)
        ))
        if registered:
            print(f"   已登记的意图: {', '.join(r.strip('| ').strip() for r in registered)}")
        print()
        return 1

    entry = int_row[1] if len(int_row) > 1 else ""
    intent_text = int_row[2] if len(int_row) > 2 else ""
    flow_pos = int_row[3] if len(int_row) > 3 else ""
    rules_cell = int_row[4] if len(int_row) > 4 else ""
    anchors_cell = int_row[5] if len(int_row) > 6 else ""

    print(f"  功能入口: {entry}")
    print(f"  用户目标: {intent_text}")
    print(f"  流程位置: {flow_pos}")

    # 关联规则：到当前制度表里取规则正文和决策记录
    rule_ids = RULE_ID_RE.findall(rules_cell)
    linked_vers = []
    if rule_ids:
        print(f"\n📏 关联规则:\n")
        rule_rows = {}
        for line in content.splitlines():
            match = re.match(r'^\|\s*(RULE-\d{3})\s*\|', line)
            if match:
                rule_rows[match.group(1)] = _split_table_row(line)
        for rule_id in rule_ids:
            cells = rule_rows.get(rule_id)
            if cells and len(cells) >= 5:
                print(f"  • {rule_id} ({cells[1]}): {cells[2]}")
                linked_vers.extend(VER_ID_RE.findall(cells[4]))
            else:
                print(f"  • {rule_id}: ⚠️ 未在当前制度表中找到定义")

    # 代码锚点：存在性即时核对
    if anchors_cell and anchors_cell.lower() != 'none':
        print(f"\n📁 代码锚点:\n")
        for anchor in re.split(r'[;，,]', anchors_cell):
            anchor = anchor.strip().strip('`')
            if not anchor:
                continue
            mark = "✅" if (root / anchor).exists() else "⚠️ 不存在"
            print(f"  {mark} {anchor}")

    # 相关决策记录：意图追溯链提及本 INT 的记录 + 关联规则链接的记录
    related = []
    seen = set()
    for record in _iter_records():
        hit = intent_id in record['content'] or record['ver_id'] in linked_vers
        if hit and record['ver_id'] not in seen:
            seen.add(record['ver_id'])
            related.append(record)
    print(f"\n📚 相关决策记录:\n")
    if related:
        for rec in related:
            print(f"  • {rec['ver_id']} ({rec['date']}): {rec['title']}")
            print(f"    文件: {rec['file']}")
    else:
        print("  (未找到相关决策记录)")

    print(f"\n{'='*70}\n")
    return 0


def list_recent_decisions(limit=10):
    """列出最近的决策记录。返回退出码。

    `limit` 对应 CLI 的 `recall list [数量]`。此前本函数不接受参数，
    而 recall.py 一直按文档形式传入数量，导致 `recall list 20` 抛
    TypeError 并退出 1——被上层的宽异常捕获包装成一句错误信息。
    """
    print(f"\n{'='*70}")
    print(f"📚 最近的决策记录")
    print(f"{'='*70}\n")

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        print(f"  ❌ 无效的数量: {limit!r}")
        return 1
    if limit < 1:
        print(f"  ❌ 数量必须大于 0，收到 {limit}")
        return 1

    # 按记录名倒序（version_id 里带日期和序号），比文件 mtime 稳定：
    # 编辑或重新检出文件都会改 mtime，但不改变决策的时间顺序。
    records = sorted(_iter_records(), key=lambda r: r['file'], reverse=True)

    if not records:
        print("  (没有决策记录)")
        print(f"\n{'='*70}\n")
        return 0

    for record in records[:limit]:
        print(f"  • {record['ver_id']} ({record['date']})")
        print(f"    {record['title']}")
        print(f"    Commit: {record['commit']}")
        print(f"    文件: {record['file']}")
        print()

    print(f"{'='*70}\n")
    return 0


def show_usage():
    """显示使用说明"""
    print("""
使用方法:
  python scripts/link_ver_git.py <模式> <参数>

模式:
  file <文件路径>     - 查询某个文件的 Git 历史和决策记录
  commit <提交哈希>   - 查询某个提交的详情和决策记录
  intent <INT-ID>     - 反向查询：功能意图 → 规则 → 决策记录 → 代码锚点
  list                - 列出最近的决策记录

示例:
  python scripts/link_ver_git.py file logic_readme.md
  python scripts/link_ver_git.py commit abc123d
  python scripts/link_ver_git.py intent INT-20260816-005
  python scripts/link_ver_git.py list
""")


def _force_utf8_when_redirected():
    """重定向到文件/管道时把输出流切成 UTF-8。

    Windows 上重定向后的 stdout 用 ANSI 代码页（如 cp936），
    输出里的 emoji 会触发 UnicodeEncodeError。
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main():
    """主函数"""
    _force_utf8_when_redirected()

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

    elif mode == "intent":
        if len(sys.argv) < 3:
            print("❌ 请指定意图编号（INT-YYYYMMDD-NNN）")
            show_usage()
            sys.exit(1)
        sys.exit(query_intent(sys.argv[2]))

    elif mode == "list":
        limit = sys.argv[2] if len(sys.argv) > 2 else 10
        sys.exit(list_recent_decisions(limit))

    else:
        print(f"❌ 未知模式: {mode}")
        show_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
