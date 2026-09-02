"""Test links."""
import json
import pathlib
import re
import subprocess
import sys
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]

ROUTES = [
    "assets/workflow.json", "assets/execution-ownership.json",
    "assets/run-intake.schema.json", "assets/simplicity-contract.json",
    "assets/state-record.schema.json", "assets/review-record.schema.json",
    "assets/model-record.schema.json", "assets/lineage.schema.json",
    "assets/context-bundle.schema.json", "assets/context-routing.schema.json",
    "assets/context-routing.json", "assets/section-support.json",
    "assets/section-support.schema.json",
    "assets/speed-policy.json", "assets/speed-policy.schema.json",
    "assets/file-manifest.json", "assets/reading-contract.json",
    "assets/reading-exceptions.json", "assets/eval-case-template.json",
    "references/intake.md",
    "references/research.md", "references/build.md", "references/review.md",
    "references/failure.md", "references/decisions.md",
    "references/generation-contract.md", "references/context-routing.md",
    "references/section-support.md", "references/product-states.md",
    "mise.toml", ".github/workflows/ci.yml",
    "examples/run.md", "examples/help.md", "examples/failure-missing-proof.md",
    "examples/context-packets.md", "examples/product-states.md",
    "evals/contract.md", "evals/rubric.md", "evals/manifest.json",
    "evals/cases.json", "evals/evals.json", "evals/trigger-cases.json",
    "evals/trigger-queries.json", "evals/speed-budgets.json",
    "evals/source-mapping.json", "evals/source-lineage.json",
    "evals/context-cases.json", "evals/section-support-cases.json",
    "evals/files/valid-context-record.json",
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
            "[assets/workflow.json](assets/workflow.json) is the only step order.",
            "[assets/execution-ownership.json](assets/execution-ownership.json) is the only owner map.",
            "Do not skip, merge, replace, or reorder a required step.",
            "The model performs every eye, brain, and touch review.",
            "The model checks all bad design, bad output, and bad practice rules.",
            "Mise tasks check structure. They do not make design judgments.",
            "It does not pick states, rules, options, or results.",
            "Keep a bold option until evidence or a veto rejects it.",
            "Never infer motion from a still.",
            "Never accept clear words in a false state.",
            "all source tokens and atoms",
            "standard YAML header and portable CommonMark only",
            "Every block stays clean, readable, and agent-parsable.",
            "Each run task rejects work before its turn.",
        ]
        for phrase in phrases:
            self.assertIn(phrase, text)

    def test_body_sections_follow_the_outcome_led_order(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        headings = re.findall(r"^(#{1,3}) (.+)$", text, re.MULTILINE)
        self.assertEqual(headings, [
            ("#", "Design like I am five"),
            ("##", "One contract"),
            ("##", "Ordered workflow"),
            ("###", "Commands"),
            ("###", "Prepare the run"),
            ("###", "Complete all actions in order"),
            ("###", "Build each model packet"),
            ("##", "Judge the design"),
            ("###", "Veto and failure rules"),
            ("###", "Discover product states"),
            ("###", "Run every review invariant"),
            ("###", "Build from proved parts"),
            ("##", "Prove and finish"),
            ("###", "Record model work"),
            ("###", "Reading and package owners"),
            ("###", "Eval owner map"),
            ("###", "Return and done"),
        ])

    def test_body_stays_under_the_repo_line_limit(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        body = text.split("\n---\n", 1)[1]
        self.assertLess(len(body.splitlines()), 200)

    def test_every_body_link_exists(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        missing = sorted({path for path in links
                          if not (SKILL / path).is_file()})
        self.assertEqual(missing, [])

    def test_body_gives_the_complete_run_command_loop(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        commands = [
            "mise run run-start --intake INPUT --run-dir RUN",
            "mise run run-packet --run-dir RUN --action ACTION",
            "mise run run-record --run-dir RUN --result RESULT",
            "mise run run-select-rules --run-dir RUN",
            "mise run run-check --run-dir RUN",
            "mise run lineage-file MANIFEST --run-dir RUN",
        ]
        for command in commands:
            self.assertIn(command, text)
        self.assertLess(
            text.index("mise run run-record --run-dir RUN --result RESULT"),
            text.index("### Discover product states"))

    def test_body_minimizes_wall_time_without_weakening_the_contract(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8").casefold()
        phrases = [
            "minimize_elapsed_time",
            "verified_owning-artifact_change",
            "preserve_exploratory_and_experimental_breadth",
            "same-executor_vision",
            "batch independent reads",
            "keep one writer",
            "invalidates affected captures",
            "never caches or skips",
        ]
        for phrase in phrases:
            self.assertIn(phrase.replace("_", " "), text)

    def test_body_uses_standard_checklists(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for label in ["**Run checklist:**", "**Completion checklist:**"]:
            self.assertIn(f"{label}\n\n", text)
        self.assertGreaterEqual(
            len(re.findall(r"(?m)^\s*[-*+]\s+\[ \]\s", text)), 6)

    def test_validator_accepts_the_mise_only_body_interface(self):
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "validate_skill.py"),
             str(SKILL)], capture_output=True, text=True, timeout=120)
        self.assertNotIn("body never references scripts/", result.stdout)
        self.assertNotIn("body never references scripts/tests/", result.stdout)


class TestComputerUseAuditContract(unittest.TestCase):
    def test_goal_specific_sources_stay_outside_the_portable_skill(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        roles = [
            "current product board or FigJam source",
            "originating audiovisual source",
            "originating transcript",
        ]
        for role in roles:
            self.assertNotIn(role, text)
        self.assertIn("one source record per item", text)
        self.assertIn("Outside that audit", text)

    def test_same_vision_agent_operates_portable_design_app_control(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        required = [
            ("paramount", "visual-proof", "rule"),
            ("every", "applicable", "available", "vision", "capability"),
            ("before", "and", "after"),
            ("platform-neutral", "local", "application-control", "capability"),
            ("same", "invoking", "strong", "vision-capable", "executor"),
            ("directly", "inspect", "the", "active", "design", "application"),
            ("including", "Figma"), ("the", "item", "is", "`BLOCKED`"),
        ]
        for words in required:
            self.assertIn(" ".join(words), text)


class TestFocusIntentContract(unittest.TestCase):
    def test_every_design_layer_has_one_canonical_focus_intent(self):
        text = (SKILL / "references" / "build.md").read_text(encoding="utf-8")
        levels = [
            "token", "atom", "molecule", "organism", "UI composition template",
            "screen", "flow", "transition",
        ]
        fields = [
            "user_task", "focus_target", "focus_location", "focus_timing",
            "focus_mechanism", "focus_reason", "attention_sequence",
            "competing_signals", "defocus_and_recovery", "failure_evidence",
        ]
        self.assertIn("focus-intent record", text)
        for level in levels:
            self.assertIn(level, text)
        for field in fields:
            self.assertIn(f"`{field}`", text)
        self.assertIn("prominence alone is not intent", text)


class TestOptionalImprovementContract(unittest.TestCase):
    def test_mise_gates_one_nonregressing_skill_improvement(self):
        policy = json.loads(
            (SKILL / "assets" / "speed-policy.json").read_text(encoding="utf-8")
        )["optional_skill_improvement"]
        self.assertEqual(policy["cli_owner"], "mise")
        self.assertEqual(policy["acceptance"], "pareto_non_regression")
        self.assertEqual(policy["failure"], "restore_last_accepted_version")
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("**Optional final step:**", text)
        self.assertIn("one named part", text)
        self.assertIn("restore the last passed version", text)
        self.assertIn("mise run complete", text)

if __name__ == "__main__":
    unittest.main()
