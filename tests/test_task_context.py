"""Task views must preserve uncertainty and index writes must preserve prose."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import task_context as tasks


def change(number="001", status="implementing", extra=""):
    return (f'\n<a id="chg-20260907-{number}"></a>\n## CHG-20260907-{number}: 有价值的交付\n'
            f'- status: {status}\n- scope: .\n- owner: self\n'
            '- decision_confirmed_by: user\n- decision_confirmed_at: 2026-09-07\n'
            f'{extra}\n')


def ledger(body=""):
    return ('# Changes\n\n## 文档控制\n- active_changes: 0\n\n## 议案规则\n保留规则\n'
            '\n## 活跃议案索引\n\n' + tasks.HEADER + '\n' + tasks.SEPARATOR + '\n'
            '\n---\n\n保留人工说明\n' + body)


class TaskContextTests(unittest.TestCase):
    def test_inline_empty_anchor_is_not_a_task_or_bulletin_title(self):
        text = '## CHG-20260907-001: 具体任务 <a id="chg-20260907-001"></a>\n- status: implementing\n'
        items = tasks.read_changes(text, 'logic_change.md')
        self.assertEqual(items[0]['id'], 'CHG-20260907-001')
        self.assertEqual(items[0]['title'], '具体任务')
        self.assertNotIn('<a ', tasks.bulletin(items))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="recall-task-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "logic_readme.md").write_text("# Project\n", encoding="utf-8")
        self.path = self.root / "logic_change.md"

    def write(self, text):
        self.path.write_text(text, encoding="utf-8")

    def test_intake_distinguishes_idea_and_commitment_without_counting_chg(self):
        self.write(ledger() + '\n## 待办\n| task_id | stage | context | source_ref |\n'
                   '|---|---|---|---|\n| TASK-A | idea | 可能做搜索 | user:提问 |\n'
                   '| TASK-B | planned | 改善接手 | user:已决定 |\n'
                   '| TASK-C | planned | 来源缺失 | none |\n')
        data = tasks.snapshot(self.root)
        self.assertEqual(data["counts"]["想法"], 1)
        self.assertEqual(data["counts"]["可做候选"], 1)
        self.assertEqual(data["counts"]["待核对"], 1)
        self.assertEqual(tasks.bulletin(data["items"]), tasks.HEADER + "\n" + tasks.SEPARATOR)

    def test_active_and_missing_dependency_never_imply_ready(self):
        self.write(ledger(change(extra='- depends_on: CHG-20260907-002@revision-1') +
                          change("002", extra='- depends_on: CHG-20260907-999')))
        by_id = {i["id"]: i for i in tasks.snapshot(self.root)["items"]}
        self.assertEqual(by_id["CHG-20260907-001"]["group"], "阻塞")
        self.assertEqual(by_id["CHG-20260907-002"]["group"], "待核对")

    def test_blocked_promoting_keeps_real_reason(self):
        self.write(ledger(change(status="promoting", extra='- blocked_by: cleanup\n'
                    '- blocked_reason: 文件正被使用\n- next_action: 关闭占用进程后清理\n'
                    '- review_due: event:进程退出')))
        data = tasks.snapshot(self.root)
        self.assertEqual(data["items"][0]["group"], "阻塞")
        self.assertEqual(data["items"][0]["reason"], "文件正被使用")
        self.assertFalse(data["warnings"])

    def test_missing_blocker_context_is_advisory(self):
        self.write(ledger(change(status="blocked")))
        data = tasks.snapshot(self.root)
        self.assertEqual(data["counts"]["阻塞"], 1)
        self.assertIn("review_due", data["warnings"][0])

    def test_status_groups_and_missing_authorization(self):
        self.write(ledger(change(status="promoting") + change("002", "draft") +
                          change("003", "verifying") + change("004", "unexpected") +
                          change("005").replace('- decision_confirmed_by: user', '- decision_confirmed_by: none')))
        data = tasks.snapshot(self.root)
        for group, count in (("收尾", 1), ("待决策", 1), ("进行中", 1), ("待核对", 2)):
            self.assertEqual(data["counts"][group], count)

    def test_examples_and_other_section_metadata_are_not_live(self):
        self.write(ledger('```markdown\n' + change("999") + '\n```\n' + change() +
                          '\n## Notes\n- blocked_by: not-a-task-field\n'))
        data = tasks.snapshot(self.root)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["group"], "进行中")

    def test_stale_confirmation_and_pending_decision_are_visible(self):
        self.write(ledger(change(extra='- proposal_revision: 2\n- confirmed_proposal_revision: 1') +
                          change("002", extra='- decision_state: pending')))
        data = tasks.snapshot(self.root)
        self.assertEqual(data["counts"]["待核对"], 1)
        self.assertEqual(data["counts"]["待决策"], 1)

    def test_duplicates_fail_index_without_writing(self):
        self.write(ledger(change() + change()))
        original = self.path.read_bytes()
        data = tasks.snapshot(self.root)
        self.assertEqual(data["counts"]["待核对"], 2)
        with self.assertRaises(ValueError):
            tasks.index_update(self.root, data)
        self.assertEqual(self.path.read_bytes(), original)

    def test_index_is_bounded_idempotent_and_uses_registered_ledgers(self):
        self.write(ledger(change()))
        domain = self.root / "logic_domains" / "test" / "logic_change.md"
        domain.parent.mkdir(parents=True)
        domain.write_text(ledger(change("002")), encoding="utf-8")
        sources = [("logic_change.md", self.path), ("logic_domains/test/logic_change.md", domain)]
        with patch.object(tasks, "change_ledgers", return_value=sources):
            data = tasks.snapshot(self.root)
            _, old, updated = tasks.index_update(self.root, data)
            self.assertIn("- active_changes: 1", updated)
            self.assertIn("logic_domains/test/logic_change.md#chg-20260907-002", updated)
            self.assertEqual(old.split("---\n\n保留人工说明")[1], updated.split("---\n\n保留人工说明")[1])
            self.write(updated)
            self.assertEqual(tasks.index_update(self.root, data)[2], updated)

    def test_unknown_table_does_not_overwrite_user_content(self):
        self.write(ledger(change()).replace("target/summary", "custom-column"))
        with self.assertRaises(ValueError):
            tasks.index_update(self.root, tasks.snapshot(self.root))

    def test_validate_reports_stale_index_without_mutation(self):
        from validate import ValidationResult
        self.write(ledger(change()))
        before = self.path.read_bytes()
        result = ValidationResult()
        tasks.check_consistency(self.root, result)
        self.assertTrue(result.warnings)
        self.assertTrue(result.is_valid())
        self.assertEqual(self.path.read_bytes(), before)

    def test_cli_next_index_check_and_write(self):
        self.write(ledger(change()))
        before = self.path.read_bytes()
        def run(*args):
            return subprocess.run([sys.executable, str(ROOT / "scripts/recall.py"), *args],
                                  cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        result = run("next", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["counts"]["进行中"], 1)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(run("index", "--json").returncode, 1)
        self.assertEqual(self.path.read_bytes(), before)
        result = run("index", "--write", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["written"])
        self.assertEqual(run("index", "--json").returncode, 0)


if __name__ == "__main__":
    unittest.main()
