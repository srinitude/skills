"""Reject false acceptance at the public invocation consumer; preserve its files."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from acceptance_fixtures import invoke, setup, write_json
from test_acceptance_bindings import digest


class TestEvidenceAcceptance(unittest.TestCase):
    def test_evidence_contents_and_all_bindings_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            original = (base / "evidence/row-2.json").read_bytes()
            edits = [lambda d: d.update(state="failed"), lambda d: d.update(requirement="wrong"),
                     lambda d: d.update(context_sha256="0" * 64), lambda d: d.update(components=[]),
                     lambda d: d["result"].update(lines=3),
                     lambda d: d["execution"].update(exit_code=1),
                     lambda d: d.update(producer={"id": "fabricated-human", "kind": "human"})]
            for edit in edits:
                with self.subTest(edit=edit):
                    evidence = json.loads(original)
                    edit(evidence)
                    data = copy.deepcopy(receipt)
                    data["acceptance"]["claims"]["ROW-2"]["sha256"] = write_json(base / "evidence/row-2.json", evidence)
                    current = write_json(base / "receipt.json", data)
                    rejected = invoke(base, context_sha, current)
                    self.assertNotEqual(rejected.returncode, 0, rejected.stdout)
                    self.assertNotIn("Traceback", rejected.stderr)
            (base / "evidence/row-2.json").write_bytes(original)
            write_json(base / "receipt.json", receipt)
            self.assertEqual(invoke(base, context_sha, receipt_sha).returncode, 0)

    def test_missing_coverage_claims_and_changed_context_cannot_shrink_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            for key in ["claims", "subject"]:
                data = copy.deepcopy(receipt)
                data["acceptance"][key] = {}
                altered = write_json(base / "receipt.json", data)
                self.assertNotEqual(invoke(base, context_sha, altered).returncode, 0)
            write_json(base / "receipt.json", receipt)
            context["requirements"] = {}
            write_json(base / "context.json", context)
            self.assertNotEqual(invoke(base, context_sha, receipt_sha).returncode, 0)

    def test_altered_source_subject_artifact_and_receipt_are_rejected_then_restored(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            for relative in ["source.md", "coverage.json", "release-notes/notes.txt",
                             "evidence/row-2.json", "receipt.json"]:
                path = base / relative
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                before = {p: p.read_bytes() for p in base.rglob("*") if p.is_file()}
                result = invoke(base, context_sha, receipt_sha)
                self.assertNotEqual(result.returncode, 0, (relative, result.stdout))
                self.assertEqual(before, {p: p.read_bytes() for p in base.rglob("*") if p.is_file()})
                path.write_bytes(original)
            accepted = invoke(base, context_sha, receipt_sha)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            self.assertIn("evidence acceptance", accepted.stdout)

    def test_receipt_cannot_select_its_own_trust_or_claim_human_authority(self):
        from cli import run
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            result = run("check_invocation_receipt.py", root, base / "receipt.json")
            self.assertNotEqual(result.returncode, 0)
            receipt["acceptance"]["trusted"] = True
            write_json(base / "receipt.json", receipt)
            self.assertNotEqual(invoke(base, context_sha, receipt_sha).returncode, 0)
