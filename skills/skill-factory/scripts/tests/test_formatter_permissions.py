"""Selected native formatter controls reject the tested incidental configuration write."""
import json
import tempfile
import unittest
from pathlib import Path

from standardization_test_support import native_formatter
from standardization_format import format_contents, check_formatter


def _TestFormatterPermissions_setUp(self):
    temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
    self.repo = Path(temporary.name).resolve()
    self.root = self.repo / 'skills/example'; self.root.mkdir(parents=True)
    native_formatter(self.repo)
    self.target = self.root / 'value.json'; self.target.write_bytes(b'{"value":1}')

def _TestFormatterPermissions_test_native_stdin_formatting_returns_bytes_without_changing_target(self):
    before = self.target.read_bytes(); files = {'value.json': before}
    report = format_contents(self.root, {}, files)
    self.assertEqual(files['value.json'], b'{ "value": 1 }\n')
    self.assertEqual(self.target.read_bytes(), before)
    self.assertIn('--permission', report['execution_command'])
    self.assertTrue(report['files'][0]['formatted'])

def _TestFormatterPermissions_test_config_write_rejects_without_mutation_and_static_recovery_formats(self):
    marker = self.repo / 'marker.txt'; marker.write_text('preserve')
    (self.repo / '.prettierrc.json').unlink()
    config = self.repo / 'prettier.config.mjs'
    config.write_text('import {writeFileSync} from "node:fs";\nwriteFileSync(' +
                      json.dumps(str(marker)) + ', "changed");\nexport default {};\n')
    before = self.target.read_bytes()
    with self.assertRaisesRegex(ValueError, 'Access to this API has been restricted'):
        format_contents(self.root, {}, {'value.json': before})
    self.assertEqual(marker.read_text(), 'preserve')
    self.assertEqual(self.target.read_bytes(), before)
    config.write_text('export default {};\n')
    files = {'value.json': before}; format_contents(self.root, {}, files)
    self.assertEqual(files['value.json'], b'{ "value": 1 }\n')

def _TestFormatterPermissions_test_nested_configuration_drift_invalidates_its_consumer(self):
    nested = self.root / 'nested'; nested.mkdir()
    config = nested / '.prettierrc.json'; config.write_text('{"tabWidth": 2}')
    target = nested / 'value.json'; target.write_text('{"value": 1}')
    files = {'nested/value.json': target.read_bytes()}
    report = format_contents(self.root, {}, files)
    config.write_text('{"tabWidth": 3}')
    with self.assertRaisesRegex(ValueError, 'formatter inputs changed'):
        check_formatter(report)


class TestFormatterPermissions(unittest.TestCase):
    setUp = _TestFormatterPermissions_setUp
    test_native_stdin_formatting_returns_bytes_without_changing_target = _TestFormatterPermissions_test_native_stdin_formatting_returns_bytes_without_changing_target
    test_config_write_rejects_without_mutation_and_static_recovery_formats = _TestFormatterPermissions_test_config_write_rejects_without_mutation_and_static_recovery_formats
    test_nested_configuration_drift_invalidates_its_consumer = _TestFormatterPermissions_test_nested_configuration_drift_invalidates_its_consumer


if __name__ == '__main__':
    unittest.main()
