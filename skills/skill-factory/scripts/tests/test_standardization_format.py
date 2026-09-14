"""Tests for repository-local formatting discovery."""
import tempfile
import unittest
from pathlib import Path
import shutil

from standardization_test_support import native_formatter

from standardization_format import formatter_command, format_contents


def _TestRepositoryFormat_test_uses_the_repository_local_prettier(self):
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp).resolve()
        target = repo / "skills/example"
        target.mkdir(parents=True)
        script = native_formatter(repo)
        command = formatter_command(target)
        self.assertEqual(command[0], [
            shutil.which("node"), str(script)])
        self.assertEqual(command[1], repo.resolve())

def _TestRepositoryFormat_test_skips_a_skill_without_a_repository_formatter(self):
    with tempfile.TemporaryDirectory() as temp:
        target = Path(temp) / "skill"
        target.mkdir()
        self.assertIsNone(formatter_command(target))

def _TestRepositoryFormat_test_configured_missing_formatter_rejects_instead_of_skipping(self):
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp).resolve(); (repo / '.git').mkdir()
        (repo / '.prettierrc.json').write_text('{}')
        target = repo / 'skills/example'; target.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'formatter is not ready'):
            formatter_command(target)

def _TestRepositoryFormat_test_supported_configurations_use_native_owner_and_output(self):
    configurations = [(".prettierrc.cjs", "module.exports = {};"),
                      ("package.json", '{"prettier": {}}'),
                      ("package.yaml", "prettier: {}"),
                      ("nested/.prettierrc.json", "{}")]
    for name, contents in configurations:
        with self.subTest(configuration=name), tempfile.TemporaryDirectory() as temp:
            repo = Path(temp).resolve(); target = repo / "skills/example"
            target.mkdir(parents=True); native_formatter(repo)
            (repo / ".prettierrc.json").unlink()
            nested = name.startswith("nested/")
            config = target / name if nested else repo / name
            config.parent.mkdir(parents=True, exist_ok=True); config.write_text(contents)
            path = "nested/value.json" if nested else "value.json"
            files = {path: b'{"value":1}'}
            result = format_contents(target, {}, files)
            self.assertIsNotNone(result)
            self.assertEqual(files[path], b'{ "value": 1 }\n')
            self.assertFalse((target / path).exists())

def _TestRepositoryFormat_test_package_without_formatter_configuration_is_not_an_owner(self):
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp).resolve(); target = repo / "skills/example"
        target.mkdir(parents=True); native_formatter(repo)
        (repo / ".prettierrc.json").unlink()
        (repo / "package.json").write_text('{"name": "example"}')
        self.assertIsNone(formatter_command(target))

def _assert_formatter_missing(self, target):
    with self.assertRaisesRegex(ValueError, "formatter is not ready"):
        formatter_command(target)

def _TestRepositoryFormat_test_commonjs_and_package_declarations_require_ready_native_formatter(self):
    for name, contents in [(".prettierrc.cjs", "module.exports = {};"),
                           ("package.json", '{"prettier": {}}'),
                           ("package.yaml", "prettier: {}")]:
        with self.subTest(configuration=name), tempfile.TemporaryDirectory() as temp:
            repo = Path(temp).resolve(); (repo / ".git").mkdir()
            target = repo / "skills/example"; target.mkdir(parents=True)
            (repo / name).write_text(contents)
            _assert_formatter_missing(self, target)


class TestRepositoryFormat(unittest.TestCase):
    test_uses_the_repository_local_prettier = _TestRepositoryFormat_test_uses_the_repository_local_prettier
    test_skips_a_skill_without_a_repository_formatter = _TestRepositoryFormat_test_skips_a_skill_without_a_repository_formatter
    test_configured_missing_formatter_rejects_instead_of_skipping = _TestRepositoryFormat_test_configured_missing_formatter_rejects_instead_of_skipping
    test_supported_configurations_use_native_owner_and_output = _TestRepositoryFormat_test_supported_configurations_use_native_owner_and_output
    test_package_without_formatter_configuration_is_not_an_owner = _TestRepositoryFormat_test_package_without_formatter_configuration_is_not_an_owner
    test_commonjs_and_package_declarations_require_ready_native_formatter = _TestRepositoryFormat_test_commonjs_and_package_declarations_require_ready_native_formatter


if __name__ == "__main__":
    unittest.main()
