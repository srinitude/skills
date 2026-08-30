"""Check that each skill head has direct help and one rich owner."""
import pathlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
BODY = SKILL / "SKILL.md"
SECTION_MAP = SKILL / "assets" / "section-support.json"
CHECKER = SKILL / "scripts" / "check_section_support.py"
SUPPORT_PATH = re.compile(r"(?:references|scripts|assets|evals|examples)/")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SUPPORT_FOLDERS = {"references", "scripts", "assets", "evals", "examples"}
REQUIRED_FIELDS = {
    "id", "heading", "level", "purpose", "enter_when", "support",
    "load_order", "actions", "evidence", "output", "judgment_owner",
    "deterministic_scope", "model_freedom", "fixed_constraints",
    "do_not_substitute", "wall_clock", "blocked_when",
}
FORBIDDEN_VERDICT_KEYS = {
    "decision", "rank", "score", "chosen_direction", "chosen_state",
    "design_verdict",
}


def direct_sections(text):
    sections = []
    current = None
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match:
            if current:
                sections.append(current)
            current = {
                "level": len(match.group(1)),
                "heading": match.group(2),
                "body": [],
            }
        elif current:
            current["body"].append(line)
    if current:
        sections.append(current)
    return sections


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def owner(test):
    test.assertTrue(SECTION_MAP.is_file(),
                    "missing assets/section-support.json")
    return load(SECTION_MAP)


class TestSectionSupportBaseline(unittest.TestCase):
    def test_every_direct_section_names_a_support_path(self):
        sections = direct_sections(BODY.read_text(encoding="utf-8"))
        missing = [row["heading"] for row in sections
                   if not SUPPORT_PATH.search("\n".join(row["body"]))]
        self.assertEqual(missing, [])

    def test_section_support_owner_exists(self):
        self.assertTrue(SECTION_MAP.is_file(),
                        "missing assets/section-support.json")

    def test_every_heading_has_one_ordered_owner_record(self):
        sections = direct_sections(BODY.read_text(encoding="utf-8"))
        records = owner(self)["sections"]
        expected = [(row["heading"], row["level"]) for row in sections]
        actual = [(row.get("heading"), row.get("level")) for row in records]
        self.assertEqual(actual, expected)
        ids = [row.get("id") for row in records]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_section_has_rich_hand_holding(self):
        for record in owner(self)["sections"]:
            self.assertEqual(set(record), REQUIRED_FIELDS, record.get("id"))
            for field in ["purpose", "enter_when", "output",
                          "do_not_substitute"]:
                self.assertIsInstance(record[field], str, record["id"])
                self.assertTrue(record[field].strip(), record["id"])
            for field in ["support", "load_order", "actions", "evidence",
                          "deterministic_scope", "model_freedom",
                          "fixed_constraints", "wall_clock", "blocked_when"]:
                self.assertIsInstance(record[field], list, record["id"])
                self.assertTrue(record[field], record["id"])
            self.assertEqual(record["judgment_owner"], "model")

    def test_each_support_path_exists_and_has_a_use(self):
        body = {row["heading"]: "\n".join(row["body"])
                for row in direct_sections(BODY.read_text(encoding="utf-8"))}
        for record in owner(self)["sections"]:
            mapped_paths = []
            for support in record["support"]:
                self.assertEqual(set(support),
                                 {"path", "load_when", "contribution"})
                path = support["path"]
                self.assertIn(path.split("/", 1)[0], SUPPORT_FOLDERS, path)
                self.assertTrue((SKILL / path).is_file(), path)
                self.assertTrue(support["load_when"].strip(), path)
                self.assertTrue(support["contribution"].strip(), path)
                mapped_paths.append(path)
            direct = body[record["heading"]]
            self.assertTrue(any(path in direct for path in mapped_paths),
                            record["heading"])

    def test_section_owner_never_contains_a_deterministic_verdict(self):
        for record in owner(self)["sections"]:
            self.assertFalse(FORBIDDEN_VERDICT_KEYS & set(record), record["id"])

    def test_product_states_get_all_five_support_classes(self):
        records = owner(self)["sections"]
        record = next(row for row in records
                      if row["heading"] == "Discover product states")
        folders = {row["path"].split("/", 1)[0] for row in record["support"]}
        self.assertEqual(folders, SUPPORT_FOLDERS)
        self.assertIn("references/product-states.md",
                      {row["path"] for row in record["support"]})

    def test_evals_cover_every_heading_and_open_state_risks(self):
        path = SKILL / "evals" / "section-support-cases.json"
        self.assertTrue(path.is_file(), "missing section support evals")
        cases = load(path)["cases"]
        headings = [row["heading"] for row in
                    direct_sections(BODY.read_text(encoding="utf-8"))]
        covered = [row["heading"] for row in cases]
        self.assertEqual(covered, headings)
        product = next(row for row in cases
                       if row["heading"] == "Discover product states")
        risks = set(product["reject"])
        self.assertIn("closed state list", risks)
        self.assertIn("script-owned state choice", risks)
        self.assertIn("decorative support link", risks)
        self.assertIn("collapsed concurrent states", risks)

    def test_eval_manifest_keeps_body_and_whole_skill_cold_reads_apart(self):
        contract = (SKILL / "evals" / "contract.md").read_text()
        rubric = (SKILL / "evals" / "rubric.md").read_text()
        self.assertIn("body-only cold read", contract)
        self.assertIn("whole-skill cold run", contract)
        self.assertIn("Neither pass may substitute", contract)
        self.assertIn("both first-time passes", rubric)

    def test_checker_rejects_a_heading_without_direct_support(self):
        self.assertTrue(CHECKER.is_file(),
                        "missing scripts/check_section_support.py")
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            for routed in ["references/product-states.md",
                           "assets/state-record.schema.json",
                           "examples/product-states.md",
                           "evals/section-support-cases.json"]:
                text = text.replace(routed, pathlib.Path(routed).name)
            path.write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                                     "check_section_support.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Discover product states", result.stdout)

    def test_checker_rejects_script_owned_judgment(self):
        self.assertTrue(CHECKER.is_file(),
                        "missing scripts/check_section_support.py")
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "assets" / "section-support.json"
            data = load(path)
            data["sections"][0]["judgment_owner"] = "script"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                                     "check_section_support.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("model must own judgment", result.stdout)


if __name__ == "__main__":
    unittest.main()
