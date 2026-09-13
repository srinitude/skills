"""Actual derived help, parser agreement and stale projection rejection."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SCRIPTS
from skill_package import copy_owned, inventory
from standardization_fixtures import profile, write_target


def _TestStandardizationUsage_python(self, code, *args, expected=0):
    result = subprocess.run(['uv', 'run', '--no-project', '--isolated', '--no-python-downloads',
        '--with', 'PyYAML==6.0.3', '--with', 'argparse-usage==0.1.1', 'python', '-c',
        'import sys; sys.path.insert(0, sys.argv.pop(1)); ' + code, str(SCRIPTS), *map(str, args)],
        cwd=SCRIPTS.parent, env={**os.environ, 'UV_PYTHON': sys.executable},
        capture_output=True, text=True, timeout=30)
    self.assertEqual(result.returncode, expected, result.stdout[-2000:] + result.stderr[-2000:])
    return result

def _TestStandardizationUsage_usage(self, *args, stdin=None):
    result = subprocess.run(['usage', *args], input=stdin, capture_output=True,
                            text=True, timeout=30)
    self.assertEqual(result.returncode, 0, result.stderr)
    return result.stdout

def _TestStandardizationUsage_workflow(self, factory, args, expected):
    runner = (SCRIPTS / 'run_standardization.ts').as_uri()
    code = 'import {runStandardization} from ' + json.dumps(runner) + '; await runStandardization(JSON.parse(process.argv[1]), process.argv[2]);'
    result = subprocess.run(['node', '--input-type=module', '-e', code, json.dumps(args), str(factory)],
        cwd=SCRIPTS.parent, env={**os.environ, 'UV_PYTHON': sys.executable}, capture_output=True, text=True, timeout=60)
    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
    return result

def _TestStandardizationUsage_test_native_and_usage_bindings_match_and_invalid_arguments_reject(self):
    code = 'import json; from standardization_cli import parse_args; a,w=parse_args(sys.argv[1:]); print(json.dumps([vars(a),w]))'
    valid = [
        ['target with space Ω', '--profile', 'profile with space.json', '--scope=user'],
        ['target', '--prof=p.json', '--sco=project'],
        ['--profile', 'p.json', '--', '--target'],
        ['target', '--profile', '$(touch SHOULD_NOT_EXIST); literal'],
    ]
    for arguments in valid:
        with self.subTest(arguments=arguments):
            parsed, selected = json.loads(self.python(code, *arguments).stdout)
            self.assertEqual(selected, {})
            self.assertIn(parsed['scope'], [None, 'user', 'project'])
    invalid = [
        ['target', '--profile', 'p.json', '--scope', 'invalid'],
        ['target', '--profile', 'p.json', '--review', 'r.json'],
    ]
    for arguments in invalid:
        with self.subTest(arguments=arguments):
            self.python(code, *arguments, expected=2)
    self.assertFalse((SCRIPTS.parent / 'SHOULD_NOT_EXIST').exists())

def _TestStandardizationUsage_test_missing_or_changed_projection_rejects_and_exact_restoration_recovers(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / 'skill-factory'
        (root / 'assets').mkdir(parents=True)
        (root / 'SKILL.md').write_bytes((SCRIPTS.parent / 'SKILL.md').read_bytes())
        path = root / 'assets/standardization.usage.kdl'
        spec = (SCRIPTS.parent / 'assets/standardization.usage.kdl').read_bytes()
        code = ('from pathlib import Path; import standardization_cli as c; c.FACTORY=Path(sys.argv[1]); '
                'c.parse_args(["target", "--profile", "p.json"]); print("accepted")')
        path.write_bytes(spec)
        self.assertEqual(self.python(code, root).stdout.strip(), 'accepted')
        path.write_bytes(spec + b'\n')
        self.assertIn('projection is stale', self.python(code, root, expected=1).stderr)
        path.unlink()
        self.assertIn('projection is missing', self.python(code, root, expected=1).stderr)
        path.write_bytes(spec)
        self.assertEqual(self.python(code, root).stdout.strip(), 'accepted')

def _check_shell_completion(self, path):
    for shell in ['bash', 'fish', 'nu', 'powershell', 'zsh']:
        with self.subTest(shell=shell):
            result = self.usage('complete-word', '--file', str(path), '--shell', shell,
                                '--', 'standardize-target', '--scope', '')
            self.assertIn('user', result)
            self.assertIn('project', result)


def _TestStandardizationUsage_test_current_export_retains_native_help_choices_and_workflow_notes(self):
    result = self.python('import json; from standardization_cli import checked_usage_spec, build_public_parser; '
        'p=build_public_parser(); print(json.dumps({"spec":checked_usage_spec(), '
        '"help":[a.help for a in p._actions if a.help], "notes":p.epilog}))')
    report = json.loads(result.stdout)
    exported = subprocess.run(['mise', 'run', '--jobs', '1', '--force', '--task-cache', 'off',
        '--output', 'interleave', 'standardization-usage'], cwd=SCRIPTS.parent,
        capture_output=True, text=True, timeout=30)
    self.assertEqual(exported.returncode, 0, exported.stderr)
    self.assertEqual(exported.stdout, report['spec'])
    markdown = self.usage('generate', 'markdown', '--file', '-', stdin=report['spec'])
    for text in report['help'] + report['notes'].splitlines():
        self.assertIn(text, markdown)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'usage.kdl'
        path.write_text(report['spec'])
        _check_shell_completion(self, path)


def _TestStandardizationUsage_test_workflow_rejects_stale_projection_before_state_and_current_bytes_recover(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        factory, target, state = root / 'skill-factory', root / 'clock-anchor', root / 'state'
        copy_owned(SCRIPTS.parent, factory)
        (factory / 'node_modules').symlink_to(SCRIPTS.parent / 'node_modules', target_is_directory=True)
        write_target(target)
        before = inventory(target)
        config = root / 'profile.json'
        config.write_text(json.dumps(profile()))
        state.mkdir(mode=0o700)
        asset = factory / 'assets/standardization.usage.kdl'
        current = asset.read_bytes()
        args = [str(target), '--profile', str(config), '--scope', 'user', '--workflow-state', str(state)]
        for changed, message in [(current + b'\n', 'projection is stale'), (None, 'projection is missing')]:
            asset.write_bytes(changed) if changed is not None else asset.unlink()
            self.assertIn(message, self.workflow(factory, args, 2).stderr)
            self.assertEqual(list(state.iterdir()), [])
            self.assertEqual(inventory(target), before)
        asset.write_bytes(current)
        result = self.workflow(factory, args, 0)
        self.assertEqual(json.loads(result.stdout)['workflow']['status'], 'suspended')
        self.assertEqual(inventory(target), before)


class TestStandardizationUsage(unittest.TestCase):
    python = _TestStandardizationUsage_python
    usage = _TestStandardizationUsage_usage
    test_current_export_retains_native_help_choices_and_workflow_notes = _TestStandardizationUsage_test_current_export_retains_native_help_choices_and_workflow_notes
    test_native_and_usage_bindings_match_and_invalid_arguments_reject = _TestStandardizationUsage_test_native_and_usage_bindings_match_and_invalid_arguments_reject
    workflow = _TestStandardizationUsage_workflow
    test_workflow_rejects_stale_projection_before_state_and_current_bytes_recover = _TestStandardizationUsage_test_workflow_rejects_stale_projection_before_state_and_current_bytes_recover
    test_missing_or_changed_projection_rejects_and_exact_restoration_recovers = _TestStandardizationUsage_test_missing_or_changed_projection_rejects_and_exact_restoration_recovers


if __name__ == '__main__':
    unittest.main()
