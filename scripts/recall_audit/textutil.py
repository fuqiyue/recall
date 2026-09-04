"""Markdown/控制字段解析与路径工具；不含任何审计判断。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from .constants import (
    CHANGE_ID_RE,
    CODE_SPAN_RE,
    EMPTY_LEDGER_COUNT_VALUES,
    FENCED_CODE_RE,
    ADR_NAME_RE,
    ANGLE_PLACEHOLDER_RE,
    CANONICAL_VERSION_RE,
    CHANGE_HEADING_RE,
    CONTROL_RE,
    DECISION_AUTHORITY_ID_RE,
    HEADING_RE,
    MARKDOWN_LINK_RE,
    NONE_LIKE_CONTROL_VALUES,
    TOPIC_ID_RE,
)

def relative_depth(path: Path, root: Path) -> int:
    return len(path.relative_to(root).parts)


def strip_code_segments(text: str) -> str:
    """Remove fenced code blocks and inline code spans.

    Markdown inside code is illustrative, not a reference: ``[ID](path)`` in a
    rule cell or a template excerpt must not be resolved as a file link, just
    as ``<meta>`` inside backticks is not a template placeholder.
    """
    return CODE_SPAN_RE.sub("", FENCED_CODE_RE.sub("", text))


def is_empty_ledger_count(value: str) -> bool:
    """``active_changes`` of a ledger without CHG bodies: ``none`` (template) or ``0``."""
    return value.strip().casefold() in EMPTY_LEDGER_COUNT_VALUES


def normalize_link_target(raw: str) -> str | None:
    target = raw.strip().strip("<>")
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    # `[text](path "title")`: the optional title is not part of the path
    if " " in target and target.rstrip().endswith(('"', "'")):
        target = target.split(" ", 1)[0]
    target = target.split("#", 1)[0].split("?", 1)[0]
    return target or None


def audit_links(document: Path, text: str, root: Path) -> list[str]:
    broken: list[str] = []
    for raw in MARKDOWN_LINK_RE.findall(strip_code_segments(text)):
        target = normalize_link_target(raw)
        if target is None:
            continue
        candidate = (document.parent / target).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            broken.append(f"outside-project:{raw}")
            continue
        if not candidate.exists():
            broken.append(raw)
    return sorted(set(broken))


def read_text(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig"), None
        except (OSError, UnicodeDecodeError) as exc:
            return "", str(exc)
    except OSError as exc:
        return "", str(exc)


def inspect_markdown(
    path: Path,
    root: Path,
    required_sections: set[str],
    required_fields: set[str],
) -> tuple[list[str], list[str], list[str]]:
    text, error = read_text(path)
    if error:
        return [], [], [f"unreadable:{error}"]
    headings = {heading.strip() for heading in HEADING_RE.findall(text)}
    fields = {match[0] for match in CONTROL_RE.findall(text)}
    return (
        sorted(required_sections - headings),
        sorted(required_fields - fields),
        audit_links(path, text, root),
    )


def control_values_raw(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for key, value in CONTROL_RE.findall(text):
        values.setdefault(key, []).append(value.strip())
    return values


def control_values(text: str) -> dict[str, list[str]]:
    return {
        key: [value.lower() for value in entries]
        for key, entries in control_values_raw(text).items()
    }


def normalize_scope_path(value: str) -> str:
    normalized = value.strip().strip("<>").replace("\\", "/").strip()
    if normalized.lower() in {"root", "project-root", "all-project", "全项目"}:
        return "."
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.rstrip("/")
    return normalized or "."


def scope_parts(value: str) -> tuple[str, ...]:
    normalized = normalize_scope_path(value)
    return () if normalized == "." else tuple(normalized.split("/"))


def is_scope_ancestor(parent: str, child: str) -> bool:
    parent_parts = scope_parts(parent)
    child_parts = scope_parts(child)
    return (
        len(parent_parts) < len(child_parts)
        and child_parts[: len(parent_parts)] == parent_parts
    )


def split_control_list(value: str) -> set[str]:
    return {
        normalize_scope_path(item.strip(" `[]"))
        for item in re.split(r"[,;，；]", value)
        if item.strip(" `[]")
    }


def actual_case_relative(root: Path, relative: str) -> tuple[Path, str] | None:
    """Resolve a repository-relative directory while preserving on-disk casing."""
    current = root
    actual_parts: list[str] = []
    for requested in scope_parts(relative):
        try:
            children = [child for child in current.iterdir() if child.is_dir()]
        except OSError:
            return None
        exact = next((child for child in children if child.name == requested), None)
        if exact is None:
            folded = [
                child
                for child in children
                if child.name.casefold() == requested.casefold()
            ]
            if len(folded) != 1:
                return None
            exact = folded[0]
        current = exact
        actual_parts.append(exact.name)
    return current, "/".join(actual_parts) or "."


def markdown_table_rows(text: str, heading_fragment: str) -> list[dict[str, str]]:
    """Parse the first Markdown table following a matching heading."""
    lines = text.splitlines()
    heading_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("#") and heading_fragment in line
        ),
        None,
    )
    if heading_index is None:
        return []
    section_end = next(
        (
            index
            for index in range(heading_index + 1, len(lines))
            if lines[index].lstrip().startswith("#")
        ),
        len(lines),
    )
    table_start = next(
        (
            index
            for index in range(heading_index + 1, section_end)
            if lines[index].strip().startswith("|")
        ),
        None,
    )
    if table_start is None:
        return []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    headers = cells(lines[table_start])
    separator_index = table_start + 1
    if separator_index >= section_end:
        return []
    separators = cells(lines[separator_index])
    if len(separators) != len(headers) or not all(
        re.fullmatch(r":?-{3,}:?", value) for value in separators
    ):
        return []
    rows: list[dict[str, str]] = []
    for line in lines[separator_index + 1 : section_end]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        values = cells(stripped)
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def markdown_table_headers(text: str, heading_fragment: str) -> list[str]:
    """Return the validated header row for the first table in a section."""
    lines = text.splitlines()
    heading_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("#") and heading_fragment in line
        ),
        None,
    )
    if heading_index is None:
        return []
    section_end = next(
        (
            index
            for index in range(heading_index + 1, len(lines))
            if lines[index].lstrip().startswith("#")
        ),
        len(lines),
    )
    table_start = next(
        (
            index
            for index in range(heading_index + 1, section_end)
            if lines[index].strip().startswith("|")
        ),
        None,
    )
    if table_start is None or table_start + 1 >= section_end:
        return []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    headers = cells(lines[table_start])
    separators = cells(lines[table_start + 1])
    if len(separators) != len(headers) or not all(
        re.fullmatch(r":?-{3,}:?", value) for value in separators
    ):
        return []
    return headers


def markdown_section_text(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if re.fullmatch(rf"\s*##\s+{re.escape(heading)}\s*", line)
        ),
        None,
    )
    if start is None:
        return ""
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if re.match(r"^\s*##\s+", lines[index])
        ),
        len(lines),
    )
    return chr(10).join(lines[start:end])


def cell_link_parts(cell: str) -> tuple[str | None, str | None]:
    match = MARKDOWN_LINK_RE.search(cell)
    if not match:
        return None, None
    raw = match.group(1).strip().strip("<>")
    fragment = raw.split("#", 1)[1].split("?", 1)[0] if "#" in raw else None
    return normalize_link_target(raw), fragment


def cell_link_target(cell: str) -> str | None:
    target, _ = cell_link_parts(cell)
    return target


def is_immutable_decision_record_link(cell: str) -> bool:
    """Accept only a concrete ADR or immutable VER link for a key rule."""
    target = cell_link_target(cell)
    if target is None:
        return False
    normalized = target.removeprefix("./").replace("\\", "/")
    path = Path(normalized)
    parts = tuple(part.casefold() for part in path.parts)
    # RULE-018：领域文档（logic_domains/<domain>/）向上引用根 logic_version，去掉前导 ..
    while parts and parts[0] == "..":
        parts = parts[1:]
    if parts[:2] == ("logic_version", "records"):
        return bool(CANONICAL_VERSION_RE.fullmatch(path.name))
    if parts[:2] == ("logic_version", "decisions"):
        return bool(ADR_NAME_RE.fullmatch(path.name))
    return False


def normalize_change_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return candidate.upper() if CHANGE_ID_RE.fullmatch(candidate) else ""


def normalize_topic_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return candidate.upper() if TOPIC_ID_RE.fullmatch(candidate) else ""


def normalize_authority_id(value: str) -> str:
    candidate = value.strip("` ,:;")
    return candidate.upper() if DECISION_AUTHORITY_ID_RE.fullmatch(candidate) else ""


def change_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    starts = [
        index for index, line in enumerate(lines) if CHANGE_HEADING_RE.match(line)
    ]
    blocks: dict[str, str] = {}
    for position, start in enumerate(starts):
        match = CHANGE_HEADING_RE.match(lines[start])
        change_id = normalize_change_id(match.group(1)) if match else ""
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        if change_id:
            blocks[change_id] = chr(10).join(lines[start:end])
    return blocks


def change_affected_scopes(values: dict[str, list[str]]) -> set[str]:
    affected: set[str] = set()
    for value in values.get("affected_scopes", []):
        affected |= split_control_list(value)
    return affected


def has_meaningful_value(values: dict[str, list[str]], key: str) -> bool:
    return any(
        value not in {"", "none", "unknown", "n/a", "not-applicable", "..."}
        and not contains_angle_placeholder(value)
        and not value.startswith("yyyy")
        and "event-driven" not in value
        for value in values.get(key, [])
    )


def has_lifecycle_trigger(values: dict[str, list[str]], key: str) -> bool:
    return has_meaningful_value(values, key) or any(
        value == "event-driven" for value in values.get(key, [])
    )


def is_none_like(value: str) -> bool:
    return value.strip().casefold() in NONE_LIKE_CONTROL_VALUES


def contains_angle_placeholder(value: str) -> bool:
    """Detect template placeholders (``<...>``) outside inline code spans.

    Traceability arrows (``->``), bare comparisons (``>128``) and inline code
    such as ``<meta>`` are not placeholders; the old ``"<" in value`` checks in
    the current-state gate rejected legitimate rule text for them.
    """
    return bool(ANGLE_PLACEHOLDER_RE.search(CODE_SPAN_RE.sub("", value)))


def is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def relationship_items(raw_values: dict[str, list[str]], key: str) -> list[str]:
    """Split a CHG relationship field without treating values as file scopes."""
    return [
        item.strip(" `[]")
        for value in raw_values.get(key, [])
        for item in re.split(r"[,;，；]", value)
        if item.strip(" `[]")
    ]


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
