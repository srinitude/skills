"""Creation must consume a complete reviewed plan before writing skill files."""
import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SCRIPTS, run
from test_scaffold_skill import DESCRIPTION
from scaffold_test_support import review_fixture


class TestScaffoldReview(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.args = ('--name', 'demo-skill', '--description', DESCRIPTION,
                     '--scope', 'user', '--dest', self.root)

    def test_missing_review_rejects_before_any_destination_mutation(self):
        result = run('scaffold_skill.py', *self.args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('review', result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_plan_contains_actual_complete_bytes_and_writes_nothing(self):
        result = run('scaffold_skill.py', *self.args, '--plan')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan['version'], 1)
        self.assertEqual(plan['execution_acceptance'], 'pending')
        files = plan['files']; names = [item['path'] for item in files]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names[0], 'mise.toml')
        self.assertLess(names.index('scripts/tests/test_ci_contract.py'), names.index('scripts/tests/test_scripts.py'))
        self.assertLess(names.index('scripts/tests/test_scripts.py'), names.index('scripts/skill_info.py'))
        self.assertLess(names.index('scripts/skill_info.py'), names.index('SKILL.md'))
        self.assertLess(names.index('SKILL.md'), names.index('evals/evals.json'))
        for item in files:
            raw = base64.b64decode(item['content_base64'], validate=True)
            self.assertTrue(raw)
            self.assertEqual(len(item['sha256']), 64)
            self.assertEqual(len(item['source']['sha256']), 64)
        self.assertEqual(list(self.root.iterdir()), [])

    def planned(self):
        result = run('scaffold_skill.py', *self.args, '--plan')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_reviewed_creation_matches_plan_in_order_and_stays_unaccepted(self):
        plan = self.planned(); path, _, _ = review_fixture(self, plan)
        result = run('scaffold_skill.py', *self.args, '--review', path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['execution_acceptance'], 'pending')
        self.assertIn('SCAFFOLD', report['blocked_until'])
        self.assertEqual([item['path'] for item in report['writes']], [item['path'] for item in plan['files']])
        for item in plan['files']:
            self.assertEqual((self.root / 'demo-skill' / item['path']).read_bytes(), base64.b64decode(item['content_base64']))
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = run('scaffold_skill.py', *self.args, '--review', path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_stale_or_incomplete_file_review_rejects_without_mutation_then_recovers(self):
        plan = self.planned(); path, record, _ = review_fixture(self, plan)
        original = json.dumps(record)
        alterations = [lambda v: v.update(plan_sha256='0'*64),
                       lambda v: v['files'].pop('SKILL.md'),
                       lambda v: v['files']['mise.toml']['review'].pop('Body decision'),
                       lambda v: v['context'].update(ledger_sha256='0'*64)]
        for alter in alterations:
            value = json.loads(original); alter(value); path.write_text(json.dumps(value))
            result = run('scaffold_skill.py', *self.args, '--review', path)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(list(self.root.iterdir()), [])
        path.write_text(original)
        result = run('scaffold_skill.py', *self.args, '--review', path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_actual_governing_source_drift_rejects_then_recovers(self):
        plan = self.planned(); path, record, _ = review_fixture(self, plan)
        source = Path(record['context']['original_source']['path']); raw = source.read_bytes()
        source.write_bytes(raw + b'changed')
        result = run('scaffold_skill.py', *self.args, '--review', path)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])
        source.write_bytes(raw)
        result = run('scaffold_skill.py', *self.args, '--review', path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def audited(self, path):
        code = """import pathlib,runpy,sys
script=sys.argv.pop(1); destination=pathlib.Path(sys.argv[sys.argv.index('--dest')+1])
def observe(event,args):
    if event=='os.mkdir' and pathlib.Path(str(args[0])).is_relative_to(destination):
        sys.stderr.write('DESTINATION-MUTATION\\n')
sys.addaudithook(observe);sys.path.insert(0,str(pathlib.Path(script).parent))
runpy.run_path(script,run_name='__main__')
"""
        return subprocess.run([sys.executable, '-c', code, str(SCRIPTS / 'scaffold_skill.py'),
            *map(str, self.args), '--review', str(path)], capture_output=True, text=True)

    def test_last_file_review_is_checked_before_any_staging_mutation(self):
        plan = self.planned(); path, record, _ = review_fixture(self, plan)
        original = json.dumps(record)
        record['files'][plan['files'][-1]['path']]['review']['Body decision'] = ''
        path.write_text(json.dumps(record))
        result = self.audited(path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn('DESTINATION-MUTATION', result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])
        path.write_text(original)
        result = self.audited(path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('DESTINATION-MUTATION', result.stderr)


if __name__ == '__main__':
    unittest.main()
