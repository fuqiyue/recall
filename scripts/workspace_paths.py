"""Project-relative work paths; no filesystem mutations."""

import os
import re
import stat
from pathlib import Path, PureWindowsPath


def field(text, name, default=""):
    match = re.search(rf"^- {re.escape(name)}:\s*([^\n]*)", text, re.M)
    return match.group(1).strip().strip("`") if match else default


def split_paths(value):
    return [p.strip().strip("`").replace("\\", "/").rstrip("/")
            for p in re.split(r"[,;，；]", value) if p.strip().lower() not in {"", "none", "-"}]


def linked(path):
    if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
        return True
    try:
        # Python 3.11 has no Path.is_junction; Windows reparse points still expose attributes.
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except FileNotFoundError:
        return False


def repeated_root(root, parts):
    """Detect a root suffix accidentally appended to the project root."""
    tail = tuple(p.casefold() for p in root.parts[-2:])
    values = tuple(p.casefold() for p in parts)
    return len(tail) == 2 and any(values[i:i + 2] == tail for i in range(len(values) - 1))


def project_path(root, value, *, allow_root=False):
    """Resolve a stored relative path, rejecting escapes, drive fragments and links."""
    root = Path(root).resolve()
    raw = str(value).strip().strip("`").replace("\\", "/")
    win = PureWindowsPath(raw)
    parts = Path(raw).parts
    if not raw or win.drive or win.root or Path(raw).is_absolute():
        raise ValueError(f"需要项目相对路径：{value}")
    if ".." in parts or any(":" in p for p in parts) or repeated_root(root, parts):
        raise ValueError(f"越界或重复拼接项目根：{value}")
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current /= part
        if linked(current):
            raise ValueError(f"路径含符号链接/junction，需单独核对：{value}")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root) or (resolved == root and not allow_root):
        raise ValueError(f"路径不能是项目根或项目外：{value}")
    return resolved


def contract(root):
    root = Path(root).resolve()
    text = (root / "logic_readme.md").read_text(encoding="utf-8")
    if field(text, "workspace_root", ".") != ".":
        raise ValueError("workspace_root 必须为 .（当前项目文件夹）")
    scratch = field(text, "scratch_root", ".work/").rstrip("/")
    project_path(root, scratch)
    data = split_paths(field(text, "data_roots"))
    for item in data:
        project_path(root, item)
    return {"project_root": root.as_posix(), "scratch_root": scratch, "data_roots": data}


def task_ledgers(root):
    """One fixed level; never follow links into another project."""
    root = Path(root).resolve()
    base = Path(root) / "logic_changes"
    if not base.is_dir():
        return []
    project_path(root, "logic_changes")
    result = []
    for child in sorted(base.iterdir()):
        if child.is_dir():
            path = project_path(root, child.relative_to(root).as_posix() + "/logic_change.md")
            if path.is_file():
                result.append((path.relative_to(root).as_posix(), path))
    return result


def scan_entries(directory, limit):
    """Bound directory enumeration itself, not only rendered output."""
    entries = []
    with os.scandir(directory) as stream:
        for item in stream:
            if len(entries) >= limit:
                return sorted(entries, key=lambda e: e.name.casefold()), True
            entries.append(item)
    return sorted(entries, key=lambda e: e.name.casefold()), False
