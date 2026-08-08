#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 一致性验证工具
检查 logic_readme.md, logic_change.md 和 logic_version/ 之间的一致性
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def add_error(self, msg: str):
        self.errors.append(f"❌ {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(f"⚠️  {msg}")

    def add_info(self, msg: str):
        self.info.append(f"ℹ️  {msg}")

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self):
        print("\n" + "=" * 60)
        print("📋 Recall 验证报告")
        print("=" * 60 + "\n")

        if self.errors:
            print("🔴 错误 (必须修复):")
            for err in self.errors:
                print(f"  {err}")
            print()

        if self.warnings:
            print("🟡 警告 (建议修复):")
            for warn in self.warnings:
                print(f"  {warn}")
            print()

        if self.info:
            print("🔵 信息:")
            for inf in self.info:
                print(f"  {inf}")
            print()

        if self.is_valid() and not self.warnings:
            print("✅ 所有检查通过！Recall 状态良好。\n")
        elif self.is_valid():
            print("✅ 没有错误，但有一些警告需要注意。\n")
        else:
            print("❌ 验证失败，请修复上述错误。\n")

def find_project_root() -> Path:
    """查找项目根目录（包含 logic_readme.md）"""
    current = Path.cwd()
    while current != current.parent:
        if (current / "logic_readme.md").exists():
            return current
        current = current.parent
    return Path.cwd()

def extract_rule_ids(readme_path: Path) -> List[Tuple[str, int]]:
    """从 logic_readme.md 提取所有 RULE-ID"""
    rule_ids = []
    if not readme_path.exists():
        return rule_ids

    with open(readme_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 匹配 RULE-XXX 格式
            matches = re.findall(r'\bRULE-\d{3}\b', line)
            for match in matches:
                rule_ids.append((match, line_num))

    return rule_ids

def extract_chg_ids(change_path: Path) -> List[Dict]:
    """从 logic_change.md 提取所有 CHG-ID 及状态"""
    chg_records = []
    if not change_path.exists():
        return chg_records

    with open(change_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 匹配 CHG-ID 标题
        pattern = r'##\s+(CHG-\d{8}-\d{3}):\s*(.+?)$'
        for match in re.finditer(pattern, content, re.MULTILINE):
            chg_id = match.group(1)
            title = match.group(2).strip()

            # 尝试提取状态
            status_pattern = rf'{re.escape(chg_id)}.*?状态[：:]\s*(.+?)(?:\n|$)'
            status_match = re.search(status_pattern, content, re.DOTALL)
            status = status_match.group(1).strip() if status_match else "未标注"

            chg_records.append({
                'id': chg_id,
                'title': title,
                'status': status
            })

    return chg_records

def find_version_records(version_dir: Path) -> List[Path]:
    """查找所有决策记录文件"""
    records_dir = version_dir / "records"
    if not records_dir.exists():
        return []

    return list(records_dir.glob("ver-*.md"))

def extract_commit_hash(record_path: Path) -> str:
    """从决策记录中提取 Git commit hash"""
    if not record_path.exists():
        return ""

    with open(record_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 查找关联 Commit 字段
        match = re.search(r'关联\s*Commit[：:]\s*`?([0-9a-f]{7,40})`?', content, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""

def check_required_fields(record_path: Path) -> List[str]:
    """检查决策记录的必填字段"""
    required_fields = [
        r'版本号[：:]',
        r'关联\s*Commit[：:]',
        r'创建日期[：:]',
        r'##\s*修改原因',
        r'##\s*决策过程',
        r'##\s*影响范围'
    ]

    missing_fields = []

    with open(record_path, 'r', encoding='utf-8') as f:
        content = f.read()

        for field_pattern in required_fields:
            if not re.search(field_pattern, content):
                # 提取字段名用于报告
                field_name = field_pattern.replace(r'[：:]', '').replace(r'##\s*', '').replace(r'\s*', ' ')
                missing_fields.append(field_name)

    return missing_fields

def is_valid_git_commit(commit_hash: str) -> bool:
    """检查 Git commit hash 是否有效"""
    if not commit_hash:
        return False

    try:
        result = subprocess.run(
            ['git', 'cat-file', '-t', commit_hash],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and 'commit' in result.stdout
    except:
        return False

def validate_recall() -> ValidationResult:
    """执行完整的验证流程"""
    result = ValidationResult()
    root = find_project_root()

    # 检查基础文件存在性
    readme_path = root / "logic_readme.md"
    change_path = root / "logic_change.md"
    version_dir = root / "logic_version"

    if not readme_path.exists():
        result.add_error("未找到 logic_readme.md")
        return result

    if not change_path.exists():
        result.add_warning("未找到 logic_change.md")

    if not version_dir.exists():
        result.add_warning("未找到 logic_version/ 目录")

    # 1. 提取所有 RULE-ID
    rule_ids = extract_rule_ids(readme_path)
    unique_rules = set(rid for rid, _ in rule_ids)
    result.add_info(f"在 logic_readme.md 中找到 {len(unique_rules)} 个唯一的 RULE-ID")

    # 检查 RULE-ID 重复
    rule_counts = {}
    for rid, line_num in rule_ids:
        if rid not in rule_counts:
            rule_counts[rid] = []
        rule_counts[rid].append(line_num)

    for rid, lines in rule_counts.items():
        if len(lines) > 1:
            result.add_warning(f"{rid} 在 logic_readme.md 中出现多次 (行号: {', '.join(map(str, lines))})")

    # 2. 提取所有 CHG-ID
    chg_records = extract_chg_ids(change_path)
    result.add_info(f"在 logic_change.md 中找到 {len(chg_records)} 个变更议案")

    # 检查 CHG 状态
    for chg in chg_records:
        if chg['status'] == '未标注':
            result.add_warning(f"{chg['id']}: {chg['title']} - 缺少状态标注")
        elif '进行中' in chg['status'] or '待' in chg['status']:
            result.add_info(f"{chg['id']}: {chg['title']} - 状态: {chg['status']}")

    # 3. 检查决策记录
    version_records = find_version_records(version_dir)
    result.add_info(f"在 logic_version/records/ 中找到 {len(version_records)} 个决策记录")

    for record_path in version_records:
        # 检查必填字段
        missing = check_required_fields(record_path)
        if missing:
            result.add_error(f"{record_path.name} 缺少必填字段: {', '.join(missing)}")

        # 检查 Git commit hash
        commit_hash = extract_commit_hash(record_path)
        if commit_hash:
            if not is_valid_git_commit(commit_hash):
                result.add_error(f"{record_path.name} 中的 commit hash '{commit_hash}' 无效")
        else:
            result.add_warning(f"{record_path.name} 未关联 Git commit")

    # 4. 检查 Git 仓库状态
    try:
        git_status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=5
        )
        if git_status.returncode == 0:
            uncommitted = git_status.stdout.strip()
            if uncommitted:
                result.add_warning("有未提交的文件变更")
        else:
            result.add_warning("无法检查 Git 状态（可能未初始化 Git）")
    except:
        result.add_warning("Git 不可用或未安装")

    return result

def main():
    """主入口"""
    print("\n🔍 开始验证 Recall 系统一致性...\n")

    result = validate_recall()
    result.print_report()

    return 0 if result.is_valid() else 1

if __name__ == "__main__":
    exit(main())
