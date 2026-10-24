"""Read-only reconciliation of preserved task copies awaiting permitted cleanup."""

from collections import Counter, deque
import hashlib
from pathlib import Path
import re

from recall_common import CHANGE_ID_PATTERN, _table_rows_under_heading
from task_context import meaningful, unfenced
from workspace_paths import field, project_path, linked, scan_entries

PENDING_ROOT = "logic_version/pending_cleanup"
HEADING = "待清理文件"
COLUMNS = {"task_id", "original_path", "path", "archive", "sha256", "reason", "recorded_at", "exit_condition"}


def issue(findings, code, path, message, task="", severity="error"):
    findings.append(dict(code=code, path=path, message=message, task=task, severity=severity))


def check_copy(root, row, active_ids, findings):
    task, rel = row.get("task_id", ""), row.get("path", "")
    try:
        if not COLUMNS.issubset(row) or not all(meaningful(row.get(key, "")) for key in COLUMNS):
            raise ValueError("待清理行须完整登记来源、归档、指纹、原因、登记日期和退出条件")
        if not re.fullmatch(CHANGE_ID_PATTERN, task):
            raise ValueError("task_id 必须是有效 CHG-ID")
        expected = f"{PENDING_ROOT}/{task}/logic_change.md.txt"
        in_place = rel == row["original_path"]
        if not in_place and rel != expected:
            raise ValueError(f"待清理路径须为原正文或 {expected}")
        original = project_path(root, row["original_path"])
        parts = original.relative_to(root).parts
        if len(parts) != 3 or parts[0] != "logic_changes" or parts[-1] != "logic_change.md":
            raise ValueError("仅接受已结束任务的独立正文，不能移入规则、业务数据或整个目录")
        parked = project_path(root, rel)
        archive = project_path(root, row["archive"])
        if archive.parent != root / "logic_version/records" or not re.fullmatch(
                r"logic_version-\d{8}-\d{3}-.+\.md", archive.name):
            raise ValueError("archive 须指向正式 records 决策文件")
        text = archive.read_text(encoding="utf-8")
        if field(text, "immutable") != "true" or field(text, "status") not in {"effective", "rejected", "cancelled", "rolled-back"}:
            raise ValueError("归档尚未定稿，不能退出活跃队列")
        if task not in {field(text, "change_id"), field(text, "proposal_id")}:
            raise ValueError("归档没有回链该任务")
        if (not in_place and original.exists()) or task in active_ids:
            raise ValueError("原正文或同 ID 活跃任务仍在；复制不算移动完成")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", row["sha256"]):
            raise ValueError("sha256 必须为登记时原文件的完整指纹")
        if not parked.is_file():
            raise ValueError("登记的待清理副本不存在；核实实际处置后更新清单")
        if parked.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("任务副本超过2MiB核验边界，需人工复核，未宣称保全通过")
        data = parked.read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"].lower():
            raise ValueError("待清理副本与移动前指纹不符")
        identities = re.findall(rf"^##\s+({CHANGE_ID_PATTERN})(?=\s|:|：|$)", data.decode("utf-8-sig"), re.M)
        if identities != [task]:
            raise ValueError("副本任务身份不符")
    except (ValueError, OSError, UnicodeError) as error:
        issue(findings, "invalid-pending-cleanup", rel, str(error), task)
        return
    message = "已归档正文原位待清理，已退出活跃队列；执行策略允许后可删除" if in_place else "已保全移动并退出活跃队列；仍待实际删除，移动不等于清理完成"
    issue(findings, "pending-cleanup", rel, message, task, "warning")


def pending_rows(root):
    index = project_path(root, "logic_version/index.md")
    return _table_rows_under_heading(unfenced(index.read_text(encoding="utf-8")), HEADING) if index.is_file() else []


def retired_task_paths(root):
    """Suppress only uniquely registered, unchanged, archived in-place task bodies."""
    root = Path(root).resolve()
    try:
        rows = pending_rows(root)
        counts = {key: Counter(row.get(key, "") for row in rows) for key in ("task_id", "path", "original_path")}
        retired = set()
        for row in rows:
            if row.get("path") != row.get("original_path") or any(counts[key][row.get(key, "")] != 1 for key in counts):
                continue
            findings = []
            check_copy(root, row, (), findings)
            if findings and all(f["severity"] != "error" for f in findings):
                retired.add(row["original_path"])
        return retired
    except (ValueError, OSError):
        return set()


def scan_pending(root, base, budget, findings):
    queue, files = deque([base]), set()
    while queue and budget > 0:
        folder = queue.popleft()
        entries, truncated = scan_entries(folder, budget)
        budget -= len(entries)
        if truncated:
            issue(findings, "incomplete-pending-cleanup-scan", folder.relative_to(root).as_posix(), "待清理扫描预算截断")
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            if linked(path):
                issue(findings, "invalid-pending-cleanup", rel, "待清理区不能通过链接指向其他位置")
            elif entry.is_dir(follow_symlinks=False):
                queue.append(path)
            else:
                files.add(rel)
    if queue:
        issue(findings, "incomplete-pending-cleanup-scan", PENDING_ROOT, "待清理扫描未完成")
    return files


def check_pending_cleanup(root, active_ids=(), max_entries=2000):
    root, findings = Path(root).resolve(), []
    rows = pending_rows(root)
    for row in rows:
        check_copy(root, row, active_ids, findings)
    for key in ("path", "task_id", "original_path"):
        for value, count in Counter(row.get(key, "") for row in rows).items():
            if count > 1:
                issue(findings, "duplicate-pending-cleanup", value, f"待清理清单重复 {key}")
    base_exists = False
    try:
        base = project_path(root, PENDING_ROOT)
        base_exists = base.exists()
        if base_exists and not base.is_dir():
            raise ValueError("待清理根必须是目录")
        actual = scan_pending(root, base, max_entries, findings) if base_exists else set()
        for rel in sorted(actual - {row.get("path") for row in rows}):
            issue(findings, "unlisted-pending-cleanup", rel, "待清理区有未登记文件，不能静默隐藏")
        if base_exists and not actual and not rows:
            issue(findings, "empty-pending-cleanup", PENDING_ROOT, "待清理区只剩目录，允许时清除空目录", severity="warning")
    except (ValueError, OSError) as error:
        issue(findings, "invalid-pending-cleanup", PENDING_ROOT, str(error))
    return {"items": rows, "findings": findings, "count": len(rows),
            "cleanup_complete": not rows and not findings and not base_exists}
