"""Explicit file mode changes retain exact byte and review guards."""
import copy
import unittest

import test_review_ledger_write as fixtures


def _TestLedgerModes_setUp(self):
    self.case = fixtures.TestLedgerWrite()
    self.case.setUp()
    self.addCleanup(self.case.doCleanups)
    self.case.request['change']['mode'] = {'expected': None, 'new': 0o600}

def _TestLedgerModes_test_creation_and_mode_only_replacement_use_the_native_route(self):
    case = self.case
    result = case.native()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    target = case.root / 'result.bin'
    original = target.read_bytes()
    self.assertEqual(target.stat().st_mode & 0o777, 0o600)
    case.request['change'].update(expected_sha256=fixtures.sha(original),
                                  mode={'expected': 0o600, 'new': 0o755})
    result = case.native()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual(target.read_bytes(), original)
    self.assertEqual(target.stat().st_mode & 0o777, 0o755)
    before = case.package()
    result = case.native()
    self.assertNotEqual(result.returncode, 0)
    self.assertEqual(case.package(), before)

def _TestLedgerModes_test_invalid_or_stale_modes_reject_before_writing_and_valid_review_recovers(self):
    case = self.case
    before = case.package()
    for mode in [None, {}, {'expected': None, 'new': True}, {'expected': None, 'new': 0o4755},
                 {'expected': None, 'new': -1}, {'expected': 0o644, 'new': 0o600},
                 {'expected': None, 'new': 0o600, 'other': 1}]:
        request = copy.deepcopy(case.request)
        request['change']['mode'] = mode
        with self.assertRaises(ValueError):
            case.invoke(request)
        self.assertEqual(case.package(), before)
    case.invoke()
    self.assertEqual((case.root / 'result.bin').stat().st_mode & 0o777, 0o600)


class TestLedgerModes(unittest.TestCase):
    setUp = _TestLedgerModes_setUp
    test_creation_and_mode_only_replacement_use_the_native_route = _TestLedgerModes_test_creation_and_mode_only_replacement_use_the_native_route
    test_invalid_or_stale_modes_reject_before_writing_and_valid_review_recovers = _TestLedgerModes_test_invalid_or_stale_modes_reject_before_writing_and_valid_review_recovers


if __name__ == '__main__':
    unittest.main()
