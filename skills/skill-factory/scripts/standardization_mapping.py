"""Keep source mappings truthful after factory-owned text rewrites."""
import hashlib
import json
from copy import deepcopy

from source_coverage import load_json, mapped_text_current
from standardization_markdown import BAD_MISE_LINK_RE, rewrite_script_text, route_line
from skill_package import owned_files


def text_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def snapshot_public_lines(root):
    root = root.resolve()
    snapshots = {}
    for path in (p for p in owned_files(root) if p.suffix == ".md"):
        relative = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8").split("\n")
        snapshots[relative] = {text_digest(line): line for line in lines if line.strip()}
    return snapshots


def boundary_rewrite(value, old, new):
    upper = min(len(value), len(old))
    for size in range(upper, 5, -1):
        prefix = value[:size]
        if old.endswith(prefix) and prefix[-1] in ".!?":
            return new + value[size:]
        suffix = value[-size:]
        head = value[:-size]
        if old.startswith(suffix) and head.rstrip().endswith((".", "!", "?")):
            return head + new
    return None


def rewritten_assertion(value, target, owners, profile):
    for rule in profile.get("text_rewrites", {}).get(target, []):
        boundary = boundary_rewrite(value, rule["old"], rule["new"])
        if value in rule["old"]:
            value = rule["new"]
        elif boundary is not None:
            value = boundary
        else:
            value = value.replace(rule["old"], rule["new"])
    value = rewrite_script_text(value, owners)
    value = route_line(value, profile)
    return BAD_MISE_LINK_RE.sub(lambda item: f"`{item.group(1)}`", value)


def public_line_hashes(root, target):
    path = root / target
    if not path.is_file():
        return set()
    lines = path.read_text(encoding="utf-8").split("\n")
    return {text_digest(line) for line in lines if line.strip()}


def prior_public_line(entry, snapshots):
    targets = entry.get("public_targets", [])
    if not targets:
        return None
    target = targets[0]
    digest = entry.get("public_text_sha256")
    return snapshots.get(target, {}).get(digest)


def refresh_mapping_entry(root, entry, owners, profile, snapshots):
    targets = entry.get("public_targets", [])
    if not targets:
        return
    previous = prior_public_line(entry, snapshots)
    if not previous:
        return
    rewritten = rewritten_assertion(previous, targets[0], owners, profile)
    current = text_digest(rewritten)
    if current not in public_line_hashes(root, targets[0]):
        return
    entry["public_text_sha256"] = current


def invalidate_review(entry, previous, invalid=False):
    if entry == previous and not invalid:
        return
    history = previous.get("preservation_review", {}).pop("history", [])
    history.append(previous)
    entry.pop("preservation_judgment", None)
    entry["preservation_review"] = {"state": "stale", "history": history,
                                    "reason": "Mapped public text changed; semantic review is required."}


def repair_mapping_json(root, owners, profile, snapshots):
    path = root / "evals/source-mapping.json"
    if not path.is_file():
        return
    data = load_json(path)
    for entry in data.get("entries", []):
        previous = deepcopy(entry)
        refresh_mapping_entry(root, entry, owners, profile, snapshots)
        for assertion in entry.get("public_assertions", []):
            if isinstance(assertion.get("contains"), str):
                assertion["contains"] = rewritten_assertion(
                    assertion["contains"], assertion.get("target", ""), owners, profile)
        invalid = "public_text_sha256" in entry and not mapped_text_current(root, entry)
        invalidate_review(entry, previous, invalid)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
