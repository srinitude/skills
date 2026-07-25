import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import context  # noqa: F401
import schema_tools
import yaml


def call(argv):
    """Run the command line and return its exit code with captured output."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = schema_tools.main(argv)
    return code, out.getvalue(), err.getvalue()


class SkeletonTests(unittest.TestCase):
    def test_the_skeleton_starts_with_the_first_section(self):
        code, text, _ = call(["skeleton"])
        self.assertEqual(code, 0)
        self.assertTrue(text.startswith("meta:"), text[:40])

    def test_the_skeleton_carries_the_font_rarity_fields(self):
        _, text, _ = call(["skeleton"])
        self.assertIn("google_fonts_family: true", text)
        self.assertIn("rarity_percentile:", text)

    def test_the_skeleton_matches_the_declared_section_order(self):
        _, skeleton, _ = call(["skeleton"])
        _, sections, _ = call(["sections"])
        self.assertEqual(list(yaml.safe_load(skeleton)), sections.split())


class ContractTests(unittest.TestCase):
    def test_groups_lists_the_field_detail_groups(self):
        code, text, _ = call(["groups"])
        self.assertEqual(code, 0)
        self.assertIn("foundation_tokens", text.split())

    def test_a_group_returns_parseable_yaml(self):
        code, text, _ = call(["group", "foundation_tokens"])
        self.assertEqual(code, 0)
        self.assertIn("typography.font_families.primary", yaml.safe_load(text))

    def test_a_single_field_returns_one_rule(self):
        code, text, _ = call(["field", "typography.weights"])
        self.assertEqual((code, len(yaml.safe_load(text))), (0, 1))

    def test_rules_carries_the_live_feed_and_floor(self):
        _, text, _ = call(["rules"])
        parsed = yaml.safe_load(text)["font_rules"]
        self.assertEqual(parsed["feed_url"], "https://fonts.google.com/metadata/fonts")
        self.assertEqual(parsed["min_rarity_percentile"], 70.0)

    def test_a_missing_group_exits_one(self):
        code, _, err = call(["group", "no-such-group"])
        self.assertEqual(code, 1)
        self.assertIn("group not found", err)

    def test_a_missing_field_exits_one(self):
        code, _, err = call(["field", "typography.nope"])
        self.assertEqual(code, 1)
        self.assertIn("field not found", err)


class OutputTests(unittest.TestCase):
    def test_the_output_flag_writes_a_file(self):
        target = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
        target.close()
        code, text, _ = call(["skeleton", "--output", target.name])
        self.assertEqual((code, text), (0, ""))
        self.assertIn("typography:", Path(target.name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
