"""Reconcile task artifact ledgers with real files, including Git-ignored files."""

from collections import Counter, deque
from pathlib import Path
import re

from recall_common import CHANGE_ID_PATTERN, _table_rows_under_heading, change_ledgers
from task_context import meaningful, read_changes, unfenced
from workspace_paths import contract, field, linked, project_path, scan_entries, split_paths
from pending_cleanup import check_pending_cleanup


def artifact_rows(text):
    return _table_rows_under_heading(unfenced(text), "工作区产物台账")


def has_artifact_table(text):
    section = re.search(r"^#{2,6} 工作区产物台账\s*\n(.*?)(?=^#{1,6} |\Z)", unfenced(text), re.M | re.S)
    if not section:
        return False
    header = next((line for line in section.group(1).splitlines() if line.strip().startswith("|")), "")
    columns = [c.strip() for c in header.strip().strip("|").split("|")]
    return len(columns) == len(set(columns)) and set([
        "path", "artifact_kind", "disposition", "reason", "cleaned_at"]).issubset(columns)


def task_block(text, task):
    """Legacy ledgers can contain several CHGs; each owns only its own table."""
    headings = list(re.finditer(rf"^##\s+({CHANGE_ID_PATTERN})(?=\s|:|：|$)[^\n]*", unfenced(text), re.M | re.I))
    lines = unfenced(text)
    for index, heading in enumerate(headings):
        if heading.group(1).upper() == task:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(lines)
            return lines[heading.end():end]
    return ""


def add(findings, code, path, message, severity="error", task=""):
    findings.append(dict(code=code, path=path, message=message, severity=severity, task=task))


def scan_temp(root, folder, budget):
    queue, paths, issues = deque([folder]), [], []
    while queue and budget > 0:
        current = queue.popleft()
        entries, truncated = scan_entries(current, budget)
        budget -= len(entries)
        if truncated:
            issues.append(current.relative_to(root).as_posix())
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            paths.append(rel)
            if linked(path):
                issues.append("link:" + rel)
            elif entry.is_dir(follow_symlinks=False):
                queue.append(path)
    if queue:
        issues.extend(p.relative_to(root).as_posix() for p in queue)
    return paths, issues, budget


def check_rows(root, rows, item, findings, closing):
    known, unresolved = [], []
    for row in rows:
        rel = row.get("path", "").strip().strip("`").rstrip("/")
        try:
            path = project_path(root, rel)
        except (ValueError, OSError) as error:
            add(findings, "invalid-artifact-path", rel, str(error), task=item["id"])
            continue
        known.append(rel)
        disposition = row.get("disposition", "")
        kind = row.get("artifact_kind", "")
        exists = path.exists()
        if disposition == "keep":
            if kind not in {"deliverable", "runtime-data", "evidence"}:
                add(findings, "non-deliverable-kept", rel, "非交付物必须删除；不能用keep/gitignore替代清理", task=item["id"])
            extended = "retention_basis" in row or "exit_condition" in row
            if extended or kind in {"runtime-data", "evidence"}:
                for key in ("retention_basis", "exit_condition"):
                    if not meaningful(row.get(key, "")):
                        add(findings, "missing-" + key.replace("_", "-"), rel,
                            "保留产物须说明必要依据与退出/复核条件；不能只按数量判断",
                            "error" if extended else "warning", item["id"])
            if not exists:
                add(findings, "missing-deliverable", rel, "登记保留的交付物不存在", task=item["id"])
        elif disposition == "delete":
            if exists:
                unresolved.append(rel)
                severity = "error" if closing or row.get("cleaned_at", "-") not in {"", "-", "none"} else "info"
                add(findings, "delete-still-exists", rel, "待删除产物仍存在（包含空目录）", severity, item["id"])
        else:
            unresolved.append(rel)
            add(findings, "unresolved-disposition", rel, "处置须为keep或delete；gitignore不是清理",
                "error" if closing or disposition == "gitignore" else "warning", item["id"])
    for path, count in Counter(known).items():
        if count > 1:
            add(findings, "duplicate-artifact", path, "产物在台账中重复登记", task=item["id"])
    return known, unresolved


def check_task(root, label, text, item, cfg, findings, closing, budget):
    new = label.startswith("logic_changes/")
    ledger_text = text
    if not new and item.get("temp_path") not in {None, "", "none"}:
        try:
            ledger = project_path(root, item["temp_path"])
            ledger_text = ledger.read_text(encoding="utf-8")
        except (ValueError, OSError) as error:
            add(findings, "missing-artifact-ledger", label, str(error), task=item["id"])
    rows = artifact_rows(ledger_text)
    if new and item.get("recall_route") in {"medium", "high"}:
        if not has_artifact_table(text):
            add(findings, "missing-artifact-ledger", label, "任务正文缺少产物台账表头（无产物也保留空表）", task=item["id"])
    known, unresolved = check_rows(root, rows, item, findings, closing)
    folders = split_paths(item.get("task_temp_dirs", ""))
    for rel in folders:
        try:
            folder = project_path(root, rel)
            relative = folder.relative_to(project_path(root, cfg["scratch_root"]))
            if len(relative.parts) != 1 or not relative.name.startswith("临时-") or len(relative.name) <= 3:
                raise ValueError("临时代码目录须为 scratch_root/临时-具体功能")
            if folder.exists() and not folder.is_dir():
                raise ValueError("临时目录路径实际是文件")
            if folder.is_dir():
                actual, boundaries, budget = scan_temp(root, folder, budget)
                for path in actual:
                    if not any(path == k or path.startswith(k + "/") for k in known):
                        add(findings, "unlisted-temp-artifact", path, "实际临时产物未登记", task=item["id"])
                for path in boundaries:
                    add(findings, "incomplete-temp-scan", path, "预算或链接边界：不能宣称核对完成", task=item["id"])
                if closing:
                    add(findings, "temp-folder-still-exists", rel, "关案前删除整个临时目录；交付物先晋升到正式路径", task=item["id"])
        except (ValueError, OSError) as error:
            add(findings, "invalid-temp-directory", rel, str(error), task=item["id"])
    if field(ledger_text, "ledger_cleared") == "yes" and unresolved:
        add(findings, "false-cleanup-claim", label, "台账称已清零，但实际产物/处置尚未清零", task=item["id"])
    return folders, budget


