"""Prove every generated skill receives the agentic invocation contract."""
import json
import pathlib
import tempfile
import unittest

from cli import run


class TestGeneratedAgenticScaffold(unittest.TestCase):
    def test_scaffold_carries_dispatch_task_script_test_and_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                "scaffold_skill.py", "--name", "agentic-trial",
                "--description", "Use when an agentic trial is requested.",
                "--dest", tmp)
            root = pathlib.Path(tmp) / "agentic-trial"
            config = (root / "mise.toml").read_text(encoding="utf-8")
            body = (root / "SKILL.md").read_text(encoding="utf-8")
            request_path = root / "assets" / "agentic-request-template.json"
            required = [
                root / "scripts" / "run_agentic_request.py",
                root / "scripts" / "agentic_request_contract.py",
                root / "scripts" / "tests" / "test_agentic_request.py",
                request_path,
            ]
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(all(path.exists() for path in required))
            self.assertIn("[tasks.agentic-request]", config)
            self.assertIn("agentic-trial agentic request", config)
            self.assertTrue(all(marker in body for marker in
                                ["## Ordered workflow", "Mise:", "Model:"]))
            request = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(request["version"], 1)
            self.assertIn("use_case", request)
            self.assertIn("trace", request["prompt"])
            self.assertIn("trace", request["skills"][0])
            self.assertIn("primitives", request)
            self.assertIsInstance(request["primitives"], list)
            self.assertIn("trace", request["primitives"][0])


if __name__ == "__main__":
    unittest.main()
