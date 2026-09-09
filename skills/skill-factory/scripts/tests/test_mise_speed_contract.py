"""These package-wide gates rerun until a complete cache boundary is proved."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
FRESH_CHECKS = {"validate", "lint-writing", "lint-code", "test-ci",
                "lint-placeholders", "evals", "improvement-policy"}
LIVE = {"test", "domain-research-policy", "mise-primitives-policy",
        "lineage", "doctor", "new", "validate-target", "eval-target",
        "plan-standardize", "audit-source-corpus", "mise-latest"}


def load(path):
    with path.open("rb") as handle:
        return tomllib.load(handle)


class TestMiseSpeedContract(unittest.TestCase):
    def setUp(self):
        self.configs = [
            load(SKILL_DIR / "mise.toml"),
            load(SKILL_DIR / "assets/mise-template.toml"),
        ]

    def test_independent_checks_have_bounded_concurrency(self):
        for config in self.configs:
            settings = config["settings"]
            self.assertTrue(settings["experimental"])
            self.assertGreater(settings["jobs"], 1)
            self.assertGreater(len(config["tasks"]["ci"]["depends"]), 1)

    def test_package_checks_cannot_skip_for_partial_inputs(self):
        for config in self.configs:
            for name in FRESH_CHECKS & set(config["tasks"]):
                task = config["tasks"][name]
                self.assertNotIn("sources", task, name)
                self.assertNotIn("outputs", task, name)
                self.assertFalse(task.get("cache", {}).get("enabled", False), name)

    def test_live_or_mutating_work_is_not_cached(self):
        for config in self.configs:
            for name in LIVE & set(config["tasks"]):
                task = config["tasks"][name]
                self.assertFalse(task.get("cache", {}).get("enabled", False),
                                 name)


if __name__ == "__main__":
    unittest.main()
