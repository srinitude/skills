"""Runner model-record checks."""
import json
import pathlib
import tempfile
import unittest

from pipeline_test_support import INTAKE, SKILL_DIR, run, set_next


class TestRunRecords(unittest.TestCase):
    def test_record_requires_context_acknowledgement(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            path = pathlib.Path(tmp) / "source-result.json"
            path.write_text(json.dumps({
                "action": "source_meaning", "decision": "PASS",
                "evidence": ["source:1"], "reason": "The source is current.",
                "counterevidence": [], "uncertainty": "None found.",
                "affected": [], "missing_context": []}))
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("context acknowledgement", result.stderr)

    def test_record_accepts_every_required_context_path(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            result = run("record", "--run-dir", tmp, "--result", fixture)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_advances_to_the_next_fixed_action(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            result = run("record", "--run-dir", tmp, "--result", fixture)
            data = json.loads((pathlib.Path(tmp) / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["next"], "state_judgment")

    def test_record_accepts_named_missing_context_only_when_blocked(self):
        fixture = SKILL_DIR / "evals" / "files" / "missing-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            result = run("record", "--run-dir", tmp, "--result", fixture)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_rejects_a_path_as_both_used_and_missing(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            data = json.loads(fixture.read_text(encoding="utf-8"))
            data["decision"] = "BLOCKED"
            data["missing_context"] = [data["context_acknowledgements"][0]]
            path = pathlib.Path(tmp) / "overlap.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("both used and missing", result.stderr)

    def test_record_rejects_an_unrouted_context_path(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            data = json.loads(fixture.read_text(encoding="utf-8"))
            data["context_acknowledgements"].append("references/unrouted.md")
            path = pathlib.Path(tmp) / "unrouted.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unrouted context path", result.stderr)

    def test_creative_record_blocks_a_choice_without_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "screen_design")
            run("packet", "--run-dir", tmp, "--action", "screen_design")
            path = pathlib.Path(tmp) / "screen-result.json"
            path.write_text(json.dumps({
                "action": "screen_design", "decision": "PASS",
                "evidence": ["render:1"], "reason": "The view fits.",
                "counterevidence": [], "uncertainty": "No doubt shown.",
                "affected": []}), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("four design options", result.stderr)
        self.assertIn("model choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
