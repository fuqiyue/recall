"""Reconcile task artifact ledgers with real files, including Git-ignored files."""

from collections import Counter, deque
from pathlib import Path
import re

from recall_common import _table_rows_under_heading, change_ledgers
from task_context import read_changes, unfenced
from workspace_paths import contract, field, linked, project_path, scan_entries, split_paths


def artifact_rows(text):
    return _table_rows_under_heading(unfenced(text), "工作区产物台账")


def has_artifact_table(text):
    section = re.search(r"^#{2,6} 工作区产物台账\s*\n(.*?)(?=^#{1,6} |\Z)", unfenced(text), re.M | re.S)
    if not section:
        return False
    header = next((line for line in section.group(1).splitlines() if line.strip().startswith("|")), "")
    return [c.strip() for c in header.strip().strip("|").split("|")] == [
        "path", "artifact_kind", "disposition", "reason", "cleaned_at"]


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
            if kind not in {"deliverable", "evidence"}:
                add(findings, "non-deliverable-kept", rel, "非交付物必须删除；不能用keep/gitignore替代清理", task=item["id"])
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


def check_workspace(root, *, closing=None, max_entries=2000):
    root = Path(root).resolve()
    cfg = contract(root)
    findings, declared, ids = [], {}, []
    budget = max_entries
    for label, path in change_ledgers(root):
        text = path.read_text(encoding="utf-8")
        items = read_changes(text, label)
        if label.startswith("logic_changes/") and len(items) != 1:
            add(findings, "task-body-count", label, "每个任务文件必须只有一个活跃CHG")
        for item in items:
            ids.append(item["id"])
            is_closing = closing == item["id"] or item.get("status") == "promoting"
            folders, budget = check_task(root, label, text, item, cfg, findings, is_closing, budget)
            for folder in folders:
                if folder in declared:
                    add(findings, "shared-temp-directory", folder, "多个任务共享临时目录，无法唯一收尾", task=item["id"])
                declared[folder] = item["id"]
    if closing and ids.count(closing) != 1:
        add(findings, "closing-task-not-unique", closing, "关闭核对需要唯一存在的活跃任务")
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
    return {"project_root": root.as_posix(), "closing": closing, "findings": findings,
            "ok": not any(f["severity"] == "error" for f in findings),
            "scope": "任务声明路径与临时根；不依赖Git忽略规则，不自动删除，不扫描全量数据"}
