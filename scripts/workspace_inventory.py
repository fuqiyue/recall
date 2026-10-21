"""Bounded filename inventory. Generated maps describe files, never business intent."""

from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from recall_common import registered_domains
from workspace_paths import contract, linked, project_path, repeated_root, scan_entries

SKIP = {".git", ".agents", ".codex", ".claude", ".venv", "venv", "node_modules",
        "__pycache__", ".pytest_cache", "logic_domains", "logic_changes", "logic_version"}
SOURCE = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".sh", ".ps1", ".bat",
          ".go", ".rs", ".java", ".c", ".cpp", ".sql"}
DATA_NAMES = {"assets", "data", "datasets", "资产库", "课件库", "下载记录"}
MARKER = "<!-- recall-generated-file-map -->"


def covering_domains(relative, domains):
    found = []
    for scope, owned_paths in domains:
        for owned in owned_paths:
            value = owned.replace("\\", "/").rstrip("/")
            if relative == value or relative.startswith(value + "/"):
                found.append(scope)
                break
    return sorted(found)


def describe(path, is_dir, data):
    if data:
        return "数据目录（仅列上层）" if is_dir else "数据文件"
    if is_dir:
        return "目录；功能待依据规则核实"
    if path.suffix.lower() in SOURCE:
        return "代码/界面文件"
    if path.suffix.lower() in {".md", ".txt", ".rst"}:
        return "说明/记录文件"
    return "文件"


def inventory(root, targets=(), *, data_roots=(), max_depth=3, max_entries=1000):
    root = Path(root).resolve()
    cfg = contract(root)
    data = {p.replace("\\", "/").rstrip("/") for p in [*cfg["data_roots"], *data_roots]}
    for item in data:
        project_path(root, item)
    domains = registered_domains(root)
    ownership = [(d.scope_path, d.owned_paths()) for d in domains]
    queue = deque()
    for target in targets or ["."]:
        path = project_path(root, target, allow_root=True)
        if not path.is_dir():
            raise ValueError(f"目录不存在：{target}")
        queue.append((path, 0))
    rows, notices, seen = [], [], set()
    consumed = 0
    while queue and consumed < max_entries:
        directory, depth = queue.popleft()
        if directory in seen:
            continue
        seen.add(directory)
        entries, truncated = scan_entries(directory, max_entries - consumed)
        consumed += len(entries)
        if truncated:
            notices.append(f"条目预算截断：{directory.relative_to(root).as_posix()}")
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            if entry.name in SKIP:
                continue
            is_dir = entry.is_dir(follow_symlinks=False)
            is_link = linked(path)
            declared_data = any(rel == p or rel.startswith(p + "/") for p in data)
            guessed_data = any(p in DATA_NAMES for p in Path(rel).parts)
            is_data = declared_data or guessed_data
            duplicate = repeated_root(root, Path(rel).parts)
            rows.append({"path": rel, "kind": "link" if is_link else "directory" if is_dir else "file",
                         "description": "链接（未遍历）" if is_link else describe(path, is_dir, is_data),
                         "domains": covering_domains(rel, ownership),
                         "classification_source": "declared" if declared_data else "filename-heuristic",
                         "suspected_duplicate_root": duplicate})
            if is_link:
                notices.append(f"链接未遍历：{rel}")
            elif duplicate:
                notices.append(f"疑似重复项目根，未深入：{rel}")
            elif is_dir:
                # A data directory's immediate children are enough; no asset file flood.
                parent_data = any(str(directory.relative_to(root)).replace("\\", "/") == p
                                  or str(directory.relative_to(root)).replace("\\", "/").startswith(p + "/")
                                  for p in data) or any(p in DATA_NAMES for p in directory.relative_to(root).parts)
                if parent_data or depth >= max_depth:
                    notices.append(f"深度/数据边界，未深入：{rel}")
                elif entry.name.startswith(".") and entry.name != cfg["scratch_root"].split("/")[0]:
                    notices.append(f"隐藏目录未深入：{rel}")
                else:
                    queue.append((path, depth + 1))
    if queue:
        notices.append(f"预算用尽，尚有 {len(queue)} 个目录未遍历")
    return {"project_root": root.as_posix(), "generated_at": datetime.now(timezone.utc).isoformat(),
            "targets": list(targets or ["."]), "max_depth": max_depth, "max_entries": max_entries,
            "entries_inspected": consumed, "entries": rows, "notices": notices,
            "complete": not notices, "domains": [d.scope_path for d in domains]}


def markdown(data, domain=None):
    rows = [r for r in data["entries"] if domain is None or domain in r["domains"]]
    lines = [MARKER, "# 文件地图", "", f"扫描时间：{data['generated_at']}",
             f"范围：{', '.join(data['targets'])}；深度 {data['max_depth']}；预算 {data['max_entries']}。",
             "这是可重建的文件名索引，不是规则或已确认功能说明；未映射项由领域 owned_paths 补充归属。",
             "", "| 路径 | 简要说明 | 领域 |", "|---|---|---|"]
    for row in rows:
        values = [row["path"], row["description"], ", ".join(row["domains"]) or "待登记"]
        lines.append("| " + " | ".join(v.replace("|", "&#124;").replace("\n", " ") for v in values) + " |")
    lines += ["", "扫描边界："] + [f"- {n}" for n in data["notices"]]
    if not data["notices"]:
        lines.append("- 已遍历所选范围（排除工具配置、依赖及 Recall 自身文档目录）。")
    return "\n".join(lines) + "\n"


def write_maps(root, data):
    """Preflight all outputs; never overwrite hand-authored prose or create a domain."""
    root = Path(root).resolve()
    outputs = [("logic_domains/file_map.md", markdown(data))]
    outputs += [(scope + "/file_map.md", markdown(data, scope)) for scope in data["domains"]]
    prepared = [(project_path(root, name), text) for name, text in outputs]
    for path, _ in prepared:
        if path.exists() and not path.read_text(encoding="utf-8").startswith(MARKER):
            raise ValueError(f"保留手写文件，未写入：{path}")
    for path, text in prepared:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return [p.relative_to(root).as_posix() for p, _ in prepared]
