#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 一致性验证工具
检查 logic_readme.md, logic_change.md 和 logic_version/ 之间的一致性
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_common import (
    CHANGE_ID_PATTERN,  # noqa: E402  RULE-021 ③：议案编号只此一份
    change_ledgers,
    classify_porcelain,
    find_project_root,
    force_utf8_output,
    git_output,
    run_git,
    unpushed_commit_count,
)

# 决策记录文件名：logic_version-YYYYMMDD-NNN-<scope>.md
RECORD_NAME_RE = re.compile(
    r'^logic_version-(\d{8})-(\d{3})-.+\.md$', re.IGNORECASE
)

# 规则定义行（当前制度表格里以 RULE-ID 开头的行）；正文引用不算定义
RULE_DEF_RE = re.compile(r'^\|\s*(RULE-\d{3})\s*\|')
# 三处登记对账用：索引表首列的 VER-ID。模板写裸 ID，消费项目常写成
# `[VER-…](records/…)` 或反引号，三种形态都算登记；其余形态单独提示格式
VER_ROW_RE = re.compile(
    r'^\|\s*(?:\[\s*)?`?(VER-\d{8}-\d{3})`?(?:\s*\]\([^)\n]*\))?\s*\|',
    re.MULTILINE,
)
# 首列含 VER-ID 但不是上面三种形态（如 `VER-… (草案)`）：报格式而不是报未登记
VER_FIRST_CELL_RE = re.compile(r'^\|[^|\n]*?(VER-\d{8}-\d{3})[^|\n]*\|', re.MULTILINE)
# 功能意图层（RULE-014）：完整格式的 intent_id 与流程位置
INT_ID_RE = re.compile(r'^INT-\d{8}-\d{3}$')
INT_TOKEN_RE = re.compile(r'\bINT-\d{8}-\d{3}\b')
FLOW_POS_RE = re.compile(r'\bFLOW-(\d{3})#(\d+)\b')
FLOW_DEF_RE = re.compile(r'\bFLOW-(\d{3})\b')
# 未回填的占位符：只匹配字段行（正文里叙述性的 `_待填写_` 不算）
UNFILLED_PLACEHOLDER_RE = re.compile(
    r'^\s*-\s*\w+\s*[：:]\s*_待填写_\s*$', re.MULTILINE
)
# medium/high CHG 必填的需求拆解字段（RULE-014）；
# 归档时必须搬入 VER 记录（需求保全：CHG 删除后需求拆解不得只剩 git 考古可查）
CHG_REQUIRED_ANALYSIS_FIELDS = ('raw_request', 'decomposition', 'fit_analysis')

# 非生效状态的记录不进"有效决策索引"（RULE-014 落选方案归档会产生 rejected 记录；
# 强制登记会把被否决的方案说成有效决策）。index.md 仍须登记全部记录。
INACTIVE_RECORD_STATUSES = {'rejected', 'cancelled', 'rolled-back'}

# 漂移度量（RULE-015）：纯代码/自动保存提交累积超过阈值时告警
DRIFT_WARNING_THRESHOLD = 10

# commit 关联的几种写法，按 references/ 下两个模板的实际格式
COMMIT_PATTERNS = (
    # 统一 schema 的实施提交字段: - after_commit: abc123（hook 回填）
    r'^\s*-\s*after_commit\s*[：:]\s*`?(?:commit:)?([0-9a-f]{7,40})`?\s*$',
    # 旧记录格式兼容: - **关联 Commit**: `abc123`
    r'关联\s*Commit\*{0,2}\s*[：:]\s*`?([0-9a-f]{7,40})`?',
    # logic-version-template.md 扩展 schema 的 based_on: ... code: commit:abc123
    r'\bcode\s*:\s*commit\s*:\s*`?([0-9a-f]{7,40})`?',
    # 旧快速模板的独立控制字段: - commit: abc123
    r'^\s*-\s*commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
)




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


