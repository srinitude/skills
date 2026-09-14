"""Variant publication must consume a complete ledger review before effects."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(FACTORY / 'scripts/tests'), str(FACTORY / 'scripts')]
from cli import run
from scaffold_test_support import review_fixture
from test_skill_variant import plan
from variant_fixtures import package, project, review, write_json
from skill_package import inventory


PROMOTION_DRIFT = """import pathlib,runpy,sys
entry,source,target,*arguments=sys.argv[1:]
path=pathlib.Path(source); fired=[]
def drift(event,args):
    if event=='os.rename' and str(args[1])==target and '.skill-stage-' in str(args[0]) and not fired:
        fired.append(True); path.write_bytes(path.read_bytes()+b'independent edit\\n')
sys.addaudithook(drift)
sys.path.insert(0,str(pathlib.Path(entry).parent)); sys.argv=[entry,*arguments]
runpy.run_path(entry,run_name='__main__')
"""


def _TestVariantPublicationGuard_setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.base = Path(temporary.name)
    self.source = package(self.base / 'source/demo-skill', 'project')
    self.candidate = package(self.base / 'candidate/portable-inventory', 'user')
    atlas = project(self.base / 'atlas')
    boreal = project(self.base / 'boreal', 'repo:boreal', 'lib', '.js')
    result = plan(self.source, self.base, 'user', self.candidate.name)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.plan = json.loads(result.stdout)
    write_json(self.base / 'plan.json', self.plan)
    write_json(self.base / 'review.json', review(self.source, self.candidate,
               [(atlas, 'Python src'), (boreal, 'JavaScript lib')]))
    self.args = ('accept', '--plan', self.base / 'plan.json',
                 '--candidate', self.candidate, '--review', self.base / 'review.json')

def _TestVariantPublicationGuard_test_missing_ledger_review_rejects_before_publication(self):
    before = inventory(self.source), inventory(self.candidate)
    result = run('skill_variant.py', *self.args)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn('ledger', result.stdout.lower())
    self.assertFalse((self.base / self.candidate.name).exists())
    self.assertEqual((inventory(self.source), inventory(self.candidate)), before)

def _TestVariantPublicationGuard_test_preview_contains_every_future_file_without_publishing(self):
    before = inventory(self.source), inventory(self.candidate)
    result = run('skill_variant.py', *self.args, '--preview')
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    publication = json.loads(result.stdout)['plan']
    files = {item['path']: item for item in publication['files']}
    self.assertEqual(set(files), set(inventory(self.candidate)) | {'evals/source-lineage.json'})
    self.assertIn('content_base64', files['evals/source-lineage.json'])
    self.assertEqual(publication['execution_acceptance'], 'pending')
    self.assertFalse((self.base / self.candidate.name).exists())
    self.assertEqual((inventory(self.source), inventory(self.candidate)), before)

def _TestVariantPublicationGuard_test_incomplete_review_and_mode_drift_reject_then_current_review_publishes(self):
    result = run('skill_variant.py', *self.args, '--preview')
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    publication = json.loads(result.stdout)
    path, record, _ = review_fixture(self, publication['plan'])
    saved = self.base / 'publication.json'; write_json(saved, publication)
    complete = path.read_bytes()
    record['files'].pop(next(reversed(record['files'])))
    write_json(path, record)
    apply = (*self.args, '--plan-file', saved, '--ledger-review', path)
    rejected = run('skill_variant.py', *apply)
    self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
    self.assertIn('every planned file', rejected.stdout)
    self.assertFalse((self.base / self.candidate.name).exists())
    path.write_bytes(complete)
    changed = self.candidate / 'SKILL.md'; mode = changed.stat().st_mode & 0o777
    changed.chmod(0o600 if mode != 0o600 else 0o644)
    rejected = run('skill_variant.py', *apply)
    self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
    self.assertFalse((self.base / self.candidate.name).exists())
    changed.chmod(mode)
    result = run('skill_variant.py', *apply)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    expected = {item['path']: item['sha256'] for item in publication['plan']['files']}
    self.assertEqual(inventory(self.base / self.candidate.name), expected)
    self.assertEqual(json.loads(result.stdout)['execution_acceptance'], 'pending')

def _TestVariantPublicationGuard_test_source_drift_during_promotion_is_retained_and_publication_is_withdrawn(self):
    result = run('skill_variant.py', *self.args, '--preview')
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    publication = json.loads(result.stdout)
    path, _, _ = review_fixture(self, publication['plan'])
    saved = self.base / 'publication.json'; write_json(saved, publication)
    apply = (*self.args, '--plan-file', saved, '--ledger-review', path)
    target = (self.base / self.candidate.name).resolve()
    changed = self.source / 'NOTICE'; before = changed.read_bytes()
    result = subprocess.run([sys.executable, '-c', PROMOTION_DRIFT,
        str(FACTORY / 'scripts/skill_variant.py'), str(changed), str(target), *map(str, apply)],
        capture_output=True, text=True, timeout=180)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn('source changed', result.stdout)
    self.assertFalse(target.exists())
    self.assertEqual(changed.read_bytes(), before + b'independent edit\n')
    changed.write_bytes(before)
    result = run('skill_variant.py', *apply)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual(inventory(target), {x['path']:x['sha256'] for x in publication['plan']['files']})


class TestVariantPublicationGuard(unittest.TestCase):
    setUp = _TestVariantPublicationGuard_setUp
    test_missing_ledger_review_rejects_before_publication = _TestVariantPublicationGuard_test_missing_ledger_review_rejects_before_publication
    test_preview_contains_every_future_file_without_publishing = _TestVariantPublicationGuard_test_preview_contains_every_future_file_without_publishing
    test_incomplete_review_and_mode_drift_reject_then_current_review_publishes = _TestVariantPublicationGuard_test_incomplete_review_and_mode_drift_reject_then_current_review_publishes
    test_source_drift_during_promotion_is_retained_and_publication_is_withdrawn = _TestVariantPublicationGuard_test_source_drift_during_promotion_is_retained_and_publication_is_withdrawn


if __name__ == '__main__':
    unittest.main()
