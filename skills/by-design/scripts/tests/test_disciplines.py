"""Benchmark test: coordinates proposed across eight design disciplines.

Each brief is real work from a different discipline, written in the language
that discipline uses. The benchmark guards against a change that helps one
discipline by quietly breaking another.

  1. the expected shelf appears in the top three for at least as many briefs
     as the recorded baseline holds
  2. every brief passes the gate, because every one of them is design work
  3. a place resting on one term reports itself as a weak read
"""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = SKILL_DIR / "evals" / "files"
LOCATE = SKILL_DIR / "scripts" / "locate.py"
GATE = SKILL_DIR / "scripts" / "gate.py"
BASELINE = SKILL_DIR / "evals" / "baseline.json"
FLOOR = json.loads(BASELINE.read_text(encoding="utf-8"))["locate_top3"]


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, cwd=str(SKILL_DIR))


class TestDisciplines(unittest.TestCase):
    def setUp(self):
        self.expected = json.loads((FIXTURES / "briefs.json").read_text(encoding="utf-8"))

    def test_fixtures_are_present(self):
        self.assertGreaterEqual(len(self.expected), 8)
        for name in self.expected:
            self.assertTrue((FIXTURES / f"brief-{name}.txt").is_file(), name)

    def test_the_expected_shelf_is_in_the_top_three(self):
        found = []
        for name, shelf in sorted(self.expected.items()):
            proc = run(LOCATE, "--file", str(FIXTURES / f"brief-{name}.txt"), "--top", "3")
            if shelf in proc.stdout:
                found.append(name)
        self.assertGreaterEqual(len(found), FLOOR,
                                f"only {len(found)} of {len(self.expected)} landed: {sorted(found)}")

    def test_every_discipline_passes_the_gate(self):
        for name in sorted(self.expected):
            text = (FIXTURES / f"brief-{name}.txt").read_text(encoding="utf-8")
            proc = run(GATE, "--text", text)
            self.assertTrue(proc.stdout.startswith("design:"), name)

    def test_a_one_term_place_reports_itself(self):
        proc = run(LOCATE, "--file", str(FIXTURES / "brief-04-broadcast.txt"), "--top", "1")
        if " 1 terms " in proc.stdout:
            self.assertIn("weak read", proc.stderr)
