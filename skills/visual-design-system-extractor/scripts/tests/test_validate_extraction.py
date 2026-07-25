import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import yaml

import context
import validate_design_system_yaml as cli


def call(argv):
    """Run the validator and return its exit code and parsed report."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = cli.main(argv)
    return code, json.loads(buffer.getvalue())


def write_temp(text):
    """Write text to a temporary file and return its path."""
    handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
    handle.write(text)
    handle.close()
    return handle.name


def variant(replace, with_text):
    """Write a copy of the fixture with one substring replaced."""
    text = context.FIXTURE.read_text(encoding="utf-8").replace(replace, with_text, 1)
    return write_temp(text)


def mutated(edit):
    """Write a copy of the fixture after editing its parsed document."""
    data = yaml.safe_load(context.FIXTURE.read_text(encoding="utf-8"))
    edit(data)
    return write_temp(yaml.safe_dump(data, sort_keys=False, width=100))


def set_primary(data, key, value):
    """Set one field on the primary font entry."""
    data["typography"]["font_families"]["primary"][key] = value


class FixtureTests(unittest.TestCase):
    def test_the_bundled_example_passes_static_checks(self):
        code, report = call([str(context.FIXTURE), "--no-live-fonts"])
        self.assertEqual((code, report["errors"]), (0, []))

    def test_the_example_reports_three_selected_families(self):
        _, report = call([str(context.FIXTURE), "--no-live-fonts"])
        self.assertEqual(report["font_entries"], 3)

    def test_skipping_the_live_check_is_recorded(self):
        _, report = call([str(context.FIXTURE), "--no-live-fonts"])
        self.assertFalse(report["live_fonts_checked"])


class RejectionTests(unittest.TestCase):
    def assert_fails(self, path, fragment):
        code, report = call([path, "--no-live-fonts"])
        self.assertEqual(code, 1)
        self.assertTrue(any(fragment in item for item in report["errors"]), report)

    def test_a_common_family_is_rejected(self):
        path = mutated(lambda data: set_primary(data, "family", "Roboto"))
        self.assert_fails(path, "common default")

    def test_an_undeclared_google_family_is_rejected(self):
        path = mutated(lambda data: set_primary(data, "google_fonts_family", False))
        self.assert_fails(path, "google_fonts_family")

    def test_a_missing_section_is_rejected(self):
        self.assert_fails(variant("worldbuilding:", "worldbuildings:"), "Missing required")

    def test_a_duplicate_key_is_rejected(self):
        self.assert_fails(variant("meta:", "meta: {}\nmeta:"), "Invalid YAML")

    def test_a_fenced_document_is_rejected(self):
        self.assert_fails(variant("meta:", "```yaml\nmeta:"), "code fences")

    def test_a_tab_indent_is_rejected(self):
        self.assert_fails(variant("  schema:", "\tschema:"), "tab characters")

    def test_an_empty_document_is_rejected(self):
        empty = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
        empty.close()
        self.assert_fails(empty.name, "empty")


class LiveCheckTests(unittest.TestCase):
    def test_the_default_run_compares_against_the_live_catalog(self):
        code, report = call([str(context.FIXTURE)])
        self.assertEqual((code, report["live_fonts_checked"]), (0, True))

    def test_a_stale_rank_fails_the_live_comparison(self):
        def stale(data):
            data["typography"]["font_families"]["primary"]["rarity"]["popularity_rank"] = 3

        code, report = call([mutated(stale)])
        self.assertEqual(code, 1)
        self.assertTrue(any("stale" in item for item in report["errors"]), report)


class UsageTests(unittest.TestCase):
    def test_a_missing_file_exits_two(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main([str(Path("no-such-file.yaml"))]), 2)


if __name__ == "__main__":
    unittest.main()
