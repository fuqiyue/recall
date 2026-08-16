#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure and run Recall's opt-in Git remote synchronization.

The sync policy is intentionally small and explicit:

* ``recall init`` enables it by default and installs a managed post-commit hook.
* ``recall sync`` defaults to auto-save: a dirty worktree is committed with a
  generated message before pulling and pushing (``recall.autoCommit``, default
  on; switch off with ``recall sync --manual``).
* The hook never stages files: it only backfills ``after_commit`` placeholders
  in records referenced by the fresh commit's ``Ref:`` lines or contained in
  the commit itself, then synchronizes existing commits. This keeps
  partial-commit workflows safe.
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
AUTOCOMMIT_MESSAGE = "chore(recall): 自动保存本地修改"
BACKFILL_MESSAGE = "chore(recall): 回填决策记录 after_commit"
AFTER_COMMIT_PLACEHOLDER = "- after_commit: _待填写_"
# 可回填的占位符（按优先级）：完整模板的 after_commit 与旧快速模板的 commit 字段。
# 占位符必须精确匹配；识别不了时打印警告而非静默跳过（RULE-013）。
# 占位符只按整个字段行匹配（MULTILINE 锚定行首行尾）：裸子串替换曾把
# 记录叙述文字里引用的 `- after_commit: _待填写_` 一并改成提交哈希，
# 污染不可变记录正文——与 validate 占位符检查误报同源的老病。
BACKFILL_PLACEHOLDERS = (
    re.compile(r"^(\s*-\s*after_commit\s*[：:]\s*)_待填写_[ \t]*$", re.MULTILINE),
    re.compile(r"^(\s*-\s*commit\s*[：:]\s*)_待填写_[ \t]*$", re.MULTILINE),
)
# 已填写的 after_commit/commit 字段（before_commit 不算）
COMMIT_FIELD_RE = re.compile(
    r"^\s*-\s*(?:after_)?commit\s*[：:]\s*(\S+)", re.MULTILINE
)
HEX_HASH_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)
# 规范命名的决策记录相对路径（RULE-012）
RECORD_REL_RE = re.compile(
    r"^logic_version/records/logic_version-\d{8}-\d{3}-.+\.md$", re.IGNORECASE
)
# commit message 里的 `Ref: logic_version/records/<file>.md` 行
REF_LINE_RE = re.compile(r"Ref:\s*(logic_version/records/\S+?\.md)", re.IGNORECASE)
# 内部提交（自动保存/回填）触发的嵌套 post-commit hook 必须直接退出，
# 否则 hook -> 内部 commit -> hook 会无限递归
INTERNAL_COMMIT_ENV = "RECALL_INTERNAL_COMMIT"


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
        if not pattern.search(existing):
            return True, str(hook_path)
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
        ("recall.autoCommit", "true" if enabled else "false"),
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


def _autocommit_enabled(project_root: Path) -> bool:
    """自动保存开关 ``recall.autoCommit``；未设置时默认开启（RULE-011）。"""
    ok, value, _ = run_git(["config", "--bool", "recall.autoCommit"], cwd=project_root)
    if not ok or not value:
        return True
    return value == "true"


def _run_git_internal_commit(args: Iterable[str], project_root: Path) -> Tuple[bool, str, str]:
    """Run a commit created by Recall itself, guarded against hook recursion."""
    os.environ[INTERNAL_COMMIT_ENV] = "1"
    try:
        return run_git(args, cwd=project_root)
    finally:
        os.environ.pop(INTERNAL_COMMIT_ENV, None)


def _list_dirty_files(project_root: Path) -> list:
    """返回 ``(状态, 路径)`` 列表，供自动保存前向用户展示提交范围。"""
    ok, output, _ = run_git(["status", "--porcelain"], cwd=project_root)
    if not ok:
        return []
    entries = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        entries.append((line[:2], line[3:].strip().strip('"')))
    return entries


