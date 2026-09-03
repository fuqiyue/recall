"""汇总各层结果、文本渲染与严格模式判定。

本模块由 audit_logic_map.py 按层拆出（VER-20260903-002）；入口 facade 重新导出全部公开名字，命令行与测试访问路径不变。
"""
from __future__ import annotations

import argparse
import re
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
from .constants import (
    DEFAULT_EXCLUDES,
)
from .textutil import (
    control_values,
    control_values_raw,
    is_scope_ancestor,
    normalize_change_id,
    normalize_scope_path,
    read_text,
    scope_parts,
)
from .fsclassify import (
    is_runtime_data_file,
    is_source_file,
    is_test_file,
    iter_directories,
    looks_like_runtime_data_directory,
)
from .semantic import (
    ModuleAudit,
    audit_module,
)
from .integrity import (
    active_change_ids,
    audit_current_state_integrity,
    audit_module_routes,
    audit_proposal_integrity,
)
from .formal import (
    audit_formal_review,
    audit_test_inventory,
)
from .archive import (
    audit_agent_entrypoints,
    audit_archive,
    audit_density,
    audit_root_doc_coverage,
    audit_temp_working,
    find_misplaced_records,
    find_misplaced_temp_records,
    find_nonroot_current_documents,
    find_parallel_current_candidates,
    find_scattered_backup_candidates,
    registered_child_document_paths,
    registered_child_readme_paths,
    registered_domain_scopes,
    unscanned_archive_report,
)