def find_registered_child_readmes(
    readme_content: str, root: Path
) -> Tuple[List[Path], List[str]]:
    """范围登记表中二级文档（paired 领域 + 旧式 readme-only）的 readme 路径（RULE-018）。

    返回 (存在的子文档, 登记了但文件缺失的 scope 列表)。部门法与宪法
    共用同一 RULE/INT 编号空间，必须纳入同一套一致性检查，否则拆分后
    的领域进入无检查区。
    """
    paths: List[Path] = []
    missing: List[str] = []
    for line in readme_content.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if (
            len(cells) >= 5
            and cells[2] == 'in-system'
            and cells[4] in ('readme-only', 'paired')
        ):
            scope = cells[1].strip().strip('/').replace('\\', '/')
            if scope in ('', '.'):
                continue
            candidate = root / scope / 'logic_readme.md'
            if candidate.exists():
                paths.append(candidate)
            else:
                missing.append(scope)
    return paths, missing


def split_code_anchor(anchor: str) -> Tuple[str, str]:
    """把 `path#symbol` / `path:line` 形态的代码锚点拆成 (路径, 符号)。

    旧代码拿整串去 `exists()`，`scripts/validate.py#check_intent_layer`
    这类正确锚点被报"不存在"（2026-09-03 eduai 6 处误报）。行号形态只保留路径。
    """
    path_part, _, symbol = anchor.partition('#')
    line_match = re.match(r'^(.+?):(\d+)(?:-\d+)?$', path_part)
    if line_match:
        path_part = line_match.group(1)
    return path_part.strip(), symbol.strip()


def anchor_symbol_present(target: Path, symbol: str) -> bool:
    """符号锚点的最低限度核查：符号名在目标文件文本中出现（不做语法解析）。"""
    try:
        text = target.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return True
    return symbol in text


def check_intent_layer(
    content: str, rule_ids: set, result: 'ValidationResult', root: Path = None,
    doc_label: str = 'logic_readme.md', seen_int_ids: set = None
) -> None:
    """校验功能意图与用户流程层（RULE-014）：编号格式、唯一性、引用有效性。

    传入 root 时同时检查登记表"代码锚点"列的路径存在性——反向查询
    （recall query intent）依赖这一列，锚点悬空会让 INT→代码静默断链。
    传入 seen_int_ids 时跨文档累计编号（RULE-018：根与子文档共用编号空间）。
    没有该小节时静默跳过（尚未启用此层的项目不受影响）。
    """
    section = markdown_section(content, '功能意图与用户流程')
    if not section.strip():
        return

    # 解析 INT 登记表（含表头：定位可选的"来源"列）
    int_rows = []
    source_col = None
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith('| intent_id'):
            headers = [cell.strip() for cell in stripped.strip('|').split('|')]
            for idx, header in enumerate(headers):
                if header.startswith('来源'):
                    source_col = idx
            continue
        if not stripped.startswith('| INT-'):
            continue
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if len(cells) >= 5:
            int_rows.append(cells)

    # RULE-014/016：用户表述即宪法——每条意图须标来源；AI 推断不得冒充用户确认
    if int_rows and source_col is None:
        result.add_info(
            f"{doc_label}: 功能意图登记表缺少「来源」列（RULE-014：建议补 "
            "user:YYYY-MM-DD / user-confirmed:YYYY-MM-DD / code-derived / inferred，"
            "区分用户表述与 AI 推断）"
        )
    elif source_col is not None:
        for cells in int_rows:
            source = cells[source_col] if len(cells) > source_col else ''
            lowered = source.lower()
            if not source or lowered in ('inferred', 'code-derived') or lowered.startswith(('inferred', 'code-derived')):
                result.add_warning(
                    f"{cells[0]}: 意图来源为「{source or '空'}」，尚未经用户确认"
                    "（RULE-016：意图层必须经用户确认后落盘；确认后改为 user-confirmed:日期）"
                )
            elif not re.match(r'^user(?:-confirmed)?:\d{4}-\d{2}-\d{2}', lowered):
                result.add_warning(
                    f"{cells[0]}: 意图来源「{source}」格式无法识别"
                    "（应为 user:日期 / user-confirmed:日期 / code-derived / inferred）"
                )

    int_ids = set()
    for cells in int_rows:
        intent_id = cells[0]
        if not INT_ID_RE.match(intent_id):
            result.add_error(
                f"功能意图登记 {intent_id}: 编号须为 INT-YYYYMMDD-NNN 完整格式"
                "（短编号不被审计与追溯链识别）"
            )
        if intent_id in int_ids or (seen_int_ids and intent_id in seen_int_ids):
            result.add_error(
                f"功能意图登记 {intent_id}: intent_id 重复（{doc_label}；"
                "编号空间全项目唯一，含子文档）"
            )
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
        # 代码锚点列（第 6 列，可选）：路径必须存在
        if root is not None and len(cells) >= 7:
            anchors_cell = cells[5]
            if anchors_cell and anchors_cell.lower() != 'none':
                for anchor in re.split(r'[;，,]', anchors_cell):
                    anchor = anchor.strip().strip('`')
                    if not anchor:
                        continue
                    # 只检查路径形态的锚点；纯符号/路由锚点无法静态验证
                    if '/' not in anchor and '.' not in anchor:
                        continue
                    path_part, symbol = split_code_anchor(anchor)
                    target = root / path_part
                    if not target.exists():
                        result.add_warning(
                            f"{intent_id}: 代码锚点 {path_part} 不存在"
                            "（文件改名/移动后请更新功能意图登记表）"
                        )
                    elif symbol and target.is_file() and not anchor_symbol_present(target, symbol):
                        result.add_warning(
                            f"{intent_id}: 代码锚点 {path_part} 中找不到符号 {symbol}"
                            "（函数/类改名后请更新功能意图登记表）"
                        )

    # 操作直觉约束中引用的 INT 必须已登记
    uxi_section = re.search(
        r'###\s+操作直觉约束\s*$(.*?)(?=^###\s|\Z)', section, re.MULTILINE | re.DOTALL
    )
    if uxi_section:
        for token in INT_TOKEN_RE.findall(uxi_section.group(1)):
            if token not in int_ids:
                result.add_error(f"操作直觉约束引用了未登记的 {token}")

    if seen_int_ids is not None:
        seen_int_ids.update(int_ids)

    if int_ids:
        result.add_info(
            f"功能意图层（{doc_label}）: {len(int_ids)} 个 INT、"
            f"{len(flow_steps)} 条 FLOW 校验完成"
        )


