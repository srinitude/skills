"""Real stale-input and no-staging checks for reviewed standardization."""
import json
import subprocess
import sys
import unittest

from cli import run, SCRIPTS
import test_standardization_review as fixtures


class TestStandardizationBoundaries(unittest.TestCase):
    def setUp(self):
        self.case = fixtures.TestStandardizationReview()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.review, self.record, self.plan = self.case.reviewed_plan()
        self.args = (*self.case.args, '--apply', '--plan-file', self.plan, '--review', self.review)

    def guarded_attempt(self):
        marker = self.case.base / 'unexpected-stage-attempt'
        code = """import pathlib,sys
sys.path.insert(0,sys.argv[1])
from standardize_registry_skill import main
marker=pathlib.Path(sys.argv[2])
def observe(event,args):
    if event=='tempfile.mkdtemp' and pathlib.Path(args[0]).name.startswith('.skill-stage-'):
        marker.write_text('stage attempted')
sys.addaudithook(observe)
sys.exit(main(sys.argv[3:]))
"""
        result = subprocess.run([sys.executable, '-c', code, str(SCRIPTS), str(marker),
                                 *(str(arg) for arg in self.args)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), result.stdout + result.stderr)
        return result

    def test_profile_byte_drift_rejects_before_stage_then_recovers(self):
        raw = self.case.config.read_bytes()
        self.case.config.write_bytes(raw + b' ')
        before = self.case.snapshot()
        self.assertIn('plan', self.guarded_attempt().stderr)
        self.assertEqual(self.case.snapshot(), before)
        self.case.config.write_bytes(raw)
        result = run('standardize_registry_skill.py', *self.args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_file_and_directory_mode_drift_reject_before_stage(self):
        for path in [self.case.root / 'scripts/anchor.py', self.case.root / 'scripts']:
            mode = path.stat().st_mode & 0o777
            with self.subTest(path=path):
                path.chmod(0o700 if mode != 0o700 else 0o750)
                before = self.case.snapshot()
                self.guarded_attempt()
                self.assertEqual(self.case.snapshot(), before)
                self.assertNotEqual(path.stat().st_mode & 0o777, mode)
                path.chmod(mode)
        result = run('standardize_registry_skill.py', *self.args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_last_file_and_initial_body_reviews_reject_before_stage(self):
        original = self.review.read_bytes()
        last = next(reversed(self.record['files']))
        self.record['files'][last]['review']['Contribution'] = ''
        self.review.write_text(json.dumps(self.record))
        before = self.case.snapshot()
        self.assertIn('review', self.guarded_attempt().stderr)
        self.assertEqual(self.case.snapshot(), before)
        self.review.write_bytes(original)
        from pathlib import Path
        body = Path(self.record['body_review']['path'])
        body.write_bytes(body.read_bytes() + b' ')
        self.assertIn('body review', self.guarded_attempt().stderr)
        self.assertEqual(self.case.snapshot(), before)

    def test_review_flags_have_one_grammar(self):
        result = run('standardize_registry_skill.py', *self.case.args, '--review', self.review)
        self.assertEqual(result.returncode, 2)
        self.assertIn('require --apply', result.stderr)


if __name__ == '__main__':
    unittest.main()
