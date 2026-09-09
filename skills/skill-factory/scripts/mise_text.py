"""Edit complete TOML fields while retaining the other source text."""
import json
import tomllib


def units(text):
    pending = ""
    for line in text.splitlines(keepends=True):
        pending += line
        try:
            value = tomllib.loads(pending)
        except tomllib.TOMLDecodeError:
            continue
        yield pending, value
        pending = ""
    if pending:
        tomllib.loads(pending)


def field(text, key, replacement):
    output, found, top = [], False, True
    for raw, value in units(text):
        if raw.lstrip().startswith("["):
            top = False
        if top and key in value:
            found = True
            if replacement is not None:
                output.append(f"{key} = {replacement}\n")
        else:
            output.append(raw)
    if not found and replacement is not None:
        output.insert(0, f"{key} = {replacement}\n")
    return "".join(output).rstrip()


def value(item):
    if isinstance(item, dict):
        return "{" + ", ".join(f"{json.dumps(k)} = {value(v)}" for k, v in item.items()) + "}"
    if isinstance(item, list):
        return "[" + ", ".join(map(value, item)) + "]"
    if isinstance(item, (str, bool, int, float)):
        return json.dumps(item, allow_nan=False)
    raise ValueError("TOML dependency needs an explicit supported value")


def sections(text):
    config = tomllib.loads(text)
    preamble, blocks, current, body = [], [], None, []
    for raw, item in units(text):
        tasks = item.get("tasks", {})
        if raw.lstrip().startswith("[") and len(tasks) == 1 and next(iter(tasks.values())) == {}:
            if current is not None:
                blocks.append((current, "".join(body).strip("\n")))
            current, body = next(iter(tasks)), []
        elif current is None:
            preamble.append(raw)
        else:
            body.append(raw)
    if current is not None:
        blocks.append((current, "".join(body).strip("\n")))
    if {name for name, _ in blocks} != set(config.get("tasks", {})):
        raise ValueError("task declarations need explicit table migration before standardization")
    return "".join(preamble).rstrip(), blocks


def table_defaults(text, name, defaults):
    existing = tomllib.loads(text).get(name, {})
    if not isinstance(existing, dict):
        raise ValueError(f"{name} needs an explicit table migration")
    missing = {key: item for key, item in defaults.items() if key not in existing}
    if not missing:
        return text
    output, inserted = [], False
    for raw, parsed in units(text):
        output.append(raw)
        if raw.lstrip().startswith("[") and parsed.get(name) == {}:
            output.extend(f"{json.dumps(key)} = {value(item)}\n" for key, item in missing.items())
            inserted = True
    if not inserted:
        output.insert(0, "".join(f"{json.dumps(name)}.{json.dumps(key)} = {value(item)}\n"
                                 for key, item in missing.items()))
    result = "".join(output)
    try:
        tomllib.loads(result)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"{name} needs an explicit table migration preserving existing fields") from error
    return result
