"""Pick rules after the state record. The model still picks the design."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
START = SKILL / "scripts" / "run_pipeline.py"
SELECT = SKILL / "scripts" / "select_rules.py"
INTAKE = SKILL / "evals" / "files" / "valid-intake.json"


def run(path, *args):
    return subprocess.run([sys.executable, str(path), *map(str, args)],
                          capture_output=True, text=True, timeout=120)


class TestSelectRules(unittest.TestCase):
    def test_blocks_until_state_judgment_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(START, "start", "--intake", INTAKE, "--run-dir", tmp)
            result = run(SELECT, "--run-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("state_judgment", result.stderr)

    def test_completes_its_named_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(START, "start", "--intake", INTAKE, "--run-dir", tmp)
            root = pathlib.Path(tmp)
            records = root / "records"
            records.mkdir()
            (records / "state_judgment.json").write_text("{}\n")
            data = json.loads((root / "run.json").read_text())
            data["next"] = "select_rules"
            (root / "run.json").write_text(json.dumps(data))
            result = run(SELECT, "--run-dir", tmp)
            data = json.loads((root / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(data["rules_selected"])
        self.assertTrue(data["rules"])
        self.assertEqual(data["next"], "atom_judgment")

    def test_blocks_when_the_run_is_not_at_rule_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(START, "start", "--intake", INTAKE, "--run-dir", tmp)
            records = pathlib.Path(tmp) / "records"
            records.mkdir()
            (records / "state_judgment.json").write_text("{}\n")
            result = run(SELECT, "--run-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("next action is source_meaning", result.stderr)


if __name__ == "__main__":
    unittest.main()
