#!/usr/bin/env python3
"""Exercise optional heading and paragraph checks without judging meaning."""

import json
from pathlib import Path
import tempfile

from check_markdown import check


def run(root, text, structure=None):
    (root / "guide.md").write_text(text)
    return check(root, {"files": ["guide.md"], "entrypoints": ["guide.md"],
                        "structure": {} if structure is None else structure})


def heading_cases(root):
    for text in ("# Guide\n", "## Rules\n- Keep names.\n",
                 "# Guide\n# Other\n## Rules\n", "# Guide\n### Rules\n",
                 "# Guide\n## Rules\n#### Jump\n", "# \n## Rules\n",
                 "# <span></span>\n## Rules\n"):
        assert run(root, text)["errors"], text
    valid = "# Guide\n- Follow this guide.\n## Rules\n- Keep names.\n### Details\n- Keep dates.\n## Steps\n1. Read.\n"
    assert not run(root, valid)["errors"]
    assert not run(root, "Guide\n=====\n\n- Follow this guide.\n\nRules\n-----\n\n- Keep names.\n### Details\n- Keep dates.\n")["errors"]
    # Generic mode still permits documents without this project's house style.
    (root / "guide.md").write_text("A valid CommonMark paragraph.\n")
    assert not check(root)["errors"]


def paragraph_cases(root):
    text = "# Guide\n- Follow this guide.\n## Reason\n- Keep its cause.\n### Explanation\nA linked idea needs a full sentence.\n"
    record = {"line": 6, "text": "A linked idea needs a full sentence.",
              "reason": "This explanation is a single connected cause and result."}
    structure = {"paragraphs": {"guide.md": [record]}}
    assert run(root, text)["errors"]
    result = run(root, text, structure)
    assert not result["errors"] and any("paragraph reason" in r for r in result["needs_review"])
    assert run(root, text.replace("linked idea", "different idea"), structure)["errors"]
    assert run(root, text + "\nAn unjustified second paragraph.\n", structure)["errors"]
    assert run(root, text.replace("A linked", "- A linked"), structure)["errors"]
    assert not run(root, "# Guide\n- Follow this guide.\n## Rules\n- One rule.\n\n  Its same-list explanation.\n### Detail\n- Keep names.\n")["errors"]
    assert not run(root, "# Guide\n- Follow this guide.\n## Diagram\n![Two steps](https://example.com/diagram.png)\n### Detail\n- Keep names.\n")["errors"]
    frontmatter = "---\nname: example\ndescription: One\u2028physical line.\n---\n"
    shifted = {"paragraphs": {"guide.md": [dict(record, line=10)]}}
    assert not run(root, frontmatter + text, shifted)["errors"]


def literal_cases(root):
    text = "---\nname: example\ndescription: Keep this metadata.\n---\n" + """# Guide
- Read these examples.
## Examples
- Keep their exact text.
### Literal forms

```markdown
# A literal title
### A literal skipped heading
This is exact prose.
```

    # An indented code title
    Exact code.

> # An exact quoted heading
>
> Exact quoted prose.

| Name | Value |
| --- | --- |
| Test | 3 |

<div>Review this HTML separately.</div>
"""
    result = run(root, text)
    assert not result["errors"], result
    assert any("raw HTML" in r for r in result["needs_review"])


def malformed_cases(root):
    text = "# Guide\n- Follow this guide.\n## Rules\n- One rule.\n### Detail\n- Keep names.\n"
    for value in (True, [], {"unknown": 1}, {"paragraphs": []},
                  {"paragraphs": {"missing.md": []}}, {"paragraphs": {"guide.md": {}}},
                  {"paragraphs": {"guide.md": [{"line": True, "text": "x", "reason": "y"}]}},
                  {"paragraphs": {"guide.md": [{"line": 5, "text": "x", "reason": ""}]}}):
        assert run(root, text, value)["errors"], value


def content_cases(root):
    prefix = "# Guide\n- Keep exact names.\n## Rules\n- Keep dates.\n"
    for gap in ("", "\n", "<!-- private -->\n", "---\n", "-\n", "1.\n",
                '<a id="anchor"></a>\n', "![ ](https://example.com/x.png)\n"):
        result = run(root, prefix + "### Details\n" + gap)
        assert any("needs non-heading content" in e for e in result["errors"]), gap
    for body in ("- Keep units.\n", "1. Read first.\n", "```md\n# literal\n```\n"):
        assert not run(root, prefix + "### Details\n" + body)["errors"], body
    assert run(root, "# Guide\n## Rules\n- Keep names.\n### Details\n- Keep dates.\n")["errors"]
    assert run(root, prefix + "### One\n### Two\n- Keep units.\n")["errors"]
    assert run(root, prefix + "### One\n- Keep units.\n### Two\n")["errors"]
    assert run(root, prefix + "- #### Nested jump\n  - Keep units.\n")["errors"]
    assert run(root, prefix + "- ### Nested details\n  - Keep units.\n")["errors"]
    nested = prefix + "### Details\n- Keep dates.\n- #### Nested detail\n  - Keep units.\n"
    assert not run(root, nested)["errors"]
    assert run(root, nested.replace("#### Nested", "# Nested"))["errors"]
    html = run(root, prefix + "### Details\n- Keep units.\n<h4>Raw</h4>\n")
    assert any("raw HTML" in r for r in html["needs_review"])


def ancestor_cases(root):
    def document(levels):
        return "".join("#" * level + f" Section {i}\n- Keep value {i}.\n"
                       for i, level in enumerate(levels))
    for levels in ((1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 2, 3), (1, 2, 3, 3, 2)):
        assert not run(root, document(levels))["errors"], levels
    for levels in ((1, 2), (1, 3), (1, 2, 3, 5), (1, 2, 3, 4, 6), (1, 2, 3, 2, 4)):
        assert run(root, document(levels))["errors"], levels


def run_cases():
    with tempfile.TemporaryDirectory(prefix="markdown-structure-") as directory:
        root = Path(directory)
        for cases in (heading_cases, paragraph_cases, literal_cases, malformed_cases,
                      content_cases, ancestor_cases):
            cases(root)
    return [
        "H1/H2/H3 minimum, active ancestors through H6, labels, and Setext headings",
        "heading gaps: adjacent, blank, comment, empty items, anchors, EOF; meaningful blocks",
        "generic-mode compatibility; justified, stale, missing, and list paragraphs",
        "frontmatter, fenced and indented code, quotes, tables, raw HTML review",
        "invalid structure options and exception records"]


if __name__ == "__main__":
    print(json.dumps({"status": "passed", "cases": run_cases()}, indent=2))
