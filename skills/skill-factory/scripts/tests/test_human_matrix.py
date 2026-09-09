"""Exercise higher-order matrix records through their actual public workflow."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from human_matrix_fixtures import case, query, selector
from test_human_catalogs import resources


class TestHumanMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = resources()

    def test_higher_order_groups_preserve_order_multiplicity_and_unknown_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            original = case(base)
            result = query(base, original, self.bindings)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            groups = {item["id"]: item for item in data["matrix"]["groups"]}
            self.assertEqual(groups["study"]["members"], ["education", "psychology"])
            self.assertEqual(groups["practice"]["members"], ["practice-1", "practice-2"])
            self.assertEqual(groups["work"]["members"], ["practice", "write"])
            self.assertEqual(data["view"], [{"interaction": "practice-and-create", "study": ["study"], "work": ["work"]}])
            self.assertEqual(data["coverage"]["evidence"], "not-evaluated")
            self.assertEqual(data["coverage"]["executed_tests"], "not-evaluated")
            self.assertEqual(data["matrix"]["interactions"][0]["state"], "unknown")
            original["groups"][0]["members"].reverse()
            equivalent = query(base, original, self.bindings)
            self.assertEqual(equivalent.returncode, 0, equivalent.stderr)
            self.assertEqual(json.loads(equivalent.stdout)["canonical_sha256"], data["canonical_sha256"])
            original["groups"][1]["members"].reverse()
            different = query(base, original, self.bindings)
            self.assertEqual(different.returncode, 0, different.stderr)
            self.assertNotEqual(json.loads(different.stdout)["canonical_sha256"], data["canonical_sha256"])

    def test_unknown_extensions_are_addressable_without_approximate_identity_substitution(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            document["extensions"] = [{"id": "extension:unfamiliar-practice", "label": "Unfamiliar practice",
                "definition": None, "aliases": ["local-practice"], "state": "unresolved", "source": {
                    "record": "brief", "version": "fixture-1", "url": None, "locator": "brief",
                    "scope": "Only the supplied fixture brief", "license": "Test input"}}]
            document["occurrences"].append({"id": "unfamiliar", "concept": "extension:unfamiliar-practice",
                                            "role": "activity", "conditions": []})
            document["correspondences"] = [{"id": "hypothesis", "from": "extension:unfamiliar-practice",
                "to": "icatus-2016/741", "relation": "close_match", "judgment": "brief"}]
            result = query(base, document, self.bindings)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["concepts"]["extension:unfamiliar-practice"]["state"], "unresolved")
            self.assertEqual(data["matrix"]["occurrences"][-1]["concept"], "nist-ai-200-1-2024/content-creation")
            document["occurrences"][-1]["concept"] = "local-practice"
            rejected = query(base, document, self.bindings)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("unknown concept", rejected.stderr)

    def test_cycles_changed_bindings_and_unsupported_comparator_fail_before_result(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            original = case(base)
            cycle, changed, comparator = [copy.deepcopy(original) for _ in range(3)]
            cycle["groups"][1]["members"].append("work")
            changed["records"]["brief"]["sha256"] = "0" * 64
            comparator["comparator"] = "ambient-locale"
            for name, document in [("cycle", cycle), ("changed", changed), ("comparator", comparator)]:
                result = query(base, document, self.bindings)
                self.assertNotEqual(result.returncode, 0, name)
                self.assertEqual(result.stdout, "", name)
            repaired = query(base, original, self.bindings)
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)

    def test_complete_catalog_space_is_symbolic_without_claiming_enumeration(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            space = selector("product", 1000000)
            space["pools"] = [{"catalog": "onet-31.0"}]
            document["selectors"] = [space]
            result = query(base, document, self.bindings)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["spaces"][0]["pool_sizes"], [3006])
            self.assertEqual(data["enumeration"], {"state": "not-requested"})
            self.assertLess(len(result.stdout), 1000000)


if __name__ == "__main__":
    unittest.main()
