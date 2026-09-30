# Text transforms and theme features

- Read this file when the input uses typography, progress, annotations, cards, quote extensions, or MMD raw content.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E65 Typographic replacements

- **How:** enable the required smart quote, dash, ellipsis, or symbol transform.
- **When:** publication style calls for it.
- **Where:** editable prose only.
- **Why:** provide that typography. Settings such as `smart`, `old_dashes`, `smarty`, `smartquotes`,
  `replacements`, and `SmartSymbols` are transformations, not new semantic structures. Protect exact
  text.

- **Sources:**

  - [P-SMART](https://pandoc.org/demo/example33/7.1-typography.html)
  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)
  - [PYMDOWN](https://facelessuser.github.io/pymdown-extensions/)

## E66 Progress indicator

- **How:** use `[=50% "Half done"]` or a supported fraction.
- **When:** a measured status helps.
- **Where:** a status summary.
- **Why:** show amount at a glance. PyMdown with styling; never invent progress.

- **Sources:**

  - [PROGRESS](https://facelessuser.github.io/pymdown-extensions/extensions/progressbar/)

## E67 Annotations

- **How:** use `(1)` in an `.annotate` block and its numbered notes.
- **When:** short explanations belong to a local phrase/code point.
- **Where:** supported Material content.
- **Why:** place detail near its subject. Theme/extension behavior; essential content still
  needs a visible route.

- **Sources:**

  - [MATERIAL-N](https://squidfunk.github.io/mkdocs-material/reference/annotations/)

## E68 Card/grid layout

- **How:** wrap a suitable list in `<div class="grid cards" markdown>`...`</div>`.
- **When:** presenting peer navigation choices.
- **Where:** a landing/reference section.
- **Why:** group choices. This is an HTML/CSS theme recipe, not new Markdown grammar; keep
  sensible narrow-screen order.

- **Sources:**

  - [MATERIAL-G](https://squidfunk.github.io/mkdocs-material/reference/grids/)

## E69 PyMdown bracket span

- **How:** use `[text]{.class}` with `bracketspan` and `attr_list` enabled; `{}` makes an
  unadorned span.
- **When:** an inline group needs attributes.
- **Where:** prose.
- **Why:** identify the right text. Added in 12.0; link references take precedence.

- **Sources:**

  - [PY-SPAN](https://facelessuser.github.io/pymdown-extensions/extensions/bracketspan/)

## E70 PyMdown quote callout

- **How:** enable callouts and use `> [!note]`, an optional title, and `+` or `-` folding;
  pipe-separated classes and nesting are supported.
- **When:** a typed aside is useful.
- **Where:** a blockquote with explicit `>` on each owned line.
- **Why:** keep boundaries clear. This extends E26/E27; GitHub does not inherit these extra
  forms.

- **Sources:**

  - [PY-QUOTE](https://facelessuser.github.io/pymdown-extensions/extensions/quotes/)

## E71 MMD6 raw wildcard

- **How:** mark a code span/block with `{=*}`.
- **When:** exact raw content must pass to every output.
- **Where:** inline/block.
- **Why:** retain uninterpreted source. This wildcard is MMD6-specific; do not infer MMD7 output
  support.

- **Sources:**

  - [MMD6-RAW](https://fletcher.github.io/MultiMarkdown-6/syntax/raw.html)
