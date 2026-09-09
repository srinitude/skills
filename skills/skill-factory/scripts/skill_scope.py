"""One owner for intended availability; no installation or path inference."""
import json
from pathlib import Path

from validate_skill import check_fields, parse_header, split_frontmatter
from source_coverage import load_json

SCOPES = ("user", "project")
QUESTION = "Should this skill be available across your projects (user) or for one specific project (project)?"


def read_fields(root):
    root = Path(root)
    if root.is_symlink():
        raise ValueError("skill root must not be a symlink")
    root = root.resolve()
    path = root / "SKILL.md"
    if path.is_symlink():
        raise ValueError("SKILL.md must not be a symlink")
    header, _, error = split_frontmatter(path.read_text(encoding="utf-8"))
    if error:
        raise ValueError(error)
    fields, error = parse_header(header)
    problems = [error] if error else []
    if not error:
        check_fields(fields, root.name, problems)
    if problems:
        raise ValueError("; ".join(problems))
    return fields


def resolve(existing=None, choice=None, evidence=None):
    if choice is not None and choice not in SCOPES:
        raise ValueError('scope must be the string "user" or "project"')
    if existing is not None and existing not in SCOPES:
        raise ValueError("existing metadata.scope is invalid")
    if choice or existing:
        return {"scope": choice or existing,
                "basis": "explicit choice" if choice else "preserved existing scope"}
    values = set()
    for item in evidence or []:
        if (not isinstance(item, dict) or item.get("scope") not in SCOPES
                or not all(isinstance(item.get(key), str) and item[key].strip()
                           for key in ["source", "intended_use"])):
            raise ValueError("scope evidence needs scope, authoritative source, and intended_use")
        if item["source"] in {"cwd", "location", "registry path"}:
            raise ValueError("location alone is not intended availability")
        values.add(item["scope"])
    if len(values) != 1:
        raise ValueError(QUESTION)
    return {"scope": values.pop(), "basis": "authoritative intended-use evidence"}


def scoped_text(text, scope):
    """Change only the header's scope, retaining other metadata and body."""
    import yaml
    header, body, error = split_frontmatter(text)
    if error:
        raise ValueError(error)
    fields, error = parse_header(header)
    if error:
        raise ValueError(error)
    resolve(choice=scope)
    if "metadata" not in fields:
        return "---" + header + f'\nmetadata:\n  scope: "{scope}"\n---\n' + body
    if not isinstance(fields["metadata"], dict):
        raise ValueError("metadata must be a mapping")
    node = yaml.compose(header)
    metadata = next(value for key, value in node.value if key.value == "metadata")
    existing = next((value for key, value in metadata.value if key.value == "scope"), None)
    if existing:
        start, end = existing.start_mark.index, existing.end_mark.index
        header = header[:start] + json.dumps(scope) + header[end:]
    elif metadata.flow_style:
        index = metadata.end_mark.index - 1
        prefix = ", " if metadata.value else ""
        header = header[:index] + prefix + f'scope: "{scope}"' + header[index:]
    else:
        index = metadata.end_mark.index
        header = header[:index].rstrip() + f'\n  scope: "{scope}"\n' + header[index:]
    return "---" + header.rstrip() + "\n---\n" + body


def label(scope):
    return {"user": "user-level", "project": "project-level"}.get(scope)
