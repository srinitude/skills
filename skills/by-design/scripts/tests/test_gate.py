"""Contract tests for scripts/gate.py.

Each test pins a contract a caller touches:
  1. a clear design request passes the gate
  2. a request naming another craft stops at the gate
  3. an unfamiliar request continues, because the gate continues by default
  4. a design surface overrides a named craft
  5. the verdict names every term that matched
  6. repeat runs give the same verdict
  7. empty input is a usage error
"""
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
GATE = SKILL_DIR / "scripts" / "gate.py"

DESIGN = [
    "review this checkout screen for me",
    "here's the orders table before we ship it, what am I missing",
    "which of these two onboarding directions should we go with",
    "we're adding bulk export to the reports page next sprint, nothing designed yet",
    "for the settings page I'm going to use the same 12 column grid",
    "does this landing page look generic compared to our competitors",
]
DESIGN += [
    "we are deciding whether teen conversations stay private or parents can see them",
    "at what point does the user become responsible for a mistake the system made",
    "have we explained why we did this here, or only that we did",
]
NOT_DESIGN = [
    "what time is my next meeting",
    "fix the failing test in auth.py",
    "extract the tables from this PDF report",
    "rewrite this launch tweet in my voice",
    "design a database schema for users and orders",
    "what is the weather tomorrow",
    "resolve the merge conflict in main.py",
    "write a sql query joining orders and users",
]


def run(text):
    return subprocess.run([sys.executable, str(GATE), "--text", text],
                          capture_output=True, text=True, cwd=str(SKILL_DIR))


class TestGate(unittest.TestCase):
    def test_design_requests_pass(self):
        for text in DESIGN:
            proc = run(text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(proc.stdout.startswith("design:"), text)

    def test_non_design_requests_stop(self):
        for text in NOT_DESIGN:
            proc = run(text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(proc.stdout.startswith("not-design:"), text)

    def test_an_unfamiliar_request_continues(self):
        proc = run("does the second column still read as secondary at this width")
        self.assertTrue(proc.stdout.startswith("design:"), proc.stdout)

    def test_a_design_surface_overrides_a_named_craft(self):
        proc = run("extract the design tokens from this screenshot")
        self.assertTrue(proc.stdout.startswith("design:"), proc.stdout)
        self.assertIn("overrides", proc.stdout)

    def test_a_word_ending_does_not_fake_a_match(self):
        proc = run("the apprenticeship model in building trades")
        self.assertNotIn("verbs:ship", proc.stdout)
        self.assertNotIn("strong:ui", proc.stdout)

    def test_disciplines_beyond_screens_pass(self):
        for text in ["custom ADA compliant room signage with tactile characters "
                     "and grade 2 braille mounted on the latch side",
                     "a new monospaced typeface released with a printed specimen",
                     "a refreshed on air package with lower thirds and a headline ticker"]:
            proc = run(text)
            self.assertTrue(proc.stdout.startswith("design:"), text)

    def test_verdict_names_the_matched_terms(self):
        proc = run("review this checkout screen")
        self.assertIn("strong:checkout", proc.stdout)
        self.assertIn("verbs:review", proc.stdout)

    def test_repeat_runs_agree(self):
        first, second = run("polish the empty state copy"), run("polish the empty state copy")
        self.assertEqual(first.stdout, second.stdout)

    def test_empty_input_is_a_usage_error(self):
        proc = run("   ")
        self.assertEqual(proc.returncode, 2)

    def test_stdin_works_too(self):
        proc = subprocess.run([sys.executable, str(GATE)], input="review this modal",
                              capture_output=True, text=True, cwd=str(SKILL_DIR))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stdout.startswith("design:"))

    def test_help_exits_zero(self):
        proc = subprocess.run([sys.executable, str(GATE), "--help"],
                              capture_output=True, text=True, cwd=str(SKILL_DIR))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("exit codes", proc.stdout.lower())