def rule_linked_versions(*readme_texts: str) -> set:
    """规则定义行（宪法 + 领域）决策记录列里直接链接的 VER-ID 集合。

    RULE-002：宪法有效决策索引只留指针 + 最近几条，生效 VER 的长期落点是
    相关规则行的决策记录列；这里收集这些反链供登记对账使用。
    """
    linked: set = set()
    for text in readme_texts:
        for line in (text or '').splitlines():
            if RULE_DEF_RE.match(line):
                linked.update(re.findall(r'\bVER-\d{8}-\d{3}\b', line))
    return linked


def check_ver_registrations(
    version_records: List[Path],
    index_path: Path,
    readme_content: str,
    result: 'ValidationResult',
    domain_readme_contents: Optional[List[str]] = None,
) -> None:
    """VER 登记对账：records/ 文件 ↔ logic_version/index.md ↔ 现行文档引用。

    每条记录必须登记 index.md；生效记录还必须被现行文档引用——出现在宪法
    有效决策索引，或被宪法/领域任一规则定义行的决策记录列直接链接（RULE-002：
    宪法索引只留指针 + 最近几条，全量索引在 index.md）。任何一处缺失都会让
    追溯链对部分工具静默不可见。同时检测 version_id 撞号。
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

    # 记录状态：非生效记录（rejected/cancelled/rolled-back）豁免有效决策索引登记
    record_status: Dict[str, str] = {}
    for record_path in version_records:
        match = RECORD_NAME_RE.match(record_path.name)
        if not match:
            continue
        ver_id = f"VER-{match.group(1)}-{match.group(2)}"
        status_match = re.search(
            r'^\s*-\s*status\s*[：:]\s*(\S+)', record_path.read_text(encoding='utf-8'),
            re.MULTILINE,
        )
        if status_match:
            record_status[ver_id] = status_match.group(1).strip('`').lower()

    index_vers = set()
    if index_path.exists():
        index_text = index_path.read_text(encoding='utf-8')
        index_vers = set(VER_ROW_RE.findall(index_text))
        for ver_id in sorted(set(VER_FIRST_CELL_RE.findall(index_text)) - index_vers):
            result.add_warning(
                f"logic_version/index.md 有 {ver_id} 行但首列格式不识别"
                "（应为裸 ID、[ID](path) 或 `ID`，否则会被当作未登记）"
            )
    readme_vers = set(VER_ROW_RE.findall(readme_content))
    linked_vers = rule_linked_versions(readme_content, *(domain_readme_contents or []))

    for ver_id in sorted(file_vers):
        if index_path.exists() and ver_id not in index_vers:
            result.add_warning(f"{ver_id} 未登记到 logic_version/index.md")
        inactive = record_status.get(ver_id) in INACTIVE_RECORD_STATUSES
        if ver_id not in readme_vers and ver_id not in linked_vers and not inactive:
            result.add_warning(
                f"{ver_id} 未被现行文档引用：既不在 logic_readme.md 的有效决策索引，"
                "也没有任何规则行的决策记录列链接它（RULE-002）"
            )
        if ver_id in readme_vers and inactive:
            result.add_warning(
                f"{ver_id} 状态为 {record_status.get(ver_id)}，"
                "不应登记在 logic_readme.md 的有效决策索引（index.md 登记即可）"
            )
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
        header = re.match(rf'##\s+({CHANGE_ID_PATTERN})', block)
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

def check_record_requirement_fields(
    record_text: str, record_name: str, result: 'ValidationResult'
) -> None:
    """需求保全：来自 CHG 的记录（change_id != none）必须搬入需求拆解三字段。

    CHG 归档后即从 logic_change.md 删除；三字段不落入不可变记录，
    需求拆解就只剩 git 考古可查，违反"recall 而非 rescan"的立项目的。
    只检查规则生效日（2026-08-16，RULE-014 需求保全条款）之后的记录：
    历史记录缺字段不构成当前状态审查失败（SKILL.md 调用模式约定）。
    """
    name_match = RECORD_NAME_RE.match(record_name)
    if name_match and name_match.group(1) < '20260816':
        return
    change_id = re.search(
        r'^\s*-\s*change_id\s*[：:]\s*(\S+)', record_text, re.MULTILINE
    )
    if not change_id:
        return
    value = change_id.group(1).strip('`')
    if value.lower() in ('none', 'n/a') or value.startswith('<'):
        return
    missing = [
        field
        for field in CHG_REQUIRED_ANALYSIS_FIELDS
        if not re.search(rf'^\s*-\s*{field}\s*[：:]\s*\S', record_text, re.MULTILINE)
    ]
    if missing:
        result.add_warning(
            f"{record_name} 关联 {value} 但缺少需求拆解字段: {', '.join(missing)}"
            "（归档时应从 CHG 原样搬入，否则需求原文随 CHG 删除而丢失）"
        )


def extract_chg_ids(change_path: Path) -> List[Dict]:
    """从 logic_change.md 提取所有 CHG-ID 及状态"""
    chg_records = []
    if not change_path.exists():
        return chg_records

    with open(change_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 匹配 CHG-ID 标题
        pattern = rf'^\s*##\s+({CHANGE_ID_PATTERN}):\s*(.+?)$'
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

def extract_commit_hash(record_path: Path, content: Optional[str] = None) -> str:
    """从决策记录中提取 Git commit hash（裸 SHA、反引号或 `commit:` 前缀）"""
    if content is None:
        if not record_path.exists():
            return ""
        content = record_path.read_text(encoding='utf-8')

    for pattern in COMMIT_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)

    return ""

# 记录控制字段：两套模板共有
RECORD_CONTROL_FIELDS = [
    (r'^\s*-\s*version_id\s*:', 'version_id'),
    (r'^\s*-\s*date\s*:', 'date'),
    (r'^\s*-\s*status\s*:', 'status'),
]
# 正文必备章节：references/logic-version-template.md 有两套 schema，
# 记录满足任一套即可（RULE-009 字段名以模板为准，模板有几套就认几套）
RECORD_SCHEMAS = {
    '快速模板': [
        (r'^\s*##\s*为什么', '## 为什么做这个决策？'),
        (r'^\s*##\s*影响范围', '## 影响范围'),
        (r'^\s*##\s*验证方式', '## 验证方式'),
        (r'^\s*##\s*回滚方式', '## 回滚方式'),
    ],
    '扩展 schema': [
        (r'^\s*##\s*变更摘要', '## 变更摘要'),
        (r'^\s*##\s*影响与消费者', '## 影响与消费者'),
        (r'^\s*##\s*兼容、迁移与回滚', '## 兼容、迁移与回滚'),
        (r'^\s*##\s*测试与审核', '## 测试与审核'),
    ],
}


def _missing_by_patterns(content: str, fields) -> List[str]:
    return [
        name for pattern, name in fields
        if not re.search(pattern, content, re.MULTILINE)
    ]


def check_required_fields(record_path: Path, content: Optional[str] = None) -> List[str]:
    """检查决策记录的必填字段；返回缺失字段名列表（空表示通过）。

    字段名以 references/logic-version-template.md 为准。模板有快速模板与
    扩展 schema 两套正文章节，旧代码只认快速模板，按扩展 schema 写的记录
    每条都报 4 个假缺失（2026-09-03 eduai 46 份记录全部 FAIL）。这里控制
    字段两套共有必查；正文章节满足任一套即通过，都不满足时按更接近的一套
    报缺失并注明 schema 名。
    """
    if content is None:
        content = record_path.read_text(encoding='utf-8')

    missing = _missing_by_patterns(content, RECORD_CONTROL_FIELDS)
    by_schema = {
        name: _missing_by_patterns(content, fields)
        for name, fields in RECORD_SCHEMAS.items()
    }
    if all(by_schema.values()):
        # 都不满足：取缺失最少的一套（并列时保持声明顺序，即快速模板优先）
        schema_name = min(by_schema, key=lambda name: len(by_schema[name]))
        missing.extend(f'{field}（{schema_name}）' for field in by_schema[schema_name])
    return missing

def is_valid_git_commit(commit_hash: str, cwd: Optional[Path] = None) -> bool:
    """检查 Git commit hash 在 ``cwd`` 所在仓库是否有效。

    其余 Git 调用都传项目根；这里此前漏传，skill 集中安装后从项目外目录
    运行会查到错误的仓库。
    """
    if not commit_hash:
        return False

    # git 未安装、不在 PATH 或超时时 run_git 返回 ok=False，不抛异常（RULE-021）
    ok, out, _ = run_git(['cat-file', '-t', commit_hash], cwd=cwd, timeout=5)
    return ok and 'commit' in out

def check_doc_drift(root: Path, result: 'ValidationResult') -> None:
    """漂移度量（RULE-015）：统计自上次触及 logic 文档以来累积的提交数。

    post-commit 哨兵只打一行非阻断提醒，自动化运行时无人阅读；这里把
    漂移变成可观测数字：纯代码/自动保存提交累积超过阈值时升级为警告。
    """
    logic_pathspecs = [
        'logic_change.md', 'logic_version', ':(glob)**/logic_readme.md'
    ]

    def _git(args: List[str]) -> str:
        return (git_output(args, cwd=root, timeout=10) or '').strip()

    last_logic = _git(['rev-list', '-1', 'HEAD', '--'] + logic_pathspecs)
    if not last_logic:
        return  # 非 git 仓库、无提交或从未提交过 logic 文档：不做判断
    count_output = _git(['rev-list', '--count', f'{last_logic}..HEAD'])
    if not count_output.isdigit():
        return
    count = int(count_output)
    if count > DRIFT_WARNING_THRESHOLD:
        result.add_warning(
            f"自上次触及 logic 文档以来已累积 {count} 个提交"
            "（漂移风险：请核对 logic_readme.md 是否仍反映当前代码，"
            "medium/high 变更应使用带 Ref 行的语义提交）"
        )
    elif count > 0:
        result.add_info(f"自上次触及 logic 文档以来累积 {count} 个提交")


LEFTOVER_LIST_LIMIT = 10


def report_unpushed_commits(count, result: 'ValidationResult') -> None:
    """本地领先上游的提交数 → 非阻断告警（RULE-010 推送责任核对）。

    自动同步只是默认值不是保证：未跑过 ``recall init`` 的半接入项目会静默
    退化成"只提交不推送"，2026-09-02 消费项目因此出现远端停在中间提交、
    CI 18 项失败。此前 status/validate 都只报脏工作区、不报未推送。
    ``count`` 为 None（无上游/非仓库）时不告警：是否配置远端是用户的事。
    """
    if count is None or count <= 0:
        return
    result.add_warning(
        f"本地领先上游 {count} 个未推送提交"
        "（RULE-010：请 recall sync 或 git push；一批提交只推前几个会让远端停在中间提交上）"
    )


def report_untracked_leftovers(paths: List[str], result: 'ValidationResult') -> None:
    """未跟踪且未被 .gitignore 覆盖的文件 → 非阻断告警（RULE-020 收尾归零）。

    RULE-011 让未跟踪新文件默认不进自动保存提交，保住了远端，却让 AI 解题
    过程残留的探针脚本、临时测试与草稿在本地隐形累积。这里只把它们列出来
    交给代理/用户处置，绝不删除（UXI-003/UXI-006）。
    """
    cleaned = [p.strip() for p in paths if p and p.strip()]
    if not cleaned:
        return
    shown = cleaned[:LEFTOVER_LIST_LIMIT]
    listing = "、".join(shown)
    if len(cleaned) > len(shown):
        listing += f" 等（另 {len(cleaned) - len(shown)} 个）"
    result.add_warning(
        f"{len(cleaned)} 个未跟踪且未被 .gitignore 覆盖的文件: {listing}"
        "（RULE-020 收尾归零：交付物请 git add，非交付物请删除或加入 .gitignore；"
        "medium/high 变更在 logic_temp.md 台账登记去留）"
    )


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
    # RULE-018：已登记的 readme-only 子文档与根文档共用编号空间，一并检查
    child_readmes, missing_children = find_registered_child_readmes(
        readme_content, root
    )
    for scope in missing_children:
        result.add_error(
            f"范围登记表登记了二级文档但文件不存在: {scope}/logic_readme.md"
        )

    labeled_defs: List[Tuple[str, str, int]] = [
        ('logic_readme.md', rid, line)
        for rid, line in extract_rule_definitions(readme_path)
    ]
    for child in child_readmes:
        label = child.relative_to(root).as_posix()
        labeled_defs.extend(
            (label, rid, line) for rid, line in extract_rule_definitions(child)
        )

    unique_rules = set(rid for _, rid, _ in labeled_defs)
    result.add_info(
        f"找到 {len(unique_rules)} 条规则定义"
        + (f"（含 {len(child_readmes)} 份已登记子文档）" if child_readmes else "")
    )

    rule_counts: Dict[str, List[str]] = {}
    for label, rid, line_num in labeled_defs:
        rule_counts.setdefault(rid, []).append(f"{label}:{line_num}")

    for rid, locations in rule_counts.items():
        if len(locations) > 1:
            result.add_error(
                f"{rid} 被定义多次 ({', '.join(locations)})"
                "（RULE-018：编号空间全项目唯一，含子文档）"
            )

    # 1b. 功能意图与用户流程层（RULE-014，含代码锚点存在性；子文档同查）
    seen_int_ids: set = set()
    check_intent_layer(
        readme_content, unique_rules, result, root, seen_int_ids=seen_int_ids
    )
    for child in child_readmes:
        check_intent_layer(
            child.read_text(encoding='utf-8'),
            unique_rules,
            result,
            root,
            doc_label=child.relative_to(root).as_posix(),
            seen_int_ids=seen_int_ids,
        )

    # 2. 提取所有 CHG-ID：根账本（修宪议案 + 全项目索引）+ 每个领域账本（RULE-018）
    ledgers = change_ledgers(root)
    chg_records: List[Dict] = []
    root_change_text = change_path.read_text(encoding='utf-8') if change_path.exists() else ''
    for label, ledger_path in ledgers:
        found = extract_chg_ids(ledger_path)
        for chg in found:
            chg['ledger'] = label
        chg_records.extend(found)
        if label != 'logic_change.md':
            # 领域 CHG 必须在根账本公报（活跃议案索引）登记一行
            for chg in found:
                if chg['id'] not in root_change_text:
                    result.add_warning(
                        f"{chg['id']} 在 {label} 有正文但未登记进根 logic_change.md 活跃议案索引"
                        "（RULE-018：根账本是全项目公报）"
                    )
    domain_ledgers = len(ledgers) - (1 if change_path.exists() else 0)
    result.add_info(
        f"在 {len(ledgers)} 份议案账本中找到 {len(chg_records)} 个变更议案"
        + (f"（含 {domain_ledgers} 份领域账本）" if domain_ledgers else "")
    )

    # 检查 CHG 状态
    for chg in chg_records:
        if chg['status'] == '未标注':
            result.add_warning(f"{chg['id']}: {chg['title']} - 缺少状态标注")
        elif '进行中' in chg['status'] or '待' in chg['status']:
            result.add_info(f"{chg['id']}: {chg['title']} - 状态: {chg['status']}")

    # 2b. medium/high CHG 的需求拆解字段（RULE-014），每份账本都查
    for _label, ledger_path in ledgers:
        check_chg_analysis_fields(ledger_path, result)

    # 3. 检查决策记录
    version_records = find_version_records(version_dir)
    result.add_info(f"在 logic_version/records/ 中找到 {len(version_records)} 个决策记录")

    for record_path in version_records:
        record_text = record_path.read_text(encoding='utf-8')

        # 检查必填字段（快速模板 / 扩展 schema 任一套）
        missing = check_required_fields(record_path, record_text)
        if missing:
            result.add_error(f"{record_path.name} 缺少必填字段: {', '.join(missing)}")

        # 需求保全（RULE-014）：来自 CHG 的记录必须带需求拆解三字段
        check_record_requirement_fields(record_text, record_path.name, result)

        if UNFILLED_PLACEHOLDER_RE.search(record_text):
            result.add_warning(
                f"{record_path.name} 的 after_commit 占位符尚未回填"
                "（提交时带 Ref 行、或将记录与代码同提交，hook 会自动回填）"
            )

        # 检查 Git commit hash
        commit_hash = extract_commit_hash(record_path, record_text)
        if commit_hash:
            if not is_valid_git_commit(commit_hash, cwd=root):
                result.add_error(f"{record_path.name} 中的 commit hash '{commit_hash}' 无效")
        else:
            result.add_warning(f"{record_path.name} 未关联 Git commit")

    # 3b. VER 登记对账与撞号检测（规则行反链含全部已登记领域文档）
    check_ver_registrations(
        version_records,
        version_dir / "index.md",
        readme_content,
        result,
        [child.read_text(encoding='utf-8') for child in child_readmes],
    )

    # 3c. 漂移度量（RULE-015）：文档是代码理解的缓存，量化缓存的"新鲜度"
    check_doc_drift(root, result)

    # 3d. 推送责任核对（RULE-010）：本地不得长期领先远端
    report_unpushed_commits(unpushed_commit_count(root), result)

    # 4. 检查 Git 仓库状态（RULE-021：经 recall_common.run_git，失败不抛异常）
    ok_status, porcelain, status_err = run_git(['status', '--porcelain'], cwd=root, timeout=5)
    if ok_status:
        tracked_dirty, _ = classify_porcelain(porcelain)
        if tracked_dirty:
            result.add_warning(f"有 {len(tracked_dirty)} 个已跟踪文件的未提交变更")
        # 4b. 收尾归零（RULE-020）：未跟踪且未被忽略的文件单列告警
        untracked = git_output(
            ['ls-files', '--others', '--exclude-standard'], cwd=root, timeout=5
        )
        if untracked is not None:
            report_untracked_leftovers(untracked.splitlines(), result)
    elif 'not a git repository' in status_err.lower() or 'git' in status_err.lower():
        result.add_warning("无法检查 Git 状态（可能未初始化 Git）")
    else:
        result.add_warning("Git 不可用或未安装")

    return result

def main() -> int:
    """主入口。返回退出码，供 recall.py 直接使用。"""
    force_utf8_output()
    print("\n🔍 开始验证 Recall 系统一致性...\n")

    result = validate_recall()
    result.print_report()

    return 0 if result.is_valid() else 1

if __name__ == "__main__":
    sys.exit(main())
