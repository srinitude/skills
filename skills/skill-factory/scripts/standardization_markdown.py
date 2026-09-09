"""Rewrite mechanical skill references through owning Mise tasks."""
import re

SCRIPT_RE = re.compile(
    r"(?:(?:uv run|uvx)(?:\s+(?!python3?\b)[^`\n\s]+)*\s+)?"
    r"(?:PYTHONDONTWRITEBYTECODE=1\s+)?python3?\s+"
    r'"?(?:(?:\$[A-Z_][A-Z0-9_]*/)|(?:[\w.-]+/)*)?'
    r"scripts/([\w./-]+\.py)\"?([^`\n]*)")
TEST_RE = re.compile(
    r"(?:(?:PYTHONDONTWRITEBYTECODE=1\s+)?(?:uv run|uvx)[^`\n]*?\s+)?"
    r"(?:PYTHONDONTWRITEBYTECODE=1\s+)?python3?\s+-m\s+unittest\s+discover"
    r"[^`\n]*?-s\s+scripts/tests\b[^`\n]*")
SCRIPT_LINK_RE = re.compile(r"\[[^]]+\]\((?:\.\.?/)?scripts/([\w./-]+\.py)\)")
FENCED_SCRIPT_COMMAND_RE = re.compile(r"`scripts/([\w./-]+\.py)([^`\n]*)`")
FENCED_SCRIPT_PATH_RE = re.compile(
    r"`scripts/([\w.-]*[\w-](?:/[\w.-]*[\w-])*)/?`")
BARE_SCRIPT_PATH_RE = re.compile(
    r"(?<![`\w./-])scripts/([\w.-]*[\w-](?:/[\w.-]*[\w-])*)/?(?![`\w/-])")
SCRIPT_DIR_RE = re.compile(
    r"`scripts/(?:tests/)?`|(?<![\w./-])scripts/(?:tests/)?(?![\w-])")
SCRIPT_EVIDENCE_PATH_RE = re.compile(
    r"(?P<quote>['\"])(?:/[^'\"\n\s]+)+/scripts/([\w./-]+\.py)(?P=quote)")
DUPLICATE_TASK_RE = re.compile(r"`(mise run [^`]+)`\s*(?:,|and)\s*`\1`")
BAD_MISE_LINK_RE = re.compile(r"(?:\[`|`)(mise run [^`]+)`\]\(`mise run [^`]+`\)")
RESOURCE_RE = re.compile(
    r"(?<![\w./-])(references|assets|examples|evals|fixtures|schemas|templates|"
    r"data|configs?|docs|tests|\.github|prompts|reports|artifacts)/")
FILE_PATH_RE = re.compile(
    r"(?<![\w./-])(?:\.\.?/)*[\w.-]+/(?:[\w.-]+/)*[\w.-]+\.[A-Za-z0-9]{1,12}\b|"
    r"(?<![\w./-])(?:\.\.?/)+(?:SKILL\.md|mise\.toml)\b")
URL_RE = re.compile(r"https?://[^\s)>]+")
RESOURCE_TASKS = {"evals": "evals", "tests": "test", ".github": "ci"}


def task_script_paths(task):
    run = task.get("run", "")
    values = [run] if isinstance(run, str) else run if isinstance(run, list) else []
    return [path for value in values
            for path in re.findall(r"scripts/([\w./-]+\.py)", value)]


def script_task_map(tasks):
    found = {}
    ambiguous = set()
    for name, task in tasks.items():
        for path in task_script_paths(task):
            if path in found and found[path] != name:
                ambiguous.add(path)
            found[path] = name
    return {path: task for path, task in found.items() if path not in ambiguous}


def replace_script(match, owners):
    path, tail = match.group(1), match.group(2)
    task = owners.get(path)
    return f"mise run {task}{tail}" if task else match.group(0)


def path_task(path, owners):
    if path in owners:
        return owners[path]
    if path.startswith("tests/") or path == "tests":
        return "test"
    return next((task for owner, task in owners.items() if path.endswith(owner)),
                "validate")


def replace_path(match, owners):
    path = match.group(1).rstrip(".,)")
    return f"`mise run {path_task(path, owners)}`"


def replace_link(match, owners):
    return f"`mise run {path_task(match.group(1), owners)}`"


def replace_fenced_command(match, owners):
    task = path_task(match.group(1), owners)
    return f"`mise run {task}{match.group(2)}`"


def replace_evidence_path(match):
    name = match.group(2).split("/")[-1]
    return f"{match.group('quote')}<skill-implementation>/{name}{match.group('quote')}"


