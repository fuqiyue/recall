#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure and run Recall's opt-in Git remote synchronization.

The sync policy is intentionally small and explicit:

* ``recall init`` enables it by default and installs a managed post-commit hook.
* The hook only synchronizes commits that already exist; it never stages files.
* ``recall sync --commit-message ...`` is the explicit way to include a dirty
  worktree in a synchronization.
* Network failures are reported but do not make a completed local commit fail.

All Git commands are passed as argv lists so commit messages and remote URLs are
never interpreted by a shell.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple


HOOK_MARKER = "# Recall automatic Git sync"
HOOK_BEGIN = f"{HOOK_MARKER}: begin"
HOOK_END = f"{HOOK_MARKER}: end"
DEFAULT_REMOTE = "origin"
DEFAULT_COMMIT_MESSAGE = "chore: synchronize Recall changes"


def _force_utf8_when_redirected() -> None:
    """Keep reports usable when stdout/stderr are redirected on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def run_git(args: Iterable[str], cwd: Optional[Path] = None, timeout: int = 60) -> Tuple[bool, str, str]:
    """Run Git without a shell and return ``(ok, stdout, stderr)``."""
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


def find_project_root(start: Optional[Path] = None) -> Path:
    """Find the Recall project root from ``start`` or the current directory."""
    current = (start or Path.cwd()).resolve()
    while current != current.parent:
        if (current / "logic_readme.md").exists():
            return current
        current = current.parent
    return (start or Path.cwd()).resolve()


def _git_root(project_root: Path) -> Optional[Path]:
    ok, value, _ = run_git(["rev-parse", "--show-toplevel"], cwd=project_root)
    if not ok or not value:
        return None
    try:
        return Path(value).resolve()
    except OSError:
        return None


def _current_branch(project_root: Path) -> Optional[str]:
    ok, branch, _ = run_git(["branch", "--show-current"], cwd=project_root)
    return branch if ok and branch else None


def _remote_url(project_root: Path, remote: str) -> Optional[str]:
    ok, value, _ = run_git(["remote", "get-url", remote], cwd=project_root)
    return value if ok and value else None


def _has_remote_branch(project_root: Path, remote: str, branch: str) -> bool:
    ok, output, _ = run_git(["ls-remote", "--heads", remote, branch], cwd=project_root)
    return ok and bool(output)


def _is_dirty(project_root: Path) -> bool:
    ok, output, _ = run_git(["status", "--porcelain"], cwd=project_root)
    return ok and bool(output)


def _git_hooks_path(project_root: Path) -> Optional[Path]:
    ok, path, _ = run_git(["rev-parse", "--git-path", "hooks"], cwd=project_root)
    if not ok or not path:
        return None
    hooks_path = Path(path)
    if not hooks_path.is_absolute():
        hooks_path = project_root / hooks_path
    return hooks_path.resolve()


def _hook_block() -> str:
    # Git invokes hooks through its shell on Windows and Unix. Keep this block
    # POSIX-compatible and use the repository's configured Python when supplied.
    return f'''{HOOK_BEGIN}
RECALL_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
if [ "$(git config --bool recall.autoSync 2>/dev/null)" != "true" ]; then
    exit 0
fi
RECALL_PYTHON="${{RECALL_PYTHON:-python}}"
if ! command -v "$RECALL_PYTHON" >/dev/null 2>&1; then
    RECALL_PYTHON="python3"
fi
if command -v "$RECALL_PYTHON" >/dev/null 2>&1 && [ -f "$RECALL_ROOT/scripts/git_sync.py" ]; then
    "$RECALL_PYTHON" "$RECALL_ROOT/scripts/git_sync.py" --post-commit --root "$RECALL_ROOT" || true
fi
exit 0
{HOOK_END}'''


def install_post_commit_hook(project_root: Path) -> Tuple[bool, str]:
    """Append or update the managed post-commit hook, preserving user code."""
    hooks_path = _git_hooks_path(project_root)
    if hooks_path is None:
        return False, "无法定位 Git hooks 目录"
    try:
        hooks_path.mkdir(parents=True, exist_ok=True)
        hook_path = hooks_path / "post-commit"
        existing = hook_path.read_text(encoding="utf-8") if hook_path.exists() else "#!/bin/sh\n"
        block = _hook_block()
        pattern = re.compile(
            rf"\n?{re.escape(HOOK_BEGIN)}.*?{re.escape(HOOK_END)}\n?",
            re.DOTALL,
        )
        if pattern.search(existing):
            content = pattern.sub(f"\n{block}\n", existing)
        else:
            content = existing.rstrip("\r\n") + "\n\n" + block + "\n"
        hook_path.write_text(content, encoding="utf-8", newline="\n")
        try:
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            # Git for Windows does not require the executable bit.
            pass
    except OSError as exc:
        return False, f"写入 post-commit hook 失败: {exc}"
    return True, str(hook_path)


def remove_post_commit_hook(project_root: Path) -> Tuple[bool, str]:
    """Remove only Recall's managed block from the post-commit hook."""
    hooks_path = _git_hooks_path(project_root)
    if hooks_path is None:
        return False, "无法定位 Git hooks 目录"
    hook_path = hooks_path / "post-commit"
    if not hook_path.exists():
        return True, ""
    try:
        existing = hook_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"\n?{re.escape(HOOK_BEGIN)}.*?{re.escape(HOOK_END)}\n?",
            re.DOTALL,
        )
        content = pattern.sub("\n", existing).strip("\r\n")
        if not content or content == "#!/bin/sh":
            hook_path.unlink()
        else:
            hook_path.write_text(content + "\n", encoding="utf-8", newline="\n")
    except OSError as exc:
        return False, f"移除 post-commit hook 失败: {exc}"
    return True, str(hook_path)


