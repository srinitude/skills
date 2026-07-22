from pathlib import Path

_SKILLS = (
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
)


def register(ctx):
    root = Path(__file__).resolve().parent
    for name, description in _SKILLS:
        path = root / "skills" / name / "SKILL.md"
        ctx.register_skill(name, path, description=description)