def _print_commit_plan(entries: list, excluded: list = None) -> None:
    """打印将被打包进同步提交的文件清单与被排除的未跟踪新文件。

    自动化默认只收集已跟踪文件的变更；未跟踪的新文件默认不上传，
    需要用户明确要求（--include-new 或先 git add）才纳入——非交互
    环境下事后警告拦不住已经推上远端的文件（RULE-011 / UXI-003）。
    """
    if entries:
        print(f"ℹ️  即将提交 {len(entries)} 个文件:")
        shown = entries[:20]
        for status, path in shown:
            marker = "  ← 新文件（此前未跟踪）" if status == "??" else ""
            print(f"   {status.strip() or '·'} {path}{marker}")
        if len(entries) > len(shown):
            print(f"   … 其余 {len(entries) - len(shown)} 个")
    if excluded:
        print(f"ℹ️  已排除 {len(excluded)} 个未跟踪的新文件（自动保存默认不上传新文件）:")
        for _, path in excluded[:20]:
            print(f"   ?? {path}")
        if len(excluded) > 20:
            print(f"   … 其余 {len(excluded) - 20} 个")
        print(
            "   需要上传时运行 recall sync --include-new 或先 git add <file>；"
            "私人文件请加入 .gitignore"
        )


def _commit_dirty_worktree(
    project_root: Path, message: str, quiet: bool = False, include_new: bool = False
) -> Tuple[bool, bool]:
    """Commit dirty files for an explicit or auto-save synchronization.

    Returns ``(ok, committed)``. Untracked new files are excluded unless
    ``include_new`` is set: automation must never publish files the user has
    not explicitly asked to upload (RULE-011). Callers decide whether staging
    is allowed: an explicit ``--commit-message`` or the auto-save mode of
    ``recall sync``. The post-commit hook never reaches this function.
    """
    if not _is_dirty(project_root):
        return True, False
    entries = _list_dirty_files(project_root)
    untracked = [entry for entry in entries if entry[0] == "??"]
    included = entries if include_new else [e for e in entries if e[0] != "??"]
    excluded = [] if include_new else untracked
    if not quiet:
        _print_commit_plan(included, excluded)
    add_args = ["add", "-A"] if include_new else ["add", "-u"]
    ok, _, stderr = run_git(add_args, cwd=project_root)
    if not ok:
        print(f"❌ 添加待同步文件失败: {stderr}")
        return False, False
    ok, stdout, stderr = _run_git_internal_commit(["commit", "-m", message], project_root)
    if ok:
        if not quiet:
            print(f"✅ 已创建同步提交: {message.splitlines()[0]}")
        return True, True
    combined = f"{stdout}\n{stderr}"
    if "nothing to commit" in combined or "nothing added to commit" in combined:
        return True, False
    print(f"❌ 创建同步提交失败: {stderr or stdout}")
    return False, False


def _head_commit_files(project_root: Path) -> list:
    """返回 HEAD 提交涉及的文件相对路径列表。"""
    ok, output, _ = run_git(
        ["log", "-1", "--format=", "--name-only"], cwd=project_root
    )
    if not ok or not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _fill_placeholder(text: str, short_hash: str) -> Tuple[str, bool]:
    """把新旧两种占位符之一回填为提交哈希，返回 ``(新文本, 是否回填)``。

    只匹配独立的字段行；叙述文字中引用的占位符字符串不回填。
    """
    for pattern in BACKFILL_PLACEHOLDERS:
        new_text, count = pattern.subn(
            lambda m: f"{m.group(1)}{short_hash}", text, count=1
        )
        if count:
            return new_text, True
    return text, False


def _has_filled_commit_field(text: str) -> bool:
    """记录里的 after_commit/commit 字段是否已填有效哈希（before_commit 不算）。"""
    return any(
        HEX_HASH_RE.match(match.group(1))
        for match in COMMIT_FIELD_RE.finditer(text)
    )


