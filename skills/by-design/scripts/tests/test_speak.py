"""Contract tests for scripts/speak.py and scripts/check_reply.py.

Each test pins a contract a caller touches:
  1. an inherited live decision earns a question
  2. a deliberate decision does not
  3. a decision already seen three times does not
  4. a missing ledger exits 1
  5. the reply check catches two questions, a missing posture, a missing ledger
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SPEAK = SKILL_DIR / "scripts" / "speak.py"
LEDGER = SKILL_DIR / "scripts" / "ledger.py"
REPLY = SKILL_DIR / "scripts" / "check_reply.py"


class TestSpeak(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "decision-ledger-demo.md"
        self.call(LEDGER, "init", "--file", str(self.path), "--slug", "demo")

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args],
                              capture_output=True, text=True)

    def add(self, decision, origin):
        self.call(LEDGER, "add", "--file", str(self.path),
                  "--decision", decision, "--origin", origin)

    def test_inherited_and_live_earns_a_question(self):
        proc = self.call(SPEAK, "--file", str(self.path), "--decision",
                         "Row height", "--origin", "inherited", "--live", "yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stdout.startswith("ask:"))

    def test_deliberate_holds(self):
        proc = self.call(SPEAK, "--file", str(self.path), "--decision",
                         "Row height", "--origin", "deliberate", "--live", "yes")
        self.assertTrue(proc.stdout.startswith("hold:"))

    def test_not_live_holds(self):
        proc = self.call(SPEAK, "--file", str(self.path), "--decision",
                         "Row height", "--origin", "inherited", "--live", "no")
        self.assertTrue(proc.stdout.startswith("hold:"))

    def test_three_prior_appearances_hold(self):
        for _ in range(3):
            self.add("Spacing scale", "inherited")
        proc = self.call(SPEAK, "--file", str(self.path), "--decision",
                         "Spacing scale", "--origin", "inherited", "--live", "yes")
        self.assertTrue(proc.stdout.startswith("hold:"))
        self.assertIn("project level", proc.stdout)

    def test_rank_orders_inherited_rows_least_examined_first(self):
        self.call(LEDGER, "add", "--file", str(self.path), "--decision",
                  "Fully examined choice", "--origin", "inherited",
                  "--chosen", "a", "--trades", "b", "--risks", "c",
                  "--falsifier", "d", "--source", "e")
        self.add("Bare choice", "inherited")
        proc = self.call(SPEAK, "--file", str(self.path), "--rank")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(proc.stdout.index("Bare choice"),
                        proc.stdout.index("Fully examined choice"))

    def test_rank_on_a_ledger_with_no_inherited_rows(self):
        self.add("A chosen thing", "deliberate")
        proc = self.call(SPEAK, "--file", str(self.path), "--rank")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("nothing earns a question", proc.stdout)

    def test_missing_ledger_exits_one(self):
        proc = self.call(SPEAK, "--file", "/tmp/absent-ledger.md", "--decision",
                         "x", "--origin", "inherited", "--live", "yes")
        self.assertEqual(proc.returncode, 1)


HEADER = "| The decision | What was chosen |\n|---|---|\n"
ROWS = ("| first | - | a vs b | c | inherited | - | - |\n"
        "| second | x | d vs e | f | deliberate | - | - |\n")


def ledger_in(folder):
    """Write a two row ledger, one of them inherited, and return its name."""
    (pathlib.Path(folder) / "decision-ledger-x.md").write_text(HEADER + ROWS, encoding="utf-8")
    return "decision-ledger-x.md"


class TestReplyCheck(unittest.TestCase):
    def check(self, text, *extra):
        return subprocess.run([sys.executable, str(REPLY), *extra],
                              input=text, capture_output=True, text=True)

    def draft(self, rows, inherited):
        return (f"Posture: judge\nLedger: decision-ledger-x.md, {rows} rows added, "
                f"{inherited} marked inherited\nFound: two decisions.\nOne question?")

    def test_a_clean_draft_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger_in(folder)
            proc = self.check(self.draft(2, 1), "--ledger-dir", folder)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_a_count_the_ledger_does_not_support_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger_in(folder)
            proc = self.check(self.draft(5, 4), "--ledger-dir", folder)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("the ledger holds 2", proc.stdout)

    def test_a_question_without_an_inherited_row_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            (pathlib.Path(folder) / "decision-ledger-x.md").write_text(
                HEADER + "| only | x | a vs b | c | deliberate | - | - |\n", encoding="utf-8")
            draft = ("Posture: judge\nLedger: decision-ledger-x.md, 1 rows added, "
                     "0 marked inherited\nFound: one decision.\nWhy this one?")
            proc = self.check(draft, "--ledger-dir", folder)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("earned its question", proc.stdout)

    def test_no_inherited_row_and_no_question_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            (pathlib.Path(folder) / "decision-ledger-x.md").write_text(
                HEADER + "| only | x | a vs b | c | deliberate | - | - |\n", encoding="utf-8")
            draft = ("Posture: judge\nLedger: decision-ledger-x.md, 1 rows added, "
                     "0 marked inherited\nFound: one decision.\nnone")
            proc = self.check(draft, "--ledger-dir", folder)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_a_ledger_that_was_never_written_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            proc = self.check(self.draft(2, 1), "--ledger-dir", folder)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not on disk", proc.stdout)

    def test_two_questions_fail(self):
        proc = self.check("Posture: judge. Ledger at a.md. First? Second?")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("cap is 1", proc.stdout)

    def test_missing_posture_fails(self):
        proc = self.check("Ledger at a.md, 3 rows added.")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("posture", proc.stdout)

    def test_missing_ledger_mention_fails(self):
        proc = self.check("Posture: judge. Four decisions found.")
        self.assertEqual(proc.returncode, 1)

    def test_full_slice_allows_many_questions(self):
        proc = self.check("Posture: ask\nLedger: untouched\nA? B? C?", "--full-slice")
        self.assertEqual(proc.returncode, 0, proc.stdout)
