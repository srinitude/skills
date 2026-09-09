"""Validate matrix references without deciding their meaning or evidence adequacy."""
import graphlib
import re
from pathlib import Path

from invocation_acceptance import selected_value
from source_coverage import bound_bytes, parse_json, require

STATES = {"unknown", "pending", "blocked", "failed", "stale", "satisfied", "inapplicable", "conflicting"}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]*\Z")


def shape(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + " fields differ")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + " needs nonempty text")
    return value


def identifiers(values, label):
    require(isinstance(values, list) and all(isinstance(value, str) and IDENTIFIER.fullmatch(value)
            for value in values), label + " needs identifier strings")
    return values


def index(values, label):
    require(isinstance(values, list), label + " must be an array")
    require(all(isinstance(item, dict) for item in values), label + " records must be objects")
    ids = identifiers([item.get("id") for item in values], label)
    require(len(ids) == len(set(ids)), label + " duplicate identity")
    return dict(zip(ids, values))


def references(values, owners, label):
    require(all(value in owners for value in identifiers(values, label)), "unknown " + label + " reference")


def records(values, base):
    require(isinstance(values, dict), "matrix records must be an object")
    identifiers(list(values), "matrix record")
    resolved = {}
    for name, binding in values.items():
        shape(binding, {"path", "sha256", "pointer"}, "matrix record binding")
        path = Path(text(binding["path"], "matrix record path"))
        path = path if path.is_absolute() else base / path
        raw = bound_bytes(path, binding["sha256"], "matrix record " + name)
        resolved[name] = selected_value(parse_json(raw), binding["pointer"])
    return resolved


def extensions(values, concepts, resolved):
    for name, item in index(values, "extension").items():
        shape(item, {"id", "label", "definition", "aliases", "state", "source"}, "extension")
        require(name.startswith("extension:") and name not in concepts, "extension identity must be separate")
        text(item["label"], "extension label")
        require(item["definition"] is None or isinstance(item["definition"], str), "invalid extension definition")
        require(isinstance(item["aliases"], list) and all(isinstance(alias, str) and alias.strip()
                for alias in item["aliases"]), "invalid extension aliases")
        require(item["state"] in {"named", "unresolved"}, "extension state must retain resolution status")
        require(item["state"] != "named" or bool(item["definition"]), "named extension needs its definition")
        source = item["source"]
        shape(source, {"record", "version", "url", "locator", "scope", "license"}, "extension source")
        references([source["record"]], resolved, "extension source")
        for field in ["version", "locator", "scope", "license"]:
            text(source[field], "extension source " + field)
        require(source["url"] is None or isinstance(source["url"], str) and
                source["url"].startswith(("https://", "http://")), "invalid extension source URL")
        item["aliases"].sort()
        concepts[name] = item


def correspondences(values, concepts, resolved):
    for item in index(values, "correspondence").values():
        shape(item, {"id", "from", "to", "relation", "judgment"}, "correspondence")
        references([item["from"], item["to"]], concepts, "correspondence concept")
        require(item["relation"] in {"exact_match", "close_match", "broader", "narrower", "related"},
                "unsupported concept correspondence")
        references([item["judgment"]], resolved, "correspondence judgment")


def occurrences(values, concepts, resolved):
    result = index(values, "occurrence")
    for item in result.values():
        shape(item, {"id", "concept", "role", "conditions"}, "occurrence")
        references([item["concept"]], concepts, "concept")
        text(item["role"], "occurrence role")
        references(item["conditions"], resolved, "occurrence condition")
        item["conditions"].sort()
    return result


def groups(values, instances):
    result = index(values, "group")
    require(not set(result) & set(instances), "group and occurrence identity collision")
    for item in result.values():
        shape(item, {"id", "semantics", "members"}, "group")
        require(item["semantics"] in {"ordered", "unordered"}, "invalid group semantics")
        references(item["members"], result.keys() | instances.keys(), "group member")
        if item["semantics"] == "unordered":
            item["members"].sort()
    graphlib.TopologicalSorter({name: [member for member in item["members"] if member in result]
                               for name, item in result.items()}).prepare()
    return result


def interactions(values, selections, resolved):
    fields = {"people", "context", "outcomes", "choices", "evidence", "constraints", "judgments", "dependencies"}
    for item in index(values, "interaction").values():
        shape(item, fields | {"id", "study", "work", "state"}, "interaction")
        require(item["state"] in STATES, "invalid interaction evidence state")
        for field in fields:
            references(item[field], resolved, "interaction " + field)
            item[field].sort()
        for field in ["study", "work"]:
            references(item[field], selections, "interaction " + field)
            item[field].sort()


def canonicalize(document):
    for field in ["extensions", "correspondences", "occurrences", "groups", "interactions", "selectors"]:
        document[field].sort(key=lambda item: item["id"])
    return document