def backfill_after_commit(project_root: Path, quiet: bool = False) -> bool:
    """把 HEAD 提交关联的决策记录里的 after_commit 占位符回填为提交哈希。

    双通道定位记录：commit message 中 ``Ref: logic_version/records/*.md``
    指向的记录，以及本次提交文件清单里规范命名的记录（记录与代码同一
    提交时无需 Ref 行——自动保存提交正是这种情形）。识别新旧两种占位符；
    Ref 显式指向的记录既无占位符也无已填哈希时打印警告而非静默跳过。
    回填后以内部提交落盘（只 add 被回填的文件，绝不 ``add -A``，避免把
    无关脏文件卷进来）。失败只告警，不阻断同步。
    """
    ok, output, _ = run_git(["log", "-1", "--format=%h%n%B"], cwd=project_root)
    if not ok or not output:
        return True
    short_hash, _, body = output.partition("\n")
    refs = REF_LINE_RE.findall(body)
    committed_records = [
        path
        for path in (f.replace("\\", "/") for f in _head_commit_files(project_root))
        if RECORD_REL_RE.match(path)
    ]
    # 保序去重：Ref 显式引用优先，其后是提交内的记录文件
    candidates = list(dict.fromkeys([*refs, *committed_records]))
    if not candidates:
        return True

    filled = []
    for ref in candidates:
        explicit_ref = ref in refs
        record_path = (project_root / Path(ref)).resolve()
        try:
            record_path.relative_to(project_root)
        except ValueError:
            continue  # Ref 指向项目外，不碰
        if not record_path.is_file():
            if explicit_ref and not quiet:
                print(f"⚠️  Ref 指向的记录不存在，无法回填 after_commit: {ref}")
            continue
        try:
            text = record_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        text, matched = _fill_placeholder(text, short_hash)
        if not matched:
            # 已填哈希是正常状态（同一记录被后续提交再次引用）；
            # 既无占位符也无哈希才是断链，必须让用户看见
            if explicit_ref and not quiet and not _has_filled_commit_field(text):
                print(
                    f"⚠️  记录缺少可回填的占位符（应含 `{AFTER_COMMIT_PLACEHOLDER}`），"
                    f"after_commit 未回填: {ref}"
                )
            continue
        try:
            record_path.write_text(text, encoding="utf-8")
        except OSError as exc:
            if not quiet:
                print(f"⚠️  回填 after_commit 失败（跳过）: {ref}: {exc}")
            continue
        filled.append(ref)

    if not filled:
        return True
    ok, _, stderr = run_git(["add", "--", *filled], cwd=project_root)
    if not ok:
        if not quiet:
            print(f"⚠️  暂存回填文件失败: {stderr}")
        return True
    ok, _, stderr = _run_git_internal_commit(
        ["commit", "-m", f"{BACKFILL_MESSAGE} -> {short_hash}", "--", *filled],
        project_root,
    )
    if ok and not quiet:
        print(f"✅ 已回填 after_commit: {short_hash} ({', '.join(filled)})")
    elif not ok and not quiet:
        print(f"⚠️  回填提交失败（记录已修改，未提交）: {stderr}")
    return True


def _is_doc_like_path(path: str) -> bool:
    """漂移哨兵用的文档类文件判定（.md/.txt 等不算代码变更）。"""
    name = path.rsplit("/", 1)[-1].lower()
    if name.startswith(".git"):
        return True
    if name in ("license", "notice", "claude.md", "agents.md"):
        return True
    return name.endswith((".md", ".markdown", ".rst", ".txt"))


def warn_missing_logic_docs(project_root: Path, quiet: bool = False) -> None:
    """漂移哨兵：HEAD 提交含代码变更但未触及 logic 文档时打印非阻断提醒。

    logic_readme 是代码理解的持久缓存；代码变了而文档没动，缓存就在
    静默腐烂。简单通道的提交可以忽略这行提醒，它不阻断任何操作。
    """
    if quiet:
        return
    files = [f.replace("\\", "/") for f in _head_commit_files(project_root)]
    if not files:
        return
    logic_touched = any(
        f in ("logic_readme.md", "logic_change.md") or f.startswith("logic_version/")
        for f in files
    )
    if logic_touched:
        return
    if any(not _is_doc_like_path(f) for f in files):
        print(
            "ℹ️  本次提交包含代码变更但未更新 logic 文档"
            "（简单通道可忽略；涉及规则或用户可见行为请更新 logic_readme.md）"
        )


