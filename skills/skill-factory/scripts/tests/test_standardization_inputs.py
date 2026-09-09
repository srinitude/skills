"""Test declaration preservation and preflight; no semantic acceptance claim."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_mapping_promotion import snapshot
from test_standardize_registry_skill import profile, write_target


class TestStandardizationInputs(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "clock-anchor"
        write_target(self.root)
        self.config = self.base / "profile.json"
        self.data = profile()

    def invoke(self):
        self.config.write_text(json.dumps(self.data))
        return run("standardize_registry_skill.py", self.root, "--profile", self.config,
                   "--scope", "user", "--apply")

    def test_unresolved_declarations_block_without_touching_target(self):
        good = json.dumps(self.data)
        before = snapshot(self.root)
        for field in ["audience", "initial_context"]:
            self.data = json.loads(good)
            self.data.pop(field)
            result = self.invoke()
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(field, result.stderr)
            self.assertEqual(snapshot(self.root), before)
        self.data = json.loads(good)
        self.assertEqual(self.invoke().returncode, 0)

    def test_existing_use_case_meaning_and_extensions_are_preserved(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.root / "assets/use-case-contract.json"
        original = json.loads(path.read_text())
        original.update(audience=self.data["audience"], initial_context=self.data["initial_context"])
        original["domain_dimensions"]["quality"] = ["Clock anchor keeps exact offset and per-turn freshness."]
        original["domain_extension"] = {"precision": "one observed anchor, no invented refresh"}
        raw = json.dumps(original, separators=(",", ":")) + "\n"
        path.write_text(raw)
        accepted = run("check_use_case_contract.py", self.root, "--accept")
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_text(), raw)

    def test_conflicting_existing_audience_cannot_be_relabelled(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.root / "assets/use-case-contract.json"
        original = json.loads(path.read_text())
        original.update(audience={"primary": "human"}, initial_context=self.data["initial_context"])
        path.write_text(json.dumps(original))
        before = snapshot(self.root)
        result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("audience", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_malformed_profile_sets_fail_cleanly_without_writes(self):
        before = snapshot(self.root)
        for data in [None, [], {"profiles": None}, {"profiles": {"clock-anchor": []}}]:
            self.config.write_text(json.dumps(data))
            result = run("standardize_registry_skill.py", self.root, "--profile", self.config,
                         "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(snapshot(self.root), before)

    def test_duplicate_profile_keys_fail_before_any_write(self):
        self.config.write_text('{"audience":{"primary":"human"},' + json.dumps(self.data)[1:])
        before = snapshot(self.root)
        result = run("standardize_registry_skill.py", self.root, "--profile", self.config,
                     "--scope", "user", "--apply")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("duplicate JSON key", result.stderr)
        self.assertEqual(snapshot(self.root), before)


    def test_existing_policy_records_and_bytes_survive_standardization(self):
        self.assertEqual(self.invoke().returncode, 0)
        expected = {}
        for name in ["primitive-lifecycle.json", "decision-records.json",
                     "invocation-receipt-template.json", "mise-primitives.json"]:
            path = self.root / "assets" / name
            record = json.loads(path.read_text())
            record["clock_extension"] = {"reason": "Clock anchor retains λ precision.",
                                         "evidence": ["measured offset", "historical review"]}
            raw = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\r\n").encode()
            path.write_bytes(raw)
            expected[name] = raw
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, raw in expected.items():
            self.assertEqual((self.root / "assets" / name).read_bytes(), raw)

    def test_invalid_existing_policy_input_rejects_and_recovers(self):
        self.assertEqual(self.invoke().returncode, 0)
        for name in ["primitive-lifecycle.json", "decision-records.json",
                     "invocation-receipt-template.json", "mise-primitives.json"]:
            path = self.root / "assets" / name
            valid = path.read_bytes()
            for invalid in [b"[]", b'{"skill":"clock-anchor","skill":"clock-anchor"}',
                            b'{"skill":"unrelated-skill"}']:
                path.write_bytes(invalid)
                before = snapshot(self.root)
                result = self.invoke()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(snapshot(self.root), before)
            path.write_bytes(valid)
            result = self.invoke()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(path.read_bytes(), valid)

    def test_stale_primitive_decision_blocks_promotion_then_recovers(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.root / "assets/mise-primitives.json"
        valid = path.read_bytes()
        data = json.loads(valid)
        group = data["groups"]["task"]
        group["used"].remove("description")
        group["not_applicable"].append("description")
        path.write_text(json.dumps(data))
        before = snapshot(self.root)
        result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("description", result.stderr)
        self.assertEqual(snapshot(self.root), before)
        path.write_bytes(valid)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_bytes(), valid)

    def test_existing_policy_owner_conflicts_block_promotion(self):
        self.assertEqual(self.invoke().returncode, 0)
        for name, change in [
            ("primitive-lifecycle.json", lambda d: d["profiles"][next(iter(d["profiles"]))].update(accept="unknown-task")),
            ("decision-records.json", lambda d: d["records"][0].update(owner="human")),
        ]:
            path = self.root / "assets" / name
            valid = path.read_bytes()
            data = json.loads(valid)
            change(data)
            path.write_text(json.dumps(data))
            before = snapshot(self.root)
            result = self.invoke()
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(snapshot(self.root), before)
            path.write_bytes(valid)
            result = self.invoke()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(path.read_bytes(), valid)

    def test_repository_formatter_receives_only_changed_files(self):
        self.assertEqual(self.invoke().returncode, 0)
        (self.base / ".git").mkdir()
        (self.base / ".prettierrc.json").write_text("{}")
        formatter = self.base / "node_modules/prettier/bin/prettier.cjs"
        formatter.parent.mkdir(parents=True)
        log = self.base / "format-log.json"
        formatter.write_text("require('node:fs').writeFileSync(" + json.dumps(str(log))
                             + ", JSON.stringify(process.argv.slice(2)));\n")
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(log.exists(), "a no-op must not invoke the formatter")
        self.data["text_rewrites"]["scripts/domain_check.py"].append(
            {"old": "FACTORY_ASSERTION", "new": "REVIEWED_ASSERTION"})
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        arguments = json.loads(log.read_text())
        self.assertEqual(arguments[0], "--write")
        self.assertTrue(all(Path(value).suffix for value in arguments[1:]))
        names = {Path(value).name for value in arguments[1:]}
        self.assertIn("domain_check.py", names)
        self.assertFalse(names & {"primitive-lifecycle.json", "decision-records.json",
                                 "invocation-receipt-template.json", "mise-primitives.json"})

    def test_formatter_cannot_invalidate_policy_before_promotion(self):
        (self.base / ".git").mkdir()
        (self.base / ".prettierrc.json").write_text("{}")
        formatter = self.base / "node_modules/prettier/bin/prettier.cjs"
        formatter.parent.mkdir(parents=True)
        formatter.write_text("const fs = require('node:fs');\n"
            "for (const file of process.argv.slice(3)) {\n"
            "  if (!file.endsWith('/decision-records.json')) continue;\n"
            "  const data = JSON.parse(fs.readFileSync(file));\n"
            "  data.records[0].owner = 'human';\n"
            "  fs.writeFileSync(file, JSON.stringify(data));\n}\n")
        before = snapshot(self.root)
        result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("owner", result.stderr)
        self.assertEqual(snapshot(self.root), before)
        formatter.write_text("void 0;\n")
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
