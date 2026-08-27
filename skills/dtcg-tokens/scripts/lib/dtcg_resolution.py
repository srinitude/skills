"""Reference and group-extension resolution for DTCG 2025.10 documents."""
import copy
import re
from urllib.parse import unquote

CURLY = re.compile(r"^\{([^${}.][^{}.]*(?:\.[^${}.][^{}.]*)*)\}$")


class ResolutionError(ValueError):
    """A reference cannot resolve without violating the DTCG contract."""


def is_token(node):
    return isinstance(node, dict) and ("$value" in node or "$ref" in node)


def pointer_parts(reference):
    if not isinstance(reference, str) or not reference.startswith("#/"):
        raise ResolutionError(f"invalid JSON Pointer reference: {reference}")
    return tuple(part.replace("~1", "/").replace("~0", "~") for part in unquote(reference[2:]).split("/"))


def pointer_value(document, reference):
    current = document
    for part in pointer_parts(reference):
        try:
            current = current[int(part)] if isinstance(current, list) else current[part]
        except (KeyError, IndexError, TypeError, ValueError):
            raise ResolutionError(f"JSON Pointer target does not exist: {reference}") from None
    return current


def collect_groups(node, path=(), groups=None):
    groups = {} if groups is None else groups
    if not isinstance(node, dict) or is_token(node):
        return groups
    groups[path] = node
    for name, child in node.items():
        if not name.startswith("$"):
            collect_groups(child, path + (name,), groups)
    return groups


def extension_path(reference):
    match = CURLY.fullmatch(reference) if isinstance(reference, str) else None
    if match:
        return tuple(match.group(1).split("."))
    return pointer_parts(reference)


def deep_merge(base, local):
    result = copy.deepcopy(base)
    for key, value in local.items():
        prior = result.get(key)
        if isinstance(prior, dict) and isinstance(value, dict) and not is_token(prior) and not is_token(value):
            result[key] = deep_merge(prior, value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def expand_document(document):
    if not isinstance(document, dict) or is_token(document):
        return document, []
    groups = collect_groups(document)
    cache, errors = {}, []

    def expand(path, active):
        if path in cache:
            return copy.deepcopy(cache[path])
        if path in active:
            chain = [".".join(item) or "<root>" for item in active + [path]]
            errors.append(f"{'.'.join(path) or '<root>'}: group extension cycle: {' -> '.join(chain)}")
            return {}
        node = groups[path]
        local = copy.deepcopy(node)
        for name, child in list(local.items()):
            child_path = path + (name,)
            if not name.startswith("$") and child_path in groups:
                local[name] = expand(child_path, active + [path])
        reference = node.get("$extends")
        if reference is None:
            cache[path] = local
            return copy.deepcopy(local)
        try:
            target = extension_path(reference)
        except ResolutionError as error:
            errors.append(f"{'.'.join(path) or '<root>'}: {error}")
            return local
        if target not in groups:
            errors.append(f"{'.'.join(path) or '<root>'}: group extension target is not a group: {reference}")
            return local
        merged = deep_merge(expand(target, active + [path]), local)
        cache[path] = merged
        return copy.deepcopy(merged)

    return expand((), []), errors


def token_owner(pointer_tokens, parts):
    for length in range(len(parts), -1, -1):
        if parts[:length] in pointer_tokens:
            return pointer_tokens[parts[:length]]
    return None


def reference_owner(state, reference):
    match = CURLY.fullmatch(reference) if isinstance(reference, str) else None
    if match:
        target = match.group(1)
        if target not in state["tokens"]:
            raise ResolutionError(f"reference target does not exist: {target}")
        return target
    parts = pointer_parts(reference)
    pointer_value(state["document"], reference)
    return token_owner(state["pointer_tokens"], parts)


def references_in(value):
    if isinstance(value, str) and CURLY.fullmatch(value):
        return [value]
    if isinstance(value, dict):
        if set(value) == {"$ref"}:
            return [value["$ref"]]
        return sum((references_in(item) for item in value.values()), [])
    if isinstance(value, list):
        return sum((references_in(item) for item in value), [])
    return []


def whole_alias_target(state, path):
    node = state["tokens"][path]["node"]
    value = node.get("$value")
    if isinstance(value, str) and CURLY.fullmatch(value):
        return CURLY.fullmatch(value).group(1)
    reference = node.get("$ref")
    if isinstance(value, dict) and set(value) == {"$ref"}:
        reference = value["$ref"]
    if reference is None:
        return None
    parts = pointer_parts(reference)
    owner = token_owner(state["pointer_tokens"], parts)
    owner_parts = state["tokens"].get(owner, {}).get("pointer")
    return owner if owner_parts and parts in {owner_parts, owner_parts + ("$value",)} else None


def resolve_token(state, path, active=None):
    if path not in state["tokens"]:
        raise ResolutionError(f"reference target does not exist: {path}")
    active = set() if active is None else set(active)
    marker = ("token", path)
    if marker in active:
        raise ResolutionError(f"reference cycle includes {path}")
    active.add(marker)
    node = state["tokens"][path]["node"]
    value = node.get("$value", {"$ref": node.get("$ref")})
    return resolve_any(state, value, active)


def resolve_any(state, value, active):
    if isinstance(value, str) and CURLY.fullmatch(value):
        return resolve_token(state, CURLY.fullmatch(value).group(1), active)
    if isinstance(value, dict) and set(value) == {"$ref"}:
        reference = value["$ref"]
        marker = ("pointer", reference)
        if marker in active:
            raise ResolutionError(f"reference cycle includes {reference}")
        target = pointer_value(state["document"], reference)
        owner = reference_owner(state, reference)
        if owner and target is state["tokens"][owner]["node"]:
            return resolve_token(state, owner, active | {marker})
        return resolve_any(state, target, active | {marker})
    if isinstance(value, dict):
        return {key: resolve_any(state, item, active) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_any(state, item, active) for item in value]
    return value
