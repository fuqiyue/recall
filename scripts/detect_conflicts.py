#!/usr/bin/env python3
"""
Recall 冲突检测脚本

检测 logic_readme.md 和 logic_change.md 中的规则冲突：
- RULE-* 之间的逻辑矛盾
- CHG-* 与现有 RULE 的冲突
- 提示用户需要澄清的地方
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_common import (  # noqa: E402
    change_ledgers,
    find_project_root,
    force_utf8_output,
    registered_domains,
)


def extract_rules(content: str) -> List[Dict[str, str]]:
    """从 logic_readme.md 提取所有 RULE-* 规则"""
    rules = []

    # 匹配规则表格行
    # | RULE-001 | key | 规则描述 | 原因 | ...
    pattern = r'\|\s*(RULE-\d+)\s*\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'

    for match in re.finditer(pattern, content):
        rule_id, level, description, reason = match.groups()
        rules.append({
            'id': rule_id.strip(),
            'level': level.strip(),
            'description': description.strip(),
            'reason': reason.strip()
        })

    return rules


def extract_rule_dates(content: str) -> Dict[str, str]:
    """规则行的 last_reviewed（第 9 列）：用于判断规则是否在议案之后被修改。"""
    dates: Dict[str, str] = {}
    for line in content.splitlines():
        if not line.strip().upper().startswith('| RULE-'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) >= 9 and re.match(r'^\d{4}-\d{2}-\d{2}$', cells[8]):
            dates[cells[0].upper()] = cells[8]
    return dates


def _change_field(change: Dict, key: str) -> str:
    for line in change['content']:
        m = re.match(rf'^\s*-\s*{key}\s*[：:]\s*(.+?)\s*$', line)
        if m:
            return m.group(1)
    return ''


def check_multi_proposal_conflicts(changes: List[Dict]) -> List[Tuple[str, str, str]]:
    """一法多议案：两个活跃议案的 authority_surfaces 指向同一 RULE，却未互写 conflicts_with。"""
    findings = []
    parsed = []
    for change in changes:
        targets = set(t.upper() for t in re.findall(r'\bRULE-[A-Z0-9][A-Z0-9-]*', _change_field(change, 'authority_surfaces'), re.IGNORECASE))
        conflicts = set(c.upper() for c in re.findall(r'\bCHG-[A-Z0-9][A-Z0-9-]*', _change_field(change, 'conflicts_with'), re.IGNORECASE))
        parsed.append((change, targets, conflicts))
    for i, (a, ta, ca) in enumerate(parsed):
        for b, tb, cb in parsed[i + 1:]:
            shared = sorted(ta & tb)
            if shared and (b['id'].upper() not in ca or a['id'].upper() not in cb):
                findings.append((a['id'], b['id'], f"同时指向 {', '.join(shared)}，但未互写 conflicts_with / conflict_resolution（一法多议案须显式裁定：merge / supersede / sequence-and-revalidate）"))
    return findings


def check_stale_baselines(changes: List[Dict], rule_dates: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """旧议案 vs 新法：目标规则的 last_reviewed 晚于议案的 created/last_status_change。"""
    findings = []
    for change in changes:
        dates = [d for d in (_change_field(change, 'created'), _change_field(change, 'last_status_change')) if re.match(r'^\d{4}-\d{2}-\d{2}$', d)]
        if not dates:
            continue
        change_date = max(dates)
        for rule_id in sorted(set(t.upper() for t in re.findall(r'\bRULE-[A-Z0-9][A-Z0-9-]*', _change_field(change, 'authority_surfaces'), re.IGNORECASE))):
            rule_date = rule_dates.get(rule_id, '')
            if rule_date and rule_date > change_date:
                findings.append((change['id'], rule_id, f"规则于 {rule_date} 修订，晚于议案 {change_date}；须重核 based_on 并递增 proposal_revision（生命周期第 3 步）"))
    return findings


def extract_changes(content: str) -> List[Dict[str, str]]:
    """从 logic_change.md 提取所有 CHG-* 议案"""
    changes = []

    # 找到 CHG-ID 标题行。标准写法是 `## CHG-YYYYMMDD-NNN: 标题`
    # （与 validate.py 的提取规则一致），也兼容无 # 前缀的裸写法。
    # 旧正则要求行首就是 "CHG-"，对标准标题永远匹配不到，
    # 导致议案与规则的冲突检测一直返回空。
    lines = content.split('\n')
    current_chg = None

    for line in lines:
        chg_match = re.match(r'(?:#{1,6}\s+)?CHG-(\d{8}-\d+):\s*(.+)', line)
        if chg_match:
            if current_chg:
                changes.append(current_chg)
            current_chg = {
                'id': f'CHG-{chg_match.group(1)}',
                'title': chg_match.group(2).strip(),
                'content': []
            }
        elif current_chg and line.strip():
            current_chg['content'].append(line)

    if current_chg:
        changes.append(current_chg)

    return changes


def detect_keyword_conflicts(rules: List[Dict[str, str]]) -> List[Tuple[str, str, str]]:
    """检测规则间的关键词冲突

    返回: [(rule1_id, rule2_id, conflict_reason), ...]
    """
    conflicts = []

    # 对立关键词对
    opposite_pairs = [
        (['必须', '强制', '禁止'], ['可选', '允许', '不需要']),
        (['所有', '任何', '全部'], ['部分', '某些', '特定']),
        (['永远', '总是'], ['有时', '可能', '某些情况']),
    ]

    for i, rule1 in enumerate(rules):
        for rule2 in rules[i+1:]:
            # 检查描述中是否包含对立关键词
            desc1 = rule1['description']
            desc2 = rule2['description']

            for positive_words, negative_words in opposite_pairs:
                has_positive_1 = any(word in desc1 for word in positive_words)
                has_negative_1 = any(word in desc1 for word in negative_words)
                has_positive_2 = any(word in desc2 for word in positive_words)
                has_negative_2 = any(word in desc2 for word in negative_words)

                # 如果一个规则用正面词，另一个用负面词，可能存在冲突
                if (has_positive_1 and has_negative_2) or (has_negative_1 and has_positive_2):
                    # 进一步检查：是否谈论相似主题
                    # 简单启发式：提取名词
                    nouns1 = set(re.findall(r'[一-鿿]{2,}', desc1))
                    nouns2 = set(re.findall(r'[一-鿿]{2,}', desc2))

                    common_topics = nouns1 & nouns2
                    if common_topics:
                        conflicts.append((
                            rule1['id'],
                            rule2['id'],
                            f"可能存在矛盾：涉及相同主题 {common_topics}，但使用对立表述"
                        ))

    return conflicts


def check_change_rule_conflicts(
    changes: List[Dict[str, str]],
    rules: List[Dict[str, str]]
) -> List[Tuple[str, str, str]]:
    """检查议案与现有规则的冲突"""
    conflicts = []

    for change in changes:
        chg_id = change['id']
        chg_text = change['title'] + ' '.join(change['content'])

        # 检查是否明确提到某个 RULE
        mentioned_rules = re.findall(r'RULE-\d+', chg_text)

        for rule in rules:
            rule_id = rule['id']

            # 如果议案明确提到这个规则
            if rule_id in mentioned_rules:
                # 检查是否包含"修改"、"废弃"、"覆盖"等词
                if any(word in chg_text for word in ['修改', '废弃', '取消', '覆盖', '替换']):
                    conflicts.append((
                        chg_id,
                        rule_id,
                        f"议案提议修改现有规则，需要确认优先级和迁移路径"
                    ))

    return conflicts


def format_conflict_report(
    rule_conflicts: List[Tuple[str, str, str]],
    change_conflicts: List[Tuple[str, str, str]]
) -> str:
    """格式化冲突报告"""
    report = []

    limitation = (
        "ℹ️  本检测为关键词级启发式：只识别对立表述 + 共同主题的组合，"
        "误报和漏报都可能存在；不覆盖功能意图层（INT/FLOW/UXI）的语义冲突。"
        "语义级矛盾仍须按 SKILL.md 核心原则 5 由用户澄清裁决。"
    )

    if not rule_conflicts and not change_conflicts:
        return f"✅ 未检测到明显冲突\n\n{limitation}"

    report.append("⚠️  检测到潜在冲突\n")
    report.append(limitation + "\n")

    if rule_conflicts:
        report.append("## 规则间冲突\n")
        for rule1, rule2, reason in rule_conflicts:
            report.append(f"- **{rule1}** ↔ **{rule2}**")
            report.append(f"  {reason}\n")

    if change_conflicts:
        report.append("## 议案与规则冲突\n")
        for chg, rule, reason in change_conflicts:
            report.append(f"- **{chg}** ↔ **{rule}**")
            report.append(f"  {reason}\n")

    report.append("\n## 建议行动\n")
    report.append("1. 阅读冲突的规则/议案原文")
    report.append("2. 确认是否真实冲突（可能是特例关系）")
    report.append("3. 在 logic_change.md 中标注 `conflicts_with: RULE-XXX`")
    report.append("4. 由用户明确优先级或澄清边界")

    return '\n'.join(report)


def main(argv=None):
    """主函数。``argv`` 为可选的项目根参数列表；不给时按 cwd 向上查找。

    旧实现直接读 ``sys.argv[1]``：经 ``recall conflicts`` 调用时 argv[1]
    是子命令名 ``conflicts``，于是把它当目录、永远报找不到
    logic_readme.md（VER-20260903-002）。
    """
    force_utf8_output()

    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        project_root = find_project_root(Path(args[0]))
    else:
        project_root = find_project_root()

    readme_path = project_root / 'logic_readme.md'
    change_path = project_root / 'logic_change.md'

    # 检查文件存在
    if not readme_path.exists():
        print(f"❌ 未找到 logic_readme.md: {readme_path}", file=sys.stderr)
        return 1

    # 一二级拆分法（RULE-018）：议案分布在根账本与各领域账本
    ledgers = change_ledgers(project_root)
    if not change_path.exists():
        print("ℹ️  未找到 logic_change.md，跳过根账本议案检查")
    changes = []
    for _label, ledger_path in ledgers:
        with open(ledger_path, 'r', encoding='utf-8') as f:
            changes.extend(extract_changes(f.read()))

    # 读取规则：宪法（根）+ 全部领域 readme（部门法）
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
        rules = extract_rules(readme_content)
    domain_readmes = [d.readme for d in registered_domains(project_root) if d.readme.exists()]
    for domain_readme in domain_readmes:
        rules.extend(extract_rules(domain_readme.read_text(encoding='utf-8')))

    print(
        f"📋 读取到 {len(rules)} 条规则（宪法 + {len(domain_readmes)} 份领域文档），"
        f"{len(changes)} 个活跃议案（{len(ledgers)} 份账本）\n"
    )

    rule_dates = extract_rule_dates(readme_content)
    for domain_readme in domain_readmes:
        rule_dates.update(extract_rule_dates(domain_readme.read_text(encoding='utf-8')))

    # 检测冲突
    rule_conflicts = detect_keyword_conflicts(rules)
    change_conflicts = check_change_rule_conflicts(changes, rules)
    multi_proposal = check_multi_proposal_conflicts(changes)
    stale = check_stale_baselines(changes, rule_dates)

    # 输出报告
    report = format_conflict_report(rule_conflicts, change_conflicts)
    print(report)
    if multi_proposal:
        print("\n⚖️  一法多议案（同一规则被多个活跃议案指向，未显式裁定）：")
        for a, b, reason in multi_proposal:
            print(f"  • {a} ↔ {b}: {reason}")
    if stale:
        print("\n🕰️  旧议案 vs 新法（规则在议案之后被修订，基线可能失效）：")
        for chg, rule, reason in stale:
            print(f"  • {chg} → {rule}: {reason}")
    if not multi_proposal and not stale:
        print("\n⚖️  一法多议案 / 基线失效：未发现")

    # 如果检测到冲突，返回非零退出码
    if rule_conflicts or change_conflicts or multi_proposal or stale:
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
