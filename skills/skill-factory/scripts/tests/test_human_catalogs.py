"""Exercise real captured classifications at the public matrix entry."""
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path

from cli import SKILL_DIR, run
from test_standardization_inputs import prepare, invoke
from skill_package import inventory, tree_digest


def resources():
    registry = json.loads((SKILL_DIR / "assets/human-catalogs.json").read_text())
    cache = SKILL_DIR / ".artifacts/human-resources"
    cache.mkdir(parents=True, exist_ok=True)
    result = {}
    for identifier, spec in registry["catalogs"].items():
        path = cache / (spec["sha256"] + ".source")
        if not path.is_file():
            request = urllib.request.Request(spec["url"], headers={"User-Agent": "Public-source-research/1.0"})
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read(spec["bytes"] + 1)
            if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
                raise AssertionError("Captured source changed: " + identifier)
            path.write_bytes(raw)
        result[identifier] = {"path": str(path), "sha256": spec["sha256"]}
    return {"version": 1, "resources": result}


def matrix(arguments, root=SKILL_DIR):
    return subprocess.run(["mise", "run", "--force", "--task-cache", "off", "human-matrix", "--", *map(str, arguments)],
                          cwd=root, env={**os.environ, "NO_COLOR": "1"},
                          text=True, capture_output=True, timeout=120)


class TestHumanCatalogs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = resources()

    def test_complete_sources_and_exact_lookup_through_native_workflow(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "resources.json"
            path.write_text(json.dumps(self.bindings))
            selected = ["oecd-ford-2015/5.1", "isco-08/0110", "icatus-2016/741",
                        "onet-31.0/4.A.1.a.1.a", "nist-ai-200-1-2024/content-creation"]
            result = matrix(["--resources", path, "--concepts", json.dumps(selected)])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual([item["id"] for item in data["selected"]], selected)
            self.assertEqual({key: value["concepts"] for key, value in data["catalogs"].items()},
                             {"oecd-ford-2015": 48, "isco-08": 619, "icatus-2016": 230,
                              "onet-31.0": 3006, "nist-ai-200-1-2024": 16})
            self.assertIsNone(data["selected"][3]["definition"])
            self.assertIn("Private prayer", data["selected"][2]["label"])
            self.assertIn("generating new artifacts", data["selected"][4]["definition"])
            self.assertEqual(data["acceptance"], "pending")

    def test_missing_source_or_changed_capture_rejects_and_repair_recovers(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            path = base / "resources.json"
            changed = json.loads(json.dumps(self.bindings))
            saved = changed["resources"].pop("isco-08")
            path.write_text(json.dumps(changed))
            result = matrix(["--resources", path, "--concepts", '["icatus-2016/741"]'])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete", result.stderr)
            changed["resources"]["isco-08"] = saved
            raw = base / "changed.source"
            raw.write_bytes(Path(saved["path"]).read_bytes() + b" ")
            changed["resources"]["isco-08"] = {**saved, "path": str(raw)}
            path.write_text(json.dumps(changed))
            result = matrix(["--resources", path, "--concepts", '["icatus-2016/741"]'])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("changed", result.stderr)
            path.write_text(json.dumps(self.bindings))
            result = matrix(["--resources", path, "--concepts", '["icatus-2016/741","icatus-2016/741"]'])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(len(json.loads(result.stdout)["selected"]), 2)

    def test_new_and_standardized_outputs_resolve_their_own_captured_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            path = base / "resources.json"
            path.write_text(json.dumps(self.bindings))
            created = run("scaffold_skill.py", "--name", "human-context", "--description",
                          "Use when a writing task needs human context.", "--scope", "project",
                          "--audience", "human", "--dest", base)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            source, profile, prepared = prepare(base)
            before = inventory(source)
            updated = invoke(source, profile, prepared)
            self.assertEqual(updated.returncode, 0, updated.stdout + updated.stderr)
            for root in [base / "human-context", prepared]:
                self.assertTrue((root / "references/human-matrix-format.md").is_file())
                self.assertEqual((root / "references/human-matrix-format.md").read_bytes(),
                                 (SKILL_DIR / "references/human-matrix-format.md").read_bytes())
                for name in ["json.py", "pypdf.py", "shutil.py"]:
                    (root / "scripts" / name).write_text('raise RuntimeError("UNRELATED_DOMAIN_IMPORT")\n')
                result = matrix(["--resources", path, "--concepts", '["icatus-2016/741"]'], root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("UNRELATED_DOMAIN_IMPORT", result.stdout + result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data["implementation"], tree_digest(inventory(root)))
                self.assertEqual(data["selected"][0]["id"], "icatus-2016/741")
                self.assertEqual(data["acceptance"], "pending")
            self.assertEqual(inventory(source), before)

    def test_resource_version_is_not_a_boolean_and_unknown_ids_do_not_get_substituted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "resources.json"
            data = {**self.bindings, "version": True}
            path.write_text(json.dumps(data))
            rejected = matrix(["--resources", path, "--concepts", '["icatus-2016/741"]'])
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("version", rejected.stderr)
            path.write_text(json.dumps(self.bindings))
            rejected = matrix(["--resources", path, "--concepts", '["icatus-2016/unknown"]'])
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("unknown concept", rejected.stderr)

    def test_standardization_preserves_a_different_catalog_version_and_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source, profile, prepared = prepare(base)
            path = source / "assets/human-catalogs.json"
            path.parent.mkdir(exist_ok=True)
            path.write_text('{"version":9,"catalogs":{"independent-source":{}}}\n')
            before = inventory(source)
            result = invoke(source, profile, prepared)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reconcile", result.stderr)
            self.assertEqual(inventory(source), before)
            self.assertFalse(prepared.exists())


if __name__ == "__main__":
    unittest.main()
