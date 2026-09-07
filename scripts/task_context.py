"""Read-only task context and explicitly requested root bulletin regeneration."""

import argparse
import json
import re
from collections import Counter

from recall_common import CHANGE_ID_PATTERN, change_ledgers, find_project_root


EMPTY = {"", "none", "unknown", "not-specified", "n/a", "-"}
GROUPS = ("收尾", "进行中", "可做候选", "待决策", "阻塞", "待核对", "想法")
HEADER = "| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |"
SEPARATOR = "|---|---|---|---|---|---|---|---|"


def meaningful(value):
    value = value.strip().strip("`")
    return value.lower() not in EMPTY and not (value.startswith("<") and value.endswith(">"))


def unfenced(text):
    """Keep code examples out of the live ledger model."""
    result, fence = [], None
    for line in text.splitlines():
        mark = re.match(r"^\s*(`{3,}|~{3,})", line)
        if mark:
            token = mark.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append("")
        else:
            result.append(line if fence is None else "")
    return "\n".join(result)


def read_changes(text, path):
    clean = unfenced(text)
    headings = list(re.finditer(rf"^##\s+({CHANGE_ID_PATTERN})(?=\s|:|：|$)[^\n]*", clean, re.M | re.I))
    result = []
    for n, heading in enumerate(headings):
        end = headings[n + 1].start() if n + 1 < len(headings) else len(clean)
        block = clean[heading.end():end]
        # A later unrelated level-two section is not part of this change.
        block = re.split(r"^##\s", block, maxsplit=1, flags=re.M)[0]
        fields = {}
        for key, value in re.findall(r"^\s*- ([\w-]+):\s*([^\n]*)", block, re.M):
            fields.setdefault(key, value.strip().strip("`"))
        change_id = heading.group(1).upper()
        title = heading.group(0)[heading.group(0).upper().index(change_id) + len(change_id):].lstrip(" :：")
        result.append(dict(fields, id=change_id, title=title, path=path, kind="change"))
    return result


def read_intake(text, path):
    """Optional table in the existing ledger, never another task database."""
    section = re.search(r"^## 待办\s*\n(.*?)(?=^## |\Z)", unfenced(text), re.M | re.S)
    if not section:
        return []
    columns, items = [], []
    for line in section.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "task_id" in cells and "stage" in cells:
            columns = cells
        elif columns and len(cells) == len(columns) and not all(re.fullmatch(r"[-: ]+", c) for c in cells):
            fields = dict(zip(columns, cells))
            items.append(dict(fields, id=fields["task_id"], title=fields.get("context", ""), path=path, kind="intake"))
    return items


def classify(item, ids):
    if item["kind"] == "intake":
        stage = item.get("stage")
        if stage == "idea":
            return "想法", "尚未承诺实施"
        if stage == "planned" and meaningful(item.get("source_ref", "")):
            return "可做候选", "已记录决定要做；开始前结合当前请求核对范围与授权"
        return "待核对", "待办阶段或决定来源未明确"
    status = item.get("status", "")
    if status == "blocked" or meaningful(item.get("blocked_by", "")):
        return "阻塞", item.get("blocked_reason") or item.get("blocked_by") or "阻塞原因尚未记录"
    if meaningful(item.get("conflicts_with", "")):
        return "待核对", "有冲突关系，须核对已记录的处理结果"
    dependencies = item.get("depends_on", "")
    if meaningful(dependencies):
        refs = re.findall(CHANGE_ID_PATTERN, dependencies, re.I)
        active = [ref for ref in refs if ref.upper() in ids]
        if active:
            return "阻塞", "依赖仍在活跃账本：" + ", ".join(active)
        return "待核对", "依赖需结合 VER/现行规则核实，缺席不等于完成"
    if status in {"draft", "awaiting-decision"}:
        return "待决策", "方案尚未进入实施"
    if item.get("decision_state") == "pending":
        return "待决策", "决定尚未确认"
    revision = item.get("confirmed_proposal_revision")
    if meaningful(revision or "") and revision != item.get("proposal_revision"):
        return "待核对", "确认版本与当前方案版本不一致"
    if not all(meaningful(item.get(k, "")) for k in ("decision_confirmed_by", "decision_confirmed_at")):
        return "待核对", "缺少已记录的决定来源"
    if status == "promoting":
        return "收尾", "已进入晋升，继续核对剩余交付项"
    if status in {"implementing", "verifying"}:
        return "进行中", "继续本项实施或验证"
    return "待核对", "未知或缺失的状态"


