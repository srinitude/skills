"""Preserve source mappings and check their declared public bindings.

A text transformation cannot author preservation judgments or change assertions.
These checks establish only current text bindings; semantic review, full source
coverage and the target's other acceptance gates retain their actual owners.
"""
import hashlib

from agentic_request_contract import read_json
from standardization_rewrites import safe_target

from standardization_markdown import BAD_MISE_LINK_RE, rewrite_script_text, route_line


def text_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def snapshot_public_lines(root):
    snapshots = {}
    for path in root.rglob("*.md"):
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


def mapped_text(root, target, cache):
    if not isinstance(target, str) or not target.strip():
        raise ValueError("source mapping target must be nonempty text")
    if target not in cache:
        cache[target] = safe_target(root, target).read_bytes().decode("utf-8")
    return cache[target]


def check_assertion(root, item, cache):
    if not isinstance(item, dict) or not isinstance(item.get("contains"), str) or not item["contains"]:
        raise ValueError("source mapping assertion needs target and nonempty contains")
    if item["contains"] not in mapped_text(root, item.get("target"), cache):
        raise ValueError("source mapping assertion differs; responsible source review is required")


def check_mapping_entry(root, entry, semantic, cache):
    if not isinstance(entry, dict):
        raise ValueError("source mapping entries must be objects")
    if "public_text_sha256" in entry:
        targets = entry.get("public_targets")
        if not isinstance(targets, list) or not targets:
            raise ValueError("source mapping line digest needs its first public target")
        key = (targets[0], "line_digests") if isinstance(targets[0], str) else None
        text = mapped_text(root, targets[0], cache)
        if key not in cache:
            cache[key] = {text_digest(line) for line in text.split("\n") if line.strip()}
        if not isinstance(entry["public_text_sha256"], str) or entry["public_text_sha256"] not in cache[key]:
            raise ValueError("source mapping line differs; responsible source review is required")
    if "public_semantic_id" in entry:
        if not isinstance(entry["public_semantic_id"], str) or entry["public_semantic_id"] not in semantic:
            raise ValueError("source mapping references an unknown semantic owner")
    assertions = entry.get("public_assertions", [])
    if not isinstance(assertions, list):
        raise ValueError("source mapping public_assertions must be an array")
    for assertion in assertions:
        check_assertion(root, assertion, cache)


def repair_mapping_json(root, owners=None, profile=None, snapshots=None):
    """Legacy entry point: check bindings without rewriting any mapping bytes.

    A caller may supply a separately reviewed mapping. Matching text cannot
    establish the authenticity or soundness of that review. Other mapping
    schemas need their owning validator before affected standardization.
    """
    path = root / "evals/source-mapping.json"
    if not path.exists() and not path.is_symlink():
        return
    try:
        data = read_json(safe_target(root, "evals/source-mapping.json").read_bytes().decode("utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list) or not data["entries"]:
            raise ValueError("source mapping needs its owning schema validator")
        semantic, cache = {}, {}
        mappings = data.get("semantic_mappings", [])
        if not isinstance(mappings, list):
            raise ValueError("source mapping semantic_mappings must be an array")
        for item in mappings:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"] or item["id"] in semantic:
                raise ValueError("source mapping semantic IDs must be nonempty and unique")
            check_assertion(root, item, cache)
            semantic[item["id"]] = item
        for entry in data["entries"]:
            check_mapping_entry(root, entry, semantic, cache)
    except (OSError, ValueError) as error:
        raise ValueError(f"source mapping: {error}") from error
