"""Actual guarded catalog inputs, native schema drift and reviewed recovery."""
import copy
import json
import subprocess
import sys
import unittest

from cli import run
import test_review_ledger_write as writes
from sync_mise_primitives import catalog
from skill_package import package_lock


def schema():
    return {
        "properties": {"tasks": {}, "tools": {}, "min_version": {}},
        "$defs": {
            "task_props": {"properties": {"run": {}, "depends": {}}},
            "task": {"oneOf": [{}, {}, {"allOf": [{}, {
                "properties": {"extends": {}}}]}]},
            "task_config": {"properties": {"dir": {}}},
            "tool_options": {"properties": {"version": {}, "os": {}}},
            "tool": {"oneOf": [{}, {"allOf": [{}, {
                "properties": {"lazy": {}, "postinstall": {}}}]}]},
        },
    }


INTERFERENCE = '''import json,sys
from pathlib import Path
from sync_mise_primitives import main
root, request, schema_file = map(Path,sys.argv[1:4])
target = root / 'assets/mise-primitives-catalog.json'
subject = schema_file if sys.argv[4] == 'schema' else request
original, armed = subject.read_bytes(), False
def interfere(event,args):
    global armed
    if event in {'os.rename','os.link'} and args[1] == str(target):
        armed = True
    elif event == 'open' and args[0] == str(subject) and armed:
        armed = False
        value = json.loads(original)
        if sys.argv[4] == 'schema':
            value['properties']['new-key'] = {}
        else:
            value['change']['reviewer'] += ' changed'
        subject.write_text(json.dumps(value))
sys.addaudithook(interfere)
sys.exit(main([str(root),'--version','9.9.9','--schema-file',str(schema_file),'--review',str(request)]))
'''


class TestCatalogReview(unittest.TestCase):
    package = writes.TestLedgerWrite.package

    def setUp(self):
        writes.TestLedgerWrite.setUp(self)
        (self.root / 'assets').mkdir()
        self.target = self.root / 'assets/mise-primitives-catalog.json'
        self.target.write_text('{"version":"old","groups":{}}\n')
        self.schema_path = self.folder / 'schema.json'
        self.schema_path.write_text(json.dumps(schema()))
        self.decisions = self.root / 'assets/mise-primitives.json'
        self.decisions.write_text('{"keep":"unchanged"}')
        self.request['change']['path'] = 'assets/mise-primitives-catalog.json'
        self.request_path = self.folder / 'catalog-request.json'
        self.prepare()

    def prepare(self):
        self.prepared.write_text(json.dumps(catalog('9.9.9', self.schema_path.read_bytes()), indent=2) + '\n')
        self.request['change']['expected_sha256'] = writes.sha(self.target.read_bytes())
        self.request['change']['new_file']['sha256'] = writes.sha(self.prepared.read_bytes())
        self.request_path.write_text(json.dumps(self.request))

    def invoke(self, *extra, review=True):
        options = ['--review', self.request_path] if review else []
        return run('sync_mise_primitives.py', self.root, '--version', '9.9.9',
                   '--schema-file', self.schema_path, *options, *extra)

    def test_missing_review_rejects_without_file_effect(self):
        before = self.package(); result = self.invoke(review=False)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('review', (result.stdout + result.stderr).lower())
        self.assertEqual(self.package(), before)

    def test_plan_is_read_only_and_review_mode_is_exclusive(self):
        before = self.package(); result = self.invoke('--plan', review=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        content = json.loads(result.stdout)['content_utf8']; planned = json.loads(content)
        self.assertEqual(planned['version'], '9.9.9')
        self.assertEqual(planned['schema_sha256'], writes.sha(self.schema_path.read_bytes()))
        self.assertEqual(content, json.dumps(planned, indent=2) + '\n')
        self.assertEqual(self.package(), before)
        for option in ['--check', '--plan']:
            result = self.invoke(option)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(self.package(), before)

    def test_current_review_preserves_mode_and_dispositions_and_rejects_stale_replay(self):
        self.target.chmod(0o640); result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.target.read_bytes(), self.prepared.read_bytes())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
        self.assertEqual(self.decisions.read_text(), '{"keep":"unchanged"}')
        self.assertEqual(self.invoke('--check', review=False).returncode, 0)
        before = self.package(); result = self.invoke()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.package(), before)

    def test_invalid_source_metadata_review_and_target_reject_then_recover(self):
        before = self.package(); original = copy.deepcopy(self.request)
        for change in [lambda r:r.pop('initial_body_review'), lambda r:r.update(change=[]),
                       lambda r:r['change'].update(path='assets/mise-primitives.json'),
                       lambda r:r['initial_body_review'].update(sha256='0'*64)]:
            request = copy.deepcopy(original); change(request); self.request_path.write_text(json.dumps(request))
            result = self.invoke(); self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(self.package(), before)
        self.prepare(); value = json.loads(self.prepared.read_bytes()); value['groups']['config'] = []
        self.prepared.write_text(json.dumps(value,indent=2)+'\n')
        self.request['change']['new_file']['sha256'] = writes.sha(self.prepared.read_bytes())
        self.request_path.write_text(json.dumps(self.request)); result = self.invoke()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr); self.assertEqual(self.package(), before)
        self.prepare(); value = json.loads(self.schema_path.read_bytes()); value['properties']['new-key'] = {}
        self.schema_path.write_text(json.dumps(value)); result = self.invoke()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr); self.assertEqual(self.package(), before)
        self.prepare(); result = self.invoke(); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_schema_or_request_drift_restores_catalog_and_current_inputs_recover(self):
        self.target.chmod(0o640)
        for kind in ['schema', 'request']:
            value = json.loads(self.schema_path.read_bytes()); value['properties'][kind] = {}
            self.schema_path.write_text(json.dumps(value))
            self.prepare(); previous = self.target.read_bytes()
            subject = self.schema_path if kind == 'schema' else self.request_path
            original = subject.read_bytes()
            result = subprocess.run([sys.executable,'-c',INTERFERENCE,str(self.root),str(self.request_path),
                                     str(self.schema_path),kind],cwd=writes.ROOT/'scripts',capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotEqual(subject.read_bytes(), original)
            self.assertEqual((self.target.read_bytes(),self.target.stat().st_mode & 0o777),(previous,0o640))
            self.prepare(); result = self.invoke(); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_schema_or_catalog_rejects_cleanly_without_effects(self):
        variants = [[], {'$defs': []}, {'$defs': {'task_props': None}},
                    {'$defs': {'task': {'oneOf': [None]}}},
                    {'$defs': {'task': {'oneOf': [{'allOf': None}]}}},
                    {'properties': []}, {'properties': None}]
        before = self.package()
        for value in variants:
            self.schema_path.write_text(json.dumps(value))
            result = self.invoke('--plan', review=False)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertEqual(self.package(), before)
        self.schema_path.write_text(json.dumps(schema()))
        self.target.write_text('[]'); before = self.package()
        result = self.invoke('--check', review=False)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.package(), before)

    def test_lock_blocks_effect_and_release_recovers(self):
        before = self.package()
        with package_lock(self.root):
            result = self.invoke(); self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.package(), before)
        result = self.invoke(); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
