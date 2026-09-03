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
import re
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


_BOUNDARY_EXCLUSION_PREFIXES = ("- 不负责", "- 不负责：", "- 不负责:")
_TABLE_SEPARATOR_RE = re.compile(r"^\|\s*:?-{3,}")


def _keyword_searchable_text(domain: LogicDomain) -> str:
    """领域 readme 中参与关键词匹配的正文。

    跳过两类"看起来像内容、其实是 schema 或别人职权"的行，否则关键词会把
    不相关的领域拉进读取清单、抵消按需导入的收益（2026-09-04 实例：
    `route 审计` 命中 git-pipeline——一次是"不负责：审计/校验"，一次是表头
    "why（仅一句可审计摘要）"）：
    - "目标与边界"里的"不负责"行：列出的是**别的**领域的职权；
    - Markdown 表头行（其下一行是 `|---|` 分隔符）：每份文档都一样的列名。
    """
    if not domain.readme.exists():
        return ""
    lines = domain.readme.read_text(encoding="utf-8", errors="replace").splitlines()
    kept = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(_BOUNDARY_EXCLUSION_PREFIXES):
            continue
        is_header = (
            stripped.startswith("|")
            and index + 1 < len(lines)
            and _TABLE_SEPARATOR_RE.match(lines[index + 1].strip())
        )
        if is_header or _TABLE_SEPARATOR_RE.match(stripped):
            continue
        kept.append(line)
    return "\n".join(kept).casefold()


def _keyword_matches(keyword: str, domain: LogicDomain) -> bool:
    needle = keyword.casefold()
    if needle in domain.module_id.casefold() or needle in domain.scope_path.casefold():
        return True
    return needle in _keyword_searchable_text(domain)


def _looks_like_path(root: Path, target: str) -> bool:
    return "/" in target or "\\" in target or (root / target).exists()


_INT_ID_RE = re.compile(r"^INT-\d{8}-\d{3}$", re.IGNORECASE)
_RULE_TOKEN_RE = re.compile(r"\bRULE-[A-Z0-9][A-Z0-9-]*\b", re.IGNORECASE)


def constitution_intents(root: Path) -> List[Dict[str, str]]:
    """宪法功能意图登记表：用户表述层。列：intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 | [来源] | last_verified。"""
    readme = root / "logic_readme.md"
    if not readme.exists():
        return []
    intents: List[Dict[str, str]] = []
    source_col = None
    for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("| intent_id"):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            source_col = next((i for i, h in enumerate(headers) if h.startswith("来源")), None)
            continue
        if not stripped.startswith("| INT-"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 6:
            continue
        intents.append({
            "intent_id": cells[0].upper(),
            "entry": cells[1],
            "intent": cells[2],
            "rules": [r.upper() for r in _RULE_TOKEN_RE.findall(cells[4])],
            "anchors": [a.strip().strip("`") for a in re.split(r"[;，,]", cells[5]) if a.strip() and a.strip().lower() != "none"],
            "source": cells[source_col] if source_col is not None and len(cells) > source_col else "",
        })
    return intents


def match_intents(root: Path, targets: List[str]) -> List[Dict[str, str]]:
    """目标是 INT-ID，或关键词出现在意图行的功能入口/用户目标里 → 命中该用户意图。"""
    matched: List[Dict[str, str]] = []
    for intent in constitution_intents(root):
        for target in targets:
            if _INT_ID_RE.match(target) and target.upper() == intent["intent_id"]:
                matched.append(intent)
                break
            if not _looks_like_path(root, target) and not _INT_ID_RE.match(target):
                needle = target.casefold()
                if needle in intent["entry"].casefold() or needle in intent["intent"].casefold():
                    matched.append(intent)
                    break
    return matched


def _domain_rule_ids(domain: LogicDomain) -> set:
    if not domain.readme.exists():
        return set()
    return {
        line.strip().strip("|").split("|")[0].strip().upper()
        for line in domain.readme.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip().startswith("| RULE-")
    }


def match_domains(root: Path, targets: List[str], intents: Optional[List[Dict[str, str]]] = None) -> Dict[str, List[str]]:
    """返回 {scope_path: [命中理由...]}，只含命中的领域。

    三条路径：目标路径落在职权 owned_paths；关键词出现在领域文档；
    命中的宪法意图行（用户表述）的代码锚点或关联规则属于该领域。
    """
    hits: Dict[str, List[str]] = {}
    intents = intents or []
    for domain in registered_domains(root):
        reasons: List[str] = []
        owned = domain.owned_paths()
        for target in targets:
            if _looks_like_path(root, target):
                matched = [item for item in owned if _path_matches(target, item)]
                if matched:
                    reasons.append(f"路径 {target} 属于职权 {', '.join(matched)}")
            elif not _INT_ID_RE.match(target) and _keyword_matches(target, domain):
                reasons.append(f"关键词 '{target}' 出现在该领域文档")
        domain_rules = _domain_rule_ids(domain) if intents else set()
        for intent in intents:
            anchor_hits = [a for a in intent["anchors"] if any(_path_matches(a, item) for item in owned)]
            rule_hits = [r for r in intent["rules"] if r in domain_rules]
            if anchor_hits or rule_hits:
                parts = []
                if anchor_hits:
                    parts.append(f"锚点 {', '.join(anchor_hits)}")
                if rule_hits:
                    parts.append(f"规则 {', '.join(rule_hits)}")
                reasons.append(f"用户意图 {intent['intent_id']}（{intent['intent'][:30]}）的{'与'.join(parts)}属于本领域")
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
    intents = match_intents(root, targets) if targets else []
    hits = match_domains(root, targets, intents) if targets else {}
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
        "matched_intents": [
            {k: v for k, v in intent.items()} for intent in intents
        ],
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
    if plan["matched_intents"]:
        print("\n🎯 命中的用户意图（宪法意图层——以用户表述为准）：")
        for intent in plan["matched_intents"]:
            source = intent.get("source") or "未标来源"
            flag = "" if source.lower().startswith("user") else "  ⚠️ 非用户确认来源，实施前先确认"
            print(f"   • {intent['intent_id']} {intent['entry']}：{intent['intent']}  [来源 {source}]{flag}")
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
