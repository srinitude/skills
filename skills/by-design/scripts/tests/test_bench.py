"""The ratchet: real work becomes a fixture and no measure may fall.

  1. the recorded baseline covers every discipline fixture by rank position
  2. a fixture whose shelf slips to a worse rank is reported as a fall
  3. a fixture whose shelf disappears entirely is reported as a fall
  4. an improved rank is not reported, because the ratchet only turns one way
  5. the skill as it stands meets its own recorded baseline
"""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import bench

BASELINE = SKILL_DIR / "evals" / "baseline.json"
FIXTURES = SKILL_DIR / "evals" / "files"


def run(*args):
    return subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "bench.py"), *args],
                          capture_output=True, text=True, cwd=str(SKILL_DIR))


class TestBaselineShape(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.expected = json.loads((FIXTURES / "briefs.json").read_text(encoding="utf-8"))

    def test_every_fixture_carries_a_rank_position(self):
        self.assertEqual(sorted(self.base["per_rank"]), sorted(self.expected))

    def test_the_gate_measures_are_recorded(self):
        self.assertIn("gate_recall", self.base)
        self.assertIn("gate_precision", self.base)


class TestCompare(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.now = json.loads(BASELINE.read_text(encoding="utf-8"))

    def test_an_unchanged_run_reports_nothing(self):
        self.assertEqual(bench.compare(self.now, self.base), [])

    def test_a_slipped_rank_is_reported(self):
        name = sorted(spot for spot, place in self.base["per_rank"].items() if place)[0]
        self.now["per_rank"][name] = self.base["per_rank"][name] + 3
        self.assertTrue(any("slipped" in line for line in bench.compare(self.now, self.base)))

    def test_a_lost_shelf_is_reported(self):
        name = sorted(spot for spot, place in self.base["per_rank"].items() if place)[0]
        self.now["per_rank"][name] = 0
        self.assertTrue(any("lost its shelf" in line for line in bench.compare(self.now, self.base)))

    def test_an_improved_rank_is_not_reported(self):
        name = sorted(spot for spot, place in self.base["per_rank"].items() if place > 1)[0]
        self.now["per_rank"][name] = 1
        self.assertEqual(bench.compare(self.now, self.base), [])

    def test_a_fallen_gate_measure_is_reported(self):
        self.now["gate_precision"] = self.base["gate_precision"] - 0.1
        self.assertTrue(any("gate_precision" in line for line in bench.compare(self.now, self.base)))


class TestCommand(unittest.TestCase):
    def test_help_exits_zero(self):
        done = run("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("--update", done.stdout)

    def test_the_skill_meets_its_own_baseline(self):
        done = run()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("gate recall", done.stdout)


if __name__ == "__main__":
    unittest.main()