def rewrite_script_text(text, owners):
    updated = SCRIPT_LINK_RE.sub(lambda item: replace_link(item, owners), text)
    updated = TEST_RE.sub("mise run test", updated)
    updated = SCRIPT_RE.sub(lambda item: replace_script(item, owners), updated)
    updated = FENCED_SCRIPT_COMMAND_RE.sub(
        lambda item: replace_fenced_command(item, owners), updated)
    updated = FENCED_SCRIPT_PATH_RE.sub(lambda item: replace_path(item, owners), updated)
    updated = BARE_SCRIPT_PATH_RE.sub(lambda item: replace_path(item, owners), updated)
    updated = SCRIPT_DIR_RE.sub("`mise run test`", updated)
    updated = SCRIPT_EVIDENCE_PATH_RE.sub(replace_evidence_path, updated)
    return DUPLICATE_TASK_RE.sub(r"`\1`", updated)


def pair_resource(line):
    if "mise run " in line:
        return line
    plain = URL_RE.sub("", line)
    match = RESOURCE_RE.search(plain) or FILE_PATH_RE.search(plain)
    if not match:
        return line
    task = ("evals" if "evals/" in plain else "test" if "tests/" in plain
            else "ci" if ".github/" in plain else "validate")
    return line.rstrip() + f" Use it through `mise run {task}`."


def section_starts(lines):
    return [index for index, line in enumerate(lines)
            if line.startswith("#") and line.lstrip("#").startswith(" ")]


def resource_gate_section(lines, start, end):
    body = "\n".join(lines[start:end])
    plain = URL_RE.sub("", body)
    has_resource = RESOURCE_RE.search(plain) or FILE_PATH_RE.search(plain)
    if not has_resource or "mise run " in body:
        return lines[start:end]
    gate = "Resource gate: run `mise run validate` before using package files named here."
    offset = start + 1 if lines[start].startswith("#") else start
    return lines[start:offset] + ["", gate] + lines[offset:end]


def add_resource_gates(text):
    lines = text.split("\n")
    starts = section_starts(lines)
    boundaries = sorted(set([0, *starts, len(lines)]))
    output = []
    for index in range(len(boundaries) - 1):
        output += resource_gate_section(lines, boundaries[index], boundaries[index + 1])
    return "\n".join(output)


def rewrite_body(text, owners):
    return add_resource_gates(rewrite_script_text(text, owners))


def route_line(line, profile):
    for route in profile.get("line_task_routes", []):
        if route["contains"] not in line:
            continue
        tasks = iter(route["tasks"])
        return BAD_MISE_LINK_RE.sub(lambda item: f"`mise run {next(tasks)}`", line)
    return line


def contract_resources():
    return ("Load `assets/use-case-contract.json` through `mise run use-case-policy` "
            "and `evals/evals.json` through `mise run evals` only when their "
            "contracts are needed.")


def contract_section(profile):
    term, task = profile["primary_term"], profile["main_task"]
    return ("\n## Factory execution contract\n\n"
            f"The accepted outcome is: {profile['outcome']} Preserve current {term} behavior while changing its smallest owner.\n\n"
            "1. Freeze the current package with `mise run ci` and record its digest.\n"
            f"2. Run `mise run domain-research-policy`, then judge the current {term} sources and counterevidence.\n"
            f"3. Run `mise run {task}` for the named {term} operation. Keep semantic choices with the model.\n"
            "4. Run `mise run decision-policy`, `mise run ci`, and the behavioral evals. Return to the lowest failed owner.\n"
            "5. Run `mise run invocation-policy -- <receipt>` and account for every task or its domain-specific non-use.\n"
            "6. Optionally run `mise run improvement-policy`. Keep one changed dimension only if no protected dimension regresses.\n\n"
            "Mise owns repeatable mechanics, ordering, receipts, and checks. The model owns interpretation, causal judgment, creative work, and direct perception that code cannot supply. Stop on missing authority, stale evidence, or a failed gate.\n")


def rewrite_markdown(text, owners, profile, add_contract=False):
    updated = rewrite_body(text, owners)
    updated = "\n".join(route_line(line, profile) for line in updated.split("\n"))
    updated = BAD_MISE_LINK_RE.sub(lambda item: f"`{item.group(1)}`", updated)
    if add_contract and "## Factory execution contract" not in updated:
        updated = updated.rstrip() + "\n" + contract_section(profile)
    if add_contract and contract_resources() not in updated:
        marker = "\nMise owns repeatable mechanics"
        updated = updated.replace(marker, "\n" + contract_resources() + "\n" + marker)
    return updated
