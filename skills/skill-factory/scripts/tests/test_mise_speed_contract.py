"""Contracts for fast deterministic work without caching live judgment."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from standardization_mise import normalize_mise
from standardization_seed import base_mise

CACHEABLE = {'validate', 'lint-writing', 'lint-code', 'lint-placeholders', 'evals', 'improvement-policy'}
LIVE = {"test", "domain-research-policy", "mise-primitives-policy", "lineage", "doctor", "new", "validate-target", "eval-target",
        "plan-standardize", "audit-source-corpus", "mise-latest"}

def load(path):
    with path.open("rb") as handle:
        return tomllib.load(handle)

def _TestMiseSpeedContract_setUp(self):
    self.configs = [load(SKILL_DIR / 'mise.toml'), load(SKILL_DIR / 'assets/mise-template.toml')]

def _TestMiseSpeedContract_test_bounded_concurrency_and_cache_are_enabled(self):
    for config in self.configs:
        settings = config["settings"]
        self.assertTrue(settings["experimental"])
        self.assertGreater(settings["jobs"], 1)
        self.assertGreater(len(config["tasks"]["ci"]["depends"]), 1)

def _TestMiseSpeedContract_test_static_checks_have_complete_cache_shape(self):
    for config in self.configs:
        for name in CACHEABLE:
            task = config["tasks"][name]
            self.assertTrue(task["cache"]["enabled"], name)
            self.assertTrue(task["sources"], name)
            self.assertEqual(task["outputs"], [], name)

def _TestMiseSpeedContract_test_live_or_mutating_work_is_not_cached(self):
    for config in self.configs:
        for name in LIVE & set(config["tasks"]):
            task = config["tasks"][name]
            self.assertFalse(task.get('cache', {}).get('enabled', False), name)


def native_source_files(sources, root):
    config = "[tasks.capture]\nsources = " + json.dumps(sources)
    config += "\nrun = " + json.dumps("printf '%s\\n' {{ task_source_files() | json_encode | quote }}")
    config += "\nrun_windows = " + json.dumps("echo {{ task_source_files() | json_encode }}") + "\n"
    (root / "mise.toml").write_text(config)
    result = subprocess.run(["mise", "run", "--force", "--task-cache", "off", "capture"],
        cwd=root, env=dict(os.environ, MISE_TRUSTED_CONFIG_PATHS=str(root)),
        capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise AssertionError(result.stderr + result.stdout)
    return set(json.loads(result.stdout))

def check_native_sources(case, task):
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp).resolve()
        files = ["SKILL.md", "references/guide.md", "evals/case.json",
                 "scripts/lint_writing.py", "scripts/check_placeholders.py", "scripts/skill_package.py",
                 "node_modules/vendor/README.md", "runtime/standardization/node_modules/vendor/case.json"]
        for name in files:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n")
        actual = native_source_files(task["sources"], root)
        case.assertIn("SKILL.md", actual)
        case.assertIn("references/guide.md", actual)
        case.assertIn("scripts/skill_package.py", actual)
        case.assertFalse(any("node_modules" in pathlib.PurePosixPath(path).parts for path in actual), actual)
        if "check_placeholders.py" in task["run"]:
            case.assertIn("evals/case.json", actual)

def _TestMiseSpeedContract_test_native_cache_inputs_keep_owned_prose_and_helpers(self):
    for config in self.configs:
        for name in ["lint-writing", "lint-placeholders"]:
            check_native_sources(self, config["tasks"][name])


def _TestMiseSpeedContract_test_legacy_cache_sources_migrate_without_losing_custom_rules(self):
    for name, script in [("lint-writing", "lint_writing"), ("lint-placeholders", "check_placeholders")]:
        legacy = ["**/*.md"] + (["**/*.json"] if name == "lint-placeholders" else [])
        legacy.append("scripts/" + script + ".py")
        header = "[tasks." + name + "]"
        field = "sources = " + json.dumps(legacy) + " # keep [this context]"
        source = base_mise({"primary_term": "skill"}).replace(header, header + "\n" + field)
        output = normalize_mise(source)
        expected = self.configs[0]["tasks"][name]["sources"]
        self.assertEqual(tomllib.loads(output)["tasks"][name]["sources"], expected)
        self.assertIn("# keep [this context]", output)
        self.assertEqual(normalize_mise(output), output)
        custom = source.replace(json.dumps(legacy), '["domain/*.md"]')
        with self.assertRaisesRegex(ValueError, "cache sources need explicit reconciliation"):
            normalize_mise(custom)

class TestMiseSpeedContract(unittest.TestCase):
    setUp = _TestMiseSpeedContract_setUp
    test_legacy_cache_sources_migrate_without_losing_custom_rules = _TestMiseSpeedContract_test_legacy_cache_sources_migrate_without_losing_custom_rules
    test_native_cache_inputs_keep_owned_prose_and_helpers = _TestMiseSpeedContract_test_native_cache_inputs_keep_owned_prose_and_helpers
    test_bounded_concurrency_and_cache_are_enabled = _TestMiseSpeedContract_test_bounded_concurrency_and_cache_are_enabled
    test_static_checks_have_complete_cache_shape = _TestMiseSpeedContract_test_static_checks_have_complete_cache_shape
    test_live_or_mutating_work_is_not_cached = _TestMiseSpeedContract_test_live_or_mutating_work_is_not_cached

if __name__ == "__main__":
    unittest.main()
