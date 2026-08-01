from pathlib import Path

_SKILLS = (
    (
        "always-current-datetime",
        "Use when replying. Refresh current date and time.",
    ),
    (
        "logic-audit",
        "Use when finding contradictions or reasoning gaps.",
    ),
    (
        "outcome-bounded-work",
        "Use when instructions mix outcomes with recipes.",
    ),
    (
        "prime-vector",
        "Use when a high-stakes problem needs a strategy.",
    ),
    (
        "reify",
        "Use when a vague idea, stray thought, remembered fragment, or uncertain"
        " direction needs to become a concrete outcome, tested design, decision"
        " record, artifact, or executable handoff.",
    ),
    (
        "skill-factory",
        "Use when a workflow, recipe, or capability needs to be packaged as an"
        " agent skill, or when an existing skill needs scaffolding, validation,"
        " linting, or evals. Covers requests to build, create, generate,"
        " scaffold, check, or evaluate a skill: a folder holding SKILL.md,"
        " scripts, tests, a task graph, CI, and eval cases. Applies even when"
        " the request says playbook, runbook, or reusable workflow instead of"
        " skill.",
    ),
    (
        "starting-point",
        "Use when an outcome is stated, inferred, or hidden.",
    ),
    (
        "visual-design-system-extractor",
        "Use when reference images, screenshots, moodboards, style frames,"
        " brand boards, cinematic stills, or product interface shots must"
        " become a production design system, design tokens, art direction,"
        " motion rules, or a YAML style specification. Covers reverse"
        " engineering visual references into a deterministic YAML contract"
        " with graded confidence, evidence boundaries, and typefaces drawn"
        " from the live Google Fonts catalog and ranked as rarely used. Not"
        " for generating images or for ordinary frontend work where no"
        " reference has to be decoded first.",
    ),
    (
        "would-agents-actually",
        "Use when a claim depends on an agent taking a real action.",
    ),
    (
        "would-humans-actually",
        "Use when a claim depends on people taking a real action.",
    ),
)


def register(ctx):
    root = Path(__file__).resolve().parent
    for name, description in _SKILLS:
        path = root / "skills" / name / "SKILL.md"
        ctx.register_skill(name, path, description=description)