def result_view(findings):
    return {"findings": findings, "ok": not any(f["severity"] == "error" for f in findings)}


def selected_round(root, records, task, round_id):
    """A finished round must dispose of its own rows, not close the whole task."""
    findings, rows = [], []
    matches = [(text, item) for _, text, item in records if item["id"] == task]
    if len(matches) != 1:
        add(findings, "round-task-not-unique", task, "轮次核对需要唯一存在的活跃任务", task=task)
    else:
        text, item = matches[0]
        text = task_block(text, task)
        if item.get("temp_path") not in {None, "", "none"} and not item["path"].startswith("logic_changes/"):
            text = project_path(root, item["temp_path"]).read_text(encoding="utf-8")
        rows = [row for row in artifact_rows(text) if row.get("round", "").lstrip("0") == str(round_id).lstrip("0")]
        if not rows:
            add(findings, "round-not-recorded", str(round_id), "没有该轮台账行；不能据此宣称本轮已清理", task=task)
        check_rows(root, rows, item, findings, True)
    return dict(result_view(findings), round=str(round_id), rows_checked=len(rows))


def check_workspace(root, *, closing=None, task=None, round_id=None, max_entries=2000):
    root = Path(root).resolve()
    if closing and task and closing.upper() != task.upper():
        raise ValueError("--task 与 --closing 必须指向同一任务")
    selected = (task or closing or "").upper() or None
    if round_id is not None and (not selected or closing or not str(round_id).isdigit() or int(round_id) < 1):
        raise ValueError("--round 须为正整数并搭配 --task；整案关闭不按轮次过滤")
    cfg = contract(root)
    findings, declared, ids, records = [], {}, [], []
    budget = max_entries
    for label, path in change_ledgers(root):
        text = path.read_text(encoding="utf-8")
        items = read_changes(text, label)
        if label.startswith("logic_changes/") and len(items) != 1:
            add(findings, "task-body-count", label, "每个任务文件必须只有一个活跃CHG")
        for item in items:
            records.append((label, text, item))
    # Check the requested task first; an unrelated large task cannot consume its scan budget.
    records.sort(key=lambda row: row[2]["id"] != selected)
    for label, text, item in records:
        ids.append(item["id"])
        is_closing = (closing and selected == item["id"]) or item.get("status") == "promoting"
        folders, budget = check_task(root, label, task_block(text, item["id"]), item, cfg, findings, is_closing, budget)
        for folder in folders:
            declared.setdefault(folder, []).append(item["id"])
    for folder, owners in declared.items():
        if len(owners) > 1:
            for owner in set(owners):
                add(findings, "shared-temp-directory", folder, "多个任务共享临时目录，无法唯一收尾", task=owner)
    if selected and ids.count(selected) != 1:
        add(findings, "closing-task-not-unique" if closing else "selected-task-not-unique", selected,
            "核对需要唯一存在的活跃任务", task=selected)
    duplicate = root / root.parent.name / root.name
    if duplicate.exists():
        add(findings, "suspected-duplicate-project-root", duplicate.relative_to(root).as_posix(),
            "存在重复根路径；核查来源/引用，不能凭名称自动删除", "warning")
    scratch = project_path(root, cfg["scratch_root"])
    if scratch.is_dir():
        entries, truncated = scan_entries(scratch, max_entries)
        if truncated:
            add(findings, "incomplete-scratch-scan", cfg["scratch_root"], "临时根目录预算截断")
        for entry in entries:
            rel = (scratch / entry.name).relative_to(root).as_posix()
            if rel not in declared:
                add(findings, "orphan-temp-artifact", rel, "临时根中没有活跃任务归属；核实旧任务/用户文件后处置", "warning")
    pending = check_pending_cleanup(root, ids, max_entries)
    findings.extend(pending["findings"])
    labels = {label for label, _, item in records if item["id"] == selected}
    task_findings = [f for f in findings if f["task"] == selected or (not f["task"] and f["path"] in labels)] if selected else []
    task_result = dict(result_view(task_findings), task=selected) if selected else None
    round_result = selected_round(root, records, selected, round_id) if round_id is not None else None
    if round_result and any(f["code"] in {"shared-temp-directory", "task-body-count", "selected-task-not-unique"}
                            for f in task_findings):
        round_result["ok"] = False
    global_result = result_view(findings)
    return {"project_root": root.as_posix(), "closing": closing, **global_result,
            "task_result": task_result, "round_result": round_result,
            "pending_cleanup": pending,
            "global_result": {"ok": global_result["ok"],
                              "counts": dict(Counter(f["severity"] for f in findings))},
            "other_findings": [f for f in findings if f not in task_findings] if selected else [],
            "selection_ok": (round_result or task_result or global_result)["ok"],
            "scope": "任务声明路径与临时根；不依赖Git忽略规则，不自动删除，不扫描全量数据"}
