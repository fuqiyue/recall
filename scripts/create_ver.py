#!/usr/bin/env python3
"""
创建版本决策记录的辅助工具
使用 Git 集成模板快速创建新的决策记录
"""

import sys
from datetime import date
from pathlib import Path


def get_next_ver_number(today_str):
    """获取今天的下一个可用版本号"""
    records_dir = Path(__file__).parent.parent / "logic_version" / "records"

    if not records_dir.exists():
        records_dir.mkdir(parents=True, exist_ok=True)

    # 查找今天已有的版本记录
    pattern = f"*{today_str}*.md"
    existing = list(records_dir.glob(pattern))

    # 提取序号
    max_num = 0
    for f in existing:
        # 从文件名中提取序号，格式: ver-YYYYMMDD-NNN-scope.md
        parts = f.stem.split('-')
        if len(parts) >= 3:
            try:
                num = int(parts[2])
                max_num = max(max_num, num)
            except ValueError:
                continue

    return max_num + 1


def read_template():
    """读取 Git 集成模板"""
    template_path = Path(__file__).parent.parent / "references" / "logic-version-git-template.md"

    if not template_path.exists():
        print(f"❌ 模板文件不存在: {template_path}")
        sys.exit(1)

    return template_path.read_text(encoding="utf-8")


def create_ver_record(title, scope):
    """创建版本决策记录"""
    today = date.today()
    today_str = today.strftime("%Y%m%d")
    today_iso = today.isoformat()

    # 获取下一个序号
    next_num = get_next_ver_number(today_str)

    # 生成 ID 和文件名
    ver_id = f"VER-{today_str}-{next_num:03d}"
    filename = f"ver-{today_str}-{next_num:03d}-{scope}.md"

    # 生成文件路径
    records_dir = Path(__file__).parent.parent / "logic_version" / "records"
    filepath = records_dir / filename

    # 读取模板
    template = read_template()

    # 模板中的快速模板部分（从 "## 快速模板" 到下一个 "---"）
    # 提取并使用
    lines = template.split('\n')
    in_quick_template = False
    quick_template_lines = []

    for line in lines:
        if line.strip() == '## 快速模板':
            in_quick_template = True
            continue
        if in_quick_template:
            if line.strip().startswith('```markdown'):
                continue
            if line.strip() == '```' and quick_template_lines:
                break
            quick_template_lines.append(line)

    content = '\n'.join(quick_template_lines)

    # 替换占位符
    content = content.replace("YYYYMMDD-NNN", f"{today_str}-{next_num:03d}")
    content = content.replace("<变更标题>", title)
    content = content.replace("YYYY-MM-DD", today_iso)
    content = content.replace("<git-commit-hash>", "_待填写_")
    content = content.replace("CHG-YYYYMMDD-NNN", f"CHG-{today_str}-{next_num:03d}")

    # 写入文件
    try:
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ 已创建决策记录")
        print(f"   📄 文件: {filepath.relative_to(Path.cwd())}")
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
        print("   4. 更新决策记录中的 commit hash")
        return True
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")
        return False


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
  ver-YYYYMMDD-NNN-<范围标识>.md

  例如: ver-20260808-001-dark-mode.md
""")


def main():
    """主函数"""
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)

    title = sys.argv[1]
    scope = sys.argv[2]

    # 验证范围标识符格式
    if not scope.replace('-', '').replace('_', '').isalnum():
        print("❌ 范围标识符只能包含字母、数字、连字符和下划线")
        sys.exit(1)

    # 创建记录
    success = create_ver_record(title, scope)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
