"""Contract tests for scripts/yamlread.py.

Each test pins a contract a caller touches:
  1. the bundled reader agrees with an installed parser on every file
  2. quoted text keeps its punctuation, including embedded quotes
  3. inline lists come back as lists
  4. a file holding several top level keys returns only the one asked for
  5. a missing file exits 1 and a bad key returns nothing
"""
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import yamlread  # noqa: E402

QUESTIONS = sorted((SKILL_DIR / "assets" / "questions").glob("*.yaml"))


class TestReader(unittest.TestCase):
    def test_bundled_reader_agrees_with_installed_parser(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("no installed parser to compare against")
        for path in QUESTIONS:
            text = path.read_text(encoding="utf-8")
            self.assertEqual(yamlread.parse(text, "questions"),
                             yaml.safe_load(text)["questions"], path.name)

    def test_index_agrees_too(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("no installed parser to compare against")
        text = (SKILL_DIR / "assets" / "index.yaml").read_text(encoding="utf-8")
        self.assertEqual(yamlread.parse(text, "categories"),
                         yaml.safe_load(text)["categories"])

    def test_one_key_stops_at_the_next_top_level_key(self):
        sample = ('strong:\n  - name: "screen"\n'
                  'weak:\n  - name: "table"\n'
                  'exclusions:\n  - name: "pdf"\n')
        self.assertEqual(yamlread.parse(sample, "strong"), [{"name": "screen"}])
        self.assertEqual(yamlread.parse(sample, "weak"), [{"name": "table"}])
        self.assertEqual(yamlread.parse(sample, "exclusions"), [{"name": "pdf"}])

    def test_every_tier_of_the_gate_vocabulary_stays_separate(self):
        text = (SKILL_DIR / "assets" / "gate-terms.yaml").read_text(encoding="utf-8")
        tiers = {tier: [row["name"] for row in yamlread.parse(text, tier)]
                 for tier in ("strong", "weak", "verbs", "exclusions")}
        self.assertIn("screen", tiers["strong"])
        self.assertNotIn("table", tiers["strong"])
        self.assertNotIn("pdf", tiers["strong"])
        self.assertEqual(sum(len(names) for names in tiers.values()),
                         len({name for names in tiers.values() for name in names}))

    def test_quoted_text_keeps_its_punctuation(self):
        sample = 'questions:\n  - id: "Q1"\n    question: "a \\"quoted\\" word, and a colon: here"\n'
        self.assertEqual(yamlread.parse(sample, "questions")[0]["question"],
                         'a "quoted" word, and a colon: here')

    def test_inline_lists_parse_as_lists(self):
        sample = 'questions:\n  - id: "Q1"\n    applies_to: ["screen", "flow"]\n'
        self.assertEqual(yamlread.parse(sample, "questions")[0]["applies_to"],
                         ["screen", "flow"])

    def test_confidence_parses_as_a_number(self):
        sample = 'questions:\n  - id: "Q1"\n    confidence: 0.87\n'
        self.assertEqual(yamlread.parse(sample, "questions")[0]["confidence"], 0.87)

    def test_missing_file_exits_one(self):
        proc = subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "yamlread.py"),
                               "assets/questions/nope.yaml"],
                              capture_output=True, text=True, cwd=str(SKILL_DIR))
        self.assertEqual(proc.returncode, 1)

    def test_every_shard_holds_records(self):
        self.assertEqual(len(QUESTIONS), 35)
        for path in QUESTIONS:
            self.assertTrue(yamlread.parse(path.read_text(encoding="utf-8"),
                                           "questions"), path.name)
