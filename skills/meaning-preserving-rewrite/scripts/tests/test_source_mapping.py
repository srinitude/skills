"""Lineage and portability checks for the public rewrite skill."""
import hashlib
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILL_DIR.parents[1]
MANIFEST = "aa62cbdacdfe43f82ef90507f75400c2032791701b852cfd11544014a59dad28"
DOCS_SOURCE = "references/" + "her" + "mes-docs-inventory.md"
EXPECTED_FILES = {
    "SKILL.md": "a779c5dca688441ec314426a5f0f46ea14838577054a755d3ef1ed38ed170723",
    "references/baseline-task.md":
        "ab8fb06144c9ad7d9e93cd837fc8dc99549172e6a603adb98557777ac9abe771",
    "references/final-validation.md":
        "2818fac953449a3a64941baa0c83c5deea8c245dae106d8f825071f10e58aa64",
    DOCS_SOURCE:
        "ae55b0d0377064e498e57148961ee552d0105711cdd0877cfe8f160f57a778f9",
    "references/ledger-template.md":
        "2e26202c3f1fb5cd9c14e6407c35fcff20d89ebaaca85e379e33d03da86d65c8",
    "references/voice-check.md":
        "91fe711e5c0c769baf0c5efa29224371f04c45ec59de911ac62338af57b1a082",
}
EVIDENCE_FILES = {
    "SKILL.md": "native/SKILL.native.md",
    "references/baseline-task.md": "native/references/baseline-task.md",
    "references/final-validation.md": "native/references/final-validation.md",
    DOCS_SOURCE:
        "native/references/" + "her" + "mes-docs-inventory.md",
    "references/ledger-template.md": "native/references/ledger-template.md",
    "references/voice-check.md": "native/references/voice-check.md",
}


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file(self):
        lineage = load("evals/source-lineage.json")
        files = {item["path"]: item["sha256"]
                 for item in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"],
                         ["MPR-NO-NATIVE-CASES"])
        self.assertEqual(lineage["native_manifest_sha256"], MANIFEST)

    def test_native_evidence_is_byte_exact(self):
        root = REPO / "evidence/ports/meaning-preserving-rewrite"
        records = []
        for source, relative in EVIDENCE_FILES.items():
            data = (root / relative).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(digest, EXPECTED_FILES[source])
            records.append(f"{source}\0{digest}\n")
        packet = hashlib.sha256("".join(records).encode()).hexdigest()
        self.assertEqual(packet, MANIFEST)

    def test_mapping_covers_every_nonblank_line_without_drop(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(mapping["coverage"], {
            "source_nonblank_lines": 462,
            "mapped_nonblank_lines": 462,
            "ratio": 1,
        })
        entries = mapping["entries"]
        self.assertEqual(len(entries), 462)
        self.assertNotIn("drop", {item["action"] for item in entries})
        self.assertTrue(all(item["review_state"] == "approved"
                            for item in entries))
        self.assertTrue(all(item["public_target"] for item in entries))
        self.assertTrue(all(item["evidence_target"] for item in entries))
        self.assertTrue(all("source_text" not in item for item in entries))

    def test_target_cases_bind_to_lineage(self):
        lineage = load("evals/source-lineage.json")
        cases = load("evals/cases.json")["cases"]
        self.assertEqual([case["source_id"] for case in cases],
                         lineage["active_case_ids"])

    def test_public_skill_has_no_host_only_hard_load(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        forbidden = ["Hermes Agent", "SOUL", "AGENTS", "skill_manage",
                     "skill_view", "global-coding-policy"]
        self.assertFalse(any(token in text for token in forbidden))
        for token in ["Never use `drop`", "requirement strength",
                      "owner-only backup", "non-independent",
                      "component result"]:
            self.assertIn(token, text)
        reconciliation = (SKILL_DIR / "references" /
                          "dependency-reconciliation.md").read_text()
        self.assertIn("package simplification peer", reconciliation)
        self.assertIn("host writing policy", reconciliation)
        self.assertIn("does not replace source meaning", reconciliation)


if __name__ == "__main__":
    unittest.main()