def configure_git_sync(project_root: Path, enabled: bool = True, remote: str = DEFAULT_REMOTE) -> bool:
    """Configure Git defaults and install/remove Recall's auto-sync hook.

    Missing remotes are allowed: enabling the policy before adding ``origin``
    makes later commits sync as soon as a remote is configured.
    """
    _force_utf8_when_redirected()
    values = (
        ("recall.autoSync", "true" if enabled else "false"),
        ("recall.syncRemote", remote),
        ("pull.rebase", "true"),
        ("fetch.prune", "true"),
        ("push.autoSetupRemote", "true"),
    )
    for key, value in values:
        ok, _, stderr = run_git(["config", "--local", key, value], cwd=project_root)
        if not ok:
            print(f"❌ 写入 Git 配置 {key} 失败: {stderr}")
            return False

    if enabled:
        ok, detail = install_post_commit_hook(project_root)
        if not ok:
            print(f"❌ 自动同步 hook 配置失败: {detail}")
            return False
        print(f"✅ Git 自动同步已启用 (远端: {remote})")
        print(f"   hook: {detail}")
        if not _remote_url(project_root, remote):
            print(f"⚠️  未找到远端 '{remote}'；添加远端后提交将自动同步")
    else:
        ok, detail = remove_post_commit_hook(project_root)
        if not ok:
            print(f"❌ 自动同步 hook 移除失败: {detail}")
            return False
        print("ℹ️  Git 自动同步已关闭")
    return True


def _commit_dirty_worktree(
    project_root: Path, message: str, quiet: bool = False
) -> Tuple[bool, bool]:
    """Commit all dirty files when explicitly requested.

    Returns ``(ok, committed)``. No files are staged unless this function is
    called with an explicit commit message by the user.
    """
    if not _is_dirty(project_root):
        return True, False
    ok, _, stderr = run_git(["add", "-A"], cwd=project_root)
    if not ok:
        print(f"❌ 添加待同步文件失败: {stderr}")
        return False, False
    ok, stdout, stderr = run_git(["commit", "-m", message], cwd=project_root)
    if ok:
        if not quiet:
            print(f"✅ 已创建同步提交: {message.splitlines()[0]}")
        return True, True
    combined = f"{stdout}\n{stderr}"
    if "nothing to commit" in combined or "nothing added to commit" in combined:
        return True, False
    print(f"❌ 创建同步提交失败: {stderr or stdout}")
    return False, False


