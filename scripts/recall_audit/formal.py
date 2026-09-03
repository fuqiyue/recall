"""formal-review 专用：完整字段与测试矩阵检查（compliance 模式才需要）。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from .constants import (
    CURRENT_HISTORY_ROOT,
    FORMAL_CHANGE_BLOCK_FIELDS,
    FORMAL_CHANGE_BLOCK_SECTIONS,
    FORMAL_MEANINGFUL_FIELDS,
    FORMAL_TABLE_HEADERS,
    INTENT_STATUSES,
    LAYERS,
    MARKDOWN_LINK_RE,
    TEST_LEVELS,
    VERSION_ID_RE,
    VERSION_SLUG_RE,
)
from .textutil import (
    change_blocks,
    control_values,
    control_values_raw,
    has_meaningful_value,
    is_iso_date,
    markdown_table_headers,
    markdown_table_rows,
    read_text,
)
from .fsclassify import (
    is_test_file,
    iter_directories,
)
from .semantic import (
    ModuleAudit,
)

def audit_formal_review(root: Path, test_inventory: dict, temp_working: dict) -> dict:
    proposal_issues: list[str] = []
    change_text, error = read_text(root / "logic_change.md")
    if error:
        proposal_issues.append(f"unreadable-root-logic_change:{error}")
    else:
        for change_id, block in change_blocks(change_text).items():
            headings = {
                match.group(1).strip()
                for match in re.finditer(r"^\s*###\s+(.+?)\s*$", block, re.MULTILINE)
            }
            for section in sorted(FORMAL_CHANGE_BLOCK_SECTIONS - headings):
                proposal_issues.append(f"{change_id}:missing-formal-section:{section}")
            raw_values = control_values_raw(block)
            normalized_values = control_values(block)
            for field in sorted(FORMAL_CHANGE_BLOCK_FIELDS - set(raw_values)):
                proposal_issues.append(f"{change_id}:missing-formal-field:{field}")
            for field in FORMAL_CHANGE_BLOCK_FIELDS.intersection(raw_values):
                entries = raw_values[field]
                if len(entries) != 1:
                    proposal_issues.append(
                        f"{change_id}:formal-field-must-appear-once:{field}"
                    )
                elif "<" in entries[0] or ">" in entries[0] or entries[0] == "...":
                    proposal_issues.append(
                        f"{change_id}:formal-field-is-placeholder:{field}"
                    )
            for field in sorted(FORMAL_MEANINGFUL_FIELDS):
                entries = raw_values.get(field, [])
                if len(entries) == 1 and not has_meaningful_value(
                    normalized_values, field
                ):
                    proposal_issues.append(
                        f"{change_id}:formal-field-needs-meaningful-evidence:{field}"
                    )

            intent_status_entries = raw_values.get("intent_status", [])
            if len(intent_status_entries) == 1 and (
                intent_status_entries[0].casefold() not in INTENT_STATUSES
            ):
                proposal_issues.append(
                    f"{change_id}:invalid-formal-intent-status:"
                    f"{intent_status_entries[0] or 'empty'}"
                )
            intent_date_entries = raw_values.get("intent_distilled_at", [])
            if len(intent_date_entries) == 1 and not is_iso_date(
                intent_date_entries[0]
            ):
                proposal_issues.append(
                    f"{change_id}:formal-intent-distilled-at-must-be-date"
                )

            decision_gate = (normalized_values.get("decision_gate") or [""])[0]
            if decision_gate == "required":
                for field in (
                    "decision_needed_because",
                    "decision_question",
                    "confirmation_request",
                ):
                    value = (normalized_values.get(field) or [""])[0]
                    if not has_meaningful_value(normalized_values, field) or value == "not-required":
                        proposal_issues.append(
                            f"{change_id}:required-decision-needs-formal-{field}"
                        )

            for field in ("created", "last_status_change"):
                entries = raw_values.get(field, [])
                if len(entries) == 1:
                    try:
                        date.fromisoformat(entries[0])
                    except ValueError:
                        proposal_issues.append(
                            f"{change_id}:formal-field-must-be-date:{field}"
                        )
            for field, allowed_tokens in (
                ("review_due", {"event-driven"}),
                ("target_effective", {"event-driven", "unknown"}),
            ):
                entries = raw_values.get(field, [])
                if len(entries) == 1 and entries[0].casefold() not in allowed_tokens:
                    try:
                        date.fromisoformat(entries[0])
                    except ValueError:
                        proposal_issues.append(
                            f"{change_id}:formal-field-needs-date-or-lifecycle-token:"
                            f"{field}"
                        )

            reserved_version = (raw_values.get("reserved_version_id") or [""])[0]
            version_slug = (raw_values.get("version_slug") or [""])[0]
            has_reserved_version = reserved_version.casefold() != "none"
            has_version_slug = version_slug.casefold() != "none"
            if has_reserved_version and not VERSION_ID_RE.fullmatch(reserved_version):
                proposal_issues.append(
                    f"{change_id}:invalid-reserved-version-id:{reserved_version}"
                )
            if has_version_slug and not VERSION_SLUG_RE.fullmatch(version_slug):
                proposal_issues.append(
                    f"{change_id}:invalid-version-slug:{version_slug}"
                )
            if has_reserved_version != has_version_slug:
                proposal_issues.append(
                    f"{change_id}:reserved-version-id-and-slug-must-be-paired"
                )
            if (
                has_reserved_version
                and has_version_slug
                and VERSION_ID_RE.fullmatch(reserved_version)
                and VERSION_SLUG_RE.fullmatch(version_slug)
            ):
                expected_slug_prefix = reserved_version.casefold().replace(
                    "ver-", "logic_version-", 1
                )
                if not version_slug.casefold().startswith(expected_slug_prefix + "-"):
                    proposal_issues.append(
                        f"{change_id}:reserved-version-id-slug-mismatch"
                    )

            for table_name, expected_headers in FORMAL_TABLE_HEADERS.items():
                headers = markdown_table_headers(block, table_name)
                rows = markdown_table_rows(block, table_name)
                if headers != expected_headers:
                    proposal_issues.append(
                        f"{change_id}:invalid-formal-table-columns:{table_name}"
                    )
                if not rows:
                    proposal_issues.append(
                        f"{change_id}:missing-formal-table:{table_name}"
                    )
                    continue
                for index, row in enumerate(rows, start=1):
                    for header in expected_headers:
                        value = row.get(header, "").strip()
                        if (
                            not value
                            or value.casefold() in {"none", "unknown", "n/a", "..."}
                            or "<" in value
                            or ">" in value
                        ):
                            proposal_issues.append(
                                f"{change_id}:formal-table-{table_name}-row-{index}-"
                                f"missing-{header}"
                            )
                if table_name == "方案与决策":
                    selected_count = 0
                    for index, row in enumerate(rows, start=1):
                        status = row.get("状态", "").strip().casefold()
                        if status not in {"candidate", "selected", "rejected"}:
                            proposal_issues.append(
                                f"{change_id}:formal-option-row-{index}-invalid-status:"
                                f"{status or 'empty'}"
                            )
                        if status == "selected":
                            selected_count += 1
                    if selected_count != 1:
                        proposal_issues.append(
                            f"{change_id}:formal-options-need-exactly-one-selected"
                        )
                    if decision_gate == "required" and len(rows) < 3:
                        proposal_issues.append(
                            f"{change_id}:required-decision-needs-three-options"
                        )
                if table_name == "消费者与影响":
                    for index, row in enumerate(rows, start=1):
                        layer = row.get("artifact_layer", "").strip().casefold()
                        if layer not in LAYERS:
                            proposal_issues.append(
                                f"{change_id}:formal-impact-row-{index}-invalid-layer:"
                                f"{layer or 'empty'}"
                            )

    return {
        "proposal_issues": sorted(set(proposal_issues)),
        "test_matrix_issues": list(test_inventory.get("matrix_issues", [])),
        "temp_reference_issues": sorted(
            set(temp_working.get("change_temp_link_issues", []))
        ),
    }


def audit_test_inventory(
    root: Path,
    audits: list[ModuleAudit],
    max_depth: int | None,
    excludes: set[str],
    *,
    include_history: bool = True,
) -> dict:
    test_files: list[str] = []
    configs: list[str] = []
    categories: set[str] = set()
    config_names = {
        "package.json",
        "pyproject.toml",
        "pytest.ini",
        "tox.ini",
        "vitest.config.js",
        "vitest.config.ts",
        "jest.config.js",
        "jest.config.ts",
        "playwright.config.js",
        "playwright.config.ts",
        "cypress.config.js",
        "cypress.config.ts",
    }
    for _, files in iter_directories(root, max_depth, excludes):
        for path in files:
            name = path.name
            relative = path.relative_to(root).as_posix()
            if name.lower() in config_names:
                configs.append(relative)
            if not is_test_file(path, root):
                continue
            test_files.append(relative)
            lowered = relative.lower()
            matched_category = False
            if any(token in lowered for token in ("e2e", "playwright", "cypress")):
                categories.add("e2e")
                matched_category = True
            if any(
                token in lowered for token in ("frontend", "ui", "component", "browser")
            ):
                categories.add("frontend")
                matched_category = True
            if any(token in lowered for token in ("backend", "api", "server")):
                categories.add("backend/api")
                matched_category = True
            if any(
                token in lowered for token in ("migration", "schema", "database", "db")
            ):
                categories.add("migration/data")
                matched_category = True
            if not matched_category:
                categories.add("unit/unspecified")

    matrix_issues: list[str] = []
    placeholder_values = {"", "...", "none", "unknown", "n/a", "tbd", "pending"}
    result_tokens = {"pass", "fail", "not-run", "not-applicable"}

    def missing_value(value: str) -> bool:
        normalized = value.strip().casefold()
        return (
            normalized in placeholder_values or "<" in normalized or ">" in normalized
        )

    def result_token(value: str) -> str:
        return value.strip().casefold().split(":", 1)[0]

    def has_reason(value: str) -> bool:
        return ":" in value and bool(value.split(":", 1)[1].strip())

    def has_evidence_locator(value: str) -> bool:
        if MARKDOWN_LINK_RE.search(value):
            return True
        for marker in (
            "command:",
            "ci:",
            "log:",
            "path:",
            "issue:",
            "risk:",
            "risk-accepted:",
            "decision-ref:",
            "not-run:",
        ):
            match = re.search(
                rf"{re.escape(marker)}\s*([^;|]+)", value, re.IGNORECASE
            )
            if match and not missing_value(match.group(1)):
                return True
        return False

    def has_reviewer_and_date(value: str) -> bool:
        date_candidates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", value)
        has_valid_date = False
        for candidate in date_candidates:
            try:
                date.fromisoformat(candidate)
            except ValueError:
                continue
            has_valid_date = True
            break
        reviewer = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", value).strip(
            " +,;|/"
        )
        return has_valid_date and not missing_value(reviewer)

    def has_risk_waiver(evidence: str) -> bool:
        def marker_value(marker: str) -> str:
            match = re.search(
                rf"{re.escape(marker)}\s*([^;|]+)",
                evidence,
                re.IGNORECASE,
            )
            return match.group(1).strip() if match else ""

        risk = marker_value("risk-accepted:")
        decision_ref = marker_value("decision-ref:")
        owner = marker_value("compensation-owner:")
        due = marker_value("due:")
        if any(missing_value(value) for value in (risk, decision_ref, owner, due)):
            return False
        try:
            return date.fromisoformat(due) >= date.today()
        except ValueError:
            return False

    change_required_fields = (
        "test_level",
        "case",
        "target/command",
        "baseline",
        "expected",
        "post-change",
        "evidence",
        "reviewer/date",
    )
    for audit in audits:
        if not audit.logic_change:
            continue
        directory = root if audit.path == "." else root / audit.path
        change = directory / "logic_change.md"
        text_value, error = read_text(change)
        if error:
            continue
        for change_id, block in change_blocks(text_value).items():
            rows = markdown_table_rows(block, "测试案例与审核矩阵")
            label = f"{audit.path}:{change_id}"
            if not rows:
                matrix_issues.append(f"{label}:missing-test-review-matrix")
                continue
            status = (control_values(block).get("status") or ["draft"])[0]
            for index, row in enumerate(rows, start=1):
                for field in change_required_fields:
                    if missing_value(row.get(field, "")):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-missing-{field}"
                        )
                baseline = row.get("baseline", "")
                post_change = row.get("post-change", "")
                evidence = row.get("evidence", "")
                reviewer = row.get("reviewer/date", "")
                test_level = row.get("test_level", "").strip().casefold()
                if test_level not in TEST_LEVELS:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-test-level:{test_level or 'empty'}"
                    )
                for field, value in (
                    ("baseline", baseline),
                    ("post-change", post_change),
                ):
                    token = result_token(value)
                    if token not in result_tokens:
                        matrix_issues.append(
                            f"{label}:test-row-{index}-invalid-{field}:{token or 'empty'}"
                        )
                    elif token in {"not-run", "not-applicable"} and not has_reason(
                        value
                    ):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-{field}-needs-reason"
                        )
                if not missing_value(evidence) and not has_evidence_locator(evidence):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-evidence-needs-locator"
                    )
                if not missing_value(reviewer) and not has_reviewer_and_date(reviewer):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-reviewer-needs-date"
                    )
                if (
                    status in {"implementing", "verifying"}
                    and result_token(baseline) == "not-run"
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-baseline-required-for-{status}"
                    )
                if (
                    status == "verifying"
                    and result_token(post_change) == "not-run"
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-post-change-required-for-verifying"
                    )
                if result_token(post_change) == "fail":
                    matrix_issues.append(
                        f"{label}:test-row-{index}-post-change-failed"
                    )

    records_root = root / CURRENT_HISTORY_ROOT / "records"
    if include_history and records_root.is_dir():
        for record in sorted(records_root.glob("logic_version-*.md")):
            record_text, record_error = read_text(record)
            if record_error:
                continue
            rows = markdown_table_rows(record_text, "测试与审核")
            label = record.relative_to(root).as_posix()
            if not rows:
                matrix_issues.append(f"{label}:missing-version-test-review-matrix")
                continue
            status = (control_values(record_text).get("status") or [""])[0]
            required = (
                "test_level",
                "case/command",
                "baseline",
                "post-change",
                "result",
                "evidence",
                "reviewer/date",
            )
            for index, row in enumerate(rows, start=1):
                for field in required:
                    if missing_value(row.get(field, "")):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-missing-{field}"
                        )
                evidence = row.get("evidence", "")
                reviewer = row.get("reviewer/date", "")
                result = row.get("result", "")
                test_level = row.get("test_level", "").strip().casefold()
                if test_level not in TEST_LEVELS:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-test-level:{test_level or 'empty'}"
                    )
                for field in ("baseline", "post-change"):
                    value = row.get(field, "")
                    field_token = result_token(value)
                    if field_token not in result_tokens:
                        matrix_issues.append(
                            f"{label}:test-row-{index}-invalid-{field}:{field_token or 'empty'}"
                        )
                    elif field_token in {
                        "not-run",
                        "not-applicable",
                    } and not has_reason(value):
                        matrix_issues.append(
                            f"{label}:test-row-{index}-{field}-needs-reason"
                        )
                token = result_token(result)
                if token not in result_tokens:
                    matrix_issues.append(
                        f"{label}:test-row-{index}-invalid-result:{token or 'empty'}"
                    )
                elif token in {"not-run", "not-applicable"} and not has_reason(result):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-result-needs-reason"
                    )
                if not missing_value(evidence) and not has_evidence_locator(evidence):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-evidence-needs-locator"
                    )
                if not missing_value(reviewer) and not has_reviewer_and_date(reviewer):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-reviewer-needs-date"
                    )
                if (
                    status in {"effective", "rolled-back", "correction"}
                    and token
                    not in {
                        "pass",
                        "not-applicable",
                    }
                    and not has_risk_waiver(evidence)
                ):
                    matrix_issues.append(
                        f"{label}:test-row-{index}-completed-version-needs-pass-or-waiver"
                    )
    return {
        "test_files": sorted(test_files),
        "configs": sorted(configs),
        "categories": sorted(categories),
        "matrix_issues": sorted(set(matrix_issues)),
        "limitation": "Discovery proves only that files/configs exist, not that tests ran or passed.",
    }
