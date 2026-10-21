"""Observable lifecycle, immutable traceability and diagnostic regressions."""
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import recall
import recall_common
import record_context
import validate

SLUG = 'logic_version-20261013-901-context-demo'
IDENTITY = 'VER-20261013-901'
CHANGE = 'CHG-20261013-901'


def run_cli(root, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/recall.py'), *args],
                          cwd=root, capture_output=True, text=True, encoding='utf-8', timeout=20)


def record_text(identity=IDENTITY, slug=SLUG, immutable='false', commit='none', extra=''):
    return f'''# {identity}: Context regression
## 记录控制
- version_id: {identity}
- version_slug: {slug}
- status: effective
- immutable: {immutable}
- date: 2026-10-13
- change_id: {CHANGE}
- proposal_revision: 1
- after_commit: {commit}
{extra}
## 为什么做这个决策？
Regression fixture.
- raw_request: example
- decomposition: example
- fit_analysis: example
## 影响范围
src/app.py
## 验证方式
fixture
## 回滚方式
fixture
'''


class RecordContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / 'references/examples/mini-project', self.root, dirs_exist_ok=True)
        self.record = self.root / 'logic_version/records' / (SLUG + '.md')
        self.record.parent.mkdir(parents=True)
        self.record.write_text(record_text(), encoding='utf-8')
        ledger = self.root / 'logic_change.md'
        ledger.write_text(ledger.read_text(encoding='utf-8') + f'''
<a id="{CHANGE.lower()}"></a>
## {CHANGE}: context fixture
- governance_mode: personal
- status: implementing
- effective: false
- proposal_revision: 1
- recall_route: medium
- changed_by: fixture
- owner: self
- scope: .
- affected_scopes: .
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-13
- raw_request: teaching fixture
- decomposition: teaching fixture
- fit_analysis: teaching fixture
- version_slug: {SLUG}
- next_action: verify
''', encoding='utf-8')
        self.assertEqual(run_cli(self.root, 'index', '--write').returncode, 0)
        (self.root / 'logic_version/index.md').write_text('| version_id | record |\n|---|---|\n', encoding='utf-8')

    def tearDown(self):
        self.temporary.cleanup()

    def test_live_draft_is_consistent_across_real_commands(self):
        checked = run_cli(self.root, 'validate')
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        for forbidden in ('未登记到 logic_version/index.md', '未被现行文档引用', f'{self.record.name} 未关联'):
            self.assertNotIn(forbidden, checked.stdout)
        self.assertIn('未归档草稿', checked.stdout)
        self.assertIn('活跃草稿（未归档）', run_cli(self.root, 'list').stdout)
        self.assertIn('活跃草稿（未归档）', run_cli(self.root, 'query', 'file', 'src/app.py').stdout)
        self.assertIn('活跃草稿: 1', run_cli(self.root, 'status').stdout)
        audited = run_cli(self.root, 'audit', '--json')
        self.assertEqual(audited.returncode, 0, audited.stdout + audited.stderr)
        self.assertTrue(json.loads(audited.stdout)['static_gate']['passed'])

    def test_finalization_restores_history_registration_requirements(self):
        self.record.write_text(record_text(immutable='true'), encoding='utf-8')
        checked = run_cli(self.root, 'validate')
        self.assertIn('未登记到 logic_version/index.md', checked.stdout)
        self.assertIn('未被现行文档引用', checked.stdout)
        self.assertNotIn('活跃草稿（未归档）', run_cli(self.root, 'list').stdout)

    def test_unmatched_draft_is_not_silently_treated_as_complete(self):
        for changed in (record_text().replace('proposal_revision: 1', 'proposal_revision: 2'),
                        record_text().replace(CHANGE, 'CHG-20261013-999'),
                        record_text().replace(SLUG, SLUG + '-wrong')):
            with self.subTest(changed=changed.splitlines()[4:10]):
                self.record.write_text(changed, encoding='utf-8')
                result = run_cli(self.root, 'validate')
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn('草稿未匹配唯一活跃 CHG', result.stdout)

    def test_fenced_fake_change_cannot_authorize_draft(self):
        ledger = self.root / 'logic_change.md'
        text = ledger.read_text(encoding='utf-8')
        prefix, block = text.split(f'## {CHANGE}:', 1)
        ledger.write_text(prefix + f'```markdown\n## {CHANGE}:' + block + '\n```\n', encoding='utf-8')
        state = record_context.version_record_state(self.record.read_text(encoding='utf-8'), self.record,
                                                   record_context.active_change_controls(self.root))
        self.assertEqual(state, 'invalid-draft')

    def test_fenced_record_example_is_not_state_or_commit_evidence(self):
        text = record_text(immutable='true') + '\n```markdown\n- immutable: false\n- after_commit: abcdef1\n```\n'
        self.assertEqual(record_context.version_record_state(text, self.record, {}), 'archived')
        self.assertEqual(record_context.record_commit_hash(text), '')
        self.assertEqual(validate.extract_commit_hash(self.record, text), '')

    def test_duplicate_chg_cannot_establish_draft_provenance(self):
        ledger = self.root / 'logic_change.md'
        text = ledger.read_text(encoding='utf-8')
        block = f'## {CHANGE}:' + text.split(f'## {CHANGE}:', 1)[1]
        ledger.write_text(text + '\n' + block, encoding='utf-8')
        self.assertNotIn(CHANGE.lower(), record_context.active_change_controls(self.root))

    def test_domain_token_cost_is_advisory(self):
        domain = self.root / 'logic_domains/core/logic_readme.md'
        domain.write_text(domain.read_text(encoding='utf-8') + '\n' + '文' * 6001, encoding='utf-8')
        checked = run_cli(self.root, 'audit', '--json')
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        report = json.loads(checked.stdout)
        costs = report['density']['reading_costs']
        self.assertGreater(costs['logic_domains/core/logic_readme.md']['tokens_estimate'], 6000)
        self.assertTrue(any('logic_domains/core/logic_readme.md:over-token-target' in item
                            for item in report['density']['notices']))

    def _commit(self):
        for args in (['init'], ['config', 'user.name', 'Recall Fixture'],
                     ['config', 'user.email', 'recall@example.invalid'],
                     ['config', 'core.hooksPath', str(self.root / 'disabled-hooks')],
                     ['add', 'src/app.py'], ['commit', '-m', 'test: implementation fixture']):
            result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.root).decode().strip()

    def _correct(self, commit, *, immutable='true'):
        self.record.write_text(record_text(immutable='true'), encoding='utf-8')
        path = self.record.parent / 'logic_version-20261013-902-commit-link.md'
        text = record_text('VER-20261013-902', path.stem, immutable, commit, f'- corrects: {IDENTITY}')
        text = text.replace('status: effective', 'status: correction').replace(f'change_id: {CHANGE}', 'change_id: none')
        path.write_text(text, encoding='utf-8')
        index = self.root / 'logic_version/index.md'
        index.write_text(f'| {IDENTITY} | original |\n| VER-20261013-902 | correction |\n', encoding='utf-8')
        readme = self.root / 'logic_readme.md'
        readme.write_text(readme.read_text(encoding='utf-8') + f'\n| {IDENTITY} | original |\n| VER-20261013-902 | correction |\n', encoding='utf-8')
        return path

    def test_append_commit_evidence_resolves_traceability_without_mutation(self):
        commit = self._commit()
        self._correct(commit)
        before = hashlib.sha256(self.record.read_bytes()).hexdigest()
        checked = run_cli(self.root, 'validate')
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertNotIn(f'{self.record.name} 未关联', checked.stdout)
        self.assertIn('提交关联由追加记录 VER-20261013-902 提供', checked.stdout)
        queried = run_cli(self.root, 'query', 'commit', commit)
        self.assertEqual(queried.returncode, 0, queried.stdout + queried.stderr)
        self.assertIn(IDENTITY, queried.stdout)
        self.assertIn('VER-20261013-902', queried.stdout)
        self.assertEqual(hashlib.sha256(self.record.read_bytes()).hexdigest(), before)

    def test_invalid_sha_correction_does_not_hide_missing_evidence(self):
        self._commit()
        self._correct('a' * 40)
        checked = run_cli(self.root, 'validate')
        self.assertEqual(checked.returncode, 1)
        self.assertIn(f'{self.record.name} 未关联 Git commit', checked.stdout)
        self.assertIn('无效', checked.stdout)

    def test_draft_correction_cannot_supply_commit_evidence(self):
        self._correct(self._commit(), immutable='false')
        checked = run_cli(self.root, 'validate')
        self.assertEqual(checked.returncode, 1)
        self.assertIn(f'{self.record.name} 未关联 Git commit', checked.stdout)

    def test_missing_target_or_self_correction_cannot_supply_evidence(self):
        correction = self._correct(self._commit())
        original = correction.read_text(encoding='utf-8')
        for target in ('VER-20261013-999', 'VER-20261013-902'):
            with self.subTest(target=target):
                correction.write_text(original.replace(f'corrects: {IDENTITY}', f'corrects: {target}'), encoding='utf-8')
                checked = run_cli(self.root, 'validate')
                self.assertIn(f'{self.record.name} 未关联 Git commit', checked.stdout)


