"""Contracts for vision-authored proof artifacts and script boundaries."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = SKILL_DIR / "evals" / "files"
ASSEMBLER = SKILL_DIR / "scripts" / "assemble_artifact.py"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from lib.coverage import analyze_coverage
OBLIGATIONS = (
    "conformance", "inputs", "intent", "possibilities", "narrowing",
    "coverage", "token-specimens", "experiments", "permutations", "metrics",
    "perceptual-motor-invariants", "taste", "originality",
    "corpus-uniqueness", "non-ai-slop", "visual-review", "failures",
    "boundary", "embedded-data",
)


def coverage_markup():
    tokens = json.loads((FIXTURES / "sample.tokens.json").read_text(encoding="utf-8"))
    evidence = json.loads((FIXTURES / "sample.evidence.json").read_text(encoding="utf-8"))
    manifest, errors = analyze_coverage(tokens, evidence)
    if errors:
        raise AssertionError(errors)
    token_nodes = "".join(f'<figure data-token-path="{item["path"]}">{item["path"]}</figure>' for item in manifest["token_paths"])
    stress_nodes = "".join(f'<figure data-stress-cell="{item["id"]}">{item["id"]}</figure>' for item in manifest["stress_groups"])
    variant_nodes = "".join(f'<figure data-permutation-cell="{cell["id"]}">{cell["id"]}</figure>' for group in manifest["variant_groups"] for cell in group["cells"])
    return token_nodes + stress_nodes + variant_nodes


def candidate(omit=None, external=False, missing_experiment=False, include_coverage=True):
    sections = "".join(f'<section data-proof-obligation="{name}"><h2>{name}</h2></section>' for name in OBLIGATIONS if name != omit)
    specimens = '<figure data-experimental-token="experimental.tokens.route-signal-softening">route</figure>'
    if not missing_experiment:
        specimens += '<figure data-experimental-token="experimental.tokens.risk-pulse-duration">risk</figure>'
    asset = '<script src="https://example.com/app.js"></script>' if external else ""
    coverage = coverage_markup() if include_coverage else ""
    return f'<!doctype html><html lang="en" data-dtcg-proof="2.0" data-artifact-authorship="vision-authored" data-run-id="__DTCG_RUN_ID__" data-verdict="__DTCG_VERDICT_STATE__"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Structural fixture</title><style>body{{font:16px sans-serif}}</style></head><body><p>__DTCG_PROOF_VERDICT__</p>{sections}{specimens}{coverage}<script id="proof-data" type="application/json">__DTCG_PROOF_DATA__</script>{asset}</body></html>'


def assemble(source, output, run_id="contract-run", evidence=None):
    evidence = evidence or FIXTURES / "sample.evidence.json"
    command = [sys.executable, str(ASSEMBLER), "--candidate", str(source), "--tokens", str(FIXTURES / "sample.tokens.json"), "--evidence", str(evidence), "--output", str(output), "--run-id", run_id]
    return subprocess.run(command, capture_output=True, text=True, timeout=30)


class TestArtifactBoundary(unittest.TestCase):
    def test_no_bundled_artifact_design_engine(self):
        forbidden = ["artifact.py", "artifact_css.py", "artifact_sections.py", "artifact_theme.py"]
        for name in forbidden:
            self.assertFalse((SKILL_DIR / "scripts" / "lib" / name).exists(), name)
        self.assertFalse((SKILL_DIR / "scripts" / "render_proof.py").exists())
        self.assertFalse((SKILL_DIR / "assets" / "proof-template.html").exists())
        self.assertFalse((SKILL_DIR / "assets" / "example-identity-board.svg").exists())
        self.assertTrue((SKILL_DIR / "assets" / "exploration-strategy-catalog.json").is_file())

    def test_rejected_visual_precedents_are_negative_evals(self):
        path = FIXTURES / "rejected-visual-precedents.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        self.assertEqual({item["expected_verdict"] for item in cases}, {"fail"})
        self.assertTrue(all("render_integrity" in item["failed_gates"] for item in cases))
        self.assertTrue(all(len(item["observed_failures"]) >= 5 for item in cases))

    def test_assembler_only_fills_authored_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            html = output.read_text(encoding="utf-8")
            self.assertEqual(report["status"], "assembled-pending-visual-review")
            self.assertIn('data-artifact-authorship="vision-authored"', html)
            self.assertIn('data-run-id="contract-run"', html)
            self.assertIn("PENDING VISUAL REVIEW", html)
            self.assertIn('id="proof-data"', html)
            self.assertNotIn("__DTCG_", html)
            self.assertNotIn("style-fingerprint", html)

    def test_missing_obligation_blocks_assembly(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(omit="visual-review"), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertIn("visual-review", result.stderr)

    def test_external_runtime_asset_blocks_standalone_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(external=True), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertIn("external runtime asset", result.stderr)

    def test_relative_runtime_assets_and_css_imports_also_block(self):
        for asset in ['<script src="./app.js"></script>', '<style>@import "theme.css";</style>', '<style>.hero{background:url(./hero.png)}</style>']:
            with self.subTest(asset=asset), tempfile.TemporaryDirectory() as folder:
                source = pathlib.Path(folder) / "candidate.html"
                output = pathlib.Path(folder) / "artifact.html"
                source.write_text(candidate().replace("</body>", asset + "</body>"), encoding="utf-8")
                result = assemble(source, output)
                self.assertEqual(result.returncode, 1)
                self.assertIn("external runtime asset", result.stderr)

    def test_missing_experimental_specimen_blocks_assembly(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(missing_experiment=True), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertIn("experimental specimen coverage mismatch", result.stderr)

    def test_missing_visible_coverage_blocks_assembly(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(include_coverage=False), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertIn("token specimen coverage mismatch", result.stderr)
            self.assertIn("stress-cell coverage mismatch", result.stderr)
            self.assertIn("permutation-cell coverage mismatch", result.stderr)

    def test_hidden_coverage_markers_do_not_count_as_visible(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            hidden = coverage_markup().replace("<figure ", "<figure hidden ")
            text = candidate(include_coverage=False).replace('<script id="proof-data"', hidden + '<script id="proof-data"')
            source.write_text(text, encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertIn("token specimen coverage mismatch", result.stderr)

    def test_recorded_pass_requires_exact_reviewed_surface_hash(self):
        from scripts.tests.test_proof_review import final_evidence

        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            source = root / "candidate.html"
            evidence = root / "evidence.json"
            output = root / "artifact.html"
            document = final_evidence()
            paths = [item["path"] for item in document["experimental_output"]["entries"]]
            document["artifact_review"]["experimental_review"] = {"status": "pass", "reviewed_paths": paths, "findings": "Every experimental token has a visible specimen and use boundary."}
            source.write_text(candidate(), encoding="utf-8")
            evidence.write_text(json.dumps(document), encoding="utf-8")
            first = assemble(source, output, evidence=evidence)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_report = json.loads(first.stdout)
            self.assertEqual(first_report["status"], "assembled-pending-visual-review")
            self.assertIn("reviewed_surface_sha256", first_report)
            document["artifact_review"]["final_readback"]["reviewed_surface_sha256"] = first_report["reviewed_surface_sha256"]
            evidence.write_text(json.dumps(document), encoding="utf-8")
            second = assemble(source, output, evidence=evidence)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(second.stdout)["status"], "assembled-recorded-visual-pass")

    def test_rendering_cannot_depend_on_embedded_proof_data(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            script = "<script>document.body.dataset.count=document.getElementById('proof-data').textContent.length</script>"
            source.write_text(candidate().replace("</body>", script + "</body>"), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertIn("rendering must not depend on embedded proof data", result.stderr)

    def test_global_uniqueness_claim_is_rejected_after_candidate_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(), encoding="utf-8")
            result = assemble(source, output, evidence=FIXTURES / "global-claim.evidence.json")
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertNotIn("candidate, tokens, and evidence must exist", result.stderr)
            self.assertIn("global uniqueness is not a provable claim", result.stderr)


if __name__ == "__main__":
    unittest.main()
