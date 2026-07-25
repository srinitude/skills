import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import context
import render_preview
import yaml

SCRIPT = context.SCRIPTS / "render_preview.py"


def document():
    """Return the tested fixture as a mapping."""
    return yaml.safe_load(context.FIXTURE.read_text(encoding="utf-8"))


class FlattenTests(unittest.TestCase):
    def test_every_token_mapping_is_found(self):
        tokens = render_preview.flatten(document())
        self.assertIn("color_system.primary.ink_900", tokens)

    def test_a_css_variable_name_is_derived_from_the_path(self):
        self.assertEqual(render_preview.css_name("spacing.scale.space_200"),
                         "--spacing-scale-space-200")

    def test_a_colour_token_renders_its_hex(self):
        tokens = render_preview.flatten(document())
        token = tokens["color_system.primary.ink_900"]
        self.assertTrue(render_preview.token_value(token).startswith("#"))


class CoverageTests(unittest.TestCase):
    def test_the_fixture_covers_every_required_group(self):
        self.assertEqual(render_preview.coverage(render_preview.flatten(document())), [])

    def test_a_missing_group_is_named(self):
        stripped = document()
        stripped.pop("spacing", None)
        problems = render_preview.coverage(render_preview.flatten(stripped))
        self.assertTrue(any("spacing" in item for item in problems))


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.html = render_preview.build(document())

    def test_every_token_reaches_the_page(self):
        for path in render_preview.flatten(document()):
            self.assertIn(render_preview.css_name(path), self.html)

    def test_every_required_component_is_present(self):
        for marker in render_preview.COMPONENTS:
            self.assertIn(marker, self.html)

    def test_body_links_take_the_accent_token_in_every_mode(self):
        self.assertIn("section[data-mode] a", self.html)

    def test_the_selected_families_are_linked(self):
        self.assertIn("fonts.googleapis.com", self.html)

    def test_the_dark_block_is_absent_when_no_dark_mode_is_declared(self):
        self.assertNotIn("<section data-mode=\"dark\"", self.html)

    def test_the_dark_block_appears_when_dark_mode_is_declared(self):
        dual = document()
        dual["color_system"]["modes"] = ["light", "dark"]
        dual["color_system"]["dark"] = {"ink_dark": {
            "value": "#f2f2f2", "hex": "#f2f2f2", "usage": "Dark mode text.",
            "visual_grounding": "Inverted from the light palette.",
            "confidence": "low", "inference_basis": "Speculative inversion."}}
        self.assertIn("<section data-mode=\"dark\"", render_preview.build(dual))


class CommandTests(unittest.TestCase):
    def run_script(self, *args):
        """Run the renderer and return the completed process."""
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, check=False)

    def test_a_valid_document_renders_and_reports_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "preview.html"
            done = self.run_script(str(context.FIXTURE), "--output", str(out))
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("token_count", json.loads(done.stdout))
            self.assertIn("<html", out.read_text(encoding="utf-8"))

    def test_a_document_missing_a_group_fails_the_render(self):
        stripped = document()
        stripped.pop("radii", None)
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "thin.yaml"
            source.write_text(yaml.safe_dump(stripped), encoding="utf-8")
            done = self.run_script(str(source))
            self.assertEqual(done.returncode, 1)
            self.assertIn("radii", done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
