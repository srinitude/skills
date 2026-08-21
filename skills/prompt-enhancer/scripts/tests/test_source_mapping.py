"""Lineage tests for the native-to-public prompt-enhancer contract."""
import hashlib
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "adb4e552faaa62157b0592667a2e89ddec27f75d1eb3e3ada48a52d1e4739bd6",
    "assets/delivery-template.md": "a09fe1140f923564abc52795fb176b5ffe72f240e844a8449a3eaaaea9f547ef",
    "evals/cases.json": "3137232f836be2f1b386dbab8dcc5c67bb7f496c45744079744ed83a1fce43ac",
    "scripts/check_delivery.py": "fec1cf0110bff568880cb180d55e9f75cafa15de4f52ca82efe3a428a1a50993",
    "scripts/check_prompt.py": "b1e8cc09ec3a8a4fee008f8e5c3e64834bd0a39c3f6ac324fd42444d52e54ea8",
    "scripts/check_prose.py": "b916e0d27868e40b1573071e4beb9300738cd15c5e02dd931f139ccbc47d0a9a",
    "scripts/context_checks.py": "21f513d8f9a7bb527c0bea49cab8983f526406d07cdf3372a09ec7c4ea18e23b",
    "scripts/scan_secrets.py": "889d345d1b52e76bb9148277137ae2f78c2a864c11098a98d83231b10c53df9f",
}
EXPECTED_CASES = [f"PE-{number:03d}" for number in range(1, 17)]
EXPECTED_PACKET = "1b2dc4a3ba5b94812d22b9107291bd4dc88590daa23b2c36c8ce09d2b25ccbb2"
EVIDENCE_PATHS = {
    "SKILL.md": "native/SKILL.native.md",
    "assets/delivery-template.md": "native/assets/delivery-template.md",
    "evals/cases.json": "native/evals/cases.json",
    "scripts/check_delivery.py": "native/scripts/check_delivery.py",
    "scripts/check_prompt.py": "native/scripts/check_prompt.py",
    "scripts/check_prose.py": "native/scripts/check_prose.py",
    "scripts/context_checks.py": "native/scripts/context_checks.py",
    "scripts/scan_secrets.py": "native/scripts/scan_secrets.py",
}
NONBLANK_LINES = 871


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


def native_root():
    return SKILL_DIR.parents[1] / "evidence" / "ports" / "prompt-enhancer"


class TestSourceLineage(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"]
                 for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(lineage["native_manifest_sha256"], EXPECTED_PACKET)

    def test_mapping_covers_every_nonblank_line(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(sorted(mapping["source_files"]),
                         sorted(EXPECTED_FILES))
        self.assertEqual(mapping["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(mapping["coverage"], {
            "source_nonblank_lines": NONBLANK_LINES,
            "mapped_nonblank_lines": NONBLANK_LINES,
            "ratio": 1,
        })
        self.assertEqual(len(mapping["entries"]), NONBLANK_LINES)


class TestSourceMapping(unittest.TestCase):
    def test_mapping_has_no_loss_or_pending_review(self):
        entries = load("evals/source-mapping.json")["entries"]
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertEqual({entry["review_state"] for entry in entries},
                         {"approved"})
        self.assertTrue(all(entry["evidence_target"] for entry in entries))

    def test_mapping_binds_native_lines_to_public_text(self):
        entries = load("evals/source-mapping.json")["entries"]
        source_lines = {
            source: (native_root() / EVIDENCE_PATHS[source]).read_text(encoding="utf-8").splitlines()
            for source in EXPECTED_FILES
        }
        for entry in entries:
            source = source_lines[entry["source_path"]][entry["source_line"] - 1]
            self.assertTrue(source.strip())
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),
                             entry["source_text_sha256"])
            self.check_entry_targets(entry)

    def check_entry_targets(self, entry):
        if entry["action"] == "clarify":
            self.assertEqual(entry["public_targets"], [])
            self.assertIn("portable omission", entry["preservation_judgment"])
            return
        self.assertTrue(entry["public_targets"])
        self.assertTrue(entry["public_assertions"])
        for assertion in entry["public_assertions"]:
            self.assertIn(assertion["target"], entry["public_targets"])
            public = (SKILL_DIR / assertion["target"]).read_text(encoding="utf-8")
            self.assertIn(assertion["contains"], public)


class TestSourceCases(unittest.TestCase):
    def test_public_cases_preserve_native_acceptance(self):
        native = json.loads((native_root() / "native" / "evals" /
                             "cases.json").read_text(encoding="utf-8"))
        public = load("evals/cases.json")
        self.assertEqual(len(public["cases"]), len(native["cases"]))
        for index, pair in enumerate(zip(public["cases"], native["cases"])):
            ported, source = pair
            self.assertEqual(ported["source_id"], EXPECTED_CASES[index])
            self.assertEqual(ported["title"], source["id"])
            self.assertEqual(ported["prompt"], source["input"])
            self.assertEqual(ported["required"], [source["expect"]])
            self.assertEqual(ported["veto"], [source["forbid"]])


if __name__ == "__main__":
    unittest.main()
