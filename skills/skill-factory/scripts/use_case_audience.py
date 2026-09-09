"""Canonical primary-result audience, separate from execution and availability."""
from copy import deepcopy

from lint_writing import collect_blocks, skip_frontmatter
from source_coverage import load_json, require

AUDIENCES = ("human", "agent")
PURPOSE = {
    "human": "The main result is for a person to use or experience. Apply human-outcome criteria and identify required real human observation or choice.",
    "agent": "The main result is for an agent or model to consume. Verify its interface, actual downstream use, semantic correctness, and failure handling; retain requirements for affected people.",
}
KEY = ("Executor and workflow owner: use the named public operation and its input contract. Readers, orchestrators, executors, reviewers, and approvers may differ.\n\n"
       "Mechanical evidence: a named predicate checked captured inputs; it cannot establish an untested subjective response. Model assessment: a model inspected the actual result; identify its modalities, criteria, and limits.\n\n"
       "Human evidence: a person supplied a preference, observation, review, or decision. Identify the role, context, and artifact. Permission, preference, and task performance are distinct.\n\n"
       "Gate or open choice: required evidence blocks its dependent action or claim. Preserve optional feedback and creative choices. Audience labels grant no permissions or instruction authority.")


def checked(record):
    require(isinstance(record, dict), "audience must be an object")
    primary = record.get("primary")
    require(isinstance(primary, str) and primary in AUDIENCES, "audience.primary must be human or agent")
    return deepcopy(record)


def resolve(root, choice=None, profile=None, required=True):
    path = root / "assets/use-case-contract.json"
    data = load_json(path) if path.is_file() else {}
    require(isinstance(data, dict), "use-case contract must be an object")
    existing = checked(data["audience"]) if "audience" in data else None
    proposed = checked(profile["audience"]) if profile and "audience" in profile else None
    if choice is not None:
        result = existing or proposed or {}
        result["primary"] = choice
        return checked(result)
    if existing or proposed:
        return existing or proposed
    if not required:
        return None
    raise ValueError("Resolve whether the primary result serves a human or an agent before writing")


def reading_key(primary):
    checked({"primary": primary})
    return f"Primary audience: {primary}.\n\n{PURPOSE[primary]}\n\n{KEY}"


def labels(lines):
    return [(block[0][0], block[0][1]) for block in collect_blocks(lines)
            if len(block) == 1 and block[0][1].startswith("Primary audience:")]


def body_with_key(body, record):
    primary = checked(record)["primary"]
    lines = body.splitlines()
    prior = labels(lines)
    require(len(prior) <= 1, "conflicting primary audience labels require review")
    if prior:
        index = prior[0][0] - 1
        size = 1
        for value in AUDIENCES:
            block = reading_key(value).splitlines()
            if lines[index:index + len(block)] == block:
                size = len(block)
        del lines[index:index + size]
    start = skip_frontmatter(lines)
    heading = next((i for i in range(start, len(lines)) if lines[i].lower().startswith("## outcome")), None)
    if heading is None:
        heading = next((i for i in range(start, len(lines)) if lines[i].startswith("# ")), start - 1)
    following = lines[heading + 1:]
    while following and not following[0].strip():
        following.pop(0)
    return "\n".join([*lines[:heading + 1], "", *reading_key(primary).splitlines(), "", *following]).rstrip() + "\n"


def problems(data, root, inspect_legacy=False):
    if "audience" not in data:
        return [] if inspect_legacy else ["audience.primary is required for newly created or updated output"]
    try:
        record = checked(data["audience"])
        lines = (root / "SKILL.md").read_text("utf-8").splitlines()
        found = labels(lines)
        require(len(found) == 1 and found[0][1] == f"Primary audience: {record['primary']}.",
                "body audience label must match the canonical audience.primary")
        steps = [i + 1 for i, line in enumerate(lines) if line.startswith(("## Ordered workflow", "## Steps", "## Factory execution contract"))]
        require(not steps or found[0][0] < min(steps), "audience key must precede execution steps")
        return []
    except (ValueError, OSError) as error:
        return [str(error)]
