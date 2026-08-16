#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 一致性验证工具
检查 logic_readme.md, logic_change.md 和 logic_version/ 之间的一致性
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 决策记录文件名：logic_version-YYYYMMDD-NNN-<scope>.md
RECORD_NAME_RE = re.compile(
    r'^logic_version-(\d{8})-(\d{3})-.+\.md$', re.IGNORECASE
)

# 规则定义行（当前制度表格里以 RULE-ID 开头的行）；正文引用不算定义
RULE_DEF_RE = re.compile(r'^\|\s*(RULE-\d{3})\s*\|')
# 三处登记对账用：索引表行首的 VER-ID
VER_ROW_RE = re.compile(r'^\|\s*(VER-\d{8}-\d{3})\s*\|', re.MULTILINE)
# 功能意图层（RULE-014）：完整格式的 intent_id 与流程位置
INT_ID_RE = re.compile(r'^INT-\d{8}-\d{3}$')
INT_TOKEN_RE = re.compile(r'\bINT-\d{8}-\d{3}\b')
FLOW_POS_RE = re.compile(r'\bFLOW-(\d{3})#(\d+)\b')
FLOW_DEF_RE = re.compile(r'\bFLOW-(\d{3})\b')
# 未回填的占位符：只匹配字段行（正文里叙述性的 `_待填写_` 不算）
UNFILLED_PLACEHOLDER_RE = re.compile(
    r'^\s*-\s*\w+\s*[：:]\s*_待填写_\s*$', re.MULTILINE
)
# medium/high CHG 必填的需求拆解字段（RULE-014）
CHG_REQUIRED_ANALYSIS_FIELDS = ('raw_request', 'decomposition', 'fit_analysis')

# commit 关联的几种写法，按 references/ 下两个模板的实际格式
COMMIT_PATTERNS = (
    # 统一 schema 的实施提交字段: - after_commit: abc123（hook 回填）
    r'^\s*-\s*after_commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
    # logic-version-git-template.md: - **关联 Commit**: `abc123`
    r'关联\s*Commit\*{0,2}\s*[：:]\s*`?([0-9a-f]{7,40})`?',
    # logic-version-template.md 的 based_on: ... code: commit:abc123
    r'\bcode\s*:\s*commit\s*:\s*`?([0-9a-f]{7,40})`?',
    # 旧快速模板的独立控制字段: - commit: abc123
    r'^\s*-\s*commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
)


