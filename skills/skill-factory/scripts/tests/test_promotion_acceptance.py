"""Reject stale evidence at the actual directory replacement boundary."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from acceptance_fixtures import setup, write_json
from skill_package import inventory, promote, tree_digest


def bindings(base, context, receipt, target, expected):
    context["consumer"] = {**expected, "target": str(target.resolve())}
    context_sha = write_json(base / "context.json", context)
    evidence_path = base / "evidence/row-2.json"
    evidence = json.loads(evidence_path.read_text())
    evidence["context_sha256"] = context_sha
    receipt["acceptance"]["context_sha256"] = context_sha
    receipt["acceptance"]["claims"]["ROW-2"]["sha256"] = write_json(evidence_path, evidence)
    receipt_sha = write_json(base / "receipt.json", receipt)
    return {"context": str(base / "context.json"), "context_sha256": context_sha,
            "receipt": str(base / "receipt.json"), "receipt_sha256": receipt_sha}


class TestPromotionAcceptance(unittest.TestCase):
    def test_no_evidence_cannot_replace_an_existing_package(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            stage, _, _, _, _ = setup(base)
            target = base / "destination" / stage.name
            shutil.copytree(stage, target)
            before = inventory(target)
            with self.assertRaisesRegex(ValueError, "acceptance"):
                promote(stage, target, before)
            self.assertEqual(inventory(target), before)
            self.assertTrue(stage.is_dir())

    def test_effect_uses_current_bound_evidence_and_exact_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            stage, context, receipt, _, _ = setup(base)
            target = base / "destination" / stage.name
            target.parent.mkdir()
            expected = {"route": "variant", "inputs": {"candidate": tree_digest(inventory(stage))}}
            trusted = bindings(base, context, receipt, target, expected)
            artifact = base / "evidence/row-2.json"
            original = artifact.read_bytes()
            artifact.write_bytes(original + b" ")
            with self.assertRaisesRegex(ValueError, "evidence artifact"):
                promote(stage, target, acceptance=(expected, trusted))
            self.assertFalse(target.exists())
            artifact.write_bytes(original)
            with self.assertRaisesRegex(ValueError, "consumer"):
                promote(stage, target.parent / "wrong", acceptance=(expected, trusted))
            before = inventory(stage)
            promote(stage, target, acceptance=(expected, trusted))
            self.assertEqual(inventory(target), before)
            self.assertFalse(stage.exists())


if __name__ == "__main__":
    unittest.main()