def snapshot(root):
    items = []
    for label, path in change_ledgers(root):
        text = path.read_text(encoding="utf-8")
        items.extend(read_changes(text, label))
        items.extend(read_intake(text, label))
    counts = Counter(item["id"] for item in items)
    warnings = [f"重复 ID：{key}" for key, count in counts.items() if count > 1]
    for item in items:
        group, reason = classify(item, counts)
        if counts[item["id"]] > 1:
            group, reason = "待核对", "重复 ID，无法唯一定位"
        item.update(group=group, reason=reason)
        if group == "阻塞":
            missing = [key for key in ("blocked_reason", "next_action", "owner", "review_due") if not meaningful(item.get(key, ""))]
            if missing:
                warnings.append(f"{item['id']} 阻塞上下文待补：" + ", ".join(missing))
    items.sort(key=lambda item: (GROUPS.index(item["group"]), item["id"], item["path"]))
    return {"items": items, "counts": {group: sum(i["group"] == group for i in items) for group in GROUPS}, "warnings": warnings}


def render(data):
    print("下一步行动（账本快照；候选不是自动授权，模型结合需求与证据判断）")
    for group in GROUPS:
        print(f"\n{group}：{data['counts'][group]}")
        for item in data["items"]:
            if item["group"] != group:
                continue
            print(f"  {item['id']} {item['title']} [{item['path']}]")
            print(f"    依据：{item['reason']}")
            action = item.get('next_action', '')
            print(f"    下一步：{action if meaningful(action) else '阅读任务正文，补充具体剩余动作'}")
            if group == "阻塞":
                print(f"    执行者：{item.get('owner') or '未记录'}；复查：{item.get('review_due') or '未记录'}")
    for warning in data["warnings"]:
        print("提示：" + warning)


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ")


def bulletin(items):
    lines = [HEADER, SEPARATOR]
    for item in sorted((i for i in items if i["kind"] == "change"), key=lambda i: i["id"]):
        values = [item["id"], item.get("status", "unknown"), item.get("scope", "unknown"),
                  item.get("owner", "unknown"), item["title"], item.get("blocked_by", "none"),
                  f"[{item['id']}]({item['path']}#{item['id'].lower()})",
                  item.get("last_updated") or item.get("last_status_change") or item.get("decision_confirmed_at", "unknown")]
        lines.append("| " + " | ".join(map(cell, values)) + " |")
    return "\n".join(lines)


def index_update(root, data):
    """Prepare a bounded update; never replace free-form discussion sections."""
    if any(w.startswith("重复 ID") for w in data["warnings"]):
        raise ValueError("重复 ID；请先消除歧义，公报未写入")
    path = root / "logic_change.md"
    text = path.read_text(encoding="utf-8")
    section = re.search(r"^## 活跃议案索引[^\n]*\n(?P<body>.*?)(?=^## |^---\s*$|\Z)", text, re.M | re.S)
    if not section:
        raise ValueError("缺少根公报节；请先使用账本模板建立节与表头")
    table = re.search(r"^\|[^\n]*\n(?:\|[^\n]*(?:\n|$))+", section.group("body"), re.M)
    if not table or [c.strip() for c in table.group().splitlines()[0].split("|")] != [c.strip() for c in HEADER.split("|")]:
        raise ValueError("公报表头不明确；保留原文，未写入")
    start = section.start("body") + table.start()
    end = section.start("body") + table.end()
    updated = text[:start] + bulletin(data["items"]) + "\n" + text[end:]
    local_count = sum(i["kind"] == "change" and i["path"] == "logic_change.md" for i in data["items"])
    # Only the root document-control field; never alter CHG metadata.
    prefix, rest = updated.split("## 议案规则", 1)
    prefix = re.sub(r"^- active_changes:.*$", f"- active_changes: {local_count}", prefix, flags=re.M)
    return path, text, prefix + "## 议案规则" + rest


def main(args=None, command="next"):
    parser = argparse.ArgumentParser(description="任务上下文与派生公报")
    parser.add_argument("--json", action="store_true")
    if command == "index":
        parser.add_argument("--write", action="store_true", help="显式更新根公报表与根正文计数")
    options = parser.parse_args(args)
    root = find_project_root()
    data = snapshot(root)
    if command == "next":
        print(json.dumps(data, ensure_ascii=False, indent=2)) if options.json else render(data)
        return 0
    path, original, updated = index_update(root, data)
    changed = original != updated
    if options.write and changed:
        if path.read_text(encoding="utf-8") != original:
            raise ValueError("账本已变化，请重试；未写入")
        path.write_text(updated, encoding="utf-8", newline="\n")
    result = {"consistent": not changed, "written": bool(options.write and changed), "bulletin": bulletin(data["items"])}
    print(json.dumps(result, ensure_ascii=False, indent=2) if options.json else
          ("公报已更新" if result["written"] else "公报一致" if not changed else "公报待更新（recall index --write）") + "\n" + result["bulletin"])
    return 0 if not changed or options.write else 1


def check_consistency(root, result):
    """Advisory integration for validate; optional legacy sections stay usable."""
    data = snapshot(root)
    for warning in data["warnings"]:
        result.add_warning(warning)
    if not (root / "logic_change.md").exists():
        return
    try:
        _, original, updated = index_update(root, data)
        if original != updated:
            result.add_warning("根公报与正文不一致；recall index 查看，--write 显式更新")
    except ValueError as error:
        result.add_warning("公报检查：" + str(error))