def sync_repository(
    project_root: Path,
    remote: Optional[str] = None,
    commit_message: Optional[str] = None,
    pull: bool = True,
    push: bool = True,
    quiet: bool = False,
    autocommit: bool = True,
    drift_check: bool = False,
    include_new: bool = False,
) -> int:
    """Synchronize changes with a configured remote.

    ``autocommit=True``（手动运行 recall sync）且 ``recall.autoCommit`` 开启时，
    脏工作区先以自动保存消息提交再同步；未跟踪新文件默认排除，仅
    ``include_new=True``（--include-new）时纳入；``autocommit=False``
    （post-commit hook）绝不提交别的脏文件，只回填 after_commit 并同步已提交历史。

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
        ok, _ = _commit_dirty_worktree(
            project_root, commit_message, quiet=quiet, include_new=include_new
        )
        if not ok:
            return 1
    elif _is_dirty(project_root):
        if autocommit and _autocommit_enabled(project_root):
            # 自动保存（RULE-011）：默认把已跟踪文件的变更提交后同步，
            # 避免未提交窗口期的工作丢失；未跟踪新文件默认排除
            # （--include-new 纳入）；recall sync --manual 可切换回手动。
            ok, _ = _commit_dirty_worktree(
                project_root, AUTOCOMMIT_MESSAGE, quiet=quiet, include_new=include_new
            )
            if not ok:
                return 1
        else:
            # 手动模式 / hook 场景：脏文件绝不被自动提交，但也不阻断
            # 已提交 commit 的推送——部分提交是 post-commit hook 的
            # 常见场景。pull 侧由 --autostash 保护未提交变更。
            if not quiet:
                print("ℹ️  工作区有未提交变更；仅同步已提交历史（提交当前文件请用 --commit-message）")

    # 漂移哨兵先看用户的原始提交；回填的内部提交会改变 HEAD，必须在其之前
    if drift_check:
        warn_missing_logic_docs(project_root, quiet=quiet)

    # 提交完成后回填决策记录的 after_commit（RULE-013）；失败只告警
    backfill_after_commit(project_root, quiet=quiet)

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
    parser.add_argument("--commit-message", help="用指定消息提交当前工作区后再同步（替代自动保存消息）")
    parser.add_argument(
        "--include-new",
        action="store_true",
        help="把未跟踪的新文件也纳入本次提交（默认排除：自动化不上传用户未明确要求的新文件）",
    )
    parser.add_argument("--no-pull", action="store_true", help="只推送，不先拉取远端")
    parser.add_argument("--no-push", action="store_true", help="只拉取并变基，不推送")
    parser.add_argument("--auto", action="store_true", help="启用自动保存：sync 时脏工作区自动提交（默认）")
    parser.add_argument("--manual", action="store_true", help="切换为手动模式：脏工作区仅在提供 --commit-message 时提交")
    parser.add_argument("--disable", action="store_true", help="关闭自动同步并移除受管理的 hook")
    # hook 内部标记：软性跳过（无远端/无分支）不算失败，避免每次提交都以
    # 非零退出码结束；真正的拉取/推送失败仍返回 1 并打印警告
    parser.add_argument("--post-commit", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    _force_utf8_when_redirected()
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    # 自动保存/回填产生的内部提交会再次触发 post-commit hook；
    # 这里直接退出，外层调用继续完成拉取与推送
    if args.post_commit and os.environ.get(INTERNAL_COMMIT_ENV):
        return 0
    root = find_project_root(args.root)
    if args.disable:
        for key in ("recall.autoSync", "recall.autoCommit"):
            ok, _, stderr = run_git(["config", "--local", key, "false"], cwd=root)
            if not ok:
                print(f"❌ 关闭自动同步失败: {stderr}")
                return 1
        ok, detail = remove_post_commit_hook(root)
        if not ok:
            print(f"❌ 自动同步 hook 移除失败: {detail}")
            return 1
        print("✅ Git 自动同步已关闭")
        return 0
    if args.manual or args.auto:
        if args.manual and args.auto:
            print("❌ --auto 与 --manual 不能同时使用")
            return 1
        value = "true" if args.auto else "false"
        ok, _, stderr = run_git(["config", "--local", "recall.autoCommit", value], cwd=root)
        if not ok:
            print(f"❌ 写入 recall.autoCommit 失败: {stderr}")
            return 1
        if args.auto:
            print("✅ 已启用自动保存：recall sync 会自动提交工作区变更后同步")
        else:
            print("✅ 已切换为手动模式：仅在提供 --commit-message 时提交工作区")
        return 0
    code = sync_repository(
        root,
        remote=args.remote,
        commit_message=args.commit_message,
        pull=not args.no_pull,
        push=not args.no_push,
        # hook 场景绝不自动提交其他脏文件，保护部分提交工作流
        autocommit=not args.post_commit,
        # 漂移哨兵只看 hook 场景的新鲜用户提交；手动 sync 的 HEAD 可能是旧提交
        drift_check=args.post_commit,
        include_new=args.include_new,
    )
    if args.post_commit and code == 2:
        return 0
    return code


if __name__ == "__main__":
    sys.exit(main())
