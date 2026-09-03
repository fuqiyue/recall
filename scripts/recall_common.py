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
from typing import Iterable, Optional, Tuple

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
    """运行 Git 并返回 ``(ok, stdout, stderr)``，输出已 strip。

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
        (result.stdout or "").strip(),
        (result.stderr or "").strip(),
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
