"""Contracts for fast deterministic work without caching live judgment."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CACHEABLE = {"validate", "lint-writing", "lint-code",
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

    def test_bounded_concurrency_and_cache_are_enabled(self):
        for config in self.configs:
            settings = config["settings"]
            self.assertTrue(settings["experimental"])
            self.assertGreater(settings["jobs"], 1)
            self.assertGreater(len(config["tasks"]["ci"]["depends"]), 1)

    def test_static_checks_have_complete_cache_shape(self):
        for config in self.configs:
            for name in CACHEABLE:
                task = config["tasks"][name]
                self.assertTrue(task["cache"]["enabled"], name)
                self.assertTrue(task["sources"], name)
                self.assertEqual(task["outputs"], [], name)

    def test_live_or_mutating_work_is_not_cached(self):
        for config in self.configs:
            for name in LIVE & set(config["tasks"]):
                task = config["tasks"][name]
                self.assertFalse(task.get("cache", {}).get("enabled", False),
                                 name)


if __name__ == "__main__":
    unittest.main()
