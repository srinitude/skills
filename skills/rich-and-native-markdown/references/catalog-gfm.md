# The five formal GFM extensions

- Read this file when the input uses GFM tables, tasks, strike text, bare links, or HTML filtering.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## G01 Pipe table

- **How:** use a header row, a `---` separator per column, then rows; `:---`, `:---:`, and `---:` set alignment.
- **When:** comparing the same fields.
- **Where:** a block.
- **Why:** reveal relationships. Escape literal pipes, even inside code spans; cells hold inline content, not arbitrary blocks.

- **Sources:**

  - [GFM](https://github.github.io/gfm/)

## G02 Task item

- **How:** use `- [ ] Task` or `- [x] Done`; `X` also works.
- **When:** work has a real completion state.
- **Where:** list items.
- **Why:** show state. A checkbox does not prove work is done or guarantee interactivity.

- **Sources:**

  - [GFM](https://github.github.io/gfm/)

## G03 Strikethrough

- **How:** use `~~old text~~`; formal GFM also permits matching single tildes.
- **When:** old wording must remain visible.
- **Where:** inline.
- **Why:** show superseded text. Prefer double tildes to avoid subscript clashes.

- **Sources:**

  - [GFM](https://github.github.io/gfm/)

## G04 Extended autolink

- **How:** write a supported URL, `www` address, or email without link brackets.
- **When:** retaining a pasted address.
- **Where:** eligible text boundaries.
- **Why:** keep it clickable. Boundary and punctuation rules differ by host.

- **Sources:**

  - [GFM](https://github.github.io/gfm/)

## G05 Raw-HTML tag filter

- **How:** obey filtering of `title`, `textarea`, `style`, `xmp`, `iframe`, `noembed`, `noframes`, `script`, and `plaintext` tags.
- **When:** handling GFM HTML.
- **Where:** HTML output.
- **Why:** avoid incorrect assumptions about raw tags. This is a restriction, not an authoring feature; hosts may filter more.

- **Sources:**

  - [GFM](https://github.github.io/gfm/)
