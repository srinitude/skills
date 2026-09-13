"""Scaffold shape and copied contracts; seeded outputs must fail acceptance."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

from cli import SCRIPTS, run
from scaffold_test_support import reviewed_scaffold

sys.path.insert(0, str(SCRIPTS))
from skill_package import owned_paths
from standardization_runtime import LEDGER_EXAMPLES

DESCRIPTION = "Use when a demo skill is needed for scaffold tests."

def scaffold(dest, name="demo-skill", description=DESCRIPTION, *extra):
    return reviewed_scaffold(dest, name, description, extra if "--scope" in extra else (*extra, "--scope", "user"))

class TestScaffoldCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("scaffold_skill.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_invalid_name_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = scaffold(tmp, name="Bad_Name")
        self.assertEqual(result.returncode, 2)
        self.assertIn("name", result.stdout.lower())

    def test_description_must_state_when_to_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = scaffold(tmp, description="Formats reports.")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use when", result.stdout)

    def test_existing_target_without_force_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "demo-skill").mkdir()
            result = scaffold(tmp)
        self.assertEqual(result.returncode, 1)

def _TestScaffoldOutput_setUpClass(cls):
    cls.tmp = tempfile.TemporaryDirectory()
    result = scaffold(cls.tmp.name)
    assert result.returncode == 0, result.stdout + result.stderr
    cls.skill = Path(cls.tmp.name) / "demo-skill"

def _TestScaffoldOutput_tearDownClass(cls):
    cls.tmp.cleanup()

def _TestScaffoldOutput_test_layout_is_complete(self):
    for rel in ["SKILL.md", "mise.toml", ".github/workflows/ci.yml", "references/generation-contract.md", "assets",
                "references/resource-and-experiment-design.md", "references/improvement-dimensions.md", "references/writing-rules.md",
                "assets/improvement-contract.json", "assets/use-case-contract.json", "assets/decision-records.json", "assets/invocation-receipt-template.json",
                "assets/mise-primitives-catalog.json", "assets/mise-primitives.json", "assets/primitive-lifecycle.json",
                "scripts/skill_info.py", "scripts/tests/cli.py", "scripts/tests/test_scripts.py", "scripts/tests/test_ci_contract.py",
                "scripts/check_improvement_contract.py", "scripts/check_use_case_contract.py", "scripts/check_domain_research.py",
                "scripts/check_task_graph.py", "scripts/check_invocation_receipt.py", "scripts/domain_text.py", "scripts/check_mise_primitives.py",
                "scripts/check_primitive_lifecycle.py", "scripts/sync_mise_primitives.py", "scripts/check_decision_records.py", "examples/example-first-run.md",
                "scripts/check_placeholders.py", "evals/evals.json", "evals/trigger-queries.json"]:
        self.assertTrue((self.skill / rel).exists(), f"missing {rel}")

def _TestScaffoldOutput_test_body_points_at_examples_with_a_load_condition(self):
    body = (self.skill / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("examples/", body)
    self.assertIn("examples/example-first-run.md", body)

def _TestScaffoldOutput_test_body_routes_every_deterministic_command_through_mise(self):
    body = (self.skill / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("Mise invokes Mastra once at an explicit boundary", body)
    self.assertIn("Mastra directly invokes existing scripts or authorized runners", body)
    self.assertIn("**Agentic request contract.**", body)
    self.assertNotIn("python3 scripts/", body)
    self.assertIn("mise run info", body)
    self.assertIn("mise run ci", body)

def _TestScaffoldOutput_test_body_keeps_the_factory_language_contract(self):
    body = (self.skill / "SKILL.md").read_text(encoding="utf-8")
    rules = (self.skill / 'references' / 'writing-rules.md').read_text(encoding='utf-8')
    self.assertIn("## Motivation", body)
    self.assertIn("references/writing-rules.md", body)
    self.assertIn("## Plain language", rules)

def _TestScaffoldOutput_test_body_ends_with_optional_nonregressing_improvement_step(self):
    body = (self.skill / "SKILL.md").read_text(encoding="utf-8")
    heading = "**Efficiency and optional improvement.**"
    self.assertIn(heading, body)
    self.assertGreater(body.index(heading), body.index("## Evals"))
    self.assertIn("Only after required work is accepted", body)
    for phrase in [ "one named dimension", "fresh accepted baseline", "evaluator, fixtures, environment", "restore the accepted bytes and verify them",
        "mise run improvement-policy", "protected dimensions", ]:
        self.assertIn(phrase, body)

def _TestScaffoldOutput_test_generated_improvement_policy_passes(self):
    result = run("check_improvement_contract.py", self.skill)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestScaffoldOutput_test_generated_use_case_policy_rejects_generic_seed(self):
    result = run("check_use_case_contract.py", self.skill)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn("scaffold placeholder", result.stdout.lower())

def _TestScaffoldOutput_test_generated_mise_and_lifecycle_policies_reject_seeds(self):
    primitive = run("check_mise_primitives.py", self.skill)
    lifecycle = run("check_primitive_lifecycle.py", self.skill)
    self.assertEqual((primitive.returncode, lifecycle.returncode), (1, 1))
    self.assertIn("scaffold", primitive.stdout.lower())
    self.assertIn("lifecycle", lifecycle.stdout.lower())

def _TestScaffoldOutput_test_untouched_scaffold_fails_the_placeholder_gate(self):
    result = run("check_placeholders.py", self.skill)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("SKILL.md", result.stdout)
    self.assertIn("examples/example-first-run.md", result.stdout)
    self.assertIn("evals.json", result.stdout)

def _TestScaffoldOutput_test_seed_evals_do_not_assert_scaffolder_behavior(self):
    text = (self.skill / 'evals' / 'evals.json').read_text(encoding='utf-8').lower()
    for leftover in ["skill_info.py", "help, info, and check"]:
        self.assertNotIn(leftover, text)

def _TestScaffoldOutput_test_generated_skill_passes_validation(self):
    result = run("validate_skill.py", self.skill)
    self.assertEqual(result.returncode, 0, result.stdout)

def _TestScaffoldOutput_test_generated_docs_pass_the_writing_lint(self):
    result = run("lint_writing.py", self.skill)
    self.assertEqual(result.returncode, 0, result.stdout)

def _TestScaffoldOutput_test_generated_code_passes_code_rules(self):
    result = run("check_code_rules.py", self.skill)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestScaffoldOutput_test_generated_evals_pass_schema_checks(self):
    result = run("check_evals.py", self.skill)
    self.assertEqual(result.returncode, 0, result.stdout)

def _TestScaffoldOutput_test_generated_tests_pass(self):
    cmd = ["mise", "run", "--force", "--task-cache", "off", "--timeout", "660s", "test"]
    env = dict(os.environ, MISE_TRUSTED_CONFIG_PATHS=str(self.skill))
    proc = subprocess.run(cmd, cwd=self.skill, env=env, capture_output=True, text=True, timeout=720)
    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

def _TestScaffoldOutput_assert_platform_neutral(self, relative, text):
    # Exact reviewed citations are provenance, not runner selection.
    # Other text and every other path keep the existing rejection rule.
    if relative == "references/improvement-dimensions.md":
        for citation in ['[infrastructure experiments](https://www.anthropic.com/engineering/infrastructure-noise)', '7: Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), 2026-01-09.', '8: Gian Segato, [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise), Anthropic, 2026-02-05.']:
            text = text.replace(citation, "[reviewed research citation]")
    halves = [("her", "mes"), ("cla", "ude"), ("co", "dex"), ("openc", "ode"), ("copi", "lot"), ("cur", "sor"), ("gem", "ini"), ("g", "pt"),
              ("anthro", "pic"), ("open", "ai"), ("perple", "xity")]
    for head, tail in halves:
        self.assertFalse(head + tail in text.lower(), f'{relative} contains a named platform/model: {head + tail}')

def _TestScaffoldOutput_test_research_citation_exception_preserves_instruction_rejection(self):
    relative = "references/improvement-dimensions.md"
    text = (self.skill / relative).read_text()
    self.assert_platform_neutral(relative, text)
    for changed in [text + '\nUse the ' + 'anthro' + 'pic runner.', text.replace('/infrastructure-noise', '/unreviewed-source')]:
        with self.assertRaises(AssertionError):
            self.assert_platform_neutral(relative, changed)
    with self.assertRaises(AssertionError):
        self.assert_platform_neutral("SKILL.md", text)

def _TestScaffoldOutput_test_generated_instructions_do_not_choose_a_platform_or_model(self):
    # Complete observed records retain native schema facts, not runner choices.
    evidence = {name for name in LEDGER_EXAMPLES if name.endswith('.json')}
    for name in evidence:
        self.assertEqual((self.skill / name).read_bytes(), (SCRIPTS.parent / name).read_bytes())
    for path in owned_paths(self.skill):
        relative = path.relative_to(self.skill.resolve()).as_posix()
        if relative in evidence: continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = (json.dumps(json.loads(text, object_hook=lambda item: {key: value for key, value in item.items() if key != 'integrity'}))
                if path.name == "package-lock.json" else text)
        self.assert_platform_neutral(relative, text)

class TestScaffoldOutput(unittest.TestCase):
    setUpClass = classmethod(_TestScaffoldOutput_setUpClass)
    tearDownClass = classmethod(_TestScaffoldOutput_tearDownClass)
    test_layout_is_complete = _TestScaffoldOutput_test_layout_is_complete
    test_body_points_at_examples_with_a_load_condition = _TestScaffoldOutput_test_body_points_at_examples_with_a_load_condition
    test_body_routes_every_deterministic_command_through_mise = _TestScaffoldOutput_test_body_routes_every_deterministic_command_through_mise
    test_body_keeps_the_factory_language_contract = _TestScaffoldOutput_test_body_keeps_the_factory_language_contract
    test_body_ends_with_optional_nonregressing_improvement_step = _TestScaffoldOutput_test_body_ends_with_optional_nonregressing_improvement_step
    test_generated_improvement_policy_passes = _TestScaffoldOutput_test_generated_improvement_policy_passes
    test_generated_use_case_policy_rejects_generic_seed = _TestScaffoldOutput_test_generated_use_case_policy_rejects_generic_seed
    test_generated_mise_and_lifecycle_policies_reject_seeds = _TestScaffoldOutput_test_generated_mise_and_lifecycle_policies_reject_seeds
    test_untouched_scaffold_fails_the_placeholder_gate = _TestScaffoldOutput_test_untouched_scaffold_fails_the_placeholder_gate
    test_seed_evals_do_not_assert_scaffolder_behavior = _TestScaffoldOutput_test_seed_evals_do_not_assert_scaffolder_behavior
    test_generated_skill_passes_validation = _TestScaffoldOutput_test_generated_skill_passes_validation
    test_generated_docs_pass_the_writing_lint = _TestScaffoldOutput_test_generated_docs_pass_the_writing_lint
    test_generated_code_passes_code_rules = _TestScaffoldOutput_test_generated_code_passes_code_rules
    test_generated_evals_pass_schema_checks = _TestScaffoldOutput_test_generated_evals_pass_schema_checks
    test_generated_tests_pass = _TestScaffoldOutput_test_generated_tests_pass
    assert_platform_neutral = _TestScaffoldOutput_assert_platform_neutral
    test_research_citation_exception_preserves_instruction_rejection = _TestScaffoldOutput_test_research_citation_exception_preserves_instruction_rejection
    test_generated_instructions_do_not_choose_a_platform_or_model = _TestScaffoldOutput_test_generated_instructions_do_not_choose_a_platform_or_model

if __name__ == "__main__": unittest.main()
