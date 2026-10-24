"""Preserved copies must leave active routing without hiding cleanup debt."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from pending_cleanup import PENDING_ROOT, check_pending_cleanup
from task_context import snapshot, index_update
from route_docs import build_plan
from workspace_check import check_workspace
from recall_audit.archive import _collect_archive_layout_issues

TASK = "CHG-20261025-001"


class PendingCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="recall-pending-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        shutil.copytree(ROOT / "references/examples/mini-project", self.root, dirs_exist_ok=True)
        self.source = "logic_changes/feature/logic_change.md"
        self.parked = f"{PENDING_ROOT}/{TASK}/logic_change.md.txt"
        self.archive = "logic_version/records/logic_version-20261025-001-feature.md"
        self.body = f"## {TASK}: 已完成任务\n- scope: logic_domains/core\n- status: blocked\n"

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def prepare(self, **changes):
        original = self.write(self.source, self.body)
        fingerprint = hashlib.sha256(original.read_bytes()).hexdigest()
        self.write(self.archive, f"# 历史\n- immutable: true\n- status: effective\n- change_id: {TASK}\n")
        destination = self.root / self.parked
        destination.parent.mkdir(parents=True, exist_ok=True)
        original.rename(destination)
        self.row = dict(task_id=TASK, original_path=self.source, path=self.parked, archive=self.archive,
                        sha256=fingerprint, reason="已归档副本，删除受阻，允许无损移动", recorded_at="2026-10-25",
                        exit_condition="执行策略允许后核指纹并删除")
        self.row.update(changes)
        self.save_index()
        return destination

    def save_index(self):
        keys = list(self.row)
        self.write("logic_version/index.md", "## 待清理文件\n| " + " | ".join(keys) + " |\n|" +
                   "|".join("---" for _ in keys) + "|\n| " + " | ".join(self.row.values()) + " |\n")

    def codes(self):
        return {f["code"] for f in check_pending_cleanup(self.root)["findings"]}

    def test_preserved_move_exits_active_routes_but_reports_cleanup_debt(self):
        parked = self.prepare()
        self.assertFalse((self.root / self.source).exists())
        self.assertEqual(parked.read_text(encoding="utf-8"), self.body)
        self.assertFalse(snapshot(self.root)["items"])
        plan = build_plan(self.root, ["src/app.py"])
        self.assertFalse(plan["matched_tasks"])
        self.assertFalse(plan["related_changes"])
        _, _, bulletin = index_update(self.root, snapshot(self.root))
        self.assertNotIn(TASK, bulletin)
        result = check_workspace(self.root)
        self.assertTrue(result["ok"])
        self.assertFalse(result["pending_cleanup"]["cleanup_complete"])
        self.assertIn("pending-cleanup", self.codes())
        extras, current = _collect_archive_layout_issues(self.root, self.root / "logic_version", self.root / "logic_version/working")
        self.assertEqual((extras, current), ([], []))
        run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/recall.py"), "workspace"],
                             cwd=self.root, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("清理未完成", run.stdout)

    def test_copy_is_not_move_and_active_task_cannot_be_retired(self):
        self.prepare()
        self.write(self.source, self.body)
        self.assertIn("invalid-pending-cleanup", self.codes())
        (self.root / self.source).unlink()
        result = check_pending_cleanup(self.root, [TASK])
        self.assertEqual(result["findings"][0]["severity"], "error")

    def test_hash_drift_missing_archive_and_draft_each_fail(self):
        parked = self.prepare()
        parked.write_text("changed", encoding="utf-8")
        self.assertIn("invalid-pending-cleanup", self.codes())
        self.write(self.parked, self.body)
        self.write(self.archive, f"- immutable: false\n- status: effective\n- change_id: {TASK}\n")
        self.assertIn("invalid-pending-cleanup", self.codes())
        (self.root / self.archive).unlink()
        self.assertIn("invalid-pending-cleanup", self.codes())

    def test_unlisted_copies_and_duplicate_rows_fail(self):
        self.prepare()
        self.write(f"{PENDING_ROOT}/unknown.txt", "unlisted")
        self.assertIn("unlisted-pending-cleanup", self.codes())
        index = self.root / "logic_version/index.md"
        text = index.read_text(encoding="utf-8")
        index.write_text(text + text.splitlines()[-1] + "\n", encoding="utf-8")
        self.assertIn("duplicate-pending-cleanup", self.codes())

    def test_forbidden_source_escape_and_link_are_rejected(self):
        self.prepare()
        for key, value in [("original_path", "logic_readme.md"), ("path", "../outside"),
                           ("archive", "logic_changes/feature/logic_change.md"), ("exit_condition", "-")]:
            with self.subTest(key=key):
                old = self.row[key]
                self.row[key] = value
                self.save_index()
                self.assertIn("invalid-pending-cleanup", self.codes())
                self.row[key] = old
        self.save_index()
        with patch("workspace_paths.linked", side_effect=lambda p: p == self.root / PENDING_ROOT):
            self.assertIn("invalid-pending-cleanup", self.codes())

    def test_budget_cannot_claim_full_inspection(self):
        self.prepare()
        result = check_pending_cleanup(self.root, max_entries=1)
        self.assertIn("incomplete-pending-cleanup-scan", {f["code"] for f in result["findings"]})

    def test_in_place_retirement_preserves_bytes_but_excludes_only_that_task(self):
        parked = self.prepare()
        parked.rename(self.root / self.source)
        self.row["path"] = self.source
        self.row["reason"] = "删除和移动均被拒绝；只在历史索引记录，原文未改"
        self.save_index()
        self.write("logic_changes/other/logic_change.md", self.body.replace(TASK, "CHG-20261025-002"))
        items = snapshot(self.root)["items"]
        self.assertEqual([i["id"] for i in items], ["CHG-20261025-002"])
        self.assertEqual((self.root / self.source).read_text(encoding="utf-8"), self.body)
        result = check_pending_cleanup(self.root)
        self.assertFalse(result["cleanup_complete"])
        self.assertIn("原位待清理", result["findings"][0]["message"])
        run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/recall.py"), "audit", "--json"],
                             cwd=self.root, text=True, encoding="utf-8", capture_output=True)
        self.assertNotIn(self.source, json.loads(run.stdout)["current_state_nonroot_documents"])

    def test_changed_or_ambiguous_in_place_record_cannot_hide_live_work(self):
        parked = self.prepare()
        parked.rename(self.root / self.source)
        self.row["path"] = self.source
        self.save_index()
        self.assertFalse(snapshot(self.root)["items"])
        self.write(self.source, self.body + "新需求尚未归档\n")
        self.assertEqual(snapshot(self.root)["items"][0]["id"], TASK)
        self.assertIn("invalid-pending-cleanup", self.codes())
        self.write(self.source, self.body)
        index = self.root / "logic_version/index.md"
        text = index.read_text(encoding="utf-8")
        index.write_text(text + text.splitlines()[-1] + "\n", encoding="utf-8")
        self.assertEqual(snapshot(self.root)["items"][0]["id"], TASK)

    def test_missing_copy_needs_reconciliation_and_empty_folders_still_visible(self):
        parked = self.prepare()
        parked.unlink()
        self.assertIn("invalid-pending-cleanup", self.codes())
        self.write("logic_version/index.md", "## 待清理文件\n")
        self.assertIn("empty-pending-cleanup", self.codes())
        parked.parent.rmdir()
        parked.parent.parent.rmdir()
        self.assertTrue(check_pending_cleanup(self.root)["cleanup_complete"])

    @unittest.skipUnless(shutil.which("git"), "git unavailable")
    def test_git_preserves_snapshot_bytes_despite_autocrlf(self):
        parked = self.prepare()
        data = self.body.replace("\n", "\r\n").encode("utf-8")
        parked.write_bytes(data)
        shutil.copyfile(ROOT / ".gitattributes", self.root / ".gitattributes")
        for args in (["init", "-q"], ["-c", "core.autocrlf=true", "add", "--", ".gitattributes", self.parked]):
            result = subprocess.run(["git", *args], cwd=self.root, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        blob = subprocess.run(["git", "show", ":" + self.parked], cwd=self.root, capture_output=True)
        self.assertEqual(blob.returncode, 0, blob.stderr)
        self.assertEqual(blob.stdout, data)


if __name__ == "__main__":
    unittest.main()
