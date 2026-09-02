"""Universal SKILL.md formatting checks."""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]

TEXT_CASES = [
    ("Make a usable product", "\tMake a usable product", "tab characters"),
    ("They do not make design judgments.\n",
     "They do not make design judgments.  \n",
     "trailing whitespace"),
    ("# Design like I am five\n\n",
     "Design like I am five\n=====================\n", "Setext headings"),
    ("### Prepare the run", "#### Prepare the run", "heading levels"),
    ("# Design like I am five\n\nMake a usable product",
     "# Design like I am five\nMake a usable product",
     "blank lines around headings"),
    ("Make a usable product without hiding truth, cost, risk, state, or control.",
     "::client-only{Make a usable product without hiding truth.}",
     "client-specific directives"),
    ("Make a usable product without hiding truth, cost, risk, state, or control.",
     "<client-widget>Make a usable product.</client-widget>", "raw HTML"),
    ("Make a usable product without hiding truth, cost, risk, state, or control.",
     "| Scope | Owner |\n| --- | --- |\n", "extension-only tables"),
    ("(references/section-support.md)", "(/private/section-support.md)",
     "absolute local links"),
    ("(references/section-support.md)",
     "(file:///private/section-support.md)", "client or file URI links"),
]


def run_validator(copy):
    return subprocess.run(
        [sys.executable, str(copy / "scripts" / "validate_skill.py"),
         str(copy)], capture_output=True, text=True, timeout=120)


class TestSkillFormat(unittest.TestCase):
    def assert_text_rejected(self, root, source, old, new, message):
        copy = root / re.sub(r"\W+", "-", message) / SKILL.name
        shutil.copytree(SKILL, copy)
        changed = source.replace(old, new, 1)
        self.assertNotEqual(changed, source, message)
        (copy / "SKILL.md").write_text(changed, encoding="utf-8")
        result = run_validator(copy)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)

    def test_validator_rejects_nonportable_skill_body_formatting(self):
        source = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for old, new, message in TEXT_CASES:
                with self.subTest(message=message):
                    self.assert_text_rejected(
                        root, source, old, new, message)

    def test_validator_rejects_non_lf_or_bom_encoded_skill_body(self):
        source = (SKILL / "SKILL.md").read_bytes()
        cases = [(source.replace(b"\n", b"\r\n"), "non-LF line endings"),
                 (b"\xef\xbb\xbf" + source, "UTF-8 BOM")]
        with tempfile.TemporaryDirectory() as tmp:
            for payload, message in cases:
                with self.subTest(message=message):
                    copy = pathlib.Path(tmp) / message.replace(" ", "-") / SKILL.name
                    shutil.copytree(SKILL, copy)
                    (copy / "SKILL.md").write_bytes(payload)
                    result = run_validator(copy)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn(message, result.stdout)


if __name__ == "__main__":
    unittest.main()
