import copy
import unittest

import context
import viability_rules as rules
import yaml


def document():
    """Return the tested fixture as a mapping."""
    return yaml.safe_load(context.FIXTURE.read_text(encoding="utf-8"))


def errors_for(doc):
    """Return the viability problems for one document."""
    found = []
    rules.check_viability(doc, found)
    return found


class RecordedJudgmentTests(unittest.TestCase):
    def test_the_fixture_records_a_passing_judgment(self):
        self.assertEqual(errors_for(document()), [])

    def test_a_document_with_no_judgment_fails(self):
        doc = document()
        doc["meta"].pop("viability")
        problems = errors_for(doc)
        self.assertTrue(any("meta.viability" in item for item in problems))

    def test_the_overall_verdict_is_readable(self):
        self.assertEqual(rules.verdict_of(document()), "pass")


class CriteriaTests(unittest.TestCase):
    def test_a_missing_criterion_is_named(self):
        doc = document()
        doc["meta"]["viability"]["criteria"] = [
            item for item in doc["meta"]["viability"]["criteria"]
            if item["criterion"] != "contrast"]
        self.assertTrue(any("contrast" in item for item in errors_for(doc)))

    def test_a_failing_criterion_fails_the_document(self):
        doc = document()
        doc["meta"]["viability"]["criteria"][0]["verdict"] = "fail"
        self.assertTrue(any("must pass" in item for item in errors_for(doc)))

    def test_a_criterion_without_an_observation_fails(self):
        doc = document()
        doc["meta"]["viability"]["criteria"][0]["observed"] = ""
        self.assertTrue(any("observed" in item for item in errors_for(doc)))


class LoopTests(unittest.TestCase):
    def test_a_loop_past_the_cap_fails(self):
        doc = document()
        doc["meta"]["viability"]["iterations"] = rules.MAX_ITERATIONS + 1
        self.assertTrue(any("iterations" in item for item in errors_for(doc)))

    def test_a_missing_screenshot_file_fails(self):
        doc = copy.deepcopy(document())
        doc["meta"]["viability"]["screenshot_file"] = ""
        self.assertTrue(any("screenshot_file" in item for item in errors_for(doc)))


if __name__ == "__main__":
    unittest.main()
