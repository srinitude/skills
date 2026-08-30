"""Contract tests for bundled scripts other than the run pipeline."""
import json
import pathlib
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


class TestLineage(unittest.TestCase):
    def test_valid_chain_passes(self):
        script = SKILL_DIR / "scripts" / "check_lineage.py"
        path = SKILL_DIR / "evals" / "files" / "valid-lineage.json"
        result = run(script, path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_layer_skip_fails(self):
        script = SKILL_DIR / "scripts" / "check_lineage.py"
        path = SKILL_DIR / "evals" / "files" / "skipped-lineage.json"
        result = run(script, path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("skips", result.stdout)


class TestSourceLineage(unittest.TestCase):
    def test_current_public_hashes_pass(self):
        script = SKILL_DIR / "scripts" / "check_source_lineage.py"
        result = run(script, SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestReading(unittest.TestCase):
    def test_long_sentence_fails(self):
        import tempfile
        script = SKILL_DIR / "scripts" / "check_reading.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "hard-prose.md"
            words = ["This", "sentence", "has", "far", "too", "many",
                     "words", "and", "must", "fail", "the", "fixed",
                     "public", "reading", "check", "before", "anyone",
                     "can", "call", "it", "done."]
            path.write_text(" ".join(words) + "\n", encoding="utf-8")
            result = run(script, path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("long sentence", result.stdout)

    def test_exact_contract_is_the_only_exempt_file(self):
        script = SKILL_DIR / "scripts" / "check_reading.py"
        path = SKILL_DIR / "references" / "generation-contract.md"
        result = run(script, path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("approved exact copy", result.stdout)


class TestExamples(unittest.TestCase):
    def test_current_examples_match_real_commands(self):
        script = SKILL_DIR / "scripts" / "build_examples.py"
        result = run(script, "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
