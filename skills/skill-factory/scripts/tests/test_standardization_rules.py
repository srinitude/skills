"""Updates keep canonical rules in real tasks without replacing domain rules."""
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from cli import SKILL_DIR
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from standardization_fixtures import profile, write_target
from standardization_render import BODY_POLICIES, body_policy, render
from standardize_registry_skill import COPIES, SCRIPTS, CANONICAL_SCRIPTS


def updated(original=None):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "clock-anchor"
        write_target(root)
        files = original or {p.relative_to(root).as_posix(): p.read_bytes()
                             for p in root.rglob("*") if p.is_file()}
        if original is None:
            files["SKILL.md"] += b"\nNever infer a missing UTC offset.\n"
        return render(root, files, profile(), None, SKILL_DIR,
                      (COPIES, SCRIPTS, CANONICAL_SCRIPTS), "2026-01-01T00:00:00Z")


def test_updated_body_routes_complete_policies(self):
    files = updated()
    tasks = tomllib.loads(files["mise.toml"].decode())["tasks"]
    body = files["SKILL.md"].decode()
    self.assertIn("mise run rule:body-context", body)
    self.assertIn("Run `mise run anchor` once.", body)
    self.assertIn("Never infer a missing UTC offset.", body)
    template = (SKILL_DIR / "assets/skill-template.md").read_text()
    descriptions = "\n".join(task.get("description", "") for task in tasks.values())
    for prefix in BODY_POLICIES:
        _, policy = body_policy("", template, prefix)
        self.assertIn(policy.replace("{{NAME}}", "clock-anchor"), descriptions)
    for name in ["rule:body-context", "rule:body-ledger-relationships", "rule:body-loop-contract"]:
        self.assertEqual(tasks[name]["depends"], [name.replace("rule:body-", "rule:")])
        self.assertEqual(tasks[name]["run"], "node scripts/run_rule.ts " + name)
    operations = json.loads(files["assets/use-case-contract.json"])["task_graph"]["public_operations"]
    self.assertIn("rule:body-loop-contract", [row["task"] for row in operations])
    self.assertNotIn("**Relationship records.**", body)


def test_second_update_is_identical(self):
    files = updated()
    self.assertEqual(updated(files), files)


def test_prior_startup_migrates_once_and_preserves_examples(self):
    from scaffold_rules import START_RULES, LEGACY_START_RULES
    files = updated()
    old = files['SKILL.md'].decode().replace(START_RULES, LEGACY_START_RULES, 1)
    example = '\n```markdown\n' + LEGACY_START_RULES + '\n```\n'
    files['SKILL.md'] = (old + example).encode()
    result = updated(files)
    body = result['SKILL.md'].decode()
    self.assertIn(START_RULES, body)
    self.assertIn(example, body)
    self.assertIn('Never infer a missing UTC offset.', body)
    self.assertEqual(updated(result), result)


def test_mixed_duplicate_startup_requires_review(self):
    from scaffold_rules import LEGACY_START_RULES
    files = updated()
    files['SKILL.md'] += ('\n' + LEGACY_START_RULES + '\n').encode()
    before = dict(files)
    with self.assertRaisesRegex(ValueError, 'Duplicate.*reviewed.*migration'):
        updated(files)
    self.assertEqual(files, before)


def test_custom_startup_requires_review(self):
    from scaffold_rules import START_RULES
    files = updated()
    files['SKILL.md'] = files['SKILL.md'].replace(
        START_RULES.encode(), (START_RULES + '\nKeep our local approval gate.').encode(), 1)
    before = dict(files)
    with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
        updated(files)
    self.assertEqual(files, before)


def test_updated_skill_uses_broad_method_and_final_boundaries(self):
    files = updated()
    tasks = tomllib.loads(files["mise.toml"].decode())["tasks"]
    for name in ["rule:implementation-progress", "rule:selected", "rule:acceptance"]:
        self.assertEqual(tasks[name]["run"], "node scripts/run_rule.ts " + name)
    progress = tasks["rule:implementation-progress"]["description"]
    self.assertIn("main paths work", progress)
    self.assertIn("owner, required inputs, next action and deciding check", progress)
    self.assertIn("A small request needs a small change", progress)
    self.assertIn("whole domain result", tasks["rule:acceptance"]["description"])
    self.assertIn("broad working paths", tasks["rule:body-implementation-progress"]["description"])
    self.assertNotIn("Close the smallest ready functional path", tasks["rule:body-implementation-progress"]["description"])
    self.assertIn("Never infer a missing UTC offset.", files["SKILL.md"].decode())


def test_custom_policy_is_not_replaced(self):
    files = updated()
    files["SKILL.md"] += b"\n**Relationship records.** Keep our domain exception.\n"
    before = dict(files)
    with self.assertRaisesRegex(ValueError, "reviewed.*migration"):
        updated(files)
    self.assertEqual(files, before)


def test_custom_routed_owner_is_not_replaced(self):
    files = updated()
    name = "rule:body-ledger-relationships"
    self.assertIn(name.encode(), files["mise.toml"])
    files["mise.toml"] = files["mise.toml"].replace(
        ("node scripts/run_rule.ts " + name + '"').encode(), b'unsafe replacement"')
    before = dict(files)
    with self.assertRaisesRegex(ValueError, "reviewed.*migration"):
        updated(files)
    self.assertEqual(files, before)


def load_tests(loader, tests, pattern):
    methods = {name: value for name, value in globals().items() if name.startswith("test_")}
    return loader.loadTestsFromTestCase(type("UpdatedRuleTests", (unittest.TestCase,), methods))


def test_generated_skill_uses_the_same_owners(self):
    from test_scaffold_rules import rendered
    from standardization_rules import route_policies
    files = {name: raw.encode() for name, raw in rendered().items()}
    mise = files["mise.toml"]
    specs = route_policies(files, SKILL_DIR, "plain-skill")
    self.assertEqual(len(specs), 12)
    self.assertEqual(files["mise.toml"], mise)
    self.assertLessEqual(len(files["SKILL.md"].splitlines()), 200)
    once = dict(files)
    route_policies(files, SKILL_DIR, "plain-skill")
    self.assertEqual(files, once)


def test_existing_domain_records_gain_complete_routes(self):
    from check_task_graph import problems
    from standardization_runtime import MODEL_TASKS
    files = updated()
    contract = json.loads(files["assets/use-case-contract.json"])
    graph = contract["task_graph"]
    added = {name for name in graph["tasks"]
             if name.startswith("rule:body-") and name not in MODEL_TASKS}
    self.assertEqual(len(added), 12)
    graph["tasks"] = {name: row for name, row in graph["tasks"].items() if name not in added}
    graph["public_operations"] = [row for row in graph["public_operations"] if row["task"] not in added]
    contract["domain_note"] = "Keep the reviewed UTC offset rule."
    files["assets/use-case-contract.json"] = json.dumps(contract).encode()
    result = updated(files)
    actual = json.loads(result["assets/use-case-contract.json"])
    tasks = tomllib.loads(result["mise.toml"].decode())["tasks"]
    self.assertEqual(problems(tasks, actual), [])
    self.assertEqual(actual["domain_note"], contract["domain_note"])
    for name, row in graph["tasks"].items():
        self.assertEqual(actual["task_graph"]["tasks"][name], row)
