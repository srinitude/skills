"""Every actual in-place file retirement requires current review and recovery."""
import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import run, SCRIPTS
from scaffold_test_support import review_fixture
from standardization_plan import capture_files
from test_skill_variant import plan
from variant_fixtures import package, project, review, write_json


POST_READ_DRIFT = """import pathlib,runpy,sys
entry,ledger,source,target,*arguments=sys.argv[1:]
ledger=pathlib.Path(ledger); source=pathlib.Path(source); state=[False,0]
def drift(event,args):
    if event=='os.rename' and str(args[1])==target and '.skill-stage-' in str(args[0]):
        state[0]=True
    if event=='open' and state[0] and str(args[0])==str(ledger):
        state[1]+=1
        if state[1]==2: source.write_bytes(source.read_bytes()+b'independent edit\\n')
sys.addaudithook(drift)
sys.path.insert(0,str(pathlib.Path(entry).parent));sys.argv=[entry,*arguments]
runpy.run_path(entry,run_name='__main__')
"""


def _TestVariantRetirement_setUp(self):
    temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
    self.root = Path(temporary.name).resolve()
    self.source = package(self.root / 'source/demo-skill', 'project')
    self.candidate = package(self.root / 'candidate/demo-skill', 'user')
    self.retired = {'scripts/obsolete_provider.py': b'VALUE = 1\n',
                    'scripts/obsolete_consumer.py': b'import obsolete_provider\n',
                    'references/obsolete.md': b'Old optional guidance.\n'}
    for name, raw in self.retired.items():
        (self.source / name).write_bytes(raw); (self.source / name).chmod(0o600)
    state = self.source / 'node_modules/private-state'; state.parent.mkdir(); state.write_bytes(b'local state')
    self.state, self.inode = state, state.stat().st_ino
    atlas = project(self.root / 'atlas'); boreal = project(self.root / 'boreal', 'repo:boreal', 'lib', '.js')
    planned = plan(self.source, self.source.parent, 'user', self.source.name, '--in-place')
    self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
    write_json(self.root / 'plan.json', json.loads(planned.stdout))
    write_json(self.root / 'domain-review.json', review(self.source, self.candidate,
               [(atlas, 'Python src'), (boreal, 'JavaScript lib')]))
    self.args = ('accept', '--plan', self.root / 'plan.json', '--candidate', self.candidate,
                 '--review', self.root / 'domain-review.json')
    self.before, self.candidate_before = capture_files(self.source), capture_files(self.candidate)

def _TestVariantRetirement_reviewed(self, complete=True):
    result = run('skill_variant.py', *self.args, '--preview')
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    publication = json.loads(result.stdout)
    path, record, _ = review_fixture(self, publication['plan'])
    for name in self.retired:
        record['files'].pop(name, None)
        if complete:
            record['files'][name] = {'reviewer': 'Test author; removal fixture only', 'review': {
                'Contribution': 'Retire the exact old optional fixture file ' + name,
                'Body decision': 'The body requires full per-retirement context reads, identities and recovery.'}}
    write_json(path, record); saved = self.root / 'publication.json'; write_json(saved, publication)
    return (*self.args, '--plan-file', saved, '--ledger-review', path), publication['plan'], record

def _TestVariantRetirement_preserved(self):
    self.assertEqual(capture_files(self.source), self.before)
    self.assertEqual(capture_files(self.candidate), self.candidate_before)
    self.assertEqual((self.state.read_bytes(), self.state.stat().st_ino), (b'local state', self.inode))

def _TestVariantRetirement_test_reviewed_removal_reports_each_effect_and_preserves_independent_state(self):
    args, publication, _ = self.reviewed()
    result = run('skill_variant.py', *args)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    output = json.loads(result.stdout)
    removals = {item['path']: item for item in output['writes'] if item.get('action') == 'retire-file'}
    self.assertEqual(set(removals), set(self.retired))
    for name, item in removals.items():
        self.assertEqual(item['old_sha256'], self.before[name]['sha256'])
        self.assertIsNone(item['new_sha256']); self.assertFalse((self.source / name).exists())
        self.assertEqual(item['execution_acceptance'], 'pending')
    self.assertEqual(set(capture_files(self.source)), {item['path'] for item in publication['files']})
    self.assertEqual(capture_files(self.candidate), self.candidate_before)
    self.assertEqual((self.state.read_bytes(), self.state.stat().st_ino), (b'local state', self.inode))

def _TestVariantRetirement_test_retired_mode_drift_rejects_without_losing_the_edit(self):
    args, _, _ = self.reviewed()
    name = next(iter(self.retired)); (self.source / name).chmod(0o640)
    current = capture_files(self.source)
    result = run('skill_variant.py', *args)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertEqual(capture_files(self.source), current)
    self.assertEqual(capture_files(self.candidate), self.candidate_before)

def _TestVariantRetirement_test_preview_names_exact_retirements_and_observed_dependency_order(self):
    _, publication, _ = self.reviewed()
    retired = publication.get('retirements', [])
    self.assertEqual({item['path'] for item in retired}, set(self.retired))
    names = [item['path'] for item in retired]
    self.assertLess(names.index('scripts/obsolete_consumer.py'), names.index('scripts/obsolete_provider.py'))
    for item in retired:
        self.assertEqual(base64.b64decode(item['content_base64']), self.retired[item['path']])
        self.assertEqual(item['mode'], 0o600)
    self.preserved()

def _TestVariantRetirement_test_missing_retirement_review_rejects_without_effect(self):
    args, _, _ = self.reviewed(complete=False)
    result = run('skill_variant.py', *args)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn('retirement', result.stdout)
    self.preserved()

def _TestVariantRetirement_test_actual_per_retirement_post_read_drift_restores_then_recovers(self):
    args, _, record = self.reviewed()
    changed = Path(record['context']['original_source']['path']); before = changed.read_bytes()
    result = subprocess.run([sys.executable, '-c', POST_READ_DRIFT,
        str(SCRIPTS / 'skill_variant.py'), record['context']['ledger'], str(changed), str(self.source),
        *map(str, args)], capture_output=True, text=True, timeout=180)
    self.assertNotEqual(changed.read_bytes(), before, result.stdout + result.stderr)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.preserved(); changed.write_bytes(before)
    recovered = run('skill_variant.py', *args)
    self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
    self.assertTrue(all(not (self.source / name).exists() for name in self.retired))


class TestVariantRetirement(unittest.TestCase):
    setUp = _TestVariantRetirement_setUp
    reviewed = _TestVariantRetirement_reviewed
    preserved = _TestVariantRetirement_preserved
    test_preview_names_exact_retirements_and_observed_dependency_order = _TestVariantRetirement_test_preview_names_exact_retirements_and_observed_dependency_order
    test_missing_retirement_review_rejects_without_effect = _TestVariantRetirement_test_missing_retirement_review_rejects_without_effect
    test_reviewed_removal_reports_each_effect_and_preserves_independent_state = _TestVariantRetirement_test_reviewed_removal_reports_each_effect_and_preserves_independent_state
    test_retired_mode_drift_rejects_without_losing_the_edit = _TestVariantRetirement_test_retired_mode_drift_rejects_without_losing_the_edit
    test_actual_per_retirement_post_read_drift_restores_then_recovers = _TestVariantRetirement_test_actual_per_retirement_post_read_drift_restores_then_recovers


if __name__ == '__main__':
    unittest.main()
