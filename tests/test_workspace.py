"""Real filesystem regression cases for task workspaces and generated maps."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from recall_common import change_ledgers
from route_docs import build_plan
from task_context import snapshot, index_update
from workspace_check import (
    check_workspace,
    format_incomplete_temp_scan_summary,
    summarize_incomplete_temp_scan_paths,
)
from workspace_inventory import inventory, write_maps
from workspace_maps import read_map
from workspace_paths import project_path

ID = "CHG-20261020-001"


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="recall-workspace-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "vscode3" / "教材"
        shutil.copytree(ROOT / "references/examples/mini-project", self.root)
        self.root = self.root.resolve()

    def write(self, rel, text=""):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def task(self, rows="", extra="", slug="feature", scope=".", change_id=ID):
        text = (f'# 任务\n\n<a id="{ID.lower()}"></a>\n## {ID}: 目录治理\n'
                '- governance_mode: personal\n- status: implementing\n- effective: false\n'
                '- proposal_revision: 1\n- recall_route: medium\n- owner: self\n- changed_by: Codex\n'
                f'- scope: {scope}\n- affected_scopes: {scope}\n'
                '- decision_confirmed_by: user\n- decision_confirmed_at: 2026-10-20\n'
                '- raw_request: 测试任务的明确请求\n- decomposition: 修改路径治理并验证\n'
                '- fit_analysis: 复用已登记目录\n' + extra +
                '\n### 工作区产物台账\n| path | artifact_kind | disposition | reason | cleaned_at |\n'
                '|---|---|---|---|---|\n' + rows)
        text = text.replace(ID, change_id).replace(ID.lower(), change_id.lower())
        path = self.write(f"logic_changes/{slug}/logic_change.md", text)
        index, _, updated = index_update(self.root, snapshot(self.root))
        index.write_text(updated, encoding="utf-8")
        return path

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/recall.py"), *args],
                              cwd=self.root, capture_output=True, encoding="utf-8")

    def codes(self, **options):
        return {f["code"] for f in check_workspace(self.root, **options)["findings"]}

    def test_boundary_summary_preserves_count_and_groups_roots(self):
        paths = [
            ".work/临时-全部已入课提示词更新/lessons/c_a",
            ".work/临时-全部已入课提示词更新/cli-jobs/c_b",
            ".work/临时-523课提示词更新",
            ".work/临时-全部已入课提示词更新/lessons/c_a",
        ]
        summary = summarize_incomplete_temp_scan_paths(paths)
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["root_count"], 2)
        text = format_incomplete_temp_scan_summary(paths)
        self.assertIn("4 项", text)
        self.assertIn("2 个临时目录", text)
        self.assertIn("完整路径仍保留在 JSON 明细中", text)

    def test_paths_reject_escapes_windows_drives_and_duplicate_roots(self):
        for path in ["../outside", "D:/vscode3/教材/.work", "C:probe.py",
                     "vscode3/教材/.work/fixture", "/absolute", ".", r"vscode3\教材\.work"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                project_path(self.root, path)
        self.assertEqual(project_path(self.root, ".work/临时-目录核对/run.py"),
                         self.root / ".work/临时-目录核对/run.py")

    def test_path_does_not_follow_symlinks(self):
        target = Path(self.temp.name) / "outside"
        target.mkdir()
        try:
            (self.root / "linked").symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("host cannot create symlinks")
        with self.assertRaises(ValueError):
            project_path(self.root, "linked/file")
        data = inventory(self.root)
        self.assertTrue(any("链接未遍历" in n for n in data["notices"]))

    def test_junction_guard_without_host_link_privileges(self):
        boundary = self.root / "junction"
        boundary.mkdir()
        with patch("workspace_paths.linked", side_effect=lambda p: p == boundary):
            with self.assertRaises(ValueError):
                project_path(self.root, "junction/file")

    def test_inventory_separates_data_and_source_and_bounds_enumeration(self):
        self.write("content/lesson/app.py")
        self.write("资产库/book/chapters/page.png")
        data = inventory(self.root, ["content", "资产库"], data_roots=["资产库"])
        paths = {e["path"] for e in data["entries"]}
        self.assertIn("content/lesson/app.py", paths)
        self.assertNotIn("资产库/book/chapters/page.png", paths)
        limited = inventory(self.root, max_entries=2)
        self.assertEqual(limited["entries_inspected"], 2)
        self.assertFalse(limited["complete"])

    def test_inventory_reports_duplicate_project_even_empty(self):
        (self.root / "vscode3/教材/.work/empty").mkdir(parents=True)
        result = inventory(self.root, ["vscode3"])
        self.assertTrue(any(e["suspected_duplicate_root"] for e in result["entries"]))

    def test_generated_maps_use_ownership_and_preserve_handwritten_files(self):
        data = inventory(self.root, ["src"])
        written = write_maps(self.root, data)
        self.assertIn("logic_domains/core/file_map.md", written)
        self.assertIn("src/app.py", (self.root / "logic_domains/core/file_map.md").read_text(encoding="utf-8"))
        self.write("logic_domains/core/file_map.md", "手工资料")
        before = (self.root / "logic_domains/file_map.md").read_bytes()
        with self.assertRaises(ValueError):
            write_maps(self.root, data)
        self.assertEqual(before, (self.root / "logic_domains/file_map.md").read_bytes())

    def test_task_discovery_index_next_route_and_audit(self):
        self.task(scope="logic_domains/core")
        self.assertTrue(any(p.startswith("logic_changes/") for p, _ in change_ledgers(self.root)))
        self.assertEqual(len(snapshot(self.root)["items"]), 1)
        plan = build_plan(self.root, ["src/app.py"])
        self.assertEqual(plan["related_changes"][0]["id"], ID)
        self.assertFalse(any(r["path"].startswith("logic_changes/") for r in plan["reading_order"]))
        self.assertTrue(any(r["path"].startswith("logic_changes/") for r in
                            build_plan(self.root, ["src/app.py"], include_related=True)["reading_order"]))
        for args in [("index",), ("next", "--json"), ("workspace", "--closing", ID), ("audit", "--json")]:
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task_discovery_and_maps_accept_equivalent_root_spelling(self):
        task = self.task()
        alias = self.root / ".." / self.root.name
        self.assertIn(("logic_changes/feature/logic_change.md", task), change_ledgers(alias))
        written = write_maps(alias, inventory(alias, ["src"]))
        self.assertIn("logic_domains/core/file_map.md", written)

    def test_invalid_task_not_hidden_from_audit(self):
        path = self.task()
        path.write_text(path.read_text(encoding="utf-8").replace("- effective: false", "- effective: true"), encoding="utf-8")
        result = self.cli("audit", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("effective-must-be-false", result.stdout)

    def test_formal_review_does_not_skip_task_files(self):
        self.task(extra="- task_temp_dirs: none\n")
        result = self.cli("audit", "--formal-review", "--json")
        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        issues = data["formal_review"]["proposal_issues"]
        self.assertTrue(any(ID + ":missing-formal-section:" in issue for issue in issues))
        self.assertNotIn(ID + ":missing-formal-field:temp_path", issues)

    def test_published_personal_template_runs_in_task_directory(self):
        text = (ROOT / "references/logic-change-template.md").read_text(encoding="utf-8")
        block = text.split("```markdown\n", 1)[1].split("```", 1)[0]
        block = block.replace('<a id="chg-yyyymmdd-nnn"></a>', "ANCHOR")
        block = re.sub(r"<[^>]+>", "实际说明", block).replace("YYYYMMDD-NNN", "20261020-001")
        block = block.replace("ANCHOR", f'<a id="{ID.lower()}"></a>')
        self.write("logic_changes/示例/logic_change.md", block)
        path, _, text = index_update(self.root, snapshot(self.root))
        path.write_text(text, encoding="utf-8")
        result = self.cli("audit", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_readme_only_domain_is_audited_and_routed(self):
        policy = self.root / "logic_domains/core/logic_readme.md"
        policy.write_text(policy.read_text(encoding="utf-8").replace("module_doc_policy: paired", "module_doc_policy: readme-only")
                          .replace("canonical_change: logic_domains/core/logic_change.md", "canonical_change: none")
                          .replace("[logic_change.md](logic_change.md)", "[任务](../../logic_change.md)"), encoding="utf-8")
        (self.root / "logic_domains/core/logic_change.md").unlink()
        doc = self.root / "logic_readme.md"
        doc.write_text(doc.read_text(encoding="utf-8").replace(
            "domain/runtime-code | paired | [core](logic_domains/core/logic_readme.md) | [changes](logic_domains/core/logic_change.md)",
            "domain/runtime-code | readme-only | [core](logic_domains/core/logic_readme.md) | none"), encoding="utf-8")
        self.task(scope="logic_domains/core")
        result = self.cli("audit", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = build_plan(self.root, ["src/app.py"])
        self.assertIn("logic_domains/core", data["matched_domains"])
        policy.write_text(policy.read_text(encoding="utf-8").replace("| RULE-002 | ordinary", "| RULE-002 | invalid"), encoding="utf-8")
        self.assertNotEqual(self.cli("audit", "--json").returncode, 0)

    def test_ignored_files_and_false_cleanup_are_detected(self):
        self.write(".gitignore", ".work/\n")
        self.write(".work/临时-诊断/probe.py")
        self.task("| .work/临时-诊断/ | probe | delete | 临时 | 2026-10-20 |\n",
                  "- task_temp_dirs: .work/临时-诊断\n- ledger_cleared: yes\n")
        codes = self.codes(closing=ID)
        self.assertTrue({"delete-still-exists", "false-cleanup-claim", "temp-folder-still-exists"} <= codes)
        self.assertNotEqual(self.cli("workspace", "--closing", ID).returncode, 0)

    def test_unlisted_files_and_orphan_empty_directories_are_detected(self):
        self.write(".work/临时-诊断/unlisted.py")
        (self.root / ".work/临时-孤儿").mkdir()
        self.task(extra="- task_temp_dirs: .work/临时-诊断\n")
        self.assertTrue({"unlisted-temp-artifact", "orphan-temp-artifact"} <= self.codes())

    def test_gitignore_and_keep_cannot_hide_nondeliverables(self):
        self.write(".work/临时-诊断/a.py")
        for disposition in ["gitignore", "keep"]:
            self.task(f"| .work/临时-诊断/a.py | probe | {disposition} | 临时 | - |\n",
                      "- task_temp_dirs: .work/临时-诊断\n")
            self.assertFalse(check_workspace(self.root)["ok"])

    def test_delete_missing_deliverable_and_budget_checks(self):
        self.write(".work/临时-测试/a")
        self.write(".work/临时-测试/b")
        self.task("| src/absent.py | deliverable | keep | 正式功能 | - |\n"
                  "| .work/临时-测试 | scratch | delete | 临时 | - |\n",
                  "- task_temp_dirs: .work/临时-测试\n")
        self.assertIn("missing-deliverable", self.codes())
        self.assertIn("incomplete-temp-scan", self.codes(max_entries=1))

    def test_closure_succeeds_only_after_temp_directory_deleted(self):
        folder = self.root / ".work/临时-诊断"
        folder.mkdir(parents=True)
        self.task("| .work/临时-诊断 | scratch | delete | 临时 | - |\n",
                  "- task_temp_dirs: .work/临时-诊断\n")
        self.assertFalse(check_workspace(self.root, closing=ID)["ok"])
        folder.rmdir()
        self.assertTrue(check_workspace(self.root, closing=ID)["ok"])

    def test_cli_path_and_inventory(self):
        result = self.cli("path", ".work/临时-诊断/probe.py", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["resolved"].endswith("/.work/临时-诊断/probe.py"))
        self.assertNotEqual(self.cli("path", "vscode3/教材/.work").returncode, 0)
        result = self.cli("inventory", "src", "--json", "--max-entries", "10")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["entries"])

    def test_task_identity_routes_declared_rules_without_other_task_bodies(self):
        path = self.task(scope="logic_domains/core")
        other = self.task(slug="other", scope="logic_domains/core", change_id="CHG-20261020-002")
        other.write_text(other.read_text(encoding="utf-8").replace(ID, "CHG-20261020-002"), encoding="utf-8")
        for target in [ID.lower(), str(path), "logic_changes/feature", "logic_changes/feature/logic_change.md#" + ID.lower()]:
            with self.subTest(target=target):
                data = build_plan(self.root, [target])
                self.assertEqual(data["matched_domains"], ["logic_domains/core"])
                self.assertEqual(data["unmatched_targets"], [])
                self.assertEqual([i["id"] for i in data["matched_tasks"]], [ID])
                reading = [r["path"] for r in data["reading_order"]]
                self.assertIn("logic_domains/core/logic_readme.md", reading)
                self.assertIn("logic_changes/feature/logic_change.md", reading)
                self.assertNotIn("logic_changes/other/logic_change.md", reading)

    def test_task_scopes_include_primary_and_report_unregistered_scopes(self):
        path = self.task(scope="MOD-CORE")
        text = path.read_text(encoding="utf-8").replace("- affected_scopes: MOD-CORE", "- affected_scopes: .; logic_domains/missing")
        path.write_text(text, encoding="utf-8")
        data = build_plan(self.root, [ID])
        self.assertEqual(data["matched_domains"], ["logic_domains/core"])
        self.assertTrue(any("logic_domains/missing" in w for w in data["routing_warnings"]))
        unknown = build_plan(self.root, ["CHG-19990101-999"])
        self.assertEqual(unknown["matched_domains"], [])
        self.assertEqual(unknown["unmatched_targets"], ["CHG-19990101-999"])

    def test_duplicate_task_id_is_reported_without_silent_selection(self):
        path = self.task()
        self.write("logic_changes/duplicate/logic_change.md", path.read_text(encoding="utf-8"))
        data = build_plan(self.root, [ID])
        self.assertEqual(len(data["matched_tasks"]), 2)
        self.assertTrue(data["routing_warnings"])

    def saved_map(self):
        return read_map((self.root / "logic_domains/file_map.md").read_text(encoding="utf-8"))

    def test_partial_map_update_retains_other_scopes_and_timestamps(self):
        self.write("content/lesson.py")
        write_maps(self.root, inventory(self.root, ["src", "content"]))
        before = self.saved_map()
        self.write("src/new.py")
        write_maps(self.root, inventory(self.root, ["src"]))
        after = self.saved_map()
        old = next(r for r in before["entries"] if r["path"] == "content/lesson.py")
        self.assertIn(old, after["entries"])
        self.assertIn("src/new.py", {r["path"] for r in after["entries"]})
        self.assertEqual(len(after["scans"]), 2)

    def test_truncated_or_shallow_scan_preserves_unseen_children(self):
        self.write("src/sub/deep.py")
        self.write("src/tail.py")
        write_maps(self.root, inventory(self.root, ["src"]))
        old = {r["path"] for r in self.saved_map()["entries"]}
        write_maps(self.root, inventory(self.root, ["src"], max_entries=1))
        self.assertEqual(old, {r["path"] for r in self.saved_map()["entries"]})
        self.assertFalse(next(c for c in self.saved_map()["coverage"] if c["path"] == "src")["complete"])
        write_maps(self.root, inventory(self.root, ["src"], max_depth=0))
        self.assertEqual(old, {r["path"] for r in self.saved_map()["entries"]})

    def test_complete_scan_removes_vanished_subtree_from_map_only(self):
        path = self.write("src/sub/deep.py")
        write_maps(self.root, inventory(self.root, ["src"]))
        path.unlink()
        path.parent.rmdir()
        write_maps(self.root, inventory(self.root, ["src"], max_depth=0))
        self.assertFalse(any(r["path"].startswith("src/sub") for r in self.saved_map()["entries"]))
        self.assertTrue((self.root / "src/app.py").exists())

    def test_legacy_map_upgrade_keeps_unscanned_coverage(self):
        self.write("logic_domains/file_map.md", "<!-- recall-generated-file-map -->\n# 文件地图\n\n"
                   "扫描时间：2026-10-21\n范围：content；深度 3；预算 1000。\n"
                   "| 路径 | 简要说明 | 领域 |\n|---|---|---|\n| content/lesson.py | 代码/界面文件 | 待登记 |\n"
                   "\n扫描边界：\n- 数据边界未深入\n")
        write_maps(self.root, inventory(self.root, ["src"]))
        data = self.saved_map()
        self.assertEqual(data["legacy_boundary"]["generated_at"], "2026-10-21")
        self.assertTrue(any(r["path"] == "content/lesson.py" and r["scanned_at"] == "2026-10-21" for r in data["entries"]))

    def test_task_closure_separates_other_task_errors_and_exit_status(self):
        self.task()
        other = self.task(slug="other", extra="- task_temp_dirs: .work/临时-其他\n", change_id="CHG-20261020-002")
        other.write_text(other.read_text(encoding="utf-8").replace(ID, "CHG-20261020-002").replace(
            "status: implementing", "status: promoting"), encoding="utf-8")
        (self.root / ".work/临时-其他").mkdir(parents=True)
        data = check_workspace(self.root, closing=ID)
        self.assertTrue(data["task_result"]["ok"])
        self.assertFalse(data["global_result"]["ok"])
        self.assertFalse(data["ok"])
        self.assertTrue(data["other_findings"])
        self.assertEqual(self.cli("workspace", "--closing", ID).returncode, 0)
        self.assertNotEqual(self.cli("workspace").returncode, 0)
        self.assertFalse(check_workspace(self.root, task="CHG-19990101-999")["selection_ok"])

    def test_shared_temp_directory_blocks_both_tasks(self):
        self.task(extra="- task_temp_dirs: .work/临时-共用\n")
        other = self.task(slug="other", extra="- task_temp_dirs: .work/临时-共用\n", change_id="CHG-20261020-002")
        other.write_text(other.read_text(encoding="utf-8").replace(ID, "CHG-20261020-002"), encoding="utf-8")
        for task in (ID, "CHG-20261020-002"):
            data = check_workspace(self.root, task=task)
            self.assertFalse(data["selection_ok"])
            self.assertIn("shared-temp-directory", {f["code"] for f in data["task_result"]["findings"]})

    def test_task_ledger_supports_existing_level_two_sections(self):
        self.write(".work/临时-诊断/run.py")
        path = self.task("| .work/临时-诊断 | scratch | delete | 临时 | - |\n",
                         "- task_temp_dirs: .work/临时-诊断\n")
        path.write_text(path.read_text(encoding="utf-8").replace("### 工作区产物台账", "## 工作区产物台账"), encoding="utf-8")
        data = check_workspace(self.root, task=ID)
        self.assertTrue(data["selection_ok"])
        self.assertEqual({f["code"] for f in data["task_result"]["findings"]}, {"delete-still-exists"})

    def extended_task(self, rows):
        path = self.task(extra="- task_temp_dirs: .work/临时-多轮\n")
        text = path.read_text(encoding="utf-8").replace(
            "| path | artifact_kind | disposition | reason | cleaned_at |\n|---|---|---|---|---|",
            "| path | artifact_kind | disposition | reason | cleaned_at | retention_basis | exit_condition | round |\n"
            "|---|---|---|---|---|---|---|---|")
        path.write_text(text + rows, encoding="utf-8")

    def test_finished_round_cleans_own_rows_while_next_round_continues(self):
        self.write(".work/临时-多轮/round02/run.py")
        self.extended_task("| .work/临时-多轮/round01 | scratch | delete | 第一轮 | 2026-10-24 | - | 轮末清理 | 01 |\n"
                           "| .work/临时-多轮/round02 | scratch | delete | 第二轮 | - | - | 轮末清理 | 02 |\n")
        data = check_workspace(self.root, task=ID, round_id="1")
        self.assertTrue(data["round_result"]["ok"])
        self.assertFalse(check_workspace(self.root, task=ID, round_id="2")["selection_ok"])
        self.assertFalse(check_workspace(self.root, closing=ID)["selection_ok"])
        self.assertFalse(check_workspace(self.root, task=ID, round_id="3")["selection_ok"])
        self.assertEqual(self.cli("workspace", "--task", ID, "--round", "1").returncode, 0)

    def test_retained_evidence_and_runtime_data_need_basis_and_exit(self):
        self.write("data/live.json")
        self.write("logic_version/evidence/result.json")
        self.extended_task("| data/live.json | runtime-data | keep | 运行数据 | - | 业务查询引用 | 停用并确认无引用后复核 | 01 |\n"
                           "| logic_version/evidence/result.json | evidence | keep | 正式证据 | - | - | - | 01 |\n")
        self.assertIn("missing-retention-basis", self.codes())
        path = self.root / "logic_changes/feature/logic_change.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| 正式证据 | - | - | - | 01 |",
            "| 正式证据 | - | 关案结论的验证依据 | 对应决定被替代且无引用时复核 | 01 |"), encoding="utf-8")
        self.assertTrue(check_workspace(self.root, closing=ID)["selection_ok"])


if __name__ == "__main__":
    unittest.main()
