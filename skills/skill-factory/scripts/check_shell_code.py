"""Measure shell constructs from the pinned shfmt typed syntax tree."""
import subprocess

from source_coverage import parse_json

BLOCKS = {"IfClause", "ForClause", "WhileClause", "CaseClause",
          "Block", "Subshell", "FuncDecl"}


def children(node):
    if isinstance(node, dict):
        return [value for key, value in node.items() if key not in {"Pos", "End"}]
    return node if isinstance(node, list) else []


def nodes(node):
    if isinstance(node, dict):
        yield node
    for child in children(node):
        yield from nodes(child)


def code_bytes(tree, text):
    data = bytearray(text.encode("utf-8"))
    for node in nodes(tree):
        if "Hash" in node and "Pos" in node and "End" in node:
            begin, end = node["Pos"]["Offset"], node["End"]["Offset"]
            data[begin:end] = b" " * (end - begin)
    return data


def line_count(data):
    return sum(bool(line.strip()) for line in data.splitlines())


def own_lines(node, data):
    begin, end = node["Pos"]["Offset"], node["End"]["Offset"]
    section = bytearray(data[begin:end])
    for child in nodes(node.get("Body", {})):
        if child.get("Type") == "FuncDecl":
            first, last = child["Pos"]["Offset"] - begin, child["End"]["Offset"] - begin
            section[first:last] = bytes(10 if byte == 10 else 32 for byte in section[first:last])
    return line_count(section)


def depth(node):
    increment = int(isinstance(node, dict) and node.get("Type") in BLOCKS)
    return increment + max((depth(child) for child in children(node)), default=0)


def check(path, text, problems):
    parsed = subprocess.run(["shfmt", "--language-dialect", "bash", "--to-json"],
                            input=text, capture_output=True, text=True, timeout=30)
    if parsed.returncode:
        problems.append(f"{path}: shell parse failed: {parsed.stderr.strip()}")
        return
    tree = parse_json(parsed.stdout)
    data = code_bytes(tree, text)
    if line_count(data) > 200:
        problems.append(f"{path}: {line_count(data)} lines of code; cap is 200")
    for node in nodes(tree):
        if node.get("Type") != "FuncDecl":
            continue
        name = node.get("Name", {}).get("Value", "function")
        size = own_lines(node, data)
        if size > 30:
            problems.append(f"{path}: {name} has {size} lines; cap is 30")
        body = node.get("Body", {}).get("Cmd", {})
        nesting = max((depth(child) for child in children(body)), default=0)
        if nesting > 3:
            problems.append(f"{path}: {name} nesting is {nesting}; cap is 3")
