"""Persist incremental scan coverage inside the generated Markdown map itself."""

import html
import json
from pathlib import PurePosixPath
import re

MARKER = "<!-- recall-generated-file-map -->"
META = "<!-- recall-map-coverage: "


def read_map(text):
    if not text.startswith(MARKER):
        raise ValueError("保留手写文件，未写入：文件地图")
    match = re.search(r"^<!-- recall-map-coverage: (.+) -->$", text, re.M)
    if match:
        metadata = json.loads(match.group(1))
        if metadata.get("schema") != 2:
            raise ValueError("未知文件地图格式，保留原文")
    else:
        # First-generation maps have only a display table; do not claim full coverage.
        stamp = re.search(r"^扫描时间：(.*)$", text, re.M)
        scope = re.search(r"^范围：(.*)$", text, re.M)
        stamp = stamp.group(1).strip() if stamp else "unknown"
        metadata = {"schema": 2, "coverage": [], "scans": {}, "legacy_boundary": {
            "generated_at": stamp, "scope": scope.group(1) if scope else "旧版未记录范围",
            "notices": text.split("扫描边界：", 1)[-1].strip() if "扫描边界：" in text else "未记录"}}
    rows, columns = [], []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        values = [html.unescape(v.strip()) for v in line.strip("|").split("|")]
        if values[:3] == ["路径", "简要说明", "领域"]:
            columns = values
        elif columns and len(columns) == len(values) and not all(re.fullmatch(r"[-: ]+", v) for v in values):
            cells = dict(zip(columns, values))
            desc = cells["简要说明"]
            rows.append({"path": cells["路径"], "description": desc,
                         "domains": [] if cells["领域"] == "待登记" else cells["领域"].split(", "),
                         "kind": cells.get("类型", "link" if "链接" in desc else "directory" if "目录" in desc else "file"),
                         "classification_source": cells.get("分类依据", "legacy"),
                         "scanned_at": cells.get("扫描时间", metadata.get("legacy_boundary", {}).get("generated_at", "unknown"))})
    if not columns:
        raise ValueError("文件地图表头缺失，保留原文")
    return dict(metadata, entries=rows)


def merge_map(previous, data):
    previous = previous or {"coverage": [], "scans": {}, "entries": []}
    fresh = {r["path"]: dict(r, scanned_at=data["generated_at"]) for r in data["entries"]}
    complete = {d["path"] for d in data["scanned_directories"] if d["complete"]}
    vanished = {r["path"] for r in previous["entries"]
                if str(PurePosixPath(r["path"]).parent) in complete and r["path"] not in fresh}
    # A confirmed directory removal or replacement invalidates its old descendants too.
    replaced = {r["path"] for r in previous["entries"] if r["kind"] == "directory" and
                r["path"] in fresh and fresh[r["path"]]["kind"] != "directory"}
    removed = vanished | replaced

    def below_removed(path):
        return any(path == p or path.startswith(p + "/") for p in removed)

    retained = {r["path"]: r for r in previous["entries"] if not below_removed(r["path"])}
    retained.update(fresh)
    coverage = {r["path"]: r for r in previous["coverage"] if not below_removed(r["path"])}
    for directory in data["scanned_directories"]:
        coverage[directory["path"]] = dict(directory, generated_at=data["generated_at"])
    scans = dict(previous["scans"])
    scans[data["generated_at"]] = {k: data[k] for k in ("targets", "max_depth", "max_entries", "notices")}
    needed = {c["generated_at"] for c in coverage.values()} | {r["scanned_at"] for r in retained.values()}
    result = {"schema": 2, "entries": sorted(retained.values(), key=lambda r: r["path"]),
              "coverage": sorted(coverage.values(), key=lambda r: r["path"]),
              "scans": {k: v for k, v in scans.items() if k in needed}}
    if "legacy_boundary" in previous:
        legacy_time = previous["legacy_boundary"]["generated_at"]
        if any(r["scanned_at"] == legacy_time for r in result["entries"]):
            result["legacy_boundary"] = previous["legacy_boundary"]
    return result


def cell(value):
    return html.escape(str(value), quote=False).replace("|", "&#124;").replace("\n", "&#10;").replace("\r", "&#13;")


def render_map(data, domain=None):
    rows = [r for r in data["entries"] if domain is None or domain in r["domains"]]
    # Domain maps carry only relevant coverage; the master retains every scan boundary.
    coverage = data["coverage"] if domain is None else [c for c in data["coverage"] if any(
        r["path"] == c["path"] or r["path"].startswith(c["path"].rstrip("/") + "/") or c["path"] == "." for r in rows)]
    times = {c["generated_at"] for c in coverage} | {r["scanned_at"] for r in rows}
    metadata = {"schema": 2, "coverage": coverage, "scans": {k: v for k, v in data["scans"].items() if k in times}}
    if "legacy_boundary" in data:
        metadata["legacy_boundary"] = data["legacy_boundary"]
    encoded = json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")
    lines = [MARKER, "# 文件地图", "", META + encoded + " -->",
             "按目录保存最近扫描范围；未重扫条目保留原时间。此索引可重建，不是规则或已确认功能说明。",
             "截断、深度/数据/链接边界以记录为准；旧条目不是本次验证结果。", "",
             "| 路径 | 简要说明 | 领域 | 类型 | 分类依据 | 扫描时间 |", "|---|---|---|---|---|---|"]
    for row in rows:
        values = [row["path"], row["description"], ", ".join(row["domains"]) or "待登记",
                  row["kind"], row["classification_source"], row["scanned_at"]]
        lines.append("| " + " | ".join(map(cell, values)) + " |")
    lines += ["", "扫描覆盖与边界（目录列举完整不代表子树全部扫描；工具配置、依赖与 Recall 文档目录默认排除）："]
    # Show shared options once per scan, while retaining per-directory completeness.
    groups = {}
    for scan in coverage:
        groups.setdefault(scan["generated_at"], []).append(scan)
    for stamp, scan in metadata["scans"].items():
        scans = groups.get(stamp, [])
        lines += [f"- {stamp}：目标 {cell(', '.join(scan['targets']))}；深度 {scan['max_depth']}；预算 {scan['max_entries']}。",
                  "  目录：" + ("；".join(cell(s["path"]) + ("（完整列举）" if s["complete"] else "（截断，保留旧项）") for s in scans) or "旧条目仍保留该次扫描时间与边界")]
        lines += ["  - " + cell(n) for n in scan["notices"]]
    if "legacy_boundary" in data:
        legacy = data["legacy_boundary"]
        lines += [f"- 旧版范围保留：{cell(legacy['scope'])}；{cell(legacy['generated_at'])}；未提供逐目录覆盖，不能推断完整。",
                  "  " + cell(legacy["notices"])]
    return "\n".join(lines) + "\n"
