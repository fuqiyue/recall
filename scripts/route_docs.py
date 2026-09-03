#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""``recall route``：按目标路径或关键词给出本次任务应读的 Recall 文档清单。

一二级拆分法（RULE-018，VER-20260903-004）：根 ``logic_readme.md`` 是宪法、
每个任务必读；``logic_domains/<domain>/logic_readme.md`` 是部门法，只在任务
触及其职权（``owned_paths``）时读取；每份 readme 配一份 ``logic_change.md``。
本命令把"该读哪几份"从代理的猜测变成机器输出，并附行数与估算 token，
让上下文成本在读之前就可见。只读，不改文件。
"""

from __future__ import annotations

import json
import sys
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recall_common import (  # noqa: E402
    LogicDomain,
    find_project_root,
    force_utf8_output,
    registered_domains,
)


def estimate_tokens(text: str) -> int:
    """粗估 token：CJK 字符约 1 token/字，其余约 4 字符/token。只用于比较大小。"""
    cjk = sum(1 for ch in text if ord(ch) >= 0x2E80)
    return cjk + (len(text) - cjk) // 4


def _doc_stats(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {"path": path.as_posix(), "exists": False, "lines": 0, "tokens": 0}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "lines": text.count("\n") + 1,
        "tokens": estimate_tokens(text),
    }


def _normalize(value: str) -> str:
    return value.replace("\\", "/").strip().strip("/").lstrip("./") or "."


def _path_matches(target: str, owned: str) -> bool:
    """目标路径落在职权路径之下、或职权路径落在目标目录之下、或 glob 命中。"""
    target_n = _normalize(target)
    owned_n = _normalize(owned)
    if owned_n == ".":
        return False
    if target_n == owned_n or target_n.startswith(owned_n + "/"):
        return True
    if owned_n.startswith(target_n + "/"):
        return True
    return fnmatchcase(target_n, owned_n) or fnmatchcase(target_n, owned_n + "/*")


def _keyword_matches(keyword: str, domain: LogicDomain) -> bool:
    needle = keyword.casefold()
    if needle in domain.module_id.casefold() or needle in domain.scope_path.casefold():
        return True
    if domain.readme.exists():
        return needle in domain.readme.read_text(encoding="utf-8", errors="replace").casefold()
    return False


def _looks_like_path(root: Path, target: str) -> bool:
    return "/" in target or "\\" in target or (root / target).exists()


def match_domains(root: Path, targets: List[str]) -> Dict[str, List[str]]:
    """返回 {scope_path: [命中理由...]}，只含命中的领域。"""
    hits: Dict[str, List[str]] = {}
    for domain in registered_domains(root):
        reasons: List[str] = []
        owned = domain.owned_paths()
        for target in targets:
            if _looks_like_path(root, target):
                matched = [item for item in owned if _path_matches(target, item)]
                if matched:
                    reasons.append(f"路径 {target} 属于职权 {', '.join(matched)}")
            elif _keyword_matches(target, domain):
                reasons.append(f"关键词 '{target}' 出现在该领域文档")
        if reasons:
            hits[domain.scope_path] = reasons
    return hits


def _gazette_hits(root: Path, scopes: List[str]) -> List[str]:
    """根账本公报中指向命中领域的活跃 CHG 行（提示有在办议案）。"""
    change = root / "logic_change.md"
    if not change.exists():
        return []
    lines = []
    for line in change.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|") or "CHG-" not in line:
            continue
        for scope in scopes:
            if f"{scope}/logic_change.md" in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                lines.append(f"{cells[0]} ({cells[1] if len(cells) > 1 else '?'}) -> {scope}")
    return lines


def build_plan(root: Path, targets: List[str]) -> Dict[str, object]:
    domains = registered_domains(root)
    hits = match_domains(root, targets) if targets else {}
    reading: List[Dict[str, object]] = []

    def add(path: Path, role: str, reason: str) -> None:
        entry = {"path": path.relative_to(root).as_posix(), "role": role, "reason": reason}
        entry.update(_doc_stats(path))
        reading.append(entry)

    add(root / "logic_readme.md", "宪法（一级 readme）", "每个任务必读：全局规则、领域目录、功能意图")
    add(root / "logic_change.md", "修宪议案 + 全项目活跃议案索引", "必读：看是否有在办议案触及目标领域")
    for domain in domains:
        if domain.scope_path in hits:
            add(domain.readme, f"部门法 {domain.module_id}", "; ".join(hits[domain.scope_path]))
            if domain.change is not None:
                add(domain.change, f"领域议案 {domain.module_id}", "该领域一事一议的活跃 CHG 正文")
    total_tokens = sum(int(item["tokens"]) for item in reading)
    total_lines = sum(int(item["lines"]) for item in reading)
    all_domains = [
        {
            "module_id": d.module_id,
            "scope_path": d.scope_path,
            "doc_policy": d.doc_policy,
            "owned_paths": d.owned_paths(),
            "readme": _doc_stats(d.readme),
            "change": _doc_stats(d.change) if d.change is not None else None,
        }
        for d in domains
    ]
    return {
        "project_root": root.as_posix(),
        "targets": targets,
        "reading_order": reading,
        "matched_domains": sorted(hits),
        "in_flight_changes": _gazette_hits(root, sorted(hits)),
        "domains": all_domains,
        "total_lines": total_lines,
        "total_tokens_estimate": total_tokens,
    }


def _print_plan(plan: Dict[str, object]) -> None:
    targets = plan["targets"]
    print("\n📚 Recall 读取清单" + (f"（目标：{', '.join(targets)}）" if targets else "（未给目标：仅列宪法与全部领域）"))
    print("=" * 60)
    for index, item in enumerate(plan["reading_order"], start=1):
        flag = "" if item["exists"] else "  ⚠️ 文件不存在"
        print(f"{index}. {item['path']}  [{item['role']}]  {item['lines']} 行 ≈ {item['tokens']} token{flag}")
        print(f"   理由：{item['reason']}")
    print(f"\n合计约 {plan['total_lines']} 行 ≈ {plan['total_tokens_estimate']} token")
    if plan["in_flight_changes"]:
        print("\n🔄 命中领域有在办议案：")
        for line in plan["in_flight_changes"]:
            print(f"   • {line}")
    domains = plan["domains"]
    if not domains:
        print("\n⚠️  宪法未登记任何领域（RULE-018 一二级拆分法要求至少一个 logic_domains/<domain>/ paired 行）")
    elif targets and not plan["matched_domains"]:
        print("\nℹ️  目标未命中任何领域职权；可选领域：")
    if domains and (not targets or not plan["matched_domains"]):
        for d in domains:
            change = d["change"]
            change_part = f"，change {change['lines']} 行" if change and change["exists"] else ""
            print(
                f"   • {d['module_id']} ({d['scope_path']}) 职权：{', '.join(d['owned_paths']) or '未声明'}；"
                f"readme {d['readme']['lines']} 行{change_part}"
            )
        if targets:
            print("   新功能不属于任何领域时，先在宪法范围登记表新增领域行（修宪案），再动手")
    print("")


def main(argv: Optional[List[str]] = None) -> int:
    force_utf8_output()
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    targets = [a for a in args if a != "--json"]
    root = find_project_root()
    if not (root / "logic_readme.md").exists():
        print("❌ 未找到 logic_readme.md（宪法）；先建立根文档", file=sys.stderr)
        return 1
    plan = build_plan(root, targets)
    if as_json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        _print_plan(plan)
    return 0


if __name__ == "__main__":
    sys.exit(main())
