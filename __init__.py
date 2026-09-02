import json
from pathlib import Path


def _frontmatter_value(source, key):
    prefix = f"{key}:"
    line = next((item for item in source.splitlines() if item.startswith(prefix)), None)
    if line is None:
        raise ValueError(f"missing {key} in SKILL.md")
    value = line[len(prefix) :].strip()
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    return value


def register(ctx):
    root = Path(__file__).resolve().parent
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        source = path.read_text(encoding="utf-8")
        name = _frontmatter_value(source, "name")
        description = _frontmatter_value(source, "description")
        if name != path.parent.name:
            raise ValueError(f"skill directory does not match name: {path}")
        ctx.register_skill(name, path, description=description)
