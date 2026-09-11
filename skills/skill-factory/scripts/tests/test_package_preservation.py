"""Preserve excluded user/runtime state when promoting a reviewed owned-file package."""
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from skill_package import inventory, promote


def _TestPackagePreservation_setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.base = Path(temporary.name)
    self.target = self.base / 'target'
    self.stage = self.base / 'stage'
    self.target.mkdir(); self.stage.mkdir()
    (self.target / 'SKILL.md').write_bytes(b'old body')
    (self.stage / 'SKILL.md').write_bytes(b'reviewed body')
    for name in ['.git', 'node_modules']:
        (self.target / name).mkdir()
        file = self.target / name / 'private-data'
        file.write_bytes(b'preserve\x00\xff'); file.chmod(0o600)
    self.before = inventory(self.target)
    self.inodes = {name: (self.target / name).stat().st_ino for name in ['.git', 'node_modules']}

def _TestPackagePreservation_check_unowned(self):
    for name, inode in self.inodes.items():
        self.assertEqual((self.target / name).stat().st_ino, inode)
        file = self.target / name / 'private-data'
        self.assertEqual(file.read_bytes(), b'preserve\x00\xff')
        self.assertEqual(file.stat().st_mode & 0o777, 0o600)

def _TestPackagePreservation_test_empty_directories_and_directory_permissions_are_preserved(self):
    (self.target / 'empty').mkdir(mode=0o700)
    self.target.chmod(0o750)
    promote(self.stage, self.target, self.before, preserve_unowned=True)
    self.assertTrue((self.target / 'empty').is_dir())
    self.assertEqual((self.target / 'empty').stat().st_mode & 0o777, 0o700)
    self.assertEqual(self.target.stat().st_mode & 0o777, 0o750)

def _TestPackagePreservation_test_promotion_moves_unowned_state_without_copying_or_losing_it(self):
    promote(self.stage, self.target, self.before, preserve_unowned=True)
    self.assertEqual((self.target / 'SKILL.md').read_bytes(), b'reviewed body')
    self.check_unowned()

def _TestPackagePreservation_test_unowned_collision_restores_prior_moves_and_original_target(self):
    (self.stage / 'node_modules').mkdir()
    (self.stage / 'node_modules' / 'different').write_bytes(b'independent stage data')
    with self.assertRaises(ValueError):
        promote(self.stage, self.target, self.before, preserve_unowned=True)
    self.assertEqual(inventory(self.target), self.before)
    self.check_unowned()
    self.assertEqual((self.stage / 'node_modules/different').read_bytes(), b'independent stage data')

def _TestPackagePreservation_test_live_guard_runs_under_lock_before_any_directory_move(self):
    (self.target / 'SKILL.md').chmod(0o600)
    def check():
        self.assertTrue((self.base / '.target.skill-lock').is_file())
        if (self.target / 'SKILL.md').stat().st_mode & 0o777 != 0o644:
            raise ValueError('stale mode')
    with self.assertRaisesRegex(ValueError, 'stale mode'):
        promote(self.stage, self.target, self.before, check=check)
    self.assertEqual(inventory(self.target), self.before)
    self.assertTrue(self.stage.is_dir())
    self.check_unowned()

def _TestPackagePreservation_test_failed_final_guard_restores_the_whole_previous_package(self):
    def verify(backup):
        self.assertEqual((backup / "SKILL.md").read_bytes(), b"old body")
        self.assertEqual(inventory(backup), self.before)
        self.assertEqual((self.target / 'SKILL.md').read_bytes(), b'reviewed body')
        raise ValueError('current proof changed during promotion')
    with self.assertRaisesRegex(ValueError, 'current proof changed'):
        promote(self.stage, self.target, self.before, preserve_unowned=True, verify=verify)
    self.assertEqual(inventory(self.target), self.before)
    self.check_unowned()
    self.assertEqual((self.stage / 'SKILL.md').read_bytes(), b'reviewed body')

def _TestPackagePreservation_test_failed_restoration_retains_backup_for_real_recovery(self):
    code = """import pathlib,sys
sys.path.insert(0,sys.argv[1])
from skill_package import inventory,promote
target=pathlib.Path(sys.argv[2]);stage=pathlib.Path(sys.argv[3])
def deny(event,args):
    if event=='os.rename' and str(args[1])==str(target):
        raise PermissionError('Audit boundary denies promotion and immediate restoration')
sys.addaudithook(deny)
promote(stage,target,inventory(target),preserve_unowned=True)
"""
    result = subprocess.run([sys.executable, '-c', code, str(SCRIPTS), str(self.target), str(self.stage)],
                            capture_output=True, text=True)
    self.assertNotEqual(result.returncode, 0)
    backups = list(self.base.glob('.skill-backup-*/target'))
    self.assertEqual(len(backups), 1, result.stdout + result.stderr)
    self.assertEqual((backups[0] / 'SKILL.md').read_bytes(), b'old body')
    backups[0].rename(self.target)
    self.assertEqual(inventory(self.target), self.before)
    self.check_unowned()


class TestPackagePreservation(unittest.TestCase):
    setUp = _TestPackagePreservation_setUp
    check_unowned = _TestPackagePreservation_check_unowned
    test_promotion_moves_unowned_state_without_copying_or_losing_it = _TestPackagePreservation_test_promotion_moves_unowned_state_without_copying_or_losing_it
    test_unowned_collision_restores_prior_moves_and_original_target = _TestPackagePreservation_test_unowned_collision_restores_prior_moves_and_original_target
    test_live_guard_runs_under_lock_before_any_directory_move = _TestPackagePreservation_test_live_guard_runs_under_lock_before_any_directory_move
    test_failed_final_guard_restores_the_whole_previous_package = _TestPackagePreservation_test_failed_final_guard_restores_the_whole_previous_package
    test_empty_directories_and_directory_permissions_are_preserved = _TestPackagePreservation_test_empty_directories_and_directory_permissions_are_preserved
    test_failed_restoration_retains_backup_for_real_recovery = _TestPackagePreservation_test_failed_restoration_retains_backup_for_real_recovery


if __name__ == '__main__':
    unittest.main()
