from pathlib import Path

_SKILLS = (
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
