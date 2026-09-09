"""Check exact source coverage; semantic completeness remains a reviewed judgment."""
import hashlib
import json
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def parse_json(value):
    return json.loads(value, object_pairs_hook=unique_object, parse_constant=reject_constant)


def load_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bound_bytes(path, expected, label):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in [path, *path.parents]), f"{label} has a symlink")
    value = path.read_bytes()
    require(hashlib.sha256(value).hexdigest() == expected, f"{label} digest differs")
    return value


def span(item, source, seen):
    require(isinstance(item, dict), "source span must be an object")
    start, end = item.get("byte_start"), item.get("byte_end_exclusive")
    require(type(start) is int and type(end) is int, "source span offsets must be integers")
    require(0 <= start < end <= len(source), "source span outside source")
    require(source[start:end].decode("utf-8") == item.get("quote"), "source quotation differs")
    identifier = item.get("id")
    require(isinstance(identifier, str) and identifier.strip(), "source span needs an ID")
    require(identifier not in seen, "duplicate source or clause ID")
    seen.add(identifier)
    return start, end


def clauses(row, source, seen):
    values = row.get("clauses")
    require(isinstance(values, list) and values, "obligation needs clause locators")
    offset = row["byte_start"]
    for item in values:
        start, end = span(item, source, seen)
        require(offset <= start < end <= row["byte_end_exclusive"], "clause overlap or outside parent")
        require(not source[offset:start].strip(), "non-whitespace clause gap")
        offset = end
    require(not source[offset:row["byte_end_exclusive"]].strip(), "clause tail omitted")


def rows(document, source, expected):
    require(isinstance(document, dict), "coverage must be an object")
    require(document.get("source_sha256") == expected, "coverage source binding differs")
    require(type(document.get("source_bytes")) is int and document["source_bytes"] == len(source), "source byte count differs")
    lines, records = source.splitlines(keepends=True), document.get("records")
    require(isinstance(records, list) and len(records) == len(lines), "source span omitted")
    require(type(document.get("source_lines")) is int and document["source_lines"] == len(lines), "source line count differs")
    offset, seen = 0, set()
    for number, (row, line) in enumerate(zip(records, lines), 1):
        start, end = span(row, source, seen)
        require(start == offset and end == offset + len(line), "source gap or overlap")
        require(type(row.get("line_start")) is int and type(row.get("line_end")) is int,
                "source line locators must be integers")
        require(row["line_start"] == row["line_end"] == number, "source line locator differs")
        require(row.get("source_sha256") == expected, "row source binding differs")
        kind = row.get("kind")
        require(isinstance(kind, str) and (kind == "obligation" or kind.startswith("context:")), "unclassified source span")
        if kind == "obligation":
            clauses(row, source, seen)
        offset = end
    require(offset == len(source), "source tail omitted")
    return records


def validate(source_path, coverage_path, source_sha256, coverage_sha256):
    """Caller-supplied frozen digests cannot be replaced by request document fields."""
    source = bound_bytes(source_path, source_sha256, "source")
    raw = bound_bytes(coverage_path, coverage_sha256, "coverage")
    document = parse_json(raw)
    records = rows(document, source, source_sha256)
    return {"source_spans": len(records), "source_sha256": source_sha256,
            "coverage_sha256": coverage_sha256, "semantic_acceptance": "pending"}


def check_arguments(args):
    values = [getattr(args, name) for name in ["source", "coverage", "source_sha256", "coverage_sha256"]]
    if not any(values):
        return
    require(all(values), "source coverage requires all four caller-bound inputs")
    report = validate(*values)
    print("coverage mechanics: " + json.dumps(report))


def mapped_text_current(root, entry):
    expected, targets = entry.get("public_text_sha256"), entry.get("public_targets")
    require(isinstance(expected, str) and len(expected) == 64
            and all(char in "0123456789abcdef" for char in expected), "mapped public text needs a digest")
    require(isinstance(targets, list) and targets and all(isinstance(t, str) for t in targets), "mapped public targets missing")
    relative = Path(targets[0])
    require(not relative.is_absolute() and ".." not in relative.parts, "mapped target escapes package")
    require(not root.is_symlink(), "mapped package root has a symlink")
    path = root.resolve() / relative
    require(not any(p.is_symlink() for p in [path, *path.parents]), "mapped public target has a symlink")
    if not path.is_file():
        return False
    hashes = {hashlib.sha256(line.encode()).hexdigest() for line in path.read_text("utf-8").split("\n") if line.strip()}
    return expected in hashes


def mapping_problems(root):
    """Check preservation review bindings, never manufacture semantic review."""
    path = root / "evals/source-mapping.json"
    if not path.exists():
        return []
    document = load_json(path)
    require(isinstance(document, dict), "source mapping must be an object")
    entries = document.get("entries", [])
    require(isinstance(entries, list), "source mapping entries must be an array")
    found = []
    for entry in entries:
        require(isinstance(entry, dict), "source mapping entry must be an object")
        review = entry.get("preservation_review")
        if ("public_text_sha256" in entry or review is not None) and not mapped_text_current(root, entry):
            found.append("mapped public text changed; preservation evidence is stale")
        if review is None:
            continue
        require(isinstance(review, dict), "preservation review must be an object")
        if review.get("state") != "passed":
            found.append("stale preservation review requires responsible semantic assessment")
        elif (review.get("reviewed_sha256") != entry.get("public_text_sha256")
              or not isinstance(entry.get("preservation_judgment"), str)
              or not entry["preservation_judgment"].strip()):
            found.append("source mapping needs a bound preservation judgment")
    return found
