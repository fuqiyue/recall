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

import argparse
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


def find_project_root(start=None, *, project=None):
    """显式路径必须是项目根；否则沿 cwd 向上查找，缺根时失败。"""
    root = Path(project).resolve() if project is not None else _find_root(start)
    if not (root / "logic_readme.md").is_file():
        raise ValueError(f"未找到项目根 logic_readme.md: {root}；在目标项目运行，或使用 --project <项目根>")
    return root

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


def create_ver_record(title, scope, template_path=None, output_dir=None, *, project=None):
    """创建版本决策记录。返回退出码：0 成功，1 失败。"""
    # recall.py cmd_new 直接调用本函数、绕过 main()，防护必须在这里
    force_utf8_output()
    if not scope or not scope.replace('-', '').replace('_', '').isalnum():
        print("❌ 范围标识符只能包含字母、数字、连字符和下划线")
        return 1
    try:
        root = find_project_root(project=project)
    except ValueError as error:
        print(f"❌ {error}")
        return 1
    if template_path is None:
        local_template = root / "references" / "logic-version-template.md"
        template_path = local_template if local_template.is_file() else SELF_ROOT / "references" / "logic-version-template.md"
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

    print("✅ 已创建决策记录草稿；关联CHG完成验证与清理后定稿")
    print(f"   📄 文件: {display_path}")
    print(f"   🆔 版本号: {ver_id}")
    print(f"   📅 日期: {today_iso}")
    print()
    print("📝 下一步:")
    print(f"   1. 编辑文件填写详细内容: {filepath.name}")
    print("   2. 实施代码修改")
    print("   3. 更新现行文档，清理并核结果，补齐本记录后定稿和更新索引")
    print("   4. 关闭CHG并核公报；Git提交时引用本记录:")
    print(f'      git commit -m "feat: 描述本次变更" -m "Ref: logic_version/records/{filename}"')
    print("   5. after_commit 由 post-commit hook 自动回填（RULE-013），无需手动更新")
    return 0


def main(argv=None):
    """创建记录的唯一命令解析入口，recall new 与直调脚本共用。"""
    force_utf8_output()
    parser = argparse.ArgumentParser(description="在已定位的项目创建 Recall 决策记录")
    parser.add_argument("title", help="变更描述")
    parser.add_argument("scope", help="文件名短标签")
    parser.add_argument("--project", help="显式目标项目根，必须包含 logic_readme.md")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    return create_ver_record(args.title, args.scope, project=args.project)


if __name__ == "__main__":
    sys.exit(main())
