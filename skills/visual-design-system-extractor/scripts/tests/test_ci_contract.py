import json
import hashlib
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class CiContractTests(unittest.TestCase):
    def setUp(self):
        self.config = tomllib.loads((ROOT / "mise.toml").read_text())

    def test_ci_task_runs_every_gate(self):
        self.assertEqual(
            self.config["tasks"]["ci"]["run"],
            [
                "mise run test",
                "mise run validate",
                "mise run lint-writing",
                "mise run lint-code",
                "mise run evals",
            ],
        )

    def test_test_task_supplies_the_yaml_parser(self):
        run = self.config["tasks"]["test"]["run"]
        self.assertIn("uv run --no-project --with 'PyYAML>=6,<7'", run)
        self.assertIn("unittest discover -s scripts/tests", run)

    def test_toolchain_is_pinned(self):
        tools = self.config["tools"]
        self.assertEqual(tools["python"], "3.13.14")
        self.assertEqual(tools["uv"], "0.11.29")

    def test_workflow_calls_only_the_ci_task(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("- run: mise run ci", workflow)
        self.assertNotIn("python3 scripts/", workflow)

    def test_eval_contract_pins_the_current_skill_version(self):
        skill = (ROOT / "SKILL.md").read_text()
        match = re.search(r"^  version: '([^']+)'$", skill, re.MULTILINE)
        if match is None:
            self.fail('SKILL.md metadata.version is missing')
        version = match.group(1)
        contract = (ROOT / "evals/contract.md").read_text()
        self.assertIn(f'metadata.version: "{version}"', contract)

    def test_active_example_artifacts_share_selected_fonts(self):
        document = yaml.safe_load((ROOT / "examples/extract-output.yaml").read_text())
        fonts = document["typography"]["font_families"]
        expected = [fonts["primary"]["family"], fonts["supporting"]["family"]]
        decision = json.loads((ROOT / "examples/work/set.json").read_text())
        self.assertEqual([item["family"] for item in decision["chosen"]], expected)
        for relative in ["examples/extract.md", "examples/viability-loop.md", "examples/work/pass2.html"]:
            text = (ROOT / relative).read_text()
            for family in expected:
                self.assertIn(family, text)

    def test_visual_review_binds_the_current_pixels_and_viability(self):
        review = json.loads((ROOT / "examples/work/pass2-review.json").read_text())
        screenshot = ROOT / "examples/work/pass2.png"
        digest = hashlib.sha256(screenshot.read_bytes()).hexdigest()
        expected = {
            "legibility",
            "contrast",
            "hierarchy",
            "font_pairing",
            "spacing_rhythm",
            "color_harmony",
            "state_distinction",
            "reference_fidelity",
        }
        document = yaml.safe_load((ROOT / "examples/extract-output.yaml").read_text())
        self.assertEqual(review["input_sha256"], digest)
        self.assertEqual(review["verdict"], "PASS")
        self.assertEqual({item["criterion"] for item in review["criteria"]}, expected)
        self.assertTrue(all(item["verdict"] == "PASS" for item in review["criteria"]))
        recorded = document["meta"]["viability"]["criteria"]
        normalized = [dict(item, verdict=item["verdict"].lower()) for item in review["criteria"]]
        self.assertEqual(recorded, normalized)
        self.assertEqual(document["meta"]["viability"]["iterations"], 1)

    def test_named_failure_fixtures_fail_only_for_their_named_contract(self):
        cases = {
            "examples/work/no-viability.yaml": ["meta.viability.criteria.legibility.verdict is 'fail'"],
            "examples/work/order-fail.yaml": ["Top-level section order"],
            "examples/work/pairing-fail.yaml": ["pairing fails on vertical_proportion"],
        }
        for relative, expected in cases.items():
            done = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_design_system_yaml.py"), str(ROOT / relative)],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(done.stdout)
            self.assertEqual(done.returncode, 1, relative)
            self.assertEqual(len(payload["errors"]), len(expected), payload)
            for fragment in expected:
                self.assertTrue(any(fragment in error for error in payload["errors"]), payload)


if __name__ == "__main__":
    unittest.main()
