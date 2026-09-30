"""Apply reviewed, profile-bound text migrations."""
from pathlib import Path


def safe_target(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"unsafe text rewrite path: {relative}")
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"text rewrite leaves target: {relative}")
    if not path.is_file():
        raise ValueError(f"text rewrite target is missing: {relative}")
    return path


def terminal_replacement(value, remaining):
    terminal = value
    for rule in remaining:
        if rule["old"] == terminal:
            terminal = rule["new"]
    return terminal


def apply_rule(text, rule, remaining, relative, strict):
    old, new = rule["old"], rule["new"]
    if old in text or new in text:
        return text.replace(old, new)
    if terminal_replacement(new, remaining) in text:
        return text
    if not strict:
        return text
    raise ValueError(f"text rewrite source is missing: {relative}")


def apply_rewrites(root, profile, strict=True):
    for relative, rules in profile.get("text_rewrites", {}).items():
        path = safe_target(root, relative)
        text = path.read_text(encoding="utf-8")
        path.write_text(rewritten_text(text, rules, relative, strict), encoding="utf-8")


def rewritten_text(text, rules, relative, strict=True):
    for index, rule in enumerate(rules):
        text = apply_rule(text, rule, rules[index + 1:], relative, strict)
    return text


def apply_section_rewrites(root, profile):
    for rule in profile.get("section_rewrites", []):
        path = safe_target(root, rule["path"])
        text = path.read_text(encoding="utf-8")
        updated = rewritten_section(text, rule)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def rewritten_section(text, rule):
    replacement = rule["replacement"].rstrip() + "\n\n"
    if replacement in text:
        return text
    start = text.find(rule["heading"] + "\n")
    end = text.find(rule["until"] + "\n", start + 1)
    if start < 0 or end < 0:
        raise ValueError(f"section rewrite boundary is missing: {rule['path']}")
    return text[:start] + replacement + text[end:]


RESOURCE_OWNERS = (
    "Read the [generation contract](references/generation-contract.md) through `mise run validate` "
    "before accepting a created or updated skill. Read the [file-review example](examples/example-ledger-write.md) "
    "through `mise run ledger` before a file change. Actual reading and semantic review remain required."
)


def contract_resources():
    return ("Load `assets/use-case-contract.json` through `mise run use-case-policy` "
            "and `evals/evals.json` through `mise run evals` only when their "
            "contracts are needed.")


def legacy_contract_section(profile):
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



def contract_section(profile):
    term, task = profile["primary_term"], profile["main_task"]
    return ("\n## Factory execution contract\n\n"
            f"The accepted outcome is: {profile['outcome']} Preserve required {term} behavior.\n\n"
            "1. Capture current inputs and their digests. Keep required reads, safety, authority, data integrity and consumer inputs.\n"
            f"2. Run `mise run domain-research-policy`, then judge the current {term} sources and counterevidence.\n"
            f"3. Build broad working paths at shared owners. Run `mise run {task}` for the named {term} operation. Keep semantic choices with the model.\n"
            "4. Check available effects. Record what works, fails or remains untested. Give each gap an owner, next action, required inputs and deciding check.\n"
            "5. Switch to precise repair when the main paths exist and each gap has that repair path. Fix prerequisites first; keep partial work distinct from acceptance.\n"
            "6. Before acceptance, run `mise run decision-policy`, `mise run ci`, and the behavioral evals. Check the whole skill and domain result. Close every required gap.\n"
            "7. Run `mise run invocation-policy -- <receipt>` and account for every task or its domain-specific non-use.\n"
            "8. Optionally run `mise run improvement-policy`. Keep one changed dimension only if no protected dimension regresses.\n\n"
            + contract_resources() + "\n\n" + RESOURCE_OWNERS + "\n\n"
            "Mise owns repeatable mechanics, ordering, receipts, and checks. The model owns interpretation, causal judgment, creative work, and direct perception that code cannot supply. Stop on missing authority, stale evidence, or a failed gate.\n")


def contract_headings(text):
    from standardization_rules import policy_blocks
    import re
    headings = []
    for start, end, _ in policy_blocks(text):
        block = text[start:end]
        for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]+\S", block):
            headings.append((start + match.start(), 0, ""))
        for match in re.finditer(r"(?m)^ {0,3}(#{1,6})[ \t]+([^\n]+)", block):
            title = re.sub(r"[ \t]+#+[ \t]*$", "", match[2]).strip()
            headings.append((start + match.start(), len(match[1]), title))
        for match in re.finditer(r"(?m)^ {0,3}([^\n]+)\n {0,3}(=+|-+)[ \t]*(?:\n|$)", block):
            headings.append((start + match.start(), 1 if match[2][0] == "=" else 2, match[1].strip()))
    return sorted(headings)


def contract_content(text):
    for resource in [contract_resources(), RESOURCE_OWNERS]:
        text = text.replace("\n" + resource + "\n", "\n")
    return "\n\n".join(part.strip() for part in text.split("\n\n") if part.strip())


def rewrite_execution_contract(text, profile):
    headings = contract_headings(text)
    matches = [row for row in headings if row[2] == "Factory execution contract"]
    current = contract_section(profile)
    if not matches:
        return text.rstrip() + "\n" + current
    if len(matches) != 1 or matches[0][1] != 2:
        raise ValueError("Execution contract needs an explicit reviewed profile migration")
    start = matches[0][0]
    end = next((offset for offset, level, _ in headings if offset > start and level <= 2), len(text))
    allowed = {contract_content(current), contract_content(legacy_contract_section(profile))}
    if contract_content(text[start:end]) not in allowed:
        raise ValueError("Execution contract needs an explicit reviewed profile migration")
    return text[:start] + current.lstrip("\n").rstrip() + "\n" + ("\n" if end < len(text) else "") + text[end:]
