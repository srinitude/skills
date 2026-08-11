from pathlib import Path

_SKILLS = (
    (
        "always-current-datetime",
        "Use when replying. Refresh current date and time.",
    ),
    (
        "dedupe",
        "Use when deduplicating bounded collections.",
    ),
    (
        "goal-prompt",
        "Use when packaging source input for a standing goal.",
    ),
    (
        "logic-audit",
        "Use when finding contradictions or reasoning gaps.",
    ),
    (
        "meaning-preserving-rewrite",
        "Use when rewriting rules without meaning loss.",
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
        "simplify-skill",
        "Use when simplifying a skill without losing behavior.",
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
        "Use when a request prescribes a method, tool, metric, or artifact that"
        " may not reach the result the user described, or when doing the request"
        " as written would leave that result unproved: \"A/B test the signup"
        " button color\" for a conversion problem, \"add a cache\" for a slow"
        " page, \"the focused tests passed, announce the release\". Also use when"
        " a stated constraint contradicts itself, when an unknown fact would have"
        " to be invented to finish, or when an external or irreversible step"
        " needs an authorization decision. Keywords: right approach, wrong"
        " metric, root cause, outcome versus output, what counts as done, proof,"
        " is this worth doing. Not for a literal edit, format, translation, or"
        " lookup whose method is the deliverable. Not a replacement for the"
        " design, debugging, research, or writing method that performs the work."
        " Use the reify skill instead when the request is still too vague to have"
        " any method or outcome yet.",
    ),
    (
        "visual-design-system-extractor",
        "Use when reference images, screenshots, moodboards, style frames,"
        " brand boards, cinematic stills, product interface shots, or a live"
        " site URL must become a production design system, design tokens, art"
        " direction, motion rules, or a YAML style specification. Covers"
        " reverse engineering visual references into a deterministic YAML"
        " contract with graded confidence, evidence boundaries, and typefaces"
        " drawn from the live Google Fonts catalog and ranked as rarely used."
        " Not for generating images or for ordinary frontend work where no"
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
