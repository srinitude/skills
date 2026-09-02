"""Package-map, extension, and Markdown readability contracts."""
import pathlib
import unittest


SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


class TestPackageMap(unittest.TestCase):
    def setUp(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        sections = skill.split("## Package map\n", 1)
        self.package_map = sections[1].split("\n## ", 1)[0] if len(sections) == 2 else ""

    def test_package_map_explains_each_resource_type_and_trigger(self):
        header = next((line for line in self.package_map.splitlines() if line.startswith("| Path")), "")
        cells = [cell.strip() for cell in header.strip("|").split("|")]
        self.assertEqual(cells, ["Path", "Contains", "Load or run when"])
        paths = [
            "`references/`", "`assets/`", "`assets/exploration-corpus/`",
            "`evals/`", "`evals/files/`", "`examples/`", "`mise.toml`",
            "`.github/workflows/`",
        ]
        for path in paths:
            self.assertIn(path, self.package_map)
        self.assertNotIn("`scripts/`", self.package_map)

    def test_package_map_forbids_directory_only_loading(self):
        self.assertIn("A directory name does not load a file", self.package_map)
        self.assertIn("exact relative path", self.package_map)


class TestMarkdownLineBreaks(unittest.TestCase):
    def test_markdown_uses_real_lines_instead_of_html_break_tags(self):
        for path in sorted(SKILL_DIR.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            message = f"replace HTML break tags with real lines: {path}"
            pattern = r"(?i)<" + r"br\s*/?>"
            self.assertNotRegex(text, pattern, message)

    def test_execution_labels_are_intentional_line_boundaries(self):
        from scripts import lint_writing

        labels = ["**Input**", "**Action**", "**Save**", "**Pass**", "**Blocked**", "**Feeds**"]
        for label in labels:
            broke, fence = lint_writing.breaks_block(label, False)
            self.assertTrue(broke, label)
            self.assertFalse(fence, label)


class TestOpenExtensionContract(unittest.TestCase):
    def test_fixed_core_and_open_surface_are_both_explicit(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        relative = "references/extension-protocol.md"
        self.assertIn(relative, skill)
        reference = (SKILL_DIR / relative).read_text(encoding="utf-8")
        markers = ["## Fixed core", "## Open surface", "## Add one extension", "## Customization boundary"]
        for marker in markers:
            self.assertIn(marker, reference)
        dimensions = ["input", "intent", "token", "lens", "defect", "invariant", "experiment"]
        for dimension in dimensions:
            self.assertIn(dimension, reference.lower())
        self.assertIn("No catalog is a ceiling", reference)


class TestClaimScope(unittest.TestCase):
    def test_global_uniqueness_has_no_exhaustive_corpus_escape(self):
        suffixes = {".md", ".json", ".py"}
        escape = "without an exhaustive " + "comparison corpus"
        for path in sorted(SKILL_DIR.rglob("*")):
            if path.is_file() and path.suffix in suffixes:
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn(escape, text, path)


class TestComputerUseAuditContract(unittest.TestCase):
    def test_goal_specific_sources_stay_outside_the_portable_skill(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        roles = [
            "current product board or FigJam source",
            "originating audiovisual source",
            "originating transcript",
        ]
        for role in roles:
            self.assertNotIn(role, skill)
        self.assertIn("item-level source dispositions", skill)
        self.assertIn("Outside that audit", skill)

    def test_same_vision_agent_operates_portable_design_app_control(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("paramount visual-proof rule", skill)
        self.assertIn("every applicable available vision capability", skill)
        self.assertIn("before and after", skill)
        self.assertIn("platform-neutral local application-control capability", skill)
        self.assertIn("same invoking strong vision-capable executor", skill)
        self.assertIn("directly inspect the active design application", skill)
        self.assertIn("including Figma", skill)
        self.assertIn("the item is `BLOCKED`", skill)


class TestFocusIntentContract(unittest.TestCase):
    def test_token_focus_intent_has_stable_fields_and_boundary(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        fields = [
            "user_task", "focus_target", "focus_location", "focus_timing",
            "focus_mechanism", "focus_reason", "attention_sequence",
            "competing_signals", "defocus_and_recovery", "failure_evidence",
        ]
        self.assertIn("focus-intent record", skill)
        for field in fields:
            self.assertIn(f"`{field}`", skill)
        self.assertIn("does not prove product-level focus success", skill)


if __name__ == "__main__":
    unittest.main()
