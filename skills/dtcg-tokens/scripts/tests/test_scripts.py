"""Contract tests for every bundled script in this skill."""
import json
import pathlib
import re
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


def run(path, *args):
    cmd = [sys.executable, str(path)]
    cmd.extend(str(arg) for arg in args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


class TestScriptContracts(unittest.TestCase):
    def test_every_script_documents_help(self):
        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))
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


class TestWorkedExamples(unittest.TestCase):
    def setUp(self):
        self.result = run(SKILL_DIR / "scripts" / "validate_dtcg.py", SKILL_DIR / "evals" / "files" / "sample.tokens.json")
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.report = json.loads(self.result.stdout)

    def test_validator_examples_match_current_output(self):
        for name in ["generate.md", "validate.md"]:
            text = (SKILL_DIR / "examples" / name).read_text(encoding="utf-8")
            self.assertRegex(text, r"\|\s*Command\s*\|\s*Purpose\s*\|", name)
            self.assertIn("`python3 scripts/validate_dtcg.py evals/files/sample.tokens.json`", text, name)
            match = re.search(r"## Verified output\n\n```json\n(\{.*?\})\n```\n\nExit code: `0`", text, flags=re.DOTALL)
            self.assertIsNotNone(match, name)
            self.assertEqual(json.loads(match.group(1)), self.report, name)
            self.assertIn(f'{self.report["token_count"]} tokens', text, name)
            self.assertIn(f'{self.report["resolved_references"]} resolved references', text, name)

    def test_markdown_commands_use_tables(self):
        markdown = sorted(SKILL_DIR.rglob("*.md"))
        command_line = re.compile(r"^\$\s+(python3|mise|git|cp|find|rg|mkdir)\b", re.MULTILINE)
        shell_fence = re.compile(r"^```(?:sh|bash|shell|console)\s*$", re.MULTILINE)
        for path in markdown:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(command_line.search(text), str(path.relative_to(SKILL_DIR)))
            self.assertIsNone(shell_fence.search(text), str(path.relative_to(SKILL_DIR)))

    def test_generation_eval_requires_all_four_deliverables(self):
        evals = json.loads((SKILL_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
        generation = next(item for item in evals if item["id"] == 1)
        self.assertIn("Four files", generation["expected_output"])
        self.assertIn("run JSON", generation["expected_output"])
        cases = json.loads((SKILL_DIR / "evals" / "cases.json").read_text(encoding="utf-8"))["cases"]
        required = next(item for item in cases if item["id"] == "DTCG-001")["required"]
        self.assertIn("run JSON", required)

    def test_all_steps_scope_excludes_diagnostic_commands(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        execution = skill.split("## Execution\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`generate` and `prove` run all 25 steps", execution)
        self.assertIn("`help`", execution)
        self.assertIn("`validate`", execution)
        self.assertNotIn("Run all 25 steps in order for every command", execution)


if __name__ == "__main__":
    unittest.main()