def collect_audit(args: argparse.Namespace) -> dict:
    root = args.project_root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    if args.max_depth is not None and args.max_depth < 0:
        raise ValueError("--max-depth must be zero or greater")
    if args.strict_v2 and args.max_depth is not None:
        raise ValueError(
            "--strict-v2 requires an unlimited scan; omit --max-depth and use "
            "--exclude for known dependency or generated trees"
        )
    selected_profiles = sum(
        bool(value)
        for value in (args.current_state, args.formal_review, args.strict_v2)
    )
    if selected_profiles > 1:
        raise ValueError(
            "--current-state, --formal-review, and --strict-v2 are mutually exclusive"
        )
    if args.current_state and args.require_test_matrix:
        raise ValueError(
            "--current-state does not inspect historical test matrices; run a "
            "--formal-review instead of combining it with --require-test-matrix"
        )

    current_profile = args.current_state or args.formal_review
    if current_profile and args.max_depth is not None:
        raise ValueError(
            "current/formal root-only audits require an unlimited scan; omit --max-depth"
        )

    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    audits: list[ModuleAudit] = []
    skipped_dirs = 0
    nested_project_roots: list[str] = []

    for directory, files in iter_directories(
        root, args.max_depth, excludes, nested_project_roots
    ):
        is_root = directory == root
        has_source = any(is_source_file(file) for file in files)
        has_runtime_data = any(
            is_runtime_data_file(file) for file in files
        ) or looks_like_runtime_data_directory(directory, root)
        has_test = any(is_test_file(file, root) for file in files)
        has_docs = (directory / "logic_readme.md").exists() or (
            directory / "logic_change.md"
        ).exists()
        if (
            args.all_dirs
            or is_root
            or has_source
            or has_runtime_data
            or has_test
            or has_docs
        ):
            audits.append(audit_module(directory, files, root))
        else:
            skipped_dirs += 1

    missing_map_candidates = [
        audit.path
        for audit in audits
        if audit.has_source_files and not audit.logic_readme
    ]
    runtime_data_candidates = [
        audit.path
        for audit in audits
        if audit.has_runtime_data and not audit.logic_readme
    ]
    malformed_maps = [
        audit.path
        for audit in audits
        if (
            (
                audit.logic_readme
                and (audit.missing_readme_sections or audit.missing_readme_fields)
            )
            or (
                audit.logic_change
                and (audit.missing_change_sections or audit.missing_change_fields)
            )
            or audit.semantic_issues
            or audit.change_without_readme
        )
    ]

    archive = unscanned_archive_report() if current_profile else audit_archive(root)
    proposal_integrity = (
        {
            "duplicate_ids": [],
            "missing_root_index": [],
            "unknown_root_index": [],
            "route_issues": [],
            "cross_module_link_issues": [],
            "authority_registry_issues": [],
            "authority_issues": [],
            "closed_change_ids_still_active": [],
        }
        if current_profile
        else audit_proposal_integrity(root, audits)
    )
    closed_change_records: dict[str, list[str]] = {}
    if not current_profile:
        for relative_record in archive["version_records"]:
            record_path = root / relative_record
            record_text, record_error = read_text(record_path)
            if record_error:
                continue
            record_values = control_values_raw(record_text)
            for raw_change_id in record_values.get("change_id", []):
                change_id = normalize_change_id(raw_change_id)
                if change_id:
                    closed_change_records.setdefault(change_id, []).append(
                        relative_record
                    )
        still_active = active_change_ids(root, audits).intersection(
            closed_change_records
        )
        proposal_integrity["closed_change_ids_still_active"] = sorted(
            f"{change_id}:{','.join(sorted(closed_change_records[change_id]))}"
            for change_id in still_active
        )
    module_routes = audit_module_routes(root, audits)
    registered_inherited_scopes = {
        normalize_scope_path(row.get("scope_path", ""))
        for row in module_routes["rows"]
        if row.get("doc_policy", "").strip().lower() == "inherited"
    }

    root_policy_text, _ = read_text(root / "logic_readme.md")
    root_policy_values = control_values(root_policy_text)
    registry_every_folder = "registry-every-folder" in root_policy_values.get(
        "coverage_policy", []
    )
    if registry_every_folder and not args.all_dirs:
        module_routes["route_issues"] = sorted(
            set(module_routes["route_issues"])
            | {"registry-every-folder-policy-requires---all-dirs"}
        )
    if registry_every_folder and args.all_dirs:
        registered_scopes = {
            normalize_scope_path(row.get("scope_path", ""))
            for row in module_routes["rows"]
            if row.get("scope_path", "").strip()
        }
        module_routes["route_issues"] = sorted(
            set(module_routes["route_issues"])
            | {
                f"registry-every-folder-unregistered:{audit.path}"
                for audit in audits
                if audit.path != "." and audit.path not in registered_scopes
            }
        )

    def covered_without_local_doc(scope: str) -> bool:
        if any(
            inherited == scope or is_scope_ancestor(inherited, scope)
            for inherited in registered_inherited_scopes
        ):
            return True
        candidates = [
            audit
            for audit in audits
            if audit.logic_readme
            and audit.path != "."
            and is_scope_ancestor(audit.path, scope)
        ]
        if not candidates:
            return False
        owner = max(candidates, key=lambda audit: len(scope_parts(audit.path)))
        owner_text, owner_error = read_text(root / owner.path / "logic_readme.md")
        if owner_error:
            return False
        raw_values = control_values_raw(owner_text)
        policy_values = control_values(owner_text)
        child_policy = (policy_values.get("child_policy") or [""])[0]
        if child_policy not in {"inherit", "review-before-split"}:
            return False
        patterns = {
            item.strip()
            for value in raw_values.get("owned_paths", [])
            for item in re.split(r"[,;，；]", value)
            if item.strip()
        }
        return any(
            scope == normalize_scope_path(pattern)
            or is_scope_ancestor(normalize_scope_path(pattern), scope)
            or fnmatchcase(scope, normalize_scope_path(pattern))
            for pattern in patterns
        )

    missing_map_candidates = [
        scope
        for scope in missing_map_candidates
        if not covered_without_local_doc(scope)
    ]
    runtime_data_candidates = [
        scope
        for scope in runtime_data_candidates
        if not covered_without_local_doc(scope)
    ]
    temp_working = audit_temp_working(root, audits)
    test_inventory = audit_test_inventory(
        root,
        audits,
        args.max_depth,
        excludes,
        include_history=not current_profile,
    )
    if args.current_state:
        test_inventory["matrix_issues"] = []
    if current_profile:
        misplaced_versions, misplaced_decisions = [], []
    else:
        misplaced_versions, misplaced_decisions = find_misplaced_records(root, excludes)
    parallel_current = find_parallel_current_candidates(root, excludes)
    nonroot_current_documents = find_nonroot_current_documents(
        root, excludes, registered_child_document_paths(root)
    )
    misplaced_temp = find_misplaced_temp_records(root, excludes)
    entrypoints, private_knowledge, private_candidates = audit_agent_entrypoints(root)
    required_entry_names: set[str] = set()
    if args.require_agent_entry in {"codex", "both"}:
        required_entry_names.add("AGENTS.md")
    if args.require_agent_entry in {"claude", "both"}:
        required_entry_names.add("CLAUDE.md")
    missing_required_entries = sorted(
        entry["path"]
        for entry in entrypoints
        if entry["path"] in required_entry_names and not entry["exists"]
    )
    missing_default_agent_entry = current_profile and not any(
        entry["exists"] for entry in entrypoints
    )
    scattered_backups = (
        [] if current_profile else find_scattered_backup_candidates(root)
    )
    current_integrity = audit_current_state_integrity(
        root, audits, module_routes, all_dirs=args.all_dirs
    )
    density = audit_density(root, audits)
    root_doc_coverage = audit_root_doc_coverage(root)
    formal_review = (
        audit_formal_review(root, test_inventory, temp_working)
        if args.formal_review
        else {
            "proposal_issues": [],
            "test_matrix_issues": [],
            "temp_reference_issues": [],
        }
    )

    limitations = [
        "A directory candidate is not automatically a meaningful governance boundary.",
        "The audit does not prove dependency, consumer, deployment, or runtime coverage.",
        "Backup-like directory names are advisory candidates, not confirmed violations.",
        "A missing AGENTS.md/.agents or CLAUDE.md/.claude pair fails only when --require-agent-entry selects it; an invalid existing entrypoint always fails strict mode.",
        "Agent read-order validation is a textual pointer check, not proof of agent runtime behavior.",
        "Private-directory content candidates are heuristic; inspect them before classifying as business truth.",
        "Missing maps are prompts for review, not automatic file-creation instructions.",
        "Runtime-data candidates require classification; they are not automatically code modules.",
        "Test discovery does not prove that any test ran or passed.",
        "Zero discovered test files is not by itself a failure; active and closed changes must still carry status-appropriate matrix evidence or an allowed not-applicable reason.",
    ]
    if current_profile:
        limitations = [
            "This root-only profile checks current-document structure, scope routes, active CHG lifecycle and declared coordination metadata, and agent entrypoints.",
            "It does not prove code semantics, undeclared dependencies, consumers, deployment, runtime behavior, or that discovered tests passed.",
            "History format and completed-version evidence do not determine this profile's result.",
        ]
        if args.formal_review:
            limitations.append(
                "Formal-review validates evidence containers and current test matrices; Codex, Claude, or a human must still inspect the affected code and runtime evidence."
            )

    reported_modules = [asdict(audit) for audit in audits]
    if current_profile:
        for module in reported_modules:
            module["missing_readme_sections"] = []
            module["missing_readme_fields"] = []
            module["missing_change_sections"] = []
            module["missing_change_fields"] = []
            module["v2_issues"] = []
            module["module_binding_issues"] = []

    current_gate_failed = current_profile and (
        any(current_integrity.values())
        or bool(nonroot_current_documents)
        or bool(parallel_current)
        or bool(root_doc_coverage["unregistered"])
        or any(entry["exists"] and entry["issues"] for entry in entrypoints)
        or bool(private_knowledge)
        or bool(missing_required_entries)
        or bool(missing_default_agent_entry)
        or (args.formal_review and any(formal_review.values()))
    )

    return {
        "project_root": str(root),
        "candidate_policy": (
            "all directories"
            if args.all_dirs
            else "root, source/runtime-data/test, or documented directories"
        ),
        "max_depth": args.max_depth,
        "profile": (
            "current-state"
            if args.current_state
            else "formal-review"
            if args.formal_review
            else "v2"
            if args.strict_v2
            else "base"
        ),
        "excluded_names": sorted(excludes),
        "summary": {
            "candidate_directories": len(audits),
            "skipped_directories": skipped_dirs,
            "logic_readmes": sum(audit.logic_readme for audit in audits),
            "logic_changes": sum(audit.logic_change for audit in audits),
            "version_records": len(archive["version_records"]),
            "decision_records": len(archive["decision_records"]),
            "missing_map_candidates": len(missing_map_candidates),
            "runtime_data_candidates": len(runtime_data_candidates),
            "malformed_current_docs": (
                int(bool(current_integrity["document_issues"]))
                if current_profile
                else len(malformed_maps)
            ),
            "v2_document_gaps": (
                0
                if current_profile
                else sum(len(audit.v2_issues) for audit in audits)
            ),
            "module_binding_issues": (
                0
                if current_profile
                else sum(len(audit.module_binding_issues) for audit in audits)
            ),
            "module_route_issues": (
                len(module_routes["route_issues"])
                + len(module_routes["duplicate_module_ids"])
                + len(module_routes["duplicate_scope_paths"])
                + len(module_routes["unregistered_governance_dirs"])
                + len(module_routes["hierarchy_issues"])
            ),
            "logic_temp_records": len(temp_working["records"]),
            "logic_temp_issues": (
                len(temp_working["malformed"])
                + len(temp_working["missing_logic_temp"])
                + len(temp_working["orphan_change_ids"])
                + len(temp_working["expired"])
                + len(temp_working["forbidden_files"])
                + len(temp_working["unindexed"])
                + len(temp_working["extra_entries"])
                + len(temp_working["stale_index_entries"])
                + len(temp_working["change_temp_link_issues"])
            ),
            "test_files": len(test_inventory["test_files"]),
            "test_matrix_issues": len(test_inventory["matrix_issues"]),
            "broken_links": (
                sum(len(audit.broken_links) for audit in audits)
                + len(archive["broken_links"])
            ),
            "misplaced_history": len(misplaced_versions) + len(misplaced_decisions),
            "agent_entrypoint_issues": sum(
                len(entry["issues"]) for entry in entrypoints if entry["exists"]
            ),
            "missing_required_agent_entries": len(missing_required_entries),
            "missing_default_agent_entry": int(missing_default_agent_entry),
            "current_integrity_issues": sum(
                len(current_integrity[key])
                for key in (
                    "document_issues",
                    "scope_registry_issues",
                    "proposal_issues",
                    "responsibility_issues",
                )
            ),
            "formal_review_issues": sum(
                len(formal_review[key])
                for key in (
                    "proposal_issues",
                    "test_matrix_issues",
                    "temp_reference_issues",
                )
            ),
            "density_issues": len(density["issues"]),
            "private_agent_knowledge_files": len(private_knowledge),
            "private_agent_knowledge_candidates": len(private_candidates),
            "duplicate_change_ids": len(proposal_integrity["duplicate_ids"]),
            "unindexed_module_changes": len(proposal_integrity["missing_root_index"]),
            "unknown_root_change_ids": len(proposal_integrity["unknown_root_index"]),
            "closed_changes_still_active": len(
                proposal_integrity["closed_change_ids_still_active"]
            ),
            "parallel_current_candidates": len(parallel_current),
            "nonroot_current_documents": len(nonroot_current_documents),
            "misplaced_logic_temp": len(misplaced_temp),
        },
        "missing_map_candidates": missing_map_candidates,
        "runtime_data_candidates": runtime_data_candidates,
        "modules": reported_modules,
        "archive": archive,
        "module_routes": module_routes,
        "logic_temp": temp_working,
        "test_inventory": test_inventory,
        "misplaced_version_records": misplaced_versions,
        "misplaced_decision_records": misplaced_decisions,
        "parallel_current_candidates": parallel_current,
        "current_state_nonroot_documents": nonroot_current_documents,
        "root_doc_coverage": root_doc_coverage,
        "misplaced_logic_temp": misplaced_temp,
        "scattered_backup_candidates": scattered_backups,
        "agent_entrypoints": entrypoints,
        "required_agent_entry": args.require_agent_entry,
        "missing_required_agent_entries": missing_required_entries,
        "missing_default_agent_entry": missing_default_agent_entry,
        "private_agent_knowledge_files": private_knowledge,
        "private_agent_knowledge_candidates": private_candidates,
        "proposal_integrity": proposal_integrity,
        "current_integrity": current_integrity,
        "density": density,
        "formal_review": formal_review,
        "static_gate": {
            "performed": current_profile,
            "passed": (not current_gate_failed) if current_profile else None,
            "scope": (
                "current-logic-map-and-formal-evidence-containers"
                if args.formal_review
                else "current-logic-map"
                if args.current_state
                else "not-requested"
            ),
            "meaning": (
                "Static document gate only; this is not a code-semantic review result."
                if current_profile
                else "No current/formal static gate was requested."
            ),
        },
        "semantic_review": {
            "performed": False,
            "status": "not-performed",
            "required_for_complete_review": current_profile,
            "scope": (
                "static-logic-map-and-evidence-container-checks"
                if current_profile
                else "not-requested"
            ),
            "next_step": (
                "Inspect affected code, callers, schema, tests, test results, and "
                "runtime evidence with Codex, Claude, or a human reviewer."
                if current_profile
                else "none"
            ),
        },
        "limitations": limitations,
    }


