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
from workspace_check import check_workspace
from workspace_inventory import inventory, write_maps
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

    def task(self, rows="", extra="", slug="feature", scope="."):
        text = (f'# 任务\n\n<a id="{ID.lower()}"></a>\n## {ID}: 目录治理\n'
                '- governance_mode: personal\n- status: implementing\n- effective: false\n'
                '- proposal_revision: 1\n- recall_route: medium\n- owner: self\n- changed_by: Codex\n'
                f'- scope: {scope}\n- affected_scopes: {scope}\n'
                '- decision_confirmed_by: user\n- decision_confirmed_at: 2026-10-20\n'
                '- raw_request: 测试任务的明确请求\n- decomposition: 修改路径治理并验证\n'
                '- fit_analysis: 复用已登记目录\n' + extra +
                '\n### 工作区产物台账\n| path | artifact_kind | disposition | reason | cleaned_at |\n'
                '|---|---|---|---|---|\n' + rows)
        path = self.write(f"logic_changes/{slug}/logic_change.md", text)
        index, _, updated = index_update(self.root, snapshot(self.root))
        index.write_text(updated, encoding="utf-8")
        return path

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/recall.py"), *args],
                              cwd=self.root, capture_output=True, encoding="utf-8")

    def codes(self, **options):
        return {f["code"] for f in check_workspace(self.root, **options)["findings"]}

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
        self.assertTrue(any(r["path"].startswith("logic_changes/") for r in build_plan(self.root, ["src/app.py"])["reading_order"]))
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


if __name__ == "__main__":
    unittest.main()
