import hashlib
import tempfile
import unittest
from pathlib import Path

from test_validate import VALIDATE


class WorklogRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'logic_readme.md').write_text('- scope: .\n', encoding='utf-8')
        self.slug = 'logic_version-20261013-101-test-active'
        (self.root / 'logic_change.md').write_text(
            '## CHG-20261013-101: live\n- status: implementing\n'
            '- proposal_revision: 2\n- version_slug: ' + self.slug + '\n', encoding='utf-8')
        self.worklog = self.root / 'logic_version/working' / self.slug / 'logic_temp.md'
        self.worklog.parent.mkdir(parents=True)
        self.worklog.write_text(
            '- version_id: VER-20261013-101\n- state: working\n'
            '- source_change_id: CHG-20261013-101\n- proposal_revision: 2\n'
            '- version_slug: ' + self.slug + '\n', encoding='utf-8')
        self.index = self.root / 'logic_version/index.md'
        self.row = ('| VER-20261013-101 | CHG-20261013-101 | working | '
                    f'[work](working/{self.slug}/logic_temp.md) |\n')
        self.index.write_text('## 活跃临时记录\n| version_id | change_id | state | path |\n'
                              '|---|---|---|---|\n' + self.row, encoding='utf-8')

    def run_check(self):
        result = VALIDATE.ValidationResult()
        VALIDATE.check_ver_registrations([], self.index, '', result)
        return result.errors

    def test_live_worklog_is_not_reported_as_missing_archive(self):
        self.assertEqual([], self.run_check())

    def test_missing_worklog_still_fails(self):
        self.worklog.unlink()
        self.assertTrue(self.run_check())

    def test_explicit_temp_path_binds_ledger_without_optional_slug(self):
        text = (self.root / 'logic_change.md').read_text(encoding='utf-8')
        text = text.replace('- version_slug: ' + self.slug,
                            '- temp_path: logic_version/working/' + self.slug + '/logic_temp.md')
        (self.root / 'logic_change.md').write_text(text, encoding='utf-8')
        self.assertEqual([], self.run_check())

    def test_wrong_revision_still_fails(self):
        text = self.worklog.read_text(encoding='utf-8').replace('revision: 2', 'revision: 3')
        self.worklog.write_text(text, encoding='utf-8')
        self.assertTrue(self.run_check())

    def test_outside_working_path_cannot_exempt_record(self):
        text = self.index.read_text(encoding='utf-8').replace('working/', 'records/')
        self.index.write_text(text, encoding='utf-8')
        self.assertTrue(self.run_check())

    def test_same_id_in_archive_table_still_requires_record(self):
        text = '## 决策记录\n| VER-20261013-101 | effective |\n' + self.index.read_text(encoding='utf-8')
        self.index.write_text(text, encoding='utf-8')
        self.assertTrue(any('没有对应记录文件' in e for e in self.run_check()))

    def test_closed_change_cannot_exempt_worklog(self):
        (self.root / 'logic_change.md').write_text('# no active changes\n', encoding='utf-8')
        self.assertTrue(self.run_check())

    def test_fenced_example_cannot_become_registration(self):
        text = '```markdown\n' + self.index.read_text(encoding='utf-8') + '```\n'
        self.index.write_text(text, encoding='utf-8')
        self.assertEqual([], self.run_check())


class AppendOnlySchemaTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.records = self.root / 'logic_version/records'
        self.records.mkdir(parents=True)
        (self.root / 'logic_readme.md').write_text('- scope: .\n', encoding='utf-8')
        (self.root / 'logic_change.md').write_text('# no changes\n', encoding='utf-8')
        self.original = self.records / 'logic_version-20261012-101-original.md'
        self.original.write_text('# Original decision\nPreserved source evidence.\n', encoding='utf-8')
        self.original_bytes = self.original.read_bytes()
        self.correction = self.records / 'logic_version-20261013-102-schema-supplement.md'
        headings = ('## 为什么做这个决策？\nSource evidence.\n## 影响范围\nDocumentation.\n'
                    '## 验证方式\nStatic review only.\n## 回滚方式\nKeep source.\n')
        self.correction.write_text(
            '- version_id: VER-20261013-102\n- date: 2026-10-13\n- status: correction\n'
            '- immutable: true\n- corrects: VER-20261012-101\n'
            '- corrected_record_sha256: ' + hashlib.sha256(self.original_bytes).hexdigest() + '\n'
            + headings + '\n```recall-schema-supplement\n'
            '- version_id: VER-20261012-101\n- date: 2026-10-12\n- status: effective\n'
            + headings + '```\n', encoding='utf-8')
        (self.root / 'logic_version/index.md').write_text(
            '| VER-20261012-101 | original |\n| VER-20261013-102 | supplement |\n', encoding='utf-8')

    def run_check(self):
        result = VALIDATE.ValidationResult()
        VALIDATE._validate_version_records(self.root, self.root / 'logic_version', '', [], result)
        return result

    def test_valid_supplement_resolves_format_without_modifying_source(self):
        result = self.run_check()
        self.assertEqual([], result.errors)
        self.assertEqual(self.original_bytes, self.original.read_bytes())
        self.assertTrue(any('原字节保持不变' in m for m in result.info))

    def test_changed_source_bytes_invalidate_supplement(self):
        self.original.write_bytes(self.original_bytes + b'changed\n')
        self.assertTrue(self.run_check().errors)

    def test_wrong_target_cannot_fix_original(self):
        text = self.correction.read_text(encoding='utf-8').replace('corrects: VER-20261012-101',
                                                                 'corrects: VER-20261012-999')
        self.correction.write_text(text, encoding='utf-8')
        self.assertTrue(self.run_check().errors)

    def test_nonfinal_correction_cannot_fix_original(self):
        text = self.correction.read_text(encoding='utf-8').replace('immutable: true', 'immutable: false')
        self.correction.write_text(text, encoding='utf-8')
        self.assertTrue(self.run_check().errors)

    def test_missing_correction_sections_cannot_fix_original(self):
        text = self.correction.read_text(encoding='utf-8').replace('## 验证方式', '## Other')
        self.correction.write_text(text, encoding='utf-8')
        self.assertTrue(self.run_check().errors)

    def test_payload_cannot_supply_own_correction_schema(self):
        text = self.correction.read_text(encoding='utf-8')
        outer, payload = text.split('```recall-schema-supplement', 1)
        self.correction.write_text(outer.replace('## 验证方式', '## Other') +
                                   '```recall-schema-supplement' + payload, encoding='utf-8')
        self.assertTrue(self.run_check().errors)


if __name__ == '__main__':
    unittest.main()
