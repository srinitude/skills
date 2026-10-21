"""Inspect recorded task declarations without executing or resolving native tasks."""
import json

from review_ledger_context import relation, require

TASK_LIMIT = (
    "No native resolution, execution or acceptance is asserted. These are recorded same-file literal "
    "references, bound to the recorded file identity. Aliases, patterns, templates, includes, inheritance, "
    "argument interpolation, platform selection and external tasks still need native resolution. "
    "Keep the whole declaration, its conditions, arguments, environment, order and repeated occurrences.")
CONDITIONS = {
    "depends": "Prerequisites precede their parent; sibling list order is not sequence. Optionality and forwarding retain their declared conditions.",
    "depends_post": "The parent has started and then finished, including failure. A prerequisite that prevents its start also prevents the post-task subtree. No rollback or crash recovery is promised.",
    "wait_for": "Wait only for matching tasks already scheduled; this declaration does not schedule an absent task.",
    "run": "Referenced execution entries are sequential, with parallel members inside one tasks entry; these are not depends edges. Shell entries keep their positions. Referenced tasks retain their own prerequisites.",
    "run_windows": "Windows-specific execution entries retain their order and parallel groups, subject to native platform selection. These are not depends edges.",
}


def reference_targets(field, value, locator):
    running = field in {"run", "run_windows"}
    grouping = "ordered-run-entry" if running else "declared-prerequisite"
    if isinstance(value, str):
        return [] if running else [(value, locator, grouping)]
    if isinstance(value, dict) and isinstance(value.get("task"), str):
        return [(value["task"], locator + ["task"], grouping)]
    if running and isinstance(value, dict) and isinstance(value.get("tasks"), list):
        return [(target, locator + ["tasks", number], "parallel-run-entry")
                for number, target in enumerate(value["tasks"])]
    if not running and isinstance(value, list) and value and isinstance(value[0], str):
        return [(value[0], locator + [0], grouping)]
    return [(None, locator, "requires-native-resolution")]


def occurrence_references(path, field, value, locator, number, tasks):
    references = []
    for target, location, grouping in reference_targets(field, value, locator):
        resolved = isinstance(target, str) and target in tasks and not any(
            char.isspace() or char in "*?[]{}" for char in target)
        references.append({"field": field, "locator": location, "value": value,
            "target": f"task:{path}#{target}" if resolved else None,
            "state": "same-file-literal-reference" if resolved else "requires-native-resolution",
            "grouping": grouping, "run_entry": number if field in {"run", "run_windows"} else None})
    return references


def task_references(path, name, declaration, tasks):
    fields = declaration if isinstance(declaration, dict) else {"run": declaration}
    references = []
    for field in CONDITIONS:
        if field not in fields:
            continue
        values = fields[field] if isinstance(fields[field], list) else [fields[field]]
        for number, value in enumerate(values):
            locator = ["tasks", name] + ([field] if isinstance(declaration, dict) else [])
            locator += [number] if isinstance(fields[field], list) else []
            references.extend(occurrence_references(path, field, value, locator, number, tasks))
    return references


def task_subjects(data, index):
    result, snapshot = {}, data.get("dependency_snapshot", {})
    for path, observation in snapshot.get("files", {}).items():
        tasks = observation.get("mise_tasks")
        if tasks is None:
            continue
        require(type(snapshot.get("version")) is int and snapshot["version"] == 2
                and snapshot.get("method") == "python-imports-and-toml-tasks-v2", "unsupported task observation")
        require(path.endswith(".toml") and isinstance(tasks, dict), "invalid TOML task observation")
        current = index.get("file:" + path, {}).get("current")
        require(current is not None and observation["sha256"] == current["sha256"], "stale task declaration binding")
        for name, declaration in tasks.items():
            require(isinstance(name, str) and name, "missing task name")
            selector = f"task:{path}#{name}"
            require(selector not in result, "ambiguous task selector: " + selector)
            require(isinstance(declaration, (dict, str, list)), "invalid task declaration: " + selector)
            references = task_references(path, name, declaration, tasks)
            result[selector] = {"id": selector, "file": path, "name": name,
                "sha256": observation["sha256"], "declaration": declaration, "references": references,
                "unresolved_references": [row for row in references if row["target"] is None], "limit": TASK_LIMIT}
    return result


def task_edges(index):
    for selector, task in index.items():
        if not selector.startswith("task:"):
            continue
        basis, kind = ["file:" + task["file"], selector], "recorded-current-task-declaration"
        common = {"basis": basis, "subject_sha256": task["sha256"]}
        yield {**relation("MISE:part-of:" + selector, "part-of", selector, basis[0],
                         "The task declaration belongs to its recorded TOML file.", TASK_LIMIT, kind), **common}
        for reference in (row for row in task["references"] if row["target"] is not None):
            field, target = reference["field"], reference["target"]
            running = field in {"run", "run_windows"}
            before, after = (selector, target) if running or field == "depends_post" else (target, selector)
            identifier = "MISE:reference:" + json.dumps([selector, reference["locator"]], ensure_ascii=False, separators=(",", ":"))
            edge = relation(identifier, "references" if running else "executes-before", before, after,
                            "This recorded occurrence declares a conditional relation, not an observed run.",
                            CONDITIONS[field] + " " + TASK_LIMIT, kind)
            yield {**edge, **common, "task_field": field, "locator": reference["locator"],
                   "declaration": reference["value"], "grouping": reference["grouping"], "run_entry": reference["run_entry"]}
