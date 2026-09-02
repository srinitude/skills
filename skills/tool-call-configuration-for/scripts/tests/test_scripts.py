"""Contract tests for every bundled script in this skill."""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CLI_SCRIPTS = ["check_code_rules.py", "check_decision_records.py", "check_domain_research.py", "check_evals.py", "check_improvement_contract.py", "check_invocation_receipt.py", "check_mise_primitives.py", "check_placeholders.py", "check_primitive_lifecycle.py", "check_task_graph.py", "check_use_case_contract.py", "lint_writing.py", "run_agentic_request.py", "sync_mise_primitives.py", "validate_skill.py"]


def run(path, *args):
    cmd = [sys.executable, str(path)]
    cmd.extend(str(arg) for arg in args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


class TestScriptContracts(unittest.TestCase):
    def test_every_script_documents_help(self):
        scripts = [SKILL_DIR / "scripts" / name for name in CLI_SCRIPTS]
        self.assertTrue(scripts, "scripts/ holds no python files")
        for script in scripts:
            result = run(script, "--help")
            self.assertEqual(result.returncode, 0, script.name)
            self.assertIn("usage", result.stdout.lower(), script.name)


class TestSkillInfo(unittest.TestCase):
    def test_info_reports_name_and_description(self):
        result = run(SKILL_DIR / "scripts" / "skill_info.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(info["name"], SKILL_DIR.name)
        self.assertTrue(info["description"])


if __name__ == "__main__":
    unittest.main()
