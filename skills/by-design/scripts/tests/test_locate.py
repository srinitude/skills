"""Contract tests for scripts/locate.py.

Each test pins a contract a caller touches:
  1. artifact text ranks the right category first, across several disciplines
  2. the ranking names the terms and how many earned each place
  3. word endings do not hide a match, and unrelated words do not fake one
  4. a place resting on one term is reported as a weak read
  5. repeat runs give the same ranking
  6. empty input is a usage error
"""
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
LOCATE = SKILL_DIR / "scripts" / "locate.py"

TABLE = ("a sun cream packaged to look melted, label copy carrying the regulatory "
         "warnings, sold on shelf in retail, recyclable mono material")
CONSENT = ("teen conversations stay private by default, parents can opt into "
           "visibility, age assurance at signup, consent")


def run(*args):
    return subprocess.run([sys.executable, str(LOCATE), *args],
                          capture_output=True, text=True, cwd=str(SKILL_DIR))


class TestLocate(unittest.TestCase):
    def test_a_packaging_brief_ranks_physical_product_first(self):
        proc = run("--text", TABLE, "--top", "1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Physical product", proc.stdout)

    def test_text_matching_nothing_exits_one_rather_than_guessing(self):
        proc = run("--text", "zzz qqq vvv wwww", "--top", "3")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout.strip(), "")

    def test_consent_text_ranks_privacy_first(self):
        proc = run("--text", CONSENT, "--top", "1")
        self.assertIn("Privacy, consent and compliance", proc.stdout)

    def test_the_ranking_names_its_terms(self):
        proc = run("--text", TABLE, "--top", "1")
        self.assertIn("[", proc.stdout)
        self.assertIn("terms", proc.stdout)

    def test_word_endings_do_not_hide_a_match(self):
        proc = run("--text", "modular repairable parts, recycled materials", "--top", "1")
        self.assertIn("Physical product", proc.stdout)

    def test_an_unrelated_ending_does_not_fake_a_match(self):
        proc = run("--text", "an eco friendly clinic", "--top", "3")
        self.assertNotIn("[friend", proc.stdout)

    def test_a_typeface_brief_finds_typography(self):
        proc = run("--text", "a new monospaced typeface, one weight, heart dotted "
                             "i's, released with a printed specimen and letterforms "
                             "drawn against an existing grotesk", "--top", "1")
        self.assertIn("Typography", proc.stdout)

    def test_a_built_space_brief_finds_spatial(self):
        proc = run("--text", "daylight in every exam room, a planted courtyard "
                             "visible from the corridor, seating in clusters, "
                             "colour coded floors and a lowered reception desk",
                   "--top", "1")
        self.assertIn("Spatial", proc.stdout)

    def test_one_term_is_reported_as_a_weak_read(self):
        proc = run("--text", "a refreshed sonic signature", "--top", "1")
        self.assertIn("weak read", proc.stderr)

    def test_the_ranking_reports_how_many_terms_matched(self):
        proc = run("--text", TABLE, "--top", "1")
        self.assertRegex(proc.stdout, r"\d+ terms")

    def test_repeat_runs_agree(self):
        first, second = run("--text", TABLE), run("--text", TABLE)
        self.assertEqual(first.stdout, second.stdout)

    def test_empty_input_is_a_usage_error(self):
        proc = run("--text", "   ")
        self.assertEqual(proc.returncode, 2)

    def test_help_exits_zero(self):
        proc = run("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("exit codes", proc.stdout.lower())
