"""Real context changes at package promotion reject and permit current recovery."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import run, SCRIPTS
from scaffold_test_support import review_fixture
from standardization_plan import capture_files
from skill_package import inventory
from test_variant_publication_guard import PROMOTION_DRIFT
import test_standardization_review as standardization_cases
import test_variant_publication_guard as variant_cases


def interfere(script, args, changed, target):
    return subprocess.run([sys.executable, '-c', PROMOTION_DRIFT,
        str(SCRIPTS / script), str(changed), str(target.resolve()), *map(str, args)],
        capture_output=True, text=True, timeout=180)


class TestPromotionContext(unittest.TestCase):
    def test_scaffold_source_and_body_review_drift_withdraw_output_and_recover(self):
        for kind in ['source-context', 'body-context']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); target = root / kind
                args = ('--name', kind, '--description', 'Use when a package needs current promotion context.',
                        '--scope', 'user', '--dest', root)
                planned = run('scaffold_skill.py', *args, '--plan')
                self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
                plan = json.loads(planned.stdout); path, review, _ = review_fixture(self, plan)
                binding = review['context']['original_source'] if kind == 'source-context' else review['body_review']
                changed = Path(binding['path']); before = changed.read_bytes()
                apply = (*args, '--review', path)
                failed = interfere('scaffold_skill.py', apply, changed, target)
                self.assertNotEqual(changed.read_bytes(), before)
                self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
                self.assertFalse(target.exists())
                changed.write_bytes(before)
                recovered = run('scaffold_skill.py', *apply)
                self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
                self.assertEqual(json.loads(recovered.stdout)['execution_acceptance'], 'pending')
                self.assertEqual(inventory(target), {item['path']: item['sha256'] for item in plan['files']})

    def test_standardization_body_review_drift_restores_target_and_recovers(self):
        case = standardization_cases.TestStandardizationReview(); case.setUp(); self.addCleanup(case.doCleanups)
        state = case.root / 'node_modules/private-state'; state.parent.mkdir(); state.write_bytes(b'preserve local state')
        identity = state.stat().st_ino; before = capture_files(case.root.resolve())
        path, review, plan_path = case.reviewed_plan()
        changed = Path(review['body_review']['path']); original = changed.read_bytes()
        args = (*case.args, '--apply', '--plan-file', plan_path, '--review', path)
        failed = interfere('standardize_registry_skill.py', args, changed, case.root)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertNotEqual(changed.read_bytes(), original)
        self.assertEqual(capture_files(case.root.resolve()), before)
        self.assertEqual((state.read_bytes(), state.stat().st_ino), (b'preserve local state', identity))
        changed.write_bytes(original)
        recovered = run('standardize_registry_skill.py', *args)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['execution_acceptance'], 'pending')
        self.assertEqual((state.read_bytes(), state.stat().st_ino), (b'preserve local state', identity))

    def test_variant_body_review_drift_withdraws_output_and_recovers(self):
        case = variant_cases.TestVariantPublicationGuard(); case.setUp(); self.addCleanup(case.doCleanups)
        source = capture_files(case.source.resolve()); candidate = capture_files(case.candidate.resolve())
        preview = run('skill_variant.py', *case.args, '--preview')
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        planned = json.loads(preview.stdout); path, review, _ = review_fixture(self, planned['plan'])
        saved = case.base / 'publication.json'; saved.write_text(preview.stdout)
        changed = Path(review['body_review']['path']); original = changed.read_bytes()
        args = (*case.args, '--plan-file', saved, '--ledger-review', path)
        target = (case.base / case.candidate.name).resolve()
        failed = interfere('skill_variant.py', args, changed, target)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertNotEqual(changed.read_bytes(), original)
        self.assertFalse(target.exists())
        self.assertEqual(capture_files(case.source.resolve()), source)
        self.assertEqual(capture_files(case.candidate.resolve()), candidate)
        changed.write_bytes(original)
        recovered = run('skill_variant.py', *args)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['execution_acceptance'], 'pending')


if __name__ == '__main__':
    unittest.main()
