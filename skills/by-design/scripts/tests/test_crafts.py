"""Universality: every design occupation on file reaches a shelf.

  1. every occupation fixture carries a task written in its own trade language
  2. the gate admits every one of them, because all of them are design work
  3. every occupation name in the fixture appears in assets/disciplines.yaml
  4. the expected shelf is a real category name
  5. the recorded baseline holds the coverage numbers, so they cannot fall
"""
import json
import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import gate
import locate
import yamlread

CRAFTS = SKILL_DIR / "evals" / "files" / "occupations.json"
BASELINE = SKILL_DIR / "evals" / "baseline.json"


class TestCrafts(unittest.TestCase):
    def setUp(self):
        self.jobs = json.loads(CRAFTS.read_text(encoding="utf-8"))
        self.names = [row["name"] for row in
                      yamlread.load(SKILL_DIR / "assets" / "index.yaml", "categories")]

    def test_every_task_is_written_out(self):
        for name, row in self.jobs.items():
            self.assertGreater(len(row["task"].split()), 8, name)

    def test_every_expected_shelf_is_a_real_category(self):
        for name, row in self.jobs.items():
            self.assertIn(row["shelf"], self.names, name)

    def test_the_gate_admits_every_craft(self):
        terms = gate.load_terms()
        stopped = [name for name, row in sorted(self.jobs.items())
                   if gate.verdict(gate.score(row["task"], terms))[0] != "design"]
        self.assertEqual(stopped, [])

    def test_every_occupation_is_mapped_to_a_shelf(self):
        listed = set()
        for row in yamlread.load(SKILL_DIR / "assets" / "disciplines.yaml", "categories"):
            listed.update(row["terms"])
        self.assertEqual(sorted(set(self.jobs) - listed), [])

    def test_the_baseline_records_coverage(self):
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(base["crafts_total"], len(self.jobs))
        self.assertEqual(base["crafts_gated"], len(self.jobs))
        self.assertGreaterEqual(base["crafts_top3"], len(self.jobs))

    def test_a_named_craft_lands_its_shelf(self):
        entries = locate.load_index()
        for name in ["floral designer", "naval architect", "type designer"]:
            ranked = locate.rank(f"I am a {name} starting a new piece of work", entries)
            self.assertEqual(ranked[0][1], self.jobs[name]["shelf"], name)


if __name__ == "__main__":
    unittest.main()


class TestCraftsCommand(unittest.TestCase):
    def run_it(self, *args):
        import subprocess
        return subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "crafts.py"), *args],
                              capture_output=True, text=True, cwd=str(SKILL_DIR))

    def test_help_exits_zero(self):
        done = self.run_it("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("--thin", done.stdout)

    def test_thin_lists_one_craft_per_line(self):
        done = self.run_it("--thin")
        self.assertEqual(done.returncode, 0, done.stderr)
        listed = [line for line in done.stdout.splitlines() if line.strip()]
        self.assertTrue(listed)
        jobs = json.loads(CRAFTS.read_text(encoding="utf-8"))
        for name in listed:
            self.assertIn(name, jobs)
