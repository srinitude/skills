"""Standardization must expose exact bytes and reject absent review before staging."""
import base64
import json
import tempfile
import unittest
import yaml
from pathlib import Path

from cli import run, SCRIPTS
from standardization_fixtures import profile, write_target
from scaffold_test_support import review_fixture
from standardization_test_support import native_formatter


class TestStandardizationReview(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'clock-anchor'
        write_target(self.root)
        self.config = self.base / 'profile.json'
        self.config.write_text(json.dumps(profile()))
        self.args = (self.root, '--profile', self.config, '--scope', 'user')

    def snapshot(self):
        return {p.relative_to(self.base).as_posix(): p.read_bytes()
                for p in self.base.rglob('*') if p.is_file()}

    def test_plan_retains_complete_before_and_after_bytes_without_writing(self):
        before = self.snapshot()
        result = run('standardize_registry_skill.py', *self.args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIn('plan', report)
        plan = report['plan']
        self.assertEqual(plan['execution_acceptance'], 'pending')
        self.assertTrue(plan['factory_files'])
        entries = {item['path']: item for item in plan['files']}
        self.assertEqual(base64.b64decode(entries['scripts/anchor.py']['content_base64']),
                         (self.root / 'scripts/anchor.py').read_bytes())
        body = base64.b64decode(entries['SKILL.md']['content_base64']).decode('utf-8')
        self.assertEqual(yaml.safe_load(body.split('---', 2)[1])['metadata']['scope'], 'user')
        self.assertIn('scripts/review_ledger_write.py', entries)
        self.assertEqual(self.snapshot(), before)

    def test_missing_review_rejects_without_changing_any_target_file(self):
        before = self.snapshot()
        result = run('standardize_registry_skill.py', *self.args, '--apply')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('review', result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)


    def test_plan_formats_changed_json_through_actual_native_stdin_without_writes(self):
        native_formatter(self.base)
        (self.root / 'assets').mkdir()
        file = self.root / 'assets/state.json'; file.write_bytes(b'{"offset":1}')
        data = profile()
        data['text_rewrites']['assets/state.json'] = [{'old': '{"offset":1}', 'new': '{"offset":2}'}]
        self.config.write_text(json.dumps(data))
        result = run('standardize_registry_skill.py', *self.args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        entries = {item['path']: item for item in json.loads(result.stdout)['plan']['files']}
        self.assertEqual(base64.b64decode(entries['assets/state.json']['content_base64']), b'{ "offset": 2 }\n')
        self.assertEqual(file.read_bytes(), b'{"offset":1}')


    def reviewed_plan(self):
        result = run('standardize_registry_skill.py', *self.args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        path, record, case = review_fixture(self, report['plan'])
        plan_path = case.folder / 'standardization-plan.json'
        plan_path.write_text(result.stdout)
        return path, record, plan_path

    def test_missing_late_review_and_source_drift_reject_then_reviewed_recovery_preserves_modes_and_state(self):
        script = self.root / 'scripts/anchor.py'; script.chmod(0o755)
        (self.root / 'node_modules').mkdir()
        state = self.root / 'node_modules/local-state'; state.write_bytes(b'private runtime state')
        inode = state.stat().st_ino
        path, record, plan_path = self.reviewed_plan()
        original = json.dumps(record); before = self.snapshot()
        last = next(reversed(record['files']))
        record['files'][last]['review']['Body decision'] = ''
        path.write_text(json.dumps(record))
        args = (*self.args, '--apply', '--plan-file', plan_path, '--review', path)
        result = run('standardize_registry_skill.py', *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)
        path.write_text(original)
        source = Path(record['context']['original_source']['path']); raw = source.read_bytes()
        source.write_bytes(raw + b'drift')
        result = run('standardize_registry_skill.py', *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)
        source.write_bytes(raw)
        result = run('standardize_registry_skill.py', *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(script.stat().st_mode & 0o777, 0o755)
        self.assertEqual(state.stat().st_ino, inode)
        self.assertEqual(state.read_bytes(), b'private runtime state')
        self.assertEqual(json.loads(result.stdout)['execution_acceptance'], 'pending')


    def reject_config_drift(self, name, initial, changed):
        native_formatter(self.base)
        config = self.base / name; config.write_bytes(initial)
        path, record, plan_path = self.reviewed_plan()
        config.write_bytes(changed)
        before = self.snapshot()
        args = (*self.args, '--apply', '--plan-file', plan_path, '--review', path)
        result = run('standardize_registry_skill.py', *args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('plan', result.stderr)
        self.assertEqual(self.snapshot(), before)
        return args

    def test_native_formatter_config_byte_drift_invalidates_the_saved_plan(self):
        self.reject_config_drift('.prettierrc.json', b'{}', b'{ }')

    def test_native_package_configuration_bytes_are_part_of_the_saved_plan(self):
        args = self.reject_config_drift('package.json', b'{"prettier":{}}', b'{ "prettier": {} }')
        (self.base / 'package.json').write_bytes(b'{"prettier":{}}')
        result = run('standardize_registry_skill.py', *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['execution_acceptance'], 'pending')

    def test_native_yaml_package_configuration_bytes_are_part_of_the_saved_plan(self):
        self.reject_config_drift('package.yaml', b'prettier: {}', b'prettier: { }')


if __name__ == '__main__':
    unittest.main()
