"""Contract tests for bundled scripts other than the run pipeline."""
import json
import hashlib
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


def run(path, *args):
    cmd = [sys.executable, str(path)]
    cmd.extend(str(arg) for arg in args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


class TestScriptContracts(unittest.TestCase):
    def test_every_script_documents_help(self):
        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))
        self.assertTrue(scripts, "scripts/ holds no python files")
        for script in scripts:
            result = run(script, "--help")
            self.assertEqual(result.returncode, 0, script.name)
            self.assertIn("usage", result.stdout.lower(), script.name)


class TestSkillInfo(unittest.TestCase):
    def test_info_reports_name_and_description(self):
        result = run(SKILL_DIR / "scripts" / "skill_info.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertEqual(info["name"], SKILL_DIR.name)
        self.assertTrue(info["description"])


class TestLineage(unittest.TestCase):
    def test_valid_chain_passes(self):
        script = SKILL_DIR / "scripts" / "check_lineage.py"
        path = SKILL_DIR / "evals" / "files" / "valid-lineage.json"
        result = run(script, path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_layer_skip_fails(self):
        script = SKILL_DIR / "scripts" / "check_lineage.py"
        path = SKILL_DIR / "evals" / "files" / "skipped-lineage.json"
        result = run(script, path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("skips", result.stdout)


class TestSourceLineage(unittest.TestCase):
    def test_skill_body_is_bound_to_context_routing_evidence(self):
        path = SKILL_DIR / "evals" / "source-lineage.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = {row["path"]: row["source_paths"]
                for row in data["public_files"]}
        self.assertIn("construction/context-routing-meaning-ledger.json",
                      rows["SKILL.md"])
        self.assertIn("construction/context-routing-validation.json",
                      rows["SKILL.md"])

    def test_current_public_hashes_pass(self):
        script = SKILL_DIR / "scripts" / "check_source_lineage.py"
        result = run(script, SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestGeneratedOwners(unittest.TestCase):
    def test_file_manifest_supports_a_non_mutating_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            import shutil
            shutil.copytree(SKILL_DIR, copy)
            script = copy / "scripts" / "build_file_manifest.py"
            self.assertEqual(run(script, copy).returncode, 0)
            matched = run(script, copy, "--check")
            manifest = copy / "assets" / "file-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")
            stale = run(script, copy, "--check")
        self.assertEqual(matched.returncode, 0, matched.stderr)
        self.assertEqual(stale.returncode, 1)
        self.assertIn("differs", stale.stderr)

    def test_lineage_builder_supports_a_non_mutating_check(self):
        claim = (SKILL_DIR.parents[1] / "evidence" / "ports" /
                 "design-like-im-5" / "source-manifest.json")
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            import shutil
            shutil.copytree(SKILL_DIR, copy)
            script = copy / "scripts" / "build_lineage.py"
            self.assertEqual(run(script, copy, "--claim-file", claim).returncode,
                             0)
            matched = run(script, copy, "--claim-file", claim, "--check")
            lineage = copy / "evals" / "source-lineage.json"
            lineage.write_text("{}\n", encoding="utf-8")
            stale = run(script, copy, "--claim-file", claim, "--check")
        self.assertEqual(matched.returncode, 0, matched.stderr)
        self.assertEqual(stale.returncode, 1)
        self.assertIn("differs", stale.stderr)

    def test_lineage_builder_refreshes_the_repository_baseline_owner(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "repo"
            copy = repo / "skills" / SKILL_DIR.name
            claim = repo / "evidence" / "ports" / SKILL_DIR.name / "source-manifest.json"
            shutil.copytree(SKILL_DIR, copy)
            claim.parent.mkdir(parents=True)
            source_claim = (SKILL_DIR.parents[1] / "evidence" / "ports" /
                            SKILL_DIR.name / "source-manifest.json")
            shutil.copy2(source_claim, claim)
            added = copy / "examples" / "new-public.md"
            added.write_text("# New public case\n", encoding="utf-8")
            script = copy / "scripts" / "build_lineage.py"
            result = run(script, copy, "--claim-file", claim,
                         "--refresh-claim-only")
            data = json.loads(claim.read_text(encoding="utf-8"))
        rows = {row["source_path"]: row for row in data["files"]}
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(rows["examples/new-public.md"]["sha256"],
                         hashlib.sha256(b"# New public case\n").hexdigest())
        self.assertEqual(rows["examples/new-public.md"]["location_kind"],
                         "repository")
        self.assertIn("construction/case-study-ledger.json", rows)
        packet = "".join(f"{row['source_path']}\0{row['sha256']}\n"
                         for row in sorted(data["files"],
                                           key=lambda item: item["source_path"]))
        digest = hashlib.sha256(packet.encode()).hexdigest()
        self.assertEqual(data["native_manifest_sha256"], digest)
        self.assertEqual(data["evidence_packet_sha256"], digest)


class TestEvalSpeedContract(unittest.TestCase):
    def test_eval_checker_accepts_the_standard_manifest(self):
        result = run(SKILL_DIR / "scripts" / "check_evals.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_speed_budget_defines_lossless_parallel_work(self):
        path = SKILL_DIR / "assets" / "speed-policy.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["objective"],
                         "minimum_elapsed_time_to_fully_verified_result")
        self.assertEqual(data["invariants"], {
            "proof_loss_allowed": False,
            "required_work": "all",
            "scope_loss_allowed": False,
            "workflow_action_concurrency": 1,
            "writers_per_artifact": 1,
        })
        self.assertEqual(
            {row["id"] for row in data["parallel_groups"]},
            {"context_reads", "current_sources", "package_checks",
             "render_capture_matrix"})
        self.assertEqual(
            {row["id"] for row in data["never_parallelize"]},
            {"missing_context_judgment", "shared_writer",
             "unfrozen_inputs", "workflow_actions"})
        self.assertEqual(data["reuse"]["required_check"],
                         "rerun_each_required_check")
        self.assertEqual(data["measurement"]["package_jobs"], 8)

    def test_eval_checker_rejects_a_lost_speed_invariant(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL_DIR, copy)
            path = copy / "assets" / "speed-policy.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data.get("invariants", {}).pop("proof_loss_allowed", None)
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run(copy / "scripts" / "check_evals.py", copy)
        self.assertEqual(result.returncode, 1)
        self.assertIn("speed-policy.json", result.stdout)

class TestReading(unittest.TestCase):
    def test_long_sentence_fails(self):
        import tempfile
        script = SKILL_DIR / "scripts" / "check_reading.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "hard-prose.md"
            words = ["This", "sentence", "has", "far", "too", "many",
                     "words", "and", "must", "fail", "the", "fixed",
                     "public", "reading", "check", "before", "anyone",
                     "can", "call", "it", "done."]
            path.write_text(" ".join(words) + "\n", encoding="utf-8")
            result = run(script, path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("long sentence", result.stdout)

    def test_exact_contract_is_the_only_exempt_file(self):
        script = SKILL_DIR / "scripts" / "check_reading.py"
        path = SKILL_DIR / "references" / "generation-contract.md"
        result = run(script, path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("approved exact copy", result.stdout)


class TestExamples(unittest.TestCase):
    def test_product_state_example_is_generated(self):
        script = SKILL_DIR / "scripts" / "build_examples.py"
        spec = importlib.util.spec_from_file_location("build_examples", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = SKILL_DIR / "examples" / "product-states.md"
        self.assertIn(expected, module.documents())

    def test_context_packet_example_is_generated(self):
        script = SKILL_DIR / "scripts" / "build_examples.py"
        spec = importlib.util.spec_from_file_location("build_examples", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = SKILL_DIR / "examples" / "context-packets.md"
        self.assertIn(expected, module.documents())

    def test_current_examples_match_real_commands(self):
        script = SKILL_DIR / "scripts" / "build_examples.py"
        result = run(script, "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
