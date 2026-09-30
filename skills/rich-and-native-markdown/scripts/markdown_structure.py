"""Opt-in checks for a heading outline and justified standalone paragraphs."""

from markdown_manifest import canonical


def structure_options(root, data, actual):
    if "structure" not in data:
        return None
    value = data["structure"]
    if not isinstance(value, dict) or set(value) - {"paragraphs"}:
        raise ValueError("structure must be an object with only optional paragraphs")
    paragraphs = value.get("paragraphs", {})
    if not isinstance(paragraphs, dict):
        raise ValueError("structure.paragraphs must be an object")
    mapped = {}
    for name, records in paragraphs.items():
        path = canonical(root, name)
        if path not in actual or path in mapped:
            raise ValueError(f"Paragraph reasons need one governed file path: {name}")
        mapped[path] = paragraph_records(records)
    return mapped


def paragraph_records(records):
    if not isinstance(records, list):
        raise ValueError("Paragraph reasons must be a list")
    mapped = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != {"line", "text", "reason"}:
            raise ValueError("Each paragraph reason needs line, text, and reason")
        line = record["line"]
        if type(line) is not int or line < 1 or line in mapped:
            raise ValueError("Paragraph lines must be unique positive integers")
        if any(not isinstance(record[k], str) or not record[k].strip()
               for k in ("text", "reason")):
            raise ValueError("Paragraph text and reason must be nonempty strings")
        mapped[line] = record
    return mapped


def without_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    end = next((i for i in range(1, len(lines))
                if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return text
    return "\n" * (end + 1) + "\n".join(lines[end + 1:])


def heading_rows(tokens):
    headings, quote_depth = [], 0
    for i, token in enumerate(tokens):
        if token.type == "blockquote_open":
            quote_depth += 1
        if token.type == "blockquote_close":
            quote_depth -= 1
        if token.type != "heading_open" or quote_depth:
            continue
        title = "".join(c.content for c in tokens[i + 1].children
                        if c.type in ("text", "code_inline", "image"))
        headings.append((i, int(token.tag[1:]), title, token.map[0] + 1))
    return headings


def check_headings(path, tokens, errors):
    headings = heading_rows(tokens)
    top = [row for row in headings if tokens[row[0]].level == 0]
    if sum(level == 1 for _, level, _, _ in top) != 1:
        errors.append(f"{path}: structure requires exactly one top-level H1")
    for required in (2, 3):
        if not any(level == required for _, level, _, _ in top):
            errors.append(f"{path}: structure requires at least one top-level H{required}")
    if any(level == 1 and tokens[i].level > 0 for i, level, _, _ in headings):
        errors.append(f"{path}: document H1 must be the top-level file title")
    previous = 0
    for _, level, title, line in headings:
        if not title.strip():
            errors.append(f"{path}:{line}: heading must have a label")
        # One-level descent plus shallower returns preserves every active ancestor.
        if level > previous + 1:
            errors.append(f"{path}:{line}: heading skips from H{previous} to H{level}")
        previous = level


def has_content(tokens):
    for i, token in enumerate(tokens):
        if token.type in ("fence", "code_block") and token.content.strip():
            return True
        if token.type != "inline" or (i and tokens[i - 1].type == "heading_open"):
            continue
        if any(c.type in ("text", "code_inline", "image") and c.content.strip()
               for c in (token.children or [])):
            return True
    return False


def check_heading_content(path, tokens, result):
    headings = heading_rows(tokens)
    for n, (start, _, _, line) in enumerate(headings):
        stop = headings[n + 1][0] if n + 1 < len(headings) else len(tokens)
        # Skip the heading's open, inline label, and close tokens.
        if not has_content(tokens[start + 3:stop]):
            result["errors"].append(
                f"{path}:{line}: heading needs non-heading content before the next heading or EOF")
    if any(t.type == "heading_open" and t.level > 0 for t in tokens):
        result["needs_review"].append(
            f"{path}: container headings need manual review; preserve exact quoted examples")


def image_only(inline):
    return bool(inline.children) and all(
        child.type == "image" or (child.type == "text" and not child.content.strip())
        for child in inline.children)


def check_paragraphs(path, tokens, records, result):
    used = set()
    for i, token in enumerate(tokens):
        if token.type != "paragraph_open" or token.level != 0:
            continue
        inline = tokens[i + 1]
        if image_only(inline):
            continue
        line = token.map[0] + 1
        record = records.get(line)
        if record and record["text"] == inline.content:
            used.add(line)
            result["needs_review"].append(f"{path}:{line}: review paragraph reason: {record['reason']}")
        else:
            result["errors"].append(f"{path}:{line}: standalone prose needs an exact paragraph reason")
    for line in records.keys() - used:
        result["errors"].append(f"{path}:{line}: paragraph reason is stale or does not match prose")


def check_structure(path, text, parser, records, result):
    # ponytail: syntax cannot prove semantic headings or procedure order; review both.
    tokens = parser.parse(without_frontmatter(text))
    check_headings(path, tokens, result["errors"])
    check_heading_content(path, tokens, result)
    check_paragraphs(path, tokens, records, result)
    has_html = any(t.type in ("html_block", "html_inline") or
                   any(c.type == "html_inline" for c in (t.children or [])) for t in tokens)
    if has_html:
        result["needs_review"].append(f"{path}: raw HTML needs manual heading, content, rule-format, and renderer review")


def check_structures(root, data, files, read, result):
    try:
        options = structure_options(root, data, {p.resolve() for p in files})
    except (ValueError, OSError) as exc:
        result["errors"].append(f"Invalid structure manifest: {exc}")
        return
    if options is None:
        return
    from markdown_it import MarkdownIt
    parser = MarkdownIt("commonmark").enable("table")
    for path in files:
        path = path.resolve()
        parts = read(path)
        if parts is not None:
            check_structure(path, parts[0], parser, options.get(path, {}), result)
    result["needs_review"].append(
        "Structure mode checks non-quoted heading levels, content presence, and standalone prose; "
        "review meaning, filler, required deeper sections, ordered steps versus unordered rules, "
        "container headings, and exact example boundaries")
