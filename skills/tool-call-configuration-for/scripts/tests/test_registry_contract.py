"""Keep local and generated eval manifests on the repository contract."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
CLI = SKILL / "scripts/tool_call_config.py"


def assert_shape(test, package):
    manifest = json.loads((package / "evals/manifest.json").read_text())
    triggers = json.loads((package / "evals/trigger-cases.json").read_text())
    budgets = json.loads((package / "evals/speed-budgets.json").read_text())
    test.assertEqual(manifest["conditions"], ["with_skill", "without_skill"])
    test.assertEqual(manifest["repetitions"], 2)
    test.assertTrue(all(re.fullmatch(r"TR-\d{3}", row["id"])
                        for row in triggers["cases"]))
    test.assertTrue({row["kind"] for row in triggers["cases"]} <= {
        "positive", "hard_negative", "near_neighbor"})
    test.assertEqual(set(budgets["fixture"]), {
        "cold_start_ms_max", "warm_start_ms_max", "case_p95_ms_max",
        "full_run_ms_max"})
    test.assertEqual(set(budgets["live"]), {
        "activation_p95_ms_max", "response_p95_ms_max", "minimum_samples"})


class TestRegistryContract(unittest.TestCase):
    def test_repository_manifests_use_shared_shape(self):
        assert_shape(self, SKILL)

    def test_generated_manifests_use_shared_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = [sys.executable, str(CLI), "generate",
                       "@evals/fixtures/established-mcp-read.json", "--behavior",
                       "@evals/fixtures/behavior-report.json", "--output", tmp]
            result = subprocess.run(command, cwd=SKILL, capture_output=True,
                                    text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            package = Path(json.loads(result.stdout)["skill_path"])
            assert_shape(self, package)


if __name__ == "__main__":
    unittest.main()
