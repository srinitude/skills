"""Real public workflow calls, reviewed effects and process-separated persistence."""
import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from cli import SCRIPTS
from scaffold_test_support import review_fixture
from standardization_fixtures import profile, write_target


class TestStandardizationWorkflow(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.root = self.folder / 'clock-anchor'
        write_target(self.root)
        self.config = self.folder / 'profile.json'
        self.config.write_text(json.dumps(profile()))
        self.state = self.folder / 'state'
        self.state.mkdir(mode=0o700)
        self.args = [str(self.root), '--profile', str(self.config), '--scope', 'user']

    def invoke(self, *options, public=False, args=None, expected=0):
        command = (['mise', 'run', '--output', 'interleave', '--force', '--task-cache', 'off', 'standardize-target', '--']
                   if public else ['node', str(SCRIPTS / 'run_standardization.ts')])
        result = subprocess.run(command + (self.args if args is None else args) + list(map(str, options)),
            cwd=SCRIPTS.parent, env={**os.environ, 'UV_PYTHON': sys.executable}, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, expected, result.stdout[-2000:] + result.stderr[-2000:])
        return result

    def report(self, *options, **kwargs):
        result = self.invoke(*options, **kwargs)
        return json.loads(next(line.removeprefix('[standardize-target] ') for line in reversed(result.stdout.splitlines())
                               if line.startswith('{') or line.startswith('[standardize-target] {')))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode & 0o777)
                for p in self.root.rglob('*') if p.is_file()}

    def review(self, planned):
        path, _, _ = review_fixture(self, planned['plan'])
        saved = path.parent / 'standardization-plan.json'
        saved.write_text(json.dumps(planned))
        return ['--apply', '--plan-file', str(saved), '--review', str(path)]

    def check_output(self, planned):
        expected = {item['path']: (base64.b64decode(item['content_base64']), item['mode'])
                    for item in planned['plan']['files']}
        self.assertEqual(self.snapshot(), expected)

    def test_public_help_and_transient_plan_expose_the_real_workflow_without_target_effects(self):
        help_result = self.invoke(public=True, args=['--help'])
        self.assertIn('Workflow options:', help_result.stdout)
        self.assertIn('--placement-receipt', help_result.stdout)
        for flag in ['-h', '--h', '--he', '--hel']:
            with self.subTest(help_flag=flag):
                self.assertIn('Workflow options:', self.invoke(args=[flag]).stdout)
        before = self.snapshot()
        planned = self.report(public=True)
        self.assertEqual(planned['workflow']['status'], 'suspended')
        self.assertFalse(planned['workflow']['persistent'])
        self.assertEqual(planned['writes'], 0)
        self.assertEqual(self.snapshot(), before)

    def test_usage_and_missing_target_reject_before_state_effects(self):
        before = self.snapshot()
        for flags in [['--workflow-state=relative'], ['--workflow-state='],
                      ['--workflow-state', str(self.state), '--workflow-state=' + str(self.state)],
                      ['--workflow-state', str(self.state), '--workflow-run=' + '-' * 36]]:
            with self.subTest(flags=flags):
                self.invoke(*flags, expected=2)
        self.invoke(args=[str(self.folder / 'absent'), '--profile', str(self.config)], expected=2)
        self.assertEqual(list(self.state.iterdir()), [])
        self.assertEqual(self.snapshot(), before)

    def test_saved_plan_applies_through_a_new_transient_workflow(self):
        planned = self.report()
        applied = self.report(*self.review(planned))
        self.assertEqual(applied['workflow']['status'], 'success')
        self.assertFalse(applied['workflow']['persistent'])
        self.assertEqual(applied['execution_acceptance'], 'pending')
        self.check_output(planned)

    def test_separate_process_resumes_exact_run_then_rejects_completed_replay(self):
        options = ['--workflow-state=' + str(self.state)]
        planned = self.report(*options)
        apply = self.review(planned) + options + ['--workflow-run=' + planned['workflow']['run_id']]
        applied = self.report(*apply)
        self.assertEqual(applied['workflow']['run_id'], planned['workflow']['run_id'])
        self.assertTrue(applied['workflow']['persistent'])
        self.check_output(planned)
        calls = sorted(p.name for p in self.state.glob('*-native-command.json'))
        self.assertIn('Selected workflow is not suspended', self.invoke(*apply, expected=1).stderr)
        self.assertEqual(sorted(p.name for p in self.state.glob('*-native-command.json')), calls)
        self.check_output(planned)

    def test_database_alias_and_target_state_reject_without_file_effects(self):
        original = self.folder / 'unrelated'
        original.write_bytes(b'preserve this file')
        link = self.state / 'standardization.db-wal'
        link.symlink_to(original)
        before = self.snapshot()
        self.assertIn('Unsafe workflow database file', self.invoke('--workflow-state', self.state, expected=1).stderr)
        self.assertEqual(original.read_bytes(), b'preserve this file')
        self.assertEqual(list(self.state.iterdir()), [link])
        self.assertIn('Workflow state must be outside the target', self.invoke('--workflow-state', self.root, expected=1).stderr)
        self.assertEqual(self.snapshot(), before)


    def test_explicit_rejection_closes_run_without_apply_and_fresh_review_recovers(self):
        before = self.snapshot()
        self.assertIn('Rejection requires a suspended run', self.invoke('--workflow-reject', expected=2).stderr)
        options = ['--workflow-state', str(self.state)]
        planned = self.report(*options)
        selected = options + ['--workflow-run', planned['workflow']['run_id']]
        calls = sorted(p.name for p in self.state.glob('*-native-command.json'))
        rejected = self.invoke(*selected, '--workflow-reject', public=True, expected=1)
        self.assertIn('Standardization review rejected', rejected.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(sorted(p.name for p in self.state.glob('*-native-command.json')), calls)
        self.assertIn('Selected workflow is not suspended', self.invoke(*selected, '--workflow-reject', expected=1).stderr)
        recovered = self.report(*options)
        self.assertNotEqual(recovered['workflow']['run_id'], planned['workflow']['run_id'])
        applied = self.report(*self.review(recovered), *options, '--workflow-run', recovered['workflow']['run_id'])
        self.assertEqual(applied['workflow']['status'], 'success')
        self.check_output(recovered)


if __name__ == '__main__':
    unittest.main()
