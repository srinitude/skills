"""Validate the supplied file inventory and declared context edges."""


def canonical(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Paths must be nonempty strings")
    return (root / value).resolve()


def path_list(root, data, field):
    values = data.get(field, [])
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list")
    return {canonical(root, value) for value in values}


def core_reasons(root, data):
    reasons = data.get("core_reasons", {})
    if not isinstance(reasons, dict):
        raise ValueError("core_reasons must be an object")
    mapped = {canonical(root, key): value for key, value in reasons.items()}
    if any(not isinstance(v, str) or not v.strip() for v in mapped.values()):
        raise ValueError("Each core reason must be a nonempty string")
    return mapped


def anchor_map(root, data):
    supplied = data.get("anchors", {})
    if not isinstance(supplied, dict):
        raise ValueError("anchors must be an object")
    mapped = {}
    for key, values in supplied.items():
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            raise ValueError("Each anchors value must be a list of nonempty strings")
        mapped[canonical(root, key)] = set(values)
    return mapped


def manifest_options(root, data, actual, errors, supplied):
    declared = path_list(root, data, "files")
    if supplied and declared != actual:
        errors.extend(f"Manifest omits Markdown file: {p}" for p in sorted(actual - declared))
        errors.extend(f"Manifest lists no governed Markdown file: {p}" for p in sorted(declared - actual))
    reasons = core_reasons(root, data)
    heading_ids = data.get("heading_ids", "github-style")
    if heading_ids not in ("github-style", "explicit"):
        raise ValueError("heading_ids must be github-style or explicit")
    anchors = anchor_map(root, data)
    starts = path_list(root, data, "entrypoints")
    for start in starts:
        if start not in actual:
            errors.append(f"Entrypoint is not a governed Markdown file: {start}")
    return reasons, heading_ids, anchors, starts


def dependency(root, edge):
    if not isinstance(edge, dict) or set(edge) != {"from", "to", "kind", "reason"}:
        raise ValueError("Each dependency needs from, to, kind, and reason")
    if edge["kind"] not in ("required", "navigation"):
        raise ValueError("Dependency kind must be required or navigation")
    if not isinstance(edge["reason"], str) or not edge["reason"].strip():
        raise ValueError("Each dependency needs a reason")
    return canonical(root, edge["from"]), canonical(root, edge["to"])


def readable_endpoint(endpoint, errors):
    if not endpoint.is_file():
        errors.append(f"Dependency file is missing: {endpoint}")
        return
    try:
        endpoint.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Dependency cannot be read: {endpoint}: {exc}")


def declared_routes(root, data, errors, reading_routes):
    edges = data.get("dependencies", [])
    if not isinstance(edges, list):
        errors.append("dependencies must be a list")
        return []
    required = []
    for edge in edges:
        try:
            source, target = dependency(root, edge)
            readable_endpoint(source, errors)
            readable_endpoint(target, errors)
            if edge["kind"] == "required":
                required.append((str(source), str(target)))
            reading_routes.append((source, target))
        except (ValueError, OSError) as exc:
            errors.append(f"Invalid dependency: {exc}")
    return required
