#!/usr/bin/env python3
"""Run the checker's boundary, link, and graph cases in a temporary folder."""

import json
from pathlib import Path
import tempfile

from check_markdown import check, physical_lines, required_cycles
from test_structure import run_cases as structure_tests


def run(root, text, reasons=None, edges=None):
    (root / "a.md").write_text(text)
    return check(root, {"files": [p.name for p in root.glob("*.md")],
                       "core_reasons": reasons or {}, "dependencies": edges or []})


def edge(a, b, kind="required"):
    return {"from": a, "to": b, "kind": kind, "reason": "Test edge."}


def line_cases(root, passed):
    for count in (149, 150, 151, 199, 200):
        text = "line\n" * count
        result = run(root, text)
        assert bool(result["errors"]) == (count >= 150), result
        result = run(root, text, {"a.md": "An exact table must remain whole."})
        assert bool(result["errors"]) == (count >= 200), result
        assert physical_lines(text.rstrip("\n")) == count
        passed.append(f"{count}-line boundary with and without a core reason")
    assert not run(root, "line\n" * 149)["errors"]
    assert run(root, "line\n" * 150)["errors"]
    assert physical_lines("") == 0
    assert physical_lines("x\u2028y") == 1
    page = root / "a.md"
    page.write_bytes(b"a\r\nb\r\n")
    assert physical_lines(page.read_text()) == 2
    passed.append("crossing 150; final line; blank file; CRLF; Unicode separator")


def link_cases(root, passed):
    (root / "b.md").write_text("# Hello World\n\n# Hello World\n\n<a id=\"exact\"></a>\n")
    good = "[a](b.md#hello-world) [b](b.md#hello-world-1) [c](b.md#exact)\n"
    assert not run(root, good)["errors"]
    assert run(root, "[x](lost.md)\n")["errors"]
    assert run(root, "[x](b.md#lost)\n")["errors"]
    assert not run(root, "[x][r]\n\n[r]: b.md#hello-world\n")["errors"]
    assert not run(root, "[Hello](b.md#hello%2Dworld)\n")["errors"]
    assert run(root, "![x](lost.png)\n")["errors"]
    assert run(root, '<a href="lost.md">x</a>\n')["errors"]
    literal = "`[literal](lost.md)`\n\n```md\n[x](lost.md)\n```\n\n    [x](lost.md)\n"
    assert not run(root, literal)["errors"]
    assert not run(root, r"\[x](lost.md)" + "\n")["errors"]
    assert any("wiki links" in w for w in run(root, "[[Elsewhere]]\n")["needs_review"])
    passed.append("local links, references, images, encoded anchors, HTML, code exclusion, dialect warning")


def cycle_cases(root, passed):
    (root / "c.md").write_text("# C\n")
    for name, edges in (
        ("self", [edge("a.md", "a.md")]),
        ("direct", [edge("a.md", "b.md"), edge("b.md", "a.md")]),
        ("indirect", [edge("a.md", "b.md"), edge("b.md", "c.md"), edge("c.md", "a.md")]),
        ("alternate path", [edge("a.md", "b.md"), edge("./b.md", "nested/../a.md")]),
    ):
        assert run(root, "# A\n", edges=edges)["cycles"], name
        passed.append(name + " cycle")
    (root / "alias.md").symlink_to(root / "a.md")
    assert run(root, "# A\n", edges=[edge("a.md", "alias.md")])["cycles"]
    (root / "alias.md").unlink()
    passed.append("symlink cycle")
    shared = [edge("a.md", "b.md"), edge("a.md", "c.md"), edge("b.md", "c.md"),
              edge("c.md", "a.md", "navigation")]
    assert not run(root, "# A\n", edges=shared)["errors"]
    assert not required_cycles([("a", "b"), ("a", "b")])
    passed.append("shared DAG, navigation backlink, completed reread")


def external_cases(root, passed):
    assert run(root, "# A\n", edges=[edge("a.md", "missing.md")])["errors"]
    outside = root.parent / (root.name + "-external.md")
    try:
        outside.write_text("# External\n")
        edges = [edge("a.md", str(outside)), edge(str(outside), "a.md")]
        assert run(root, "# A\n", edges=edges)["cycles"]
        passed.append("external transitive cycle and missing dependency")
    finally:
        outside.unlink(missing_ok=True)


def manifest_cases(root, passed):
    result = check(root, {"files": ["a.md"], "dependencies": []})
    assert any("omits" in e for e in result["errors"])
    assert check(root, {"files": "wrong"})["errors"]
    assert check(root, {"files": [], "core_reasons": []})["errors"]
    passed.append("manifest coverage and malformed inputs")
    (root / "a.md").write_text("[x](b.md#custom)\n")
    custom = {"files": ["a.md", "b.md", "c.md"], "heading_ids": "explicit",
              "anchors": {"b.md": ["custom"]}, "entrypoints": ["a.md"]}
    assert any("unreachable" in e for e in check(root, custom)["errors"])
    custom["entrypoints"].append("c.md")
    assert not check(root, custom)["errors"]
    custom["anchors"] = {}
    assert any("missing heading" in e for e in check(root, custom)["errors"])
    assert len(check(root)["files"][0]["sha256"]) == 64
    passed.append("explicit anchor map, unreachable files, version hashes")


def deep_graph_case(root, passed):
    edges = [(str(i), str(i + 1)) for i in range(1500)]
    assert not required_cycles(edges)
    edges.append(("1500", "0"))
    cycles = required_cycles(edges)
    assert len(cycles) == 1 and len(cycles[0]) == 1502
    passed.append("deep DAG and deep cycle without recursion overflow")


def main():
    passed = []
    with tempfile.TemporaryDirectory(prefix="markdown-checks-") as directory:
        root = Path(directory)
        for cases in (line_cases, link_cases, cycle_cases, external_cases, manifest_cases, deep_graph_case):
            cases(root, passed)
    passed.extend(structure_tests())
    print(json.dumps({"status": "passed", "cases": passed}, indent=2))


if __name__ == "__main__":
    main()