def _force_utf8_when_redirected() -> None:
    """重定向到文件/管道时把输出流切成 UTF-8。

    Windows 上重定向后的 stdout 用 ANSI 代码页（如 cp936），
    报告里的 emoji 会触发 UnicodeEncodeError。本脚本既可被
    recall.py 以子进程调用，也可被用户直接运行，所以必须自带这个修复。
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


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

def extract_rule_definitions(readme_path: Path) -> List[Tuple[str, int]]:
    """提取规则**定义行**（当前制度表格里以 RULE-ID 开头的行）。

    旧实现把文中每一次 RULE 引用（有效决策索引、功能意图登记、正文）都
    算作出现，导致"重复"警告全是噪音；重复只应针对定义行判定。
    """
    rule_defs = []
    if not readme_path.exists():
        return rule_defs

    with open(readme_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            match = RULE_DEF_RE.match(line)
            if match:
                rule_defs.append((match.group(1), line_num))

    return rule_defs


def markdown_section(content: str, heading: str) -> str:
    """返回 `## <heading>` 小节的正文（到下一个同级标题为止）；不存在返回空串。"""
    pattern = rf'^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ''


def check_intent_layer(content: str, rule_ids: set, result: 'ValidationResult') -> None:
    """校验功能意图与用户流程层（RULE-014）：编号格式、唯一性、引用有效性。

    没有该小节时静默跳过（尚未启用此层的项目不受影响）。
    """
    section = markdown_section(content, '功能意图与用户流程')
    if not section.strip():
        return

    # 解析 INT 登记表
    int_rows = []
    for line in section.splitlines():
        if not line.strip().startswith('| INT-'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) >= 5:
            int_rows.append(cells)

    int_ids = set()
    for cells in int_rows:
        intent_id = cells[0]
        if not INT_ID_RE.match(intent_id):
            result.add_error(
                f"功能意图登记 {intent_id}: 编号须为 INT-YYYYMMDD-NNN 完整格式"
                "（短编号不被审计与追溯链识别）"
            )
        if intent_id in int_ids:
            result.add_error(f"功能意图登记 {intent_id}: intent_id 重复")
        int_ids.add(intent_id)

    # 解析用户流程：每条 FLOW 的最大步骤号
    flow_steps = {}
    flow_section = re.search(
        r'###\s+用户流程\s*$(.*?)(?=^###\s|\Z)', section, re.MULTILINE | re.DOTALL
    )
    if flow_section:
        text = flow_section.group(1)
        positions = [(m.start(), m.group(1)) for m in FLOW_DEF_RE.finditer(text)]
        for i, (start, flow_num) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            steps = [int(n) for n in re.findall(r'(?<![#\d])(\d+)\.', text[start:end])]
            flow_steps[flow_num] = max(
                flow_steps.get(flow_num, 0), max(steps) if steps else 0
            )
        # 流程行中引用的 INT 必须已登记
        for token in INT_TOKEN_RE.findall(text):
            if token not in int_ids:
                result.add_error(f"用户流程引用了未登记的 {token}")

    # 登记表的流程位置与关联规则必须存在
    for cells in int_rows:
        intent_id, flow_pos, rules_cell = cells[0], cells[3], cells[4]
        for flow_num, step in FLOW_POS_RE.findall(flow_pos):
            if flow_num not in flow_steps:
                result.add_error(f"{intent_id}: 流程位置引用了不存在的 FLOW-{flow_num}")
            elif int(step) > flow_steps[flow_num]:
                result.add_error(
                    f"{intent_id}: 流程位置 FLOW-{flow_num}#{step} 超出该流程的步骤数"
                    f"（最大 {flow_steps[flow_num]}）"
                )
        for rule_id in re.findall(r'\bRULE-\d{3}\b', rules_cell):
            if rule_id not in rule_ids:
                result.add_error(f"{intent_id}: 关联规则 {rule_id} 未在当前制度中定义")

    # 操作直觉约束中引用的 INT 必须已登记
    uxi_section = re.search(
        r'###\s+操作直觉约束\s*$(.*?)(?=^###\s|\Z)', section, re.MULTILINE | re.DOTALL
    )
    if uxi_section:
        for token in INT_TOKEN_RE.findall(uxi_section.group(1)):
            if token not in int_ids:
                result.add_error(f"操作直觉约束引用了未登记的 {token}")

    if int_ids:
        result.add_info(
            f"功能意图层: {len(int_ids)} 个 INT、{len(flow_steps)} 条 FLOW 校验完成"
        )


def check_ver_registrations(
    version_records: List[Path],
    index_path: Path,
    readme_content: str,
    result: 'ValidationResult',
) -> None:
    """三处登记对账：records/ 文件、logic_version/index.md、logic_readme 有效决策索引。

    一条记录需要在三处登记（RULE-003）；任何一处缺失都会让追溯链对部分
    工具静默不可见。同时检测 version_id 撞号（并行会话/分支合并的风险）。
    """
    file_vers: Dict[str, List[str]] = {}
    for record_path in version_records:
        match = RECORD_NAME_RE.match(record_path.name)
        if not match:
            continue
        ver_id = f"VER-{match.group(1)}-{match.group(2)}"
        file_vers.setdefault(ver_id, []).append(record_path.name)

    for ver_id, names in file_vers.items():
        if len(names) > 1:
            result.add_error(f"{ver_id} 撞号：多个记录文件共用同一编号: {', '.join(names)}")

    index_vers = set()
    if index_path.exists():
        index_vers = set(VER_ROW_RE.findall(index_path.read_text(encoding='utf-8')))
    readme_vers = set(VER_ROW_RE.findall(readme_content))

    for ver_id in sorted(file_vers):
        if index_path.exists() and ver_id not in index_vers:
            result.add_warning(f"{ver_id} 未登记到 logic_version/index.md")
        if ver_id not in readme_vers:
            result.add_warning(f"{ver_id} 未登记到 logic_readme.md 的有效决策索引")
    for ver_id in sorted(index_vers - set(file_vers)):
        result.add_error(f"logic_version/index.md 登记的 {ver_id} 没有对应记录文件")
    for ver_id in sorted(readme_vers - set(file_vers)):
        result.add_error(f"logic_readme.md 有效决策索引登记的 {ver_id} 没有对应记录文件")


def check_chg_analysis_fields(change_path: Path, result: 'ValidationResult') -> None:
    """medium/high 通道的 CHG 必须含需求拆解与融入分析三字段（RULE-014）。"""
    if not change_path.exists():
        return
    content = change_path.read_text(encoding='utf-8')
    blocks = re.split(r'^(?=##\s+CHG-)', content, flags=re.MULTILINE)
    for block in blocks:
        header = re.match(r'##\s+(CHG-\d{8}-\d{3})', block)
        if not header:
            continue
        chg_id = header.group(1)
        route = re.search(r'^\s*-\s*recall_route\s*[：:]\s*(\S+)', block, re.MULTILINE)
        if not route or route.group(1) not in ('medium', 'high'):
            continue
        missing = [
            field
            for field in CHG_REQUIRED_ANALYSIS_FIELDS
            if not re.search(rf'^\s*-\s*{field}\s*[：:]\s*\S', block, re.MULTILINE)
        ]
        if missing:
            result.add_warning(
                f"{chg_id} (recall_route: {route.group(1)}) 缺少需求拆解字段: "
                f"{', '.join(missing)}（RULE-014 要求实施前填写）"
            )

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

            # 提取状态：优先模板字段 `- status:`（RULE-009 字段名以模板为准），
            # 兼容旧的中文"状态："写法
            block_end = content.find('\n## ', match.end())
            block = content[match.end():block_end if block_end != -1 else len(content)]
            status_match = re.search(
                r'^\s*-\s*status\s*[：:]\s*(.+?)\s*$', block, re.MULTILINE
            ) or re.search(r'状态[：:]\s*(.+?)(?:\n|$)', block)
            status = status_match.group(1).strip() if status_match else "未标注"

            chg_records.append({
                'id': chg_id,
                'title': title,
                'status': status
            })

    return chg_records

def find_version_records(version_dir: Path) -> List[Path]:
    """查找所有决策记录文件。

    实际文件名格式是 `logic_version-YYYYMMDD-NNN-<scope>.md`
    （见 references/logic-version-template.md 的 version_slug）。
    旧代码 glob 的是 `ver-*.md`，永远匹配不到任何文件，
    导致下游的必填字段和 commit 校验全部成为死代码。
    这里按记录名正则筛选，并排除 README.md 等说明文件。
    """
    records_dir = version_dir / "records"
    if not records_dir.exists():
        return []

    return sorted(
        path
        for path in records_dir.glob("*.md")
        if RECORD_NAME_RE.match(path.name)
    )

def extract_commit_hash(record_path: Path) -> str:
    """从决策记录中提取 Git commit hash"""
    if not record_path.exists():
        return ""

    with open(record_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for pattern in COMMIT_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)

    return ""

def check_required_fields(record_path: Path) -> List[str]:
    """检查决策记录的必填字段。

    字段名以 references/logic-version-template.md 为准。旧代码检查的
    `版本号` / `关联 Commit` / `创建日期` / `## 修改原因` / `## 决策过程`
    从来不是这个 schema 的字段，一旦 glob 修好就会让每条记录都报假缺失。
    """
    required_fields = [
        (r'^\s*-\s*version_id\s*:', 'version_id'),
        (r'^\s*-\s*date\s*:', 'date'),
        (r'^\s*-\s*status\s*:', 'status'),
        (r'^\s*##\s*为什么', '## 为什么做这个决策？'),
        (r'^\s*##\s*影响范围', '## 影响范围'),
        (r'^\s*##\s*验证方式', '## 验证方式'),
        (r'^\s*##\s*回滚方式', '## 回滚方式'),
    ]

    missing_fields = []

    with open(record_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for field_pattern, field_name in required_fields:
        if not re.search(field_pattern, content, re.MULTILINE):
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
            encoding='utf-8',
            errors='replace',
            timeout=5
        )
    except (OSError, subprocess.SubprocessError):
        # git 未安装、不在 PATH，或超时
        return False
    return result.returncode == 0 and 'commit' in (result.stdout or '')

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

    readme_content = readme_path.read_text(encoding='utf-8')

    # 1. 提取规则定义（只有定义行算数；正文/索引/意图层的引用不算重复）
    rule_defs = extract_rule_definitions(readme_path)
    unique_rules = set(rid for rid, _ in rule_defs)
    result.add_info(f"在 logic_readme.md 中找到 {len(unique_rules)} 条规则定义")

    rule_counts: Dict[str, List[int]] = {}
    for rid, line_num in rule_defs:
        rule_counts.setdefault(rid, []).append(line_num)

    for rid, lines in rule_counts.items():
        if len(lines) > 1:
            result.add_error(
                f"{rid} 被定义多次 (行号: {', '.join(map(str, lines))})"
            )

    # 1b. 功能意图与用户流程层（RULE-014）
    check_intent_layer(readme_content, unique_rules, result)

    # 2. 提取所有 CHG-ID
    chg_records = extract_chg_ids(change_path)
    result.add_info(f"在 logic_change.md 中找到 {len(chg_records)} 个变更议案")

    # 检查 CHG 状态
    for chg in chg_records:
        if chg['status'] == '未标注':
            result.add_warning(f"{chg['id']}: {chg['title']} - 缺少状态标注")
        elif '进行中' in chg['status'] or '待' in chg['status']:
            result.add_info(f"{chg['id']}: {chg['title']} - 状态: {chg['status']}")

    # 2b. medium/high CHG 的需求拆解字段（RULE-014）
    check_chg_analysis_fields(change_path, result)

    # 3. 检查决策记录
    version_records = find_version_records(version_dir)
    result.add_info(f"在 logic_version/records/ 中找到 {len(version_records)} 个决策记录")

    for record_path in version_records:
        # 检查必填字段
        missing = check_required_fields(record_path)
        if missing:
            result.add_error(f"{record_path.name} 缺少必填字段: {', '.join(missing)}")

        record_text = record_path.read_text(encoding='utf-8')
        if UNFILLED_PLACEHOLDER_RE.search(record_text):
            result.add_warning(
                f"{record_path.name} 的 after_commit 占位符尚未回填"
                "（提交时带 Ref 行、或将记录与代码同提交，hook 会自动回填）"
            )

        # 检查 Git commit hash
        commit_hash = extract_commit_hash(record_path)
        if commit_hash:
            if not is_valid_git_commit(commit_hash):
                result.add_error(f"{record_path.name} 中的 commit hash '{commit_hash}' 无效")
        else:
            result.add_warning(f"{record_path.name} 未关联 Git commit")

    # 3b. 三处登记对账与撞号检测
    check_ver_registrations(
        version_records, version_dir / "index.md", readme_content, result
    )

    # 4. 检查 Git 仓库状态
    try:
        git_status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=root,
            timeout=5
        )
    except (OSError, subprocess.SubprocessError):
        result.add_warning("Git 不可用或未安装")
    else:
        if git_status.returncode == 0:
            if (git_status.stdout or '').strip():
                result.add_warning("有未提交的文件变更")
        else:
            result.add_warning("无法检查 Git 状态（可能未初始化 Git）")

    return result

def main() -> int:
    """主入口。返回退出码，供 recall.py 直接使用。"""
    _force_utf8_when_redirected()
    print("\n🔍 开始验证 Recall 系统一致性...\n")

    result = validate_recall()
    result.print_report()

    return 0 if result.is_valid() else 1

if __name__ == "__main__":
    sys.exit(main())
