"""Tests for factory-owned in-place registry standardization."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run

SOURCES = [
    {"source": "https://www.rfc-editor.org/rfc/rfc3339", "source_class": "standard",
     "claim": "A clock anchor needs an offset.", "limitations": "No timezone choice."},
    {"source": "https://data.iana.org/time-zones/theory.html", "source_class": "first_party",
     "claim": "Timezone rules change.", "limitations": "No request interpretation."},
    {"source": "https://docs.python.org/3/library/datetime.html", "source_class": "first_party",
     "claim": "Aware times carry offsets.", "limitations": "No freshness proof."},
    {"source": "https://www.w3.org/TR/NOTE-datetime", "source_class": "standard",
     "claim": "Dates need a profile.", "limitations": "No current civil time."},
]
MISE_TEXT = (
    "[tasks.anchor]\ndescription = \"Read the clock anchor\"\n"
    "run = \"python3 scripts/anchor.py\"\n\n[tasks.ci]\n"
    "description = \"Check the clock anchor\"\nrun = [\"mise run anchor\"]\n\n"
    "[tasks.inspect-anchor]\ndescription = \"Old inspector\"\n"
    "run = \"python3 scripts/inspect.py\"\n"
)


def profile():
    return {
        "skill": "clock-anchor",
        "primary_term": "clock anchor",
        "domain_terms": ["clock anchor", "timezone offset", "relative date"],
        "outcome": "Return one fresh clock anchor for each direct turn.",
        "main_task": "anchor",
        "main_run": "python3 scripts/anchor.py",
        "public_tasks": ["inspect-anchor"],
        "script_tasks": {
            "inspect-anchor": {
                "script": "inspect.py",
                "description": "Inspect one clock anchor receipt",
                "args": "--format json",
                "runner": "uv run python"
            }
        },
        "text_rewrites": {
            "scripts/domain_check.py": [
                {"old": "LEGACY_ASSERTION", "new": "FACTORY_ASSERTION"}
            ]
        },
        "sources": SOURCES,
    }


def write_target(root):
    root.mkdir()
    (root / "SKILL.md").write_text(
        "---\nname: clock-anchor\ndescription: 'Use when time matters.'\n"
        "license: MIT\nmetadata:\n  author: Kiren Srinivasan\n"
        "  version: '0.1.0'\n---\n\n# Clock anchor\n\n"
        "Run `python3 scripts/anchor.py` once.\n\n"
        "Package maintainers inspect `scripts/` after a failed task.\n",
        encoding="utf-8")
    (root / "mise.toml").write_text(MISE_TEXT, encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts" / "anchor.py").write_text("print('clock anchor')\n")
    (root / "scripts" / "inspect.py").write_text("print('anchor receipt')\n")
    (root / "scripts" / "domain_check.py").write_text("LEGACY_ASSERTION\n")
    (root / "scripts" / "report_clock.py").write_text("print('report')\n")
    (root / "scripts" / "validate_skill.py").write_text(
        "def check_layout(skill, body, problems):\n"
        "    for name in REQUIRED_DIRS + [\"scripts/tests\"]:\n"
        "        if not (skill / name).is_dir():\n"
        "            problems.append(f\"missing required directory: {name}/\")\n"
        "        elif body and f\"{name}/\" not in body:\n"
        "            problems.append(f\"body never references {name}/\")\n",
        encoding="utf-8")
    (root / "references").mkdir()
    (root / "references" / "contract.md").write_text(
        "# Contract\n\nRun `python3 scripts/anchor.py`.\n\n"
        "Run `python3 scripts/report_clock.py`.\n\n"
        "Run [the receipt inspector](scripts/inspect.py).\n\nRead assets/state.json.\n\n"
        "Read ../SKILL.md and ../evals/cases.json.\n",
        encoding="utf-8")


class TestRegistryStandardization(unittest.TestCase):
    def invoke(self, root, profile_path, apply=False):
        args = ["standardize_registry_skill.py", root, "--profile", profile_path]
        return run(*args, *(["--apply"] if apply else []))

    def test_plan_makes_no_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            source = (root / "SKILL.md").read_bytes()
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path)
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(report["writes"], 0)
            self.assertEqual((root / "SKILL.md").read_bytes(), source)

    def test_apply_adds_domain_owners_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            first = self.invoke(root, profile_path, apply=True)
            second = self.invoke(root, profile_path, apply=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json.loads(second.stdout)["changed"], [])
            self.assert_package_files(root)
            self.assert_package_graph(root)

    def assert_package_files(self, root):
            self.assertTrue((root / "assets/use-case-contract.json").is_file())
            self.assertTrue((root / "assets/primitive-lifecycle.json").is_file())
            skill = (root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("mise run anchor", skill)
            self.assertNotIn("scripts/anchor.py", skill)
            self.assertNotIn("scripts/", skill)
            reference = (root / "references/contract.md").read_text()
            self.assertIn("mise run anchor", reference)
            self.assertIn("mise run report-clock", reference)
            self.assertIn("`mise run inspect-anchor`", reference)
            self.assertNotIn("[the receipt inspector]", reference)
            self.assertIn("mise run ", reference)
            self.assertNotIn("Use it through", reference)
            self.assertNotIn("scripts/", reference)
            domain_check = (root / "scripts/domain_check.py").read_text()
            self.assertEqual(domain_check, "FACTORY_ASSERTION\n")

    def assert_package_graph(self, root):
            mise = (root / "mise.toml").read_text(encoding="utf-8")
            self.assertIn('depends = ["anchor", "decision-policy"]', mise)
            self.assertIn("[tasks.inspect-anchor]", mise)
            self.assertIn("[tasks.report-clock]", mise)
            self.assertIn("uv run python scripts/inspect.py --format json", mise)
            self.assertNotIn("mise run anchor", mise)
            validator = (root / "scripts/validate_skill.py").read_text()
            self.assertNotIn('elif body and f"{name}/"', validator)
            self.assertTrue((root / "scripts/tests/test_package_contract.py").is_file())
            skill = (root / "SKILL.md").read_text()
            self.assertIn("assets/use-case-contract.json", skill)
            self.assertIn("evals/evals.json", skill)

    def test_apply_refreshes_the_recursive_generation_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            contract = root / "references/generation-contract.md"
            contract.write_text("# Stale contract\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Every generated skill follows", contract.read_text())

    def test_apply_refreshes_the_placeholder_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            checker = root / "scripts/check_placeholders.py"
            checker.write_text("print('stale')\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("documented_example", checker.read_text())

    def test_apply_rewrites_legacy_graph_and_lineage_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            tests = root / "scripts/tests"
            tests.mkdir()
            (tests / "test_ci_contract.py").write_text(
                'steps = self.tasks["ci"]["run"]\n'
                'self.assertIn(f"mise run {job}", " ".join(steps))\n')
            (tests / "test_source_mapping.py").write_text(
                "self.assertEqual(files, EXPECTED_FILES)\n")
            (tests / "test_scripts.py").write_text(
                "import pathlib\n"
                "SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]\n"
                '        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))\n'
                '        self.assertTrue(scripts, "scripts/ holds no python files")\n')
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ci_test = (tests / "test_ci_contract.py").read_text()
            source_test = (tests / "test_source_mapping.py").read_text()
            script_test = (tests / "test_scripts.py").read_text()
            self.assertIn('tasks["ci"]["depends"]', ci_test)
            self.assertNotIn('tasks["ci"]["run"]', ci_test)
            self.assertNotIn('f"mise run {job}"', ci_test)
            self.assertIn("for key in EXPECTED_FILES", source_test)
            self.assertIn("CLI_SCRIPTS", script_test)
            self.assertNotIn('glob("*.py")', script_test)

    def test_refuses_profile_or_target_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            data = profile()
            data["skill"] = "another-skill"
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "assets/use-case-contract.json").exists())


if __name__ == "__main__":
    unittest.main()
