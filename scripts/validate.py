#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recall 一致性验证工具
检查 logic_readme.md, logic_change.md 和 logic_version/ 之间的一致性
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_common import (  # noqa: E402  RULE-021
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
    r'^\s*-\s*after_commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
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
    """范围登记表中 readme-only 行对应的子文档路径（RULE-018）。

    返回 (存在的子文档, 登记了但文件缺失的 scope 列表)。子文档与根文档
    共用同一 RULE/INT 编号空间，必须纳入同一套一致性检查，否则拆分后
    的模块进入无检查区。
    """
    paths: List[Path] = []
    missing: List[str] = []
    for line in readme_content.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if len(cells) >= 5 and cells[2] == 'in-system' and cells[4] == 'readme-only':
            scope = cells[1].strip().strip('/').replace('\\', '/')
            candidate = root / scope / 'logic_readme.md'
            if candidate.exists():
                paths.append(candidate)
            else:
                missing.append(scope)
    return paths, missing


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
                    # 只检查路径形态的锚点；符号/路由锚点无法静态验证
                    if '/' not in anchor and '.' not in anchor:
                        continue
                    if not (root / anchor).exists():
                        result.add_warning(
                            f"{intent_id}: 代码锚点 {anchor} 不存在"
                            "（文件改名/移动后请更新功能意图登记表）"
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
        index_vers = set(VER_ROW_RE.findall(index_path.read_text(encoding='utf-8')))
    readme_vers = set(VER_ROW_RE.findall(readme_content))

    for ver_id in sorted(file_vers):
        if index_path.exists() and ver_id not in index_vers:
            result.add_warning(f"{ver_id} 未登记到 logic_version/index.md")
        inactive = record_status.get(ver_id) in INACTIVE_RECORD_STATUSES
        if ver_id not in readme_vers and not inactive:
            result.add_warning(f"{ver_id} 未登记到 logic_readme.md 的有效决策索引")
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

    # git 未安装、不在 PATH 或超时时 run_git 返回 ok=False，不抛异常（RULE-021）
    ok, out, _ = run_git(['cat-file', '-t', commit_hash], timeout=5)
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
            f"范围登记表登记了 readme-only 子文档但文件不存在: {scope}/logic_readme.md"
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

        # 需求保全（RULE-014）：来自 CHG 的记录必须带需求拆解三字段
        check_record_requirement_fields(record_text, record_path.name, result)

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
