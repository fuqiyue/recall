#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recall 各脚本共用的基础设施（RULE-021）。

三件事此前在每个脚本里各写一份，坏掉的总是没有测试的那一份
（VER-20260811-002 的记录命名、VER-20260903-002 的 status 编码与
conflicts 根查找都属此类）：

- 项目根查找：向上寻找 ``logic_readme.md``
- Git 子进程调用：argv 列表、不经 shell（RULE-006）、固定 utf-8 解码（RULE-008）
- 输出流 UTF-8 防护：GBK 控制台与重定向环境下 emoji 不崩

任何脚本都不得再自行实现这三项。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# Recall 自身的仓库根（skill 安装目录）；供 create_ver 等在 cwd 链上
# 找不到 logic_readme.md 时回退。
SELF_ROOT = Path(__file__).resolve().parent.parent

ROOT_MARKER = "logic_readme.md"


def force_utf8_output() -> None:
    """把 stdout/stderr 切成 UTF-8（Windows cp936 控制台与重定向都适用）。

    只看 ``isatty`` 会漏掉交互式 GBK 控制台，所以按当前编码判断。
    流可能被替换成没有 ``reconfigure`` 的对象（测试、包装器），失败时保持
    原编码而不是崩溃。
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            if (getattr(stream, "encoding", "") or "").lower() != "utf-8":
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def find_project_root(
    start: Optional[Path] = None, *, fallback: Optional[Path] = None
) -> Path:
    """从 ``start``（默认 cwd）向上查找含 ``logic_readme.md`` 的目录。

    找不到时返回 ``fallback``；未给 fallback 则返回起点本身。
    ``create_ver`` 传 ``fallback=SELF_ROOT``：skill 被集中安装、用户在无
    logic_readme.md 的目录运行时，记录应落回 Recall 自身而不是 cwd。
    """
    origin = (start or Path.cwd()).resolve()
    current = origin
    while current != current.parent:
        if (current / ROOT_MARKER).exists():
            return current
        current = current.parent
    return fallback if fallback is not None else origin


def run_git(
    args: Iterable[str], cwd: Optional[Path] = None, timeout: int = 60
) -> Tuple[bool, str, str]:
    """运行 Git 并返回 ``(ok, stdout, stderr)``，输出只去尾部空白。

    不能 ``strip()`` 前导空白：``git status --porcelain`` 用首列空格表示
    "工作区已修改、暂存区干净"（`` M path``），整体 strip 会让首行状态码
    与路径各错一位（``.github/x`` 变成 ``github/x``）。

    参数以列表传入且不经过 shell（RULE-006）；固定 utf-8 解码并替换非法
    字节（RULE-008）。中文提交信息在 GBK 默认编码下会让 ``subprocess``
    的读线程抛 ``UnicodeDecodeError`` 并把 stdout 变成 None。
    Git 不可用、超时或参数非法时返回 ``(False, "", <原因>)``，不抛异常。
    """
    try:
        result = subprocess.run(
            ["git", *list(args)],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return False, "", str(exc)
    return (
        result.returncode == 0,
        (result.stdout or "").rstrip(),
        (result.stderr or "").rstrip(),
    )


def git_output(
    args: Iterable[str], cwd: Optional[Path] = None, timeout: int = 60
) -> Optional[str]:
    """``run_git`` 的简写：成功返回 stdout，失败返回 None。"""
    ok, out, _ = run_git(args, cwd=cwd, timeout=timeout)
    return out if ok else None


def unpushed_commit_count(cwd: Optional[Path] = None) -> Optional[int]:
    """本地分支领先上游的提交数（RULE-010 推送责任核对）。

    返回 None 表示无法判断：非 Git 仓库、无提交、无上游分支或 Git 不可用。
    这些情形由调用方决定是否提示，本函数不替它下结论。
    """
    ok, out, _ = run_git(["rev-list", "--count", "@{u}..HEAD"], cwd=cwd, timeout=10)
    if not ok or not out.isdigit():
        return None
    return int(out)


def parse_porcelain(porcelain_output: Optional[str]) -> List[Tuple[str, str]]:
    """把 ``git status --porcelain`` 输出解析为 ``(两位状态码, 路径)`` 列表。

    只此一份（RULE-021）：git_sync 的提交清单与 ``recall status`` 的分类此前各
    解析一次，重命名与引号处理不一致。规则：状态码是前两列；重命名/复制
    ``R  old -> new`` 只保留新路径；含空格或非 ASCII 的路径 Git 会加双引号，
    这里去掉。空行跳过；不足三列的异常行按整行为路径、状态码为空处理。
    """
    entries: List[Tuple[str, str]] = []
    for raw_line in (porcelain_output or "").splitlines():
        if not raw_line.strip():
            continue
        if len(raw_line) > 3:
            code, path = raw_line[:2], raw_line[3:].strip()
        else:
            code, path = "", raw_line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((code, path.strip().strip('"')))
    return entries


def classify_porcelain(porcelain_output: Optional[str]) -> Tuple[List[str], List[str]]:
    """把 porcelain 输出分成 ``(已跟踪变更路径, 未跟踪文件路径)`` 两组。

    RULE-020（收尾归零）：未跟踪文件是 AI 解题过程残留的主要形态，而 RULE-011
    让它们默认不进自动保存提交，因此必须单列提示，不能与已跟踪修改混成一个
    "未提交变更"计数。只分类、不删除。
    """
    tracked: List[str] = []
    untracked: List[str] = []
    for code, path in parse_porcelain(porcelain_output):
        (untracked if code == "??" else tracked).append(path)
    return tracked, untracked


# ---------------------------------------------------------------------------
# 一二级文档模型（RULE-018）：宪法（根）+ 部门法（logic_domains/<domain>/）
# ---------------------------------------------------------------------------

REGISTRY_HEADING = "范围登记表"


def _table_rows_under_heading(text: str, heading_fragment: str) -> List[dict]:
    """返回 Markdown 标题（含 heading_fragment）之下第一张表的行，按表头取列。

    只做最小解析：一行一条，单元格以 ``|`` 分隔；表头行决定键名。
    读不到表返回空列表。此实现与审计器的 ``markdown_table_rows`` 独立，
    审计包是自洽的分层包，这里只服务 CLI 胶水层（validate / status / route / conflicts）。
    """
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("#") and heading_fragment in line:
            start = index + 1
            break
    if start is None:
        return []
    headers: Optional[List[str]] = None
    rows: List[dict] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped.startswith("|"):
            if headers is not None and rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if headers is None:
            headers = cells
            continue
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append({headers[i]: cells[i] for i in range(min(len(headers), len(cells)))})
    return rows


class LogicDomain:
    """一条已登记的二级（部门法）文档：readme + change 成对（doc_policy: paired）。"""

    def __init__(self, module_id: str, scope_path: str, root: Path, doc_policy: str):
        self.module_id = module_id
        self.scope_path = scope_path
        self.doc_policy = doc_policy
        self.readme = root / scope_path / "logic_readme.md"
        self.change = root / scope_path / "logic_change.md" if doc_policy == "paired" else None

    def owned_paths(self) -> List[str]:
        """领域 readme 声明的职权路径（``owned_paths`` 字段，逗号/分号分隔）。"""
        if not self.readme.exists():
            return []
        text = self.readme.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- owned_paths:"):
                value = stripped.split(":", 1)[1]
                return [
                    item.strip().strip("`").rstrip("/")
                    for item in value.replace("；", ";").replace("，", ",").replace(";", ",").split(",")
                    if item.strip() and item.strip().lower() != "none"
                ]
        return []


def registered_domains(root: Path) -> List[LogicDomain]:
    """宪法（根 logic_readme.md）范围登记表里登记的二级文档。

    ``paired`` 的非根行是部门法（readme + change）；``readme-only`` 是旧式
    只有 readme 的子文档（工具继续接受，文档不再推荐）。未登记的
    ``logic_domains/*`` 目录不在此列——审计器把它当平行真源。
    """
    readme = root / ROOT_MARKER
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8", errors="replace")
    domains: List[LogicDomain] = []
    for row in _table_rows_under_heading(text, REGISTRY_HEADING):
        policy = (row.get("doc_policy") or "").strip().strip("`").lower()
        membership = (row.get("membership") or "").strip().strip("`").lower()
        scope = (row.get("scope_path") or "").strip().strip("`").replace("\\", "/").strip("/")
        module_id = (row.get("module_id") or "").strip()
        if membership != "in-system" or policy not in {"paired", "readme-only"}:
            continue
        if not scope or scope == ".":
            continue
        domains.append(LogicDomain(module_id, scope, root, policy))
    return domains


def change_ledgers(root: Path) -> List[Tuple[str, Path]]:
    """全部议案账本：``[("logic_change.md", 根), ("logic_domains/x/logic_change.md", 领域), ...]``。

    根账本承载修宪议案与全项目活跃议案索引；领域账本承载本领域一事一议的 CHG 正文。
    只返回文件存在的账本。
    """
    ledgers: List[Tuple[str, Path]] = []
    root_change = root / "logic_change.md"
    if root_change.exists():
        ledgers.append(("logic_change.md", root_change))
    for domain in registered_domains(root):
        if domain.change is not None and domain.change.exists():
            ledgers.append((f"{domain.scope_path}/logic_change.md", domain.change))
    return ledgers
