# Asides, folded detail, and tabs

- Read this file when the input uses details, alerts, callouts, admonitions, tabs, or generic blocks.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E25 HTML details

- **How:** use `<details><summary>Label</summary>`, a blank-separated body, and `</details>`;
  the `open` attribute starts it expanded.
- **When:** optional detail is long.
- **Where:** after its summary.
- **Why:** reduce visible bulk. It does not reduce file lines or loaded context.

- **Sources:**

  - [GH-DETAILS](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)

## E26 GitHub-style alert

- **How:** use `> [!NOTE]\n> Text`; GitHub types are `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`.
- **When:** a brief aside must stand out.
- **Where:** beside the relevant content.
- **Why:** label its purpose. GitHub alerts must stand alone, not inside other elements; other
  hosts differ.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [GL](https://docs.gitlab.com/user/markdown/)
  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)

## E27 Obsidian callout

- **How:** use `> [!note] Title`; append `+` or `-` for initially open or closed folding.
- **When:** a named aside or optional detail helps.
- **Where:** beside its topic.
- **Why:** separate it clearly. Types include note, abstract/summary/tldr, info, todo,
  tip/hint/important, success/check/done, question/help/faq, warning/caution/attention,
  failure/fail/missing, danger/error, bug, example, quote/cite.

- **Sources:**

  - [OBS-CALL](https://obsidian.md/help/callouts)

## E28 Indented admonition

- **How:** use `!!! note "Title"` then a four-space-indented body.
- **When:** a note or warning qualifies nearby steps.
- **Where:** block flow.
- **Why:** show the aside's role. Python-Markdown/Material extension.

- **Sources:**

  - [MATERIAL-A](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)

## E29 Collapsible admonition

- **How:** use `??? note "Title"` and an indented body; `???+` starts open.
- **When:** optional detail should fold.
- **Where:** after a clear label.
- **Why:** simplify the visible page. PyMdown details; keep essential rules visible.

- **Sources:**

  - [MATERIAL-A](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)

## E30 Content tabs

- **How:** use `=== "Title"` with indented content; repeat for alternatives.
- **When:** readers choose one platform or language.
- **Where:** equivalent alternatives.
- **Why:** avoid a long serial list. PyMdown tabbed; do not hide shared required steps.

- **Sources:**

  - [MATERIAL-T](https://squidfunk.github.io/mkdocs-material/reference/content-tabs/)

## E31 Generic blocks

- **How:** use `/// type | argument\nbody\n///`, with longer fences for nesting.
- **When:** a registered block is needed.
- **Where:** block flow.
- **Why:** keep structured content readable. Built-ins: admonition, details, tab, define, html,
  caption; custom names need registration.

- **Sources:**

  - [PY-BLOCKS](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/)

## E32 Generic tab

- **How:** use `/// tab | Title` around each body.
- **When:** offering equivalent alternatives.
- **Where:** adjacent grouped blocks.
- **Why:** let the reader choose. Do not enable it with the legacy tabbed extension.

- **Sources:**

  - [PY-TAB](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/tab/)
