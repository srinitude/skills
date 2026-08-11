"""Source lineage and portability checks."""
import hashlib
import json
import pathlib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
ROOT = SKILL.parents[1]
PACKET = "0061515853b8d4bf3075b7db9d1a70d0e055b573a95cd87f560cad1ade1656dc"
FILES = {
    "SKILL.md": ("native/SKILL.native.md", "40e5fb7120ee0f12d88b1a3e746d4b5a2fbccab27e24df09a10c471931c45744"),
    "references/eval-cases.json": ("native/references/eval-cases.json", "255f8fd2faeee23517d7bf3ece71ef589c0b5740c97fd32b3da05aa876a37eb6"),
    "references/preservation-contract.md": ("native/references/preservation-contract.md", "8c5e1e6bb47f2d6be3d10bbd794992dd45ac2e11f1a51534f69a9f54d69cba75"),
    "references/simplification-model.md": ("native/references/simplification-model.md", "190898eda63f44af800c1c0cb4b18a5fab592b6c7b329d2dd3715cec88294598"),
}


def load(relative):
    return json.loads((SKILL / relative).read_text())


class TestSourceMapping(unittest.TestCase):
    def test_native_packet(self):
        evidence = ROOT / "evidence/ports/simplify-skill"
        rows = []
        for source, (relative, expected) in FILES.items():
            digest = hashlib.sha256((evidence / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected)
            rows.append(f"{source}\0{digest}\n")
        self.assertEqual(hashlib.sha256("".join(rows).encode()).hexdigest(), PACKET)

    def test_mapping_is_complete(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(mapping["coverage"], {"mapped_nonblank_lines": 503, "ratio": 1, "source_nonblank_lines": 503})
        self.assertTrue(all(row["action"] != "drop" and row["review_state"] == "approved" for row in mapping["entries"]))

    def test_cases_bind_to_lineage(self):
        lineage = load("evals/source-lineage.json")
        cases = load("evals/cases.json")
        self.assertEqual(lineage["native_manifest_sha256"], PACKET)
        self.assertEqual([case["source_id"] for case in cases["cases"]], lineage["active_case_ids"])

    def test_public_contract_has_no_private_hard_load(self):
        source = (SKILL / "SKILL.md").read_text()
        for fragment in ["skill_" + "view", "skills_" + "list", "global-coding" + "-policy"]:
            self.assertNotIn(fragment, source)
        self.assertIn("BLOCKED_DEPENDENCY", source)


if __name__ == "__main__":
    unittest.main()