class GitFailureTests(unittest.TestCase):
    def test_diagnostics_preserve_reasons_and_distinguish_failure_categories(self):
        cases = [('fatal: not a git repository', '目标不是 Git 仓库'),
                 ('Permission denied', '权限或沙箱限制'),
                 ('fatal: this operation must be run in a work tree', '无法访问工作树'),
                 ('command timed out', '命令超时'),
                 ('[WinError 2] file missing', '可执行文件或运行目录不存在'),
                 ('fatal: arbitrary failure', '命令执行失败')]
        for reason, category in cases:
            with self.subTest(reason=reason):
                message = recall_common.describe_git_failure(reason)
                self.assertIn(category, message)
                self.assertIn(reason, message)

    def test_status_reports_permission_failure_without_claiming_git_uninstalled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'logic_readme.md').write_text('# project', encoding='utf-8')
            stream = io.StringIO()
            with patch.object(recall, 'find_project_root', return_value=root), \
                 patch.object(recall, 'run_git', return_value=(False, '', 'Permission denied')), \
                 contextlib.redirect_stdout(stream):
                self.assertEqual(recall.cmd_status(), 0)
            self.assertIn('权限或沙箱限制', stream.getvalue())
            self.assertNotIn('未安装', stream.getvalue())

    def test_validate_retains_work_tree_failure_reason(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'logic_readme.md').write_text('# project', encoding='utf-8')
            (root / 'logic_change.md').write_text('# changes', encoding='utf-8')
            (root / 'logic_version').mkdir()
            reason = 'fatal: this operation must be run in a work tree'
            with patch.object(validate, 'find_project_root', return_value=root), \
                 patch.object(validate, 'run_git', return_value=(False, '', reason)), \
                 patch.object(validate, 'git_output', return_value=None):
                result = validate.validate_recall()
            self.assertTrue(any(reason in item for item in result.warnings), result.warnings)
            self.assertFalse(any('未安装' in item for item in result.warnings), result.warnings)


if __name__ == '__main__':
    unittest.main()
