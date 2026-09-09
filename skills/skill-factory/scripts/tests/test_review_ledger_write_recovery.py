"""Actual filesystem interference at the write boundary using CPython audit events."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_review_ledger_write as write_cases

INTERFERENCE = '''import json, sys
from pathlib import Path
from review_ledger_write import write_file
request = json.loads(Path(sys.argv[1]).read_text())
root, independent = Path(sys.argv[2]), sys.argv[3] == 'independent'
target, source = root / request['change']['path'], Path(request['original_source']['path'])
original, armed = source.read_bytes(), False
def interfere(event, args):
    global armed
    if event in {'os.rename', 'os.link'} and args[1] == str(target):
        armed = True
    elif event == 'open' and args[0] == str(source) and armed:
        armed = False
        source.write_bytes(original + b'changed')
        if independent:
            target.write_bytes(b'independent edit')
sys.addaudithook(interfere)
try:
    write_file(request, root)
except ValueError as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
'''


class TestFileRestoration(unittest.TestCase):
    setUp = write_cases.TestLedgerWrite.setUp
    invoke = write_cases.TestLedgerWrite.invoke

    def interrupted(self, independent=False):
        request = self.folder / 'request.json'
        request.write_text(json.dumps(self.request))
        return subprocess.run([sys.executable, '-c', INTERFERENCE, str(request), str(self.root),
                               'independent' if independent else 'source-only'],
                              cwd=write_cases.ROOT / 'scripts', capture_output=True, text=True, timeout=30)

    def test_readable_source_drift_restores_create_and_replacement_then_recovers(self):
        source = Path(self.request['original_source']['path'])
        original = source.read_bytes()
        target = self.root / 'result.bin'
        for prior in [None, b'accepted contents']:
            if prior is not None:
                target.write_bytes(prior)
                self.request['change']['expected_sha256'] = write_cases.sha(prior)
            process = self.interrupted()
            self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
            self.assertIn('current write input digest mismatch', process.stderr)
            self.assertEqual(source.read_bytes(), original + b'changed')
            self.assertEqual(target.read_bytes() if target.exists() else None, prior)
            source.write_bytes(original)
        self.invoke()
        self.assertEqual(target.read_bytes(), self.prepared.read_bytes())

    def test_independent_edit_is_preserved_and_recovery_requires_rebinding(self):
        source = Path(self.request['original_source']['path'])
        original = source.read_bytes()
        process = self.interrupted(independent=True)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertIn('independently changed target was not overwritten', process.stderr)
        target = self.root / 'result.bin'
        self.assertEqual(target.read_bytes(), b'independent edit')
        source.write_bytes(original)
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(target.read_bytes(), b'independent edit')
        self.request['change']['expected_sha256'] = write_cases.sha(target.read_bytes())
        self.invoke()
        self.assertEqual(target.read_bytes(), self.prepared.read_bytes())


if __name__ == '__main__':
    unittest.main()
