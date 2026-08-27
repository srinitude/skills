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
OBLIGATIONS = (
    "conformance", "inputs", "intent", "possibilities", "narrowing",
    "coverage", "token-specimens", "experiments", "permutations", "metrics",
    "perceptual-motor-invariants", "taste", "originality",
    "corpus-uniqueness", "non-ai-slop", "visual-review", "failures",
    "boundary", "embedded-data",
)


def candidate(omit=None, external=False, missing_experiment=False):
    sections = "".join(f'<section data-proof-obligation="{name}"><h2>{name}</h2></section>' for name in OBLIGATIONS if name != omit)
    specimens = '<figure data-experimental-token="experimental.tokens.route-signal-softening">route</figure>'
    if not missing_experiment:
        specimens += '<figure data-experimental-token="experimental.tokens.risk-pulse-duration">risk</figure>'
    asset = '<script src="https://example.com/app.js"></script>' if external else ""
    return f'<!doctype html><html lang="en" data-dtcg-proof="2.0" data-artifact-authorship="vision-authored" data-run-id="__DTCG_RUN_ID__" data-verdict="__DTCG_VERDICT_STATE__"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Structural fixture</title><style>body{{font:16px sans-serif}}</style></head><body><p>__DTCG_PROOF_VERDICT__</p>{sections}{specimens}<script id="proof-data" type="application/json">__DTCG_PROOF_DATA__</script>{asset}</body></html>'


def assemble(source, output, run_id="contract-run"):
    command = [sys.executable, str(ASSEMBLER), "--candidate", str(source), "--tokens", str(FIXTURES / "sample.tokens.json"), "--evidence", str(FIXTURES / "sample.evidence.json"), "--output", str(output), "--run-id", run_id]
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

    def test_missing_experimental_specimen_blocks_assembly(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "candidate.html"
            output = pathlib.Path(folder) / "artifact.html"
            source.write_text(candidate(missing_experiment=True), encoding="utf-8")
            result = assemble(source, output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())
            self.assertIn("experimental specimen coverage mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
