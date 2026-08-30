"""Contract tests for scripts/slice.py.

Each test pins a contract a caller touches:
  1. a category slice returns rows and exits 0
  2. the widening ladder reports every coordinate it drops
  3. the limit flag caps the row count
  4. both formats carry the question text
  5. an unknown category is a usage error, not an empty answer
  6. repeat runs are byte identical, and a known pin returns a known first id
"""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SLICE = SKILL_DIR / "scripts" / "slice.py"


def run(*args):
    return subprocess.run([sys.executable, str(SLICE), *args],
                          capture_output=True, text=True, cwd=str(SKILL_DIR))


class TestSlice(unittest.TestCase):
    def test_category_slice_returns_rows(self):
        proc = run("--category", "Accessibility", "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = json.loads(proc.stdout)["questions"]
        self.assertTrue(rows)
        self.assertEqual(rows[0]["category"], "Accessibility")

    def test_widening_names_every_dropped_coordinate(self):
        proc = run("--category", "Color, theming and dark mode",
                   "--stage", "concept", "--applies-to", "artifact")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("widened", proc.stderr)
        self.assertIn("applies-to", proc.stderr)

    def test_limit_caps_the_row_count(self):
        proc = run("--category", "Accessibility", "--limit", "7",
                   "--format", "json")
        self.assertEqual(len(json.loads(proc.stdout)["questions"]), 7)

    def test_both_formats_carry_the_question_text(self):
        as_json = run("--category", "Forms and input", "--limit", "3",
                      "--format", "json")
        first = json.loads(as_json.stdout)["questions"][0]["question"]
        as_md = run("--category", "Forms and input", "--limit", "3",
                    "--format", "md")
        self.assertIn(first, as_md.stdout)

    def test_unknown_category_is_a_usage_error(self):
        proc = run("--category", "Nonexistent shelf")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown category", proc.stderr.lower())

    def test_missing_category_is_a_usage_error(self):
        proc = run("--limit", "3")
        self.assertEqual(proc.returncode, 2)

    def test_lens_filter_narrows_the_result(self):
        wide = run("--category", "Pricing, checkout and billing",
                   "--limit", "500", "--format", "json")
        lensed = run("--category", "Pricing, checkout and billing",
                     "--lens", "ethics", "--limit", "500", "--format", "json")
        self.assertLess(len(json.loads(lensed.stdout)["questions"]),
                        len(json.loads(wide.stdout)["questions"]))

    def test_repeat_runs_are_byte_identical(self):
        args = ("--category", "Navigation, IA and search", "--stage",
                "pre-ship", "--limit", "12", "--format", "json")
        first, second = run(*args), run(*args)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, second.stderr)

    def test_a_known_pin_returns_a_known_first_id(self):
        proc = run("--category", "Accessibility", "--limit", "1",
                   "--format", "json")
        rows = json.loads(proc.stdout)["questions"]
        self.assertEqual(rows[0]["id"], "Q01289")

    def test_a_match_that_finds_nothing_widens_instead_of_failing(self):
        proc = run("--category", "Empty, loading, error and edge states",
                   "--match", "out of stock", "--limit", "3")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dropped match", proc.stderr)

    def test_a_match_that_finds_something_is_kept(self):
        proc = run("--category", "Empty, loading, error and edge states",
                   "--match", "placeholder", "--limit", "4", "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["widened"], [])
        for row in payload["questions"]:
            blob = " ".join([row["question"], row["tension"],
                             row["failure_it_catches"], row["subcategory"]]).lower()
            self.assertIn("placeholder", blob)

    def test_a_match_on_a_subcategory_name_is_kept(self):
        proc = run("--category", "Game feel, teaching and difficulty",
                   "--match", "hud", "--limit", "4", "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["widened"], [])
        self.assertTrue(payload["questions"])

    def test_a_thin_match_widens_the_other_pins(self):
        proc = run("--category", "Platform conventions and responsive fit",
                   "--stage", "pre-ship", "--match", "touch", "--limit", "6")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dropped stage", proc.stderr)

    def test_help_exits_zero(self):
        proc = run("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("exit codes", proc.stdout.lower())
