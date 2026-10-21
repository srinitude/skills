"""Explicit refresh uses the recorded baseline and preserves intentional edits."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scope_standardization import snapshot
from test_skill_variant import plan
from test_variant_acceptance import accept, reviewed_accept
from variant_fixtures import package, project, review, write_json


def initial(base):
    atlas = project(base / "atlas")
    boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
    scenarios = [(atlas, "Python src"), (boreal, "JavaScript lib")]
    source = package(base / "source" / "demo-skill", "project")
    candidate = package(base / "stage" / "portable-inventory", "user")
    dest = base / "accepted"
    dest.mkdir()
    result = plan(source, dest, "user", candidate.name)
    data = json.loads(result.stdout)
    result = accept(base, data, source, candidate, scenarios)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return source, candidate, dest / candidate.name, scenarios, data


def _TestVariantRefresh_test_exact_rerun_is_a_noop_and_collision_keeps_files(self):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source, candidate, target, scenarios, data = initial(base)
        before = snapshot(target)
        result = accept(base, data, source, candidate, scenarios)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["unchanged"])
        self.assertEqual(snapshot(target), before)
        self.assertEqual(output.get("execution_acceptance"), "pending")
        self.assertIn("reviewed rerun", output["validation"][0]["claim"])
        (target / "CUSTOM.md").write_text("Intentional customization.\n")
        before = snapshot(target)
        result = accept(base, data, source, candidate, scenarios)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(snapshot(target), before)

def _TestVariantRefresh_complete_merge(self, base, source, target, merged, scenarios, data):
    file = merged / "scripts/inventory.py"
    file.write_text(file.read_text().replace('not line.startswith("#")', 'bool(line.strip()) and not line.startswith("#")'))
    for project_root, _ in scenarios:
        config = json.loads((project_root / "inventory.json").read_text())
        next((project_root / config["directory"]).rglob("*" + config["extension"])).write_text("first\n\n# comment\nsecond\n")
    value = review(source, merged, scenarios)
    value["resolutions"] = {"scripts/inventory.py": "Keep variant comment exclusion and add upstream blank-line exclusion."}
    write_json(base / "review.json", value)
    result = reviewed_accept("accept", "--plan", base / "plan.json",
                 "--candidate", merged, "--review", base / "review.json")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual((target / "CUSTOM.md").read_text(), "Keep comment exclusion.\n")
    lineage = json.loads((target / "evals/source-lineage.json").read_text())
    self.assertEqual(lineage["derivation"]["source"]["digest"], data["source"]["digest"])
    for name, expected in self.preserved.items():
        file = target / name
        self.assertTrue(file.is_file(), name)
        self.assertEqual((file.read_bytes(), file.stat().st_mode, file.stat().st_ino), expected)

def _TestVariantRefresh_exercise_conflict(self, base):
    source, candidate, target, scenarios, _ = initial(base)
    expression = "len(p.read_text().splitlines())"
    upstream = source / "scripts/inventory.py"
    upstream.write_text(upstream.read_text().replace(expression, "sum(bool(line.strip()) for line in p.read_text().splitlines())"))
    custom = target / "scripts/inventory.py"
    custom.write_text(custom.read_text().replace(expression, 'sum(not line.startswith("#") for line in p.read_text().splitlines())'))
    (target / "CUSTOM.md").write_text("Keep comment exclusion.\n")
    self.preserved = {}
    for name in ['.git/local-state', 'node_modules/local-state']:
        file = target / name; file.parent.mkdir(parents=True)
        file.write_bytes(b'preserve refresh state\x00'); file.chmod(0o600)
        self.preserved[name] = (file.read_bytes(), file.stat().st_mode, file.stat().st_ino)
    before_source, before_target = snapshot(source), snapshot(target)
    result = plan(source, target.parent, "user", target.name, "--refresh")
    data = json.loads(result.stdout)
    self.assertEqual(data["refresh"]["conflicts"], ["scripts/inventory.py"])
    merged = base / "merged" / target.name
    shutil.copytree(target, merged)
    result = accept(base, data, source, merged, scenarios)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertEqual(snapshot(source), before_source)
    self.assertEqual(snapshot(target), before_target)
    self.complete_merge(base, source, target, merged, scenarios, data)

def _TestVariantRefresh_test_conflicting_refresh_blocks_then_merges_without_losing_customization(self):
    with tempfile.TemporaryDirectory() as temp:
        self.exercise_conflict(Path(temp))


class TestVariantRefresh(unittest.TestCase):
    test_exact_rerun_is_a_noop_and_collision_keeps_files = _TestVariantRefresh_test_exact_rerun_is_a_noop_and_collision_keeps_files
    test_conflicting_refresh_blocks_then_merges_without_losing_customization = _TestVariantRefresh_test_conflicting_refresh_blocks_then_merges_without_losing_customization
    exercise_conflict = _TestVariantRefresh_exercise_conflict
    complete_merge = _TestVariantRefresh_complete_merge
