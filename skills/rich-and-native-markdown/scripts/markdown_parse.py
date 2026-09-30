"""Read CommonMark links and a limited heading-ID convention."""

from collections import Counter
from html.parser import HTMLParser
import re
import unicodedata


def physical_lines(text):
    return text.count("\n") + int(bool(text) and not text.endswith("\n"))


def heading_slug(text):
    text = text.lower()
    return "".join(c for c in text if c in "_- " or
                   unicodedata.category(c)[0] not in "PZC").replace(" ", "-")


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("id", "name" if tag == "a" else "id"):
            if attrs.get(key):
                self.ids.add(attrs[key])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def add_html(content, links, anchors):
    html = HTMLLinks()
    html.feed(content)
    links.extend(html.links)
    anchors.update(html.ids)


def add_heading(children, anchors, duplicates):
    label = "".join(t.content for t in children
                    if t.type in ("text", "code_inline", "image"))
    slug = heading_slug(label)
    suffix = duplicates[slug]
    candidate = slug if not suffix else f"{slug}-{suffix}"
    while candidate in anchors:
        suffix += 1
        candidate = f"{slug}-{suffix}"
    duplicates[slug] = suffix + 1
    anchors.add(candidate)


def add_inline(children, links, anchors, visible):
    for child in children:
        if child.type == "link_open":
            links.append(child.attrGet("href"))
            continue
        if child.type == "image":
            links.append(child.attrGet("src"))
            continue
        if child.type == "html_inline":
            add_html(child.content, links, anchors)
            continue
        if child.type == "text":
            visible.append(child.content)


def dialect_warnings(visible):
    patterns = [
        (r"\[\[", "wiki links"),
        (r"\[\^[^\]]+\]", "footnotes"),
        (r"\{[#.][^}]+\}", "attribute blocks"),
        (r"(?:^|\n)\s*:::", "directives or fenced divs"),
        (r"\{\{[<%]", "shortcodes"),
        (r"!INCLUDE|\{\s*(?:include|embed)\b", "include syntax"),
    ]
    prose = "\n".join(visible)
    return [f"Review {name} with the target renderer"
            for pattern, name in patterns if re.search(pattern, prose)]


def markdown_parts(text, parser, heading_ids="github-style"):
    tokens = parser.parse(text)
    links, anchors, visible = [], set(), []
    duplicates = Counter()
    for i, token in enumerate(tokens):
        if token.type in ("html_block", "html_inline"):
            add_html(token.content, links, anchors)
        if token.type != "inline":
            continue
        children = token.children or []
        if heading_ids == "github-style" and i and tokens[i - 1].type == "heading_open":
            add_heading(children, anchors, duplicates)
        add_inline(children, links, anchors, visible)
    return links, anchors, dialect_warnings(visible)
