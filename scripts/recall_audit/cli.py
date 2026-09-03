"""命令行参数与入口。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .report import (
    collect_audit,
    print_text,
    strict_failure,
)

# RULE-008/RULE-021：重定向下 stdout 走 ANSI 代码页，`--json` 里的中文会写成 GBK
# 或抛 UnicodeEncodeError（2026-09-03 消费项目实测需 PYTHONIOENCODING 才能落盘）。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from recall_common import force_utf8_output  # noqa: E402

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only audit of current policy/proposals, tests, agent entrypoints, "
            "and optional legacy module/history governance."
        )
    )
    parser.add_argument("project_root", type=Path, help="Project directory to inspect")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help=(
            "Maximum directory depth below the project root for non-strict-v2 "
            "inventory; the default is unlimited"
        ),
    )
    parser.add_argument(
        "--all-dirs",
        action="store_true",
        help="Treat every non-excluded directory as a documentation candidate",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional directory name to exclude; repeat as needed",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print JSON instead of text"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Return 1 for missing root policy/change entry, malformed documents, "
            "broken links, misplaced history, or invalid existing agent entrypoints"
        ),
    )
    parser.add_argument(
        "--strict-v2",
        action="store_true",
        help=(
            "Legacy migration audit for distributed/module-local Recall v2 "
            "documents, history roots, and controlled logic_temp records; "
            "do not use this as the root-only release audit"
        ),
    )
    parser.add_argument(
        "--current-state",
        action="store_true",
        help=(
            "Run a lightweight root-only logic-map audit: current documents, "
            "scope routes, active CHG lifecycle/declared coordination metadata, and "
            "at least one agent entrypoint. It does not claim to audit code semantics."
        ),
    )
    parser.add_argument(
        "--formal-review",
        action="store_true",
        help=(
            "Run the root-only current-state checks plus complete active-CHG "
            "sections and current test-review matrices. Code semantics still "
            "require a Codex, Claude, or human review."
        ),
    )
    parser.add_argument(
        "--require-test-matrix",
        action="store_true",
        help=(
            "Require status-aware baseline/post-change matrices for active changes "
            "and completed version records; test-file discovery remains evidence, "
            "not an unconditional requirement"
        ),
    )
    parser.add_argument(
        "--require-agent-entry",
        choices=("codex", "claude", "both"),
        help=(
            "Require a valid root AGENTS.md plus .agents/, CLAUDE.md plus .claude/, "
            "or both for the agents actually enabled in this project. Current/formal "
            "profiles already require at least one root entry."
        ),
    )
    return parser.parse_args()


def main() -> int:
    force_utf8_output()
    args = parse_args()
    try:
        report = collect_audit(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)

    strict_requested = (
        args.strict
        or args.strict_v2
        or args.current_state
        or args.formal_review
        or args.require_test_matrix
        or bool(args.require_agent_entry)
    )
    return (
        1
        if strict_requested
        and strict_failure(
            report,
            v2=args.strict_v2,
            current_state=args.current_state,
            formal_review=args.formal_review,
            require_test_matrix=args.require_test_matrix,
        )
        else 0
    )