def print_text(report: dict) -> None:
    summary = report["summary"]
    lightweight_current = report["profile"] == "current-state"
    formal_review_profile = report["profile"] == "formal-review"
    current_profile = lightweight_current or formal_review_profile
    depth_label = (
        "unlimited" if report["max_depth"] is None else str(report["max_depth"])
    )
    print(f"Project: {report['project_root']}")
    print(
        f"Policy: {report['candidate_policy']}; max depth: {depth_label}; "
        f"profile: {report['profile']}"
    )
    if current_profile:
        print(
            "Summary: "
            f"{summary['candidate_directories']} scanned directories, "
            f"{summary['logic_readmes']} current policies, "
            f"{summary['logic_changes']} active-change files, "
            f"{summary['current_integrity_issues']} current-integrity issues, "
            f"{summary['formal_review_issues']} formal-review issues"
        )
        print(
            "Static gate: "
            + ("PASS" if report["static_gate"]["passed"] else "FAIL")
        )
        print(
            "Semantic review: NOT PERFORMED; inspect affected code, callers, "
            "schema, tests, results, and runtime evidence separately."
        )
    else:
        print(
            "Summary: "
            f"{summary['candidate_directories']} candidates, "
            f"{summary['logic_readmes']} current policies, "
            f"{summary['logic_changes']} active-change files, "
            f"{summary['version_records']} version records, "
            f"{summary['logic_temp_records']} working temp records, "
            f"{summary['malformed_current_docs']} malformed current documents, "
            f"{summary['broken_links']} broken links, "
            f"{summary['misplaced_history']} misplaced history records"
        )

    root_module = next(
        (module for module in report["modules"] if module["path"] == "."), None
    )
    missing_root_entries: list[str] = []
    if root_module is None or not root_module["logic_readme"]:
        missing_root_entries.append("logic_readme.md")
    if root_module is None or not root_module["logic_change"]:
        missing_root_entries.append("logic_change.md")
    if missing_root_entries:
        print("\nMissing root entries:")
        for name in missing_root_entries:
            print(f"  - {name}")

    if report["current_state_nonroot_documents"]:
        print("\nNon-root current documents:")
        for path in report["current_state_nonroot_documents"]:
            print(f"  - {path}")

    if report["root_doc_coverage"]["unregistered"]:
        print(
            "\nUnregistered top-level Markdown entries"
            " (add to owned_paths or unmapped_paths, or archive):"
        )
        for name in report["root_doc_coverage"]["unregistered"]:
            print(f"  - {name}")

    if not current_profile and report["missing_map_candidates"]:
        print("\nMissing-map candidates (review boundaries before creating files):")
        for path in report["missing_map_candidates"]:
            print(f"  - {path}")

    if not current_profile and report["runtime_data_candidates"]:
        print("\nRuntime-data candidates (classify; do not assume code module):")
        for path in report["runtime_data_candidates"]:
            print(f"  - {path}")

    problems = [
        module
        for module in report["modules"]
        if (
            module["missing_readme_sections"]
            or module["missing_readme_fields"]
            or module["missing_change_sections"]
            or module["missing_change_fields"]
            or module["semantic_issues"]
            or module["change_without_readme"]
            or module["broken_links"]
        )
    ]
    if problems and not current_profile:
        print("\nCurrent-document problems:")
        for module in problems:
            print(f"  - {module['path']}")
            if module["change_without_readme"]:
                print("    logic_change exists without logic_readme")
            if module["missing_readme_sections"]:
                print(
                    "    logic_readme missing sections: "
                    + ", ".join(module["missing_readme_sections"])
                )
            if module["missing_readme_fields"]:
                print(
                    "    logic_readme missing fields: "
                    + ", ".join(module["missing_readme_fields"])
                )
            if module["missing_change_sections"]:
                print(
                    "    logic_change missing sections: "
                    + ", ".join(module["missing_change_sections"])
                )
            if module["missing_change_fields"]:
                print(
                    "    logic_change missing fields: "
                    + ", ".join(module["missing_change_fields"])
                )
            if module["semantic_issues"]:
                print("    semantic issues: " + ", ".join(module["semantic_issues"]))
            if module["broken_links"]:
                print("    broken links: " + ", ".join(module["broken_links"]))

    v2_modules = [
        module
        for module in report["modules"]
        if module["v2_issues"] or module["module_binding_issues"]
    ]
    if v2_modules and not current_profile:
        print("\nRecall v2 document/binding gaps:")
        for module in v2_modules:
            print(f"  - {module['path']}")
            if module["v2_issues"]:
                print("    v2 fields/sections: " + ", ".join(module["v2_issues"]))
            if module["module_binding_issues"]:
                print("    binding: " + ", ".join(module["module_binding_issues"]))

    routes = report["module_routes"]
    route_problem_lists = (
        routes["route_issues"],
        routes["duplicate_module_ids"],
        routes["duplicate_scope_paths"],
        routes["unregistered_governance_dirs"],
        routes["hierarchy_issues"],
    )
    if not current_profile and any(route_problem_lists):
        print("\nModule-route problems:")
        for key in (
            "route_issues",
            "duplicate_module_ids",
            "duplicate_scope_paths",
            "unregistered_governance_dirs",
            "hierarchy_issues",
        ):
            for item in routes[key]:
                print(f"  - {key}: {item}")

    current_integrity = report["current_integrity"]
    if current_profile and any(current_integrity.values()):
        print("\nCurrent-state integrity problems:")
        for key in (
            "document_issues",
            "scope_registry_issues",
            "proposal_issues",
            "responsibility_issues",
        ):
            for item in current_integrity[key]:
                print(f"  - {key}: {item}")

    formal_review = report["formal_review"]
    if formal_review_profile and any(formal_review.values()):
        print("\nFormal-review evidence problems:")
        for key in (
            "proposal_issues",
            "test_matrix_issues",
            "temp_reference_issues",
        ):
            for item in formal_review[key]:
                print(f"  - {key}: {item}")

    archive = report["archive"]
    proposal_integrity = report["proposal_integrity"]
    if not current_profile and (
        proposal_integrity["duplicate_ids"]
        or proposal_integrity["missing_root_index"]
        or proposal_integrity["unknown_root_index"]
        or proposal_integrity["route_issues"]
        or proposal_integrity["cross_module_link_issues"]
        or proposal_integrity["authority_registry_issues"]
        or proposal_integrity["authority_issues"]
        or proposal_integrity["closed_change_ids_still_active"]
    ):
        print("\nActive-proposal problems:")
        for item in proposal_integrity["duplicate_ids"]:
            print(f"  - duplicate CHG-ID: {item}")
        for item in proposal_integrity["missing_root_index"]:
            print(f"  - module proposal missing from root index: {item}")
        for item in proposal_integrity["unknown_root_index"]:
            print(f"  - root index references unknown CHG-ID: {item}")
        for item in proposal_integrity["route_issues"]:
            print(f"  - proposal route: {item}")
        for item in proposal_integrity["cross_module_link_issues"]:
            print(f"  - cross-module link: {item}")
        for item in proposal_integrity["authority_registry_issues"]:
            print(f"  - decision-authority registry: {item}")
        for item in proposal_integrity["authority_issues"]:
            print(f"  - decision-authority: {item}")
        for item in proposal_integrity["closed_change_ids_still_active"]:
            print(f"  - closed change still active: {item}")

    archive_issues = (
        archive["malformed_versions"]
        or archive["malformed_decisions"]
        or archive["backups_missing_manifest"]
        or archive["malformed_backups"]
        or archive["broken_links"]
        or archive["index"] not in {"ok", "not-needed"}
        or archive["index_consistency"]["unindexed_records"]
        or archive["index_consistency"]["duplicate_ids"]
        or archive["index_consistency"]["row_mismatches"]
        or archive["index_consistency"]["unknown_record_links"]
        or report["misplaced_version_records"]
        or report["misplaced_decision_records"]
        or archive["duplicate_history_roots"]
        or archive["extra_paths"]
        or archive["forbidden_current_docs"]
        or archive["legacy_records"]
    )
    if archive_issues and not current_profile:
        print("\nLogic-version/history problems:")
        if archive["duplicate_history_roots"]:
            print("  - both logic_version and legacy logic_archive exist")
        for path in archive["legacy_records"]:
            print(f"  - legacy history record requires review/migration: {path}")
        for path in archive["extra_paths"]:
            print(f"  - unexpected logic_version path: {path}")
        for path in archive["forbidden_current_docs"]:
            print(f"  - current truth stored under logic_version: {path}")
        if archive["index"] not in {"ok", "not-needed"}:
            print(f"  - index: {archive['index']}")
        for item in archive["malformed_versions"]:
            print(f"  - malformed version: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for item in archive["malformed_decisions"]:
            print(f"  - malformed decision: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for path in archive["backups_missing_manifest"]:
            print(f"  - backup missing manifest: {path}")
        for item in archive["malformed_backups"]:
            print(f"  - malformed backup manifest: {item['path']}")
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for path in report["misplaced_version_records"]:
            print(f"  - misplaced version: {path}")
        for path in report["misplaced_decision_records"]:
            print(f"  - misplaced decision: {path}")
        for item in archive["broken_links"]:
            print(f"  - broken logic_version link: {item}")
        for path in archive["index_consistency"]["unindexed_records"]:
            print(f"  - logic_version record not indexed: {path}")
        for item in archive["index_consistency"]["duplicate_ids"]:
            print(f"  - duplicate logic_version id: {item}")
        for item in archive["index_consistency"]["row_mismatches"]:
            print(f"  - logic_version index row mismatch: {item}")
        for path in archive["index_consistency"]["unknown_record_links"]:
            print(f"  - unknown logic_version record link: {path}")

    temp = report["logic_temp"]
    if not current_profile and summary["logic_temp_issues"]:
        print("\nLogic-temp problems:")
        for item in temp["malformed"]:
            print(f"  - malformed: {item['path']}")
            if item.get("missing_sections"):
                print("    missing sections: " + ", ".join(item["missing_sections"]))
            if item.get("missing_fields"):
                print("    missing fields: " + ", ".join(item["missing_fields"]))
            if item.get("semantic_issues"):
                print("    semantic issues: " + ", ".join(item["semantic_issues"]))
        for key in (
            "missing_logic_temp",
            "orphan_change_ids",
            "expired",
            "forbidden_files",
            "unindexed",
            "extra_entries",
            "stale_index_entries",
            "change_temp_link_issues",
        ):
            for item in temp[key]:
                print(f"  - {key}: {item}")

    if report["parallel_current_candidates"]:
        print("\nParallel current-truth candidates:")
        for path in report["parallel_current_candidates"]:
            print(f"  - {path}")

    if not current_profile and report["misplaced_logic_temp"]:
        print("\nMisplaced logic_temp records:")
        for path in report["misplaced_logic_temp"]:
            print(f"  - {path}")

    if not current_profile and report["test_inventory"]["matrix_issues"]:
        print("\nTest-matrix findings:")
        for item in report["test_inventory"]["matrix_issues"]:
            print(f"  - {item}")

    entry_issues = [
        entry
        for entry in report["agent_entrypoints"]
        if entry["exists"] and entry["issues"]
    ]
    if entry_issues or report["private_agent_knowledge_files"]:
        print("\nAgent-entry problems:")
        for entry in entry_issues:
            print(f"  - {entry['path']}: {', '.join(entry['issues'])}")
        for path in report["private_agent_knowledge_files"]:
            print(f"  - business knowledge stored in agent-private path: {path}")
    if report["missing_required_agent_entries"]:
        print("\nMissing required agent entries:")
        for path in report["missing_required_agent_entries"]:
            print(f"  - {path}")
    if report["missing_default_agent_entry"]:
        print("\nMissing agent entry:")
        print(
            "  - current/formal profiles require at least one root AGENTS.md or "
            "CLAUDE.md with its matching .agents/ or .claude/ directory"
        )
    if report["private_agent_knowledge_candidates"]:
        print("\nAgent-private knowledge candidates (review):")
        for path in report["private_agent_knowledge_candidates"]:
            print(f"  - {path}")

    if report["scattered_backup_candidates"]:
        print("\nBackup-like directories to review (advisory):")
        for path in report["scattered_backup_candidates"]:
            print(f"  - {path}")

    density = report.get("density") or {}
    if density.get("issues") or density.get("notices"):
        print("\nDensity (advisory; limits in references/field-vocabulary.md):")
        for item in density.get("issues", []):
            print(f"  - {item}")
        for item in density.get("notices", []):
            print(f"  - {item}")

    print("\nLimitations:")
    for limitation in report["limitations"]:
        print(f"  - {limitation}")


def strict_failure(
    report: dict,
    *,
    v2: bool = False,
    current_state: bool = False,
    formal_review: bool = False,
    require_test_matrix: bool = False,
) -> bool:
    root_module = next(
        (module for module in report["modules"] if module["path"] == "."), None
    )
    if (
        root_module is None
        or not root_module["logic_readme"]
        or not root_module["logic_change"]
    ):
        return True

    if current_state or formal_review:
        current_integrity = report.get("current_integrity", {})
        if any(
            current_integrity.get(key, [])
            for key in (
                "document_issues",
                "scope_registry_issues",
                "proposal_issues",
                "responsibility_issues",
            )
        ):
            return True
        if (
            report["current_state_nonroot_documents"]
            or report["parallel_current_candidates"]
        ):
            return True
        if any(
            entry["exists"] and entry["issues"] for entry in report["agent_entrypoints"]
        ):
            return True
        if report["private_agent_knowledge_files"]:
            return True
        if report["missing_required_agent_entries"] or report.get(
            "missing_default_agent_entry", False
        ):
            return True
        if formal_review:
            formal = report.get("formal_review", {})
            if any(
                formal.get(key, [])
                for key in (
                    "proposal_issues",
                    "test_matrix_issues",
                    "temp_reference_issues",
                )
            ):
                return True
        return False

    if any(
        module["change_without_readme"]
        or module["missing_readme_sections"]
        or module["missing_readme_fields"]
        or module["missing_change_sections"]
        or module["missing_change_fields"]
        or module["semantic_issues"]
        or module["broken_links"]
        for module in report["modules"]
    ):
        return True

    proposal_integrity = report["proposal_integrity"]
    if (
        proposal_integrity["duplicate_ids"]
        or proposal_integrity["missing_root_index"]
        or proposal_integrity["unknown_root_index"]
        or proposal_integrity["closed_change_ids_still_active"]
        or proposal_integrity["authority_issues"]
    ):
        return True

    archive = report["archive"]
    if (
        archive["index"] not in {"ok", "not-needed"}
        or archive["malformed_versions"]
        or archive["malformed_decisions"]
        or archive["backups_missing_manifest"]
        or archive["malformed_backups"]
        or archive["broken_links"]
        or archive["index_consistency"]["unindexed_records"]
        or archive["index_consistency"]["duplicate_ids"]
        or archive["index_consistency"]["row_mismatches"]
        or archive["index_consistency"]["unknown_record_links"]
        or report["misplaced_version_records"]
        or report["misplaced_decision_records"]
        or archive["duplicate_history_roots"]
        or archive["extra_paths"]
        or archive["forbidden_current_docs"]
    ):
        return True

    if report["parallel_current_candidates"]:
        return True

    if any(
        entry["exists"] and entry["issues"] for entry in report["agent_entrypoints"]
    ):
        return True

    if report["private_agent_knowledge_files"]:
        return True

    if report["missing_required_agent_entries"]:
        return True

    if require_test_matrix and report["test_inventory"]["matrix_issues"]:
        return True

    if v2:
        if report["missing_map_candidates"] or report["runtime_data_candidates"]:
            return True
        if any(
            module["v2_issues"] or module["module_binding_issues"]
            for module in report["modules"]
        ):
            return True
        if report["misplaced_logic_temp"]:
            return True
        routes = report["module_routes"]
        if any(
            routes[key]
            for key in (
                "route_issues",
                "duplicate_module_ids",
                "duplicate_scope_paths",
                "unregistered_governance_dirs",
                "hierarchy_issues",
            )
        ):
            return True
        if (
            proposal_integrity["route_issues"]
            or proposal_integrity["cross_module_link_issues"]
            or proposal_integrity["authority_registry_issues"]
        ):
            return True
        temp = report["logic_temp"]
        if any(
            temp[key]
            for key in (
                "malformed",
                "missing_logic_temp",
                "orphan_change_ids",
                "expired",
                "forbidden_files",
                "unindexed",
                "extra_entries",
                "stale_index_entries",
                "change_temp_link_issues",
            )
        ):
            return True
        if not archive["exists"] or archive["index"] != "ok" or archive["legacy_roots"]:
            return True

    return False