def sync_repository(
    project_root: Path,
    remote: Optional[str] = None,
    commit_message: Optional[str] = None,
    pull: bool = True,
    push: bool = True,
    quiet: bool = False,
) -> int:
    """Synchronize committed changes with a configured remote.

    Pull uses rebase and autostash when the remote branch already exists. Push
    sets the upstream on first use. A non-zero result means synchronization did
    not complete; local commits are never discarded.
    """
    _force_utf8_when_redirected()
    project_root = project_root.resolve()
    if _git_root(project_root) != project_root:
        if not quiet:
            print("❌ 当前目录不是 Git 仓库根目录")
        return 1
    remote_name = remote or (_remote_config(project_root) or DEFAULT_REMOTE)
    if not _remote_url(project_root, remote_name):
        if not quiet:
            print(f"⚠️  未配置 Git 远端 '{remote_name}'，请先运行 git remote add {remote_name} <url>")
        return 2

    if commit_message:
        ok, _ = _commit_dirty_worktree(project_root, commit_message, quiet=quiet)
        if not ok:
            return 1
    elif _is_dirty(project_root):
        if not quiet:
            print("⚠️  工作区有未提交变更；未自动提交。使用 --commit-message 明确提交后再同步")
        return 2

    branch = _current_branch(project_root)
    if not branch:
        if not quiet:
            print("⚠️  当前没有可同步的分支（请先创建一次提交）")
        return 2

    if pull and _has_remote_branch(project_root, remote_name, branch):
        ok, _, stderr = run_git(
            ["pull", "--rebase", "--autostash", remote_name, branch],
            cwd=project_root,
            timeout=120,
        )
        if not ok:
            if not quiet:
                print(f"❌ 拉取/变基失败，已停止推送: {stderr}")
            return 1

    if push:
        ok, stdout, stderr = run_git(
            ["push", "--set-upstream", remote_name, branch],
            cwd=project_root,
            timeout=120,
        )
        if not ok:
            if not quiet:
                print(f"⚠️  推送失败（本地提交保留）: {stderr or stdout}")
            return 1
        if not quiet:
            print(f"✅ Git 已同步: {remote_name}/{branch}")
    return 0


def _remote_config(project_root: Path) -> Optional[str]:
    ok, value, _ = run_git(["config", "--get", "recall.syncRemote"], cwd=project_root)
    return value if ok and value else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recall sync",
        description="拉取远端变基并推送已提交的 Recall 变更",
    )
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--remote", default=None, help="远端名称，默认使用 recall.syncRemote 或 origin")
    parser.add_argument("--commit-message", help="明确提交当前工作区后再同步；不提供时脏工作区不会被自动提交")
    parser.add_argument("--no-pull", action="store_true", help="只推送，不先拉取远端")
    parser.add_argument("--no-push", action="store_true", help="只拉取并变基，不推送")
    parser.add_argument("--disable", action="store_true", help="关闭自动同步并移除受管理的 hook")
    parser.add_argument("--post-commit", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    _force_utf8_when_redirected()
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    root = find_project_root(args.root)
    if args.disable:
        ok, _, stderr = run_git(["config", "--local", "recall.autoSync", "false"], cwd=root)
        if not ok:
            print(f"❌ 关闭自动同步失败: {stderr}")
            return 1
        ok, detail = remove_post_commit_hook(root)
        if not ok:
            print(f"❌ 自动同步 hook 移除失败: {detail}")
            return 1
        print("✅ Git 自动同步已关闭")
        return 0
    return sync_repository(
        root,
        remote=args.remote,
        commit_message=args.commit_message,
        pull=not args.no_pull,
        push=not args.no_push,
    )


if __name__ == "__main__":
    sys.exit(main())
