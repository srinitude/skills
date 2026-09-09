"""Bound complete enumeration, keeping native positional identity and honest scope."""
import json
import tempfile
import unittest
from pathlib import Path

from human_matrix_fixtures import case, query, selector
from test_human_catalogs import resources

LIMITS = ["--enumerate", "space", "--max-members", "12", "--max-output-bytes", "1000000",
          "--max-memory-bytes", "200000000", "--max-seconds", "30"]


class TestHumanEnumeration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = resources()

    def test_native_combinatorial_operators_have_exact_complete_outputs(self):
        expected = {"combinations": [[0, 1], [0, 2], [1, 2]],
                    "permutations": [[0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1]],
                    "combinations_with_replacement": [[0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [2, 2]],
                    "product": [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]}
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            for operation, indices in expected.items():
                document["selectors"] = [selector(operation)]
                result = query(base, document, self.bindings, LIMITS)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                data = json.loads(result.stdout)["enumeration"]
                self.assertEqual([[item["index"] for item in member["positions"]]
                                  for member in data["members"]], indices)
                self.assertEqual(data["state"], "complete")
                self.assertEqual(data["count"], str(len(indices)))
                self.assertGreater(data["metrics"]["peak_traced_bytes"], 0)
                self.assertGreater(data["metrics"]["input_pool_bytes"], 0)
                self.assertLessEqual(data["metrics"]["peak_traced_bytes"], 200000000)
                self.assertLessEqual(len(result.stdout.encode()), 1000000)

    def test_missing_or_exceeded_budgets_cannot_return_partial_success(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            document["selectors"] = [selector("product", 1000000)]
            rejected = query(base, document, self.bindings, LIMITS)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout, "")
            self.assertIn("budget", rejected.stderr)
            document["selectors"] = [selector("combinations")]
            for extra in [["--enumerate", "space"], ["--max-members", "2"],
                          [*LIMITS[:3], "2", *LIMITS[4:]], [*LIMITS[:5], "10", *LIMITS[6:]],
                          [*LIMITS[:7], "1", *LIMITS[8:]]]:
                rejected = query(base, document, self.bindings, extra)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(rejected.stdout, "")
            restored = query(base, document, self.bindings, LIMITS)
            self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)

    def test_repetitions_keep_distinct_positions_and_each_member_uses_the_existing_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            document["selectors"] = [selector("permutations", ids=["icatus-2016/741", "icatus-2016/741"])]
            result = query(base, document, self.bindings, LIMITS)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            members = json.loads(result.stdout)["enumeration"]["members"]
            self.assertEqual(len(members), 2)
            self.assertNotEqual(members[0]["address"], members[1]["address"])
            member = members[1]
            document["occurrences"].extend(member["occurrences"])
            document["groups"].extend(member["groups"])
            document["interactions"][0]["work"].append(member["groups"][0]["id"])
            consumed = query(base, document, self.bindings)
            self.assertEqual(consumed.returncode, 0, consumed.stdout + consumed.stderr)
            self.assertEqual(json.loads(consumed.stdout)["coverage"]["executed_tests"], "not-evaluated")

    def test_empty_spaces_and_zero_length_do_not_allocate_impossible_members(self):
        cases = [("product", 0, [], 1), ("combinations", 0, [], 1),
                 ("combinations_with_replacement", 2, [], 0),
                 ("combinations", 1000000000, ["icatus-2016/741"], 0),
                 ("permutations", 1000000000, ["icatus-2016/741"], 0)]
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            for operator, length, ids, expected in cases:
                document["selectors"] = [selector(operator, length, ids)]
                result = query(base, document, self.bindings, LIMITS)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["enumeration"]["count"], str(expected))

    def test_deadline_rejects_and_budget_arguments_use_the_documented_numeric_grammar(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            document = case(base)
            document["selectors"] = [selector("combinations")]
            timed = query(base, document, self.bindings, [*LIMITS[:-1], "0.000001"])
            self.assertNotEqual(timed.returncode, 0)
            self.assertEqual(timed.stdout, "")
            self.assertIn("time budget exceeded", timed.stderr)
            for invalid in ["1e2", "0x10", ""]:
                rejected = query(base, document, self.bindings, [*LIMITS[:3], invalid, *LIMITS[4:]])
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(rejected.stdout, "")


if __name__ == "__main__":
    unittest.main()
