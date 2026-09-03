#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建版本决策记录的辅助工具
按唯一模板 references/logic-version-template.md 的"快速模板"块生成记录

文件名遵循 references/logic-version-template.md 的规范：
logic_version-YYYYMMDD-NNN-<scope>.md。validate.py / link_ver_git.py /
recall status 都按这个名字发现记录，任何一方改名都会让记录静默消失
（RULE-009）。
"""

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_common import SELF_ROOT, force_utf8_output, git_output  # noqa: E402
from recall_common import find_project_root as _find_root  # noqa: E402

# 规范记录名；旧命名 ver-YYYYMMDD-NNN-*.md 只用于提取已占用的序号
RECORD_NAME_RE = re.compile(r'^logic_version-(\d{8})-(\d{3})-.+\.md$', re.IGNORECASE)
LEGACY_NAME_RE = re.compile(r'^ver-(\d{8})-(\d{3})-.+\.md$', re.IGNORECASE)


def find_project_root(start=None):
    """向上查找 logic_readme.md；找不到时退回 Recall 自身（RULE-021 公共实现）。

    skill 被集中安装、而用户在无 logic_readme.md 的目录运行时，记录应
    落回 Recall 自身而不是 cwd。
    """
    return _find_root(start, fallback=SELF_ROOT)


def head_short_hash(cwd):
    """返回当前 HEAD 短哈希；无 Git/无提交时返回 None。"""
    return git_output(["rev-parse", "--short", "HEAD"], cwd=cwd, timeout=5) or None


def get_next_ver_number(records_dir, today_str):
    """获取当天的下一个可用序号；新旧两种文件名的序号都计入，避免撞号。"""
    if not records_dir.exists():
        return 1

    max_num = 0
    for f in records_dir.glob("*.md"):
        for pattern in (RECORD_NAME_RE, LEGACY_NAME_RE):
            match = pattern.match(f.name)
            if match and match.group(1) == today_str:
                max_num = max(max_num, int(match.group(2)))
    return max_num + 1


def extract_quick_template(template_text):
    """提取 "## 快速模板" 小节里 ```markdown 围栏内的内容。

    只收集围栏内部的行：小节标题与围栏之间允许有说明文字，
    不应进入生成的记录。块内不支持嵌套围栏（模板中已注明）。
    """
    lines = template_text.split('\n')
    in_section = False
    in_fence = False
    collected = []

    for line in lines:
        stripped = line.strip()
        if stripped == '## 快速模板':
            in_section = True
            continue
        if not in_section:
            continue
        if not in_fence:
            if stripped.startswith('```markdown'):
                in_fence = True
            continue
        if stripped == '```':
            break
        collected.append(line)

    return '\n'.join(collected).strip('\n')


def create_ver_record(title, scope, template_path=None, output_dir=None):
    """创建版本决策记录。返回退出码：0 成功，1 失败。"""
    # recall.py cmd_new 直接调用本函数、绕过 main()，防护必须在这里
    force_utf8_output()
    root = find_project_root()
    if template_path is None:
        template_path = root / "references" / "logic-version-template.md"
    if output_dir is None:
        output_dir = root / "logic_version" / "records"

    template_path = Path(template_path)
    output_dir = Path(output_dir)

    if not template_path.exists():
        print(f"❌ 模板文件不存在: {template_path}")
        return 1

    today = date.today()
    today_str = today.strftime("%Y%m%d")
    today_iso = today.isoformat()

    next_num = get_next_ver_number(output_dir, today_str)

    ver_id = f"VER-{today_str}-{next_num:03d}"
    filename = f"logic_version-{today_str}-{next_num:03d}-{scope}.md"
    filepath = output_dir / filename

    content = extract_quick_template(template_path.read_text(encoding="utf-8"))
    if not content:
        print(f"❌ 模板中找不到 '## 快速模板' 代码块: {template_path}")
        return 1

    content = content.replace("YYYYMMDD-NNN", f"{today_str}-{next_num:03d}")
    content = content.replace("<变更标题>", title)
    content = content.replace("<scope>", scope)
    content = content.replace("YYYY-MM-DD", today_iso)
    # before_commit 记录创建时的基线；after_commit 留占位符由 hook 回填（RULE-013）
    content = content.replace("<before-commit-hash>", head_short_hash(root) or "none")
    # 旧版模板兼容：`- commit: <git-commit-hash>` 字段仍替换为占位符
    content = content.replace("<git-commit-hash>", "_待填写_")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content + "\n", encoding="utf-8")
    except OSError as e:
        print(f"❌ 创建文件失败: {e}")
        return 1

    try:
        display_path = filepath.relative_to(Path.cwd())
    except ValueError:
        display_path = filepath

    print(f"✅ 已创建决策记录")
    print(f"   📄 文件: {display_path}")
    print(f"   🆔 版本号: {ver_id}")
    print(f"   📅 日期: {today_iso}")
    print()
    print("📝 下一步:")
    print(f"   1. 编辑文件填写详细内容: {filepath.name}")
    print("   2. 实施代码修改")
    print("   3. Git 提交时引用此记录:")
    print(f"      git commit -m 'feat: {title}'")
    print(f"      git commit -m '...'")
    print(f"      git commit -m 'Ref: logic_version/records/{filename}'")
    print("   4. after_commit 由 post-commit hook 自动回填（RULE-013），无需手动更新")
    return 0


def show_usage():
    """显示使用说明"""
    print("""
使用方法:
  python scripts/create_ver.py <标题> <范围标识>

参数:
  <标题>      - 变更的简短标题（用引号包围）
  <范围标识>  - 用于文件名的范围标识符（小写，用连字符分隔）

示例:
  python scripts/create_ver.py "添加暗色模式支持" "dark-mode"
  python scripts/create_ver.py "优化数据库查询性能" "db-optimization"
  python scripts/create_ver.py "修复登录Bug" "login-fix"

生成的文件命名规则:
  logic_version-YYYYMMDD-NNN-<范围标识>.md

  例如: logic_version-20260808-001-dark-mode.md
""")


def main():
    """主函数"""
    _force_utf8_output()

    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)

    title = sys.argv[1]
    scope = sys.argv[2]

    # 验证范围标识符格式
    if not scope.replace('-', '').replace('_', '').isalnum():
        print("❌ 范围标识符只能包含字母、数字、连字符和下划线")
        sys.exit(1)

    sys.exit(create_ver_record(title, scope))


if __name__ == "__main__":
    main()
