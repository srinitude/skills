"""Check local link targets using cached CommonMark parses."""

import hashlib
from urllib.parse import unquote, urlsplit

from markdown_parse import markdown_parts


def read_parts(path, cache, parser, heading_ids, extra_anchors, errors):
    path = path.resolve()
    if path not in cache:
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
            parts = markdown_parts(text, parser, heading_ids)
            parts[1].update(extra_anchors.get(path, set()))
            cache[path] = (text, parts, hashlib.sha256(raw).hexdigest())
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"Cannot read {path}: {exc}")
            return None
    return cache[path]


def check_fragment(path, target, url, destination, read, result):
    if target.suffix.lower() != ".md":
        result["needs_review"].append(f"{path}: non-Markdown anchor needs review: {destination}")
        return
    target_parts = read(target)
    if target_parts and unquote(url.fragment) not in target_parts[1][1]:
        result["errors"].append(f"{path}: missing heading or HTML anchor {destination}")


def check_link(path, destination, read, result, routes):
    if not destination:
        return
    try:
        url = urlsplit(destination)
    except ValueError as exc:
        result["errors"].append(f"{path}: invalid link {destination!r}: {exc}")
        return
    if url.scheme or url.netloc:
        return
    local_path = unquote(url.path)
    # ponytail: site routes need renderer rules; use its resolver when required.
    if local_path.startswith("/"):
        result["needs_review"].append(f"{path}: site-root link needs a renderer check: {destination}")
        return
    target = (path.parent / local_path).resolve() if local_path else path
    if target.suffix.lower() == ".md":
        routes.append((path, target))
    if not target.exists():
        result["errors"].append(f"{path}: missing local target {destination}")
    elif url.fragment:
        check_fragment(path, target, url, destination, read, result)
