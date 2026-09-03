"""文件与目录分类：源码/运行数据/测试/生成物/嵌套项目根。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from .constants import (
    CAMEL_TEST_NAME_RE,
    RUNTIME_DATA_DIR_NAMES,
    RUNTIME_DATA_SUFFIXES,
    SOURCE_SUFFIXES,
    TEST_DIRECTORY_NAMES,
    TEST_NAME_RE,
)
from .textutil import (
    control_values,
    is_within,
    markdown_section_text,
    normalize_scope_path,
    read_text,
    relative_depth,
)

def is_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES


def is_runtime_data_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in RUNTIME_DATA_SUFFIXES


def looks_like_runtime_data_directory(path: Path, root: Path) -> bool:
    if path == root:
        return False
    return any(
        part.lower() in RUNTIME_DATA_DIR_NAMES for part in path.relative_to(root).parts
    )


def is_test_file(path: Path, root: Path | None = None) -> bool:
    scoped_parts = (
        path.relative_to(root).parts[:-1]
        if root is not None and is_within(path, root)
        else path.parent.parts
    )
    return path.is_file() and (
        bool(TEST_NAME_RE.match(path.name))
        or bool(CAMEL_TEST_NAME_RE.match(path.name))
        or any(part.casefold() in TEST_DIRECTORY_NAMES for part in scoped_parts)
    )


def is_generated_file(path: Path) -> bool:
    lowered = path.name.lower()
    return path.is_file() and (
        lowered.endswith((".min.js", ".min.css", ".map"))
        or "generated" in {part.lower() for part in path.parts}
    )


def is_dependency_tree_root(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """Identify a vendored Python virtualenv before it becomes a map candidate."""
    if path == root:
        return False
    names = {name.lower() for name in file_names}
    return "pyvenv.cfg" in names


def is_nested_project_root(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """Identify a separately-governed project vendored inside this one.

    A subdirectory whose own ``logic_readme.md`` declares ``scope: .`` plus
    ``scope_type: root`` is another project's root (a vendored dependency,
    a bundled example, or an audit fixture), not a module of this project.

    Auditing it as a module corrupts the enclosing result: its ``module_id``
    is usually ``MOD-ROOT`` too, so it displaces the real root document in
    the ``module_id``-keyed maps, which then makes the genuine root scope
    look like it has no governance parent.  It is also counted as an
    unregistered governance directory even though registering it would be
    wrong -- it is not in this project's scope hierarchy at all.
    """
    if path == root:
        return False
    if "logic_readme.md" not in {name.lower() for name in file_names}:
        return False
    text, error = read_text(path / "logic_readme.md")
    if error:
        return False
    # Read the document-control block only.  ``control_values`` over the whole
    # file also picks up per-scope sections (e.g. a nested ``- scope_path: src``
    # for a sub-module), which would mask the root declaration.
    values = control_values(markdown_section_text(text, "文档控制"))
    declared_scopes = {
        normalize_scope_path(value)
        for field in ("scope", "scope_path")
        for value in values.get(field, [])
    }
    return declared_scopes == {"."} and (values.get("scope_type") or [""])[0] == "root"


def is_foreign_subtree(path: Path, root: Path, file_names: Iterable[str]) -> bool:
    """A subtree whose contents must not be attributed to this project.

    Covers vendored Python environments and separately-governed projects
    nested inside this one.  Scanners that report "this project has a
    problem" must prune these, otherwise another project's parallel files,
    stray temp records or misplaced history get blamed on this one.
    """
    return is_dependency_tree_root(path, root, file_names) or is_nested_project_root(
        path, root, file_names
    )


def iter_directories(
    root: Path,
    max_depth: int | None,
    excludes: set[str],
    nested_project_roots: list[str] | None = None,
) -> Iterable[tuple[Path, list[Path]]]:
    for current_raw, dir_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_raw)
        if is_dependency_tree_root(current, root, file_names):
            # Do not report the environment itself or descend into its
            # site-packages as if they were project modules.
            dir_names[:] = []
            continue
        if is_nested_project_root(current, root, file_names):
            # Skip the nested root and its whole subtree; its modules belong
            # to that project's registry, not to this one.
            if nested_project_roots is not None:
                nested_project_roots.append(current.relative_to(root).as_posix())
            dir_names[:] = []
            continue
        depth = relative_depth(current, root)
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in excludes
            and not name.startswith(".")
            and (max_depth is None or depth < max_depth)
        )
        yield current, [current / name for name in file_names]
