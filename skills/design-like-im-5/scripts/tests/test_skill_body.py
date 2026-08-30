"""The skill body must route every governed outcome to its owner."""
import pathlib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]

ROUTES = [
    "assets/workflow.json", "assets/execution-ownership.json",
    "assets/run-intake.schema.json", "assets/simplicity-contract.json",
    "assets/state-record.schema.json", "assets/review-record.schema.json",
    "assets/model-record.schema.json", "assets/lineage.schema.json",
    "assets/context-bundle.schema.json", "assets/context-routing.schema.json",
    "assets/context-routing.json",
    "assets/file-manifest.json", "assets/reading-contract.json",
    "assets/reading-exceptions.json", "assets/eval-case-template.json",
    "references/intake.md",
    "references/research.md", "references/build.md", "references/review.md",
    "references/failure.md", "references/decisions.md",
    "references/generation-contract.md", "scripts/run_pipeline.py",
    "references/context-routing.md", "scripts/check_context_routing.py",
    "scripts/run_scaffold.py", "scripts/review_checklist.py",
    "scripts/human_capability_sweep.py", "scripts/check_lineage.py",
    "scripts/audit_directories.py", "scripts/audit_ownership.py",
    "scripts/build_examples.py", "scripts/build_file_manifest.py",
    "scripts/build_lineage.py",
    "scripts/check_code_rules.py", "scripts/check_evals.py",
    "scripts/check_placeholders.py", "scripts/check_reading.py",
    "scripts/check_source_lineage.py", "scripts/lint_writing.py",
    "scripts/skill_info.py", "scripts/validate_skill.py",
    "scripts/tests/", "mise.toml", ".github/workflows/ci.yml",
    "examples/run.md", "examples/help.md", "examples/failure-missing-proof.md",
    "examples/context-packets.md",
    "evals/contract.md", "evals/rubric.md", "evals/manifest.json",
    "evals/cases.json", "evals/evals.json", "evals/trigger-cases.json",
    "evals/trigger-queries.json", "evals/speed-budgets.json",
    "evals/source-mapping.json", "evals/source-lineage.json",
    "evals/context-cases.json", "evals/files/valid-context-record.json",
    "evals/files/missing-context-record.json",
    "evals/files/valid-intake.json", "evals/files/missing-proof.json",
    "evals/files/valid-lineage.json", "evals/files/skipped-lineage.json",
]


class TestSkillBodyRoutes(unittest.TestCase):
    def test_body_names_every_governing_route(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for route in ROUTES:
            self.assertIn(route, text, route)

    def test_body_pins_order_owner_and_model_boundary(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        phrases = [
            "assets/workflow.json is the only step order.",
            "assets/execution-ownership.json is the only owner map.",
            "Do not skip, merge, replace, or reorder a required step.",
            "The model performs every eye, brain, and touch review.",
            "The model checks every bad design, bad output, and bad practice invariant.",
            "Scripts check structure. They do not make design judgments.",
        ]
        for phrase in phrases:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
