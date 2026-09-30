# Extended tables and figures

- Read this file when the input uses table variants, captions, figures, or image attributes.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E51 Simple table

- **How:** align text columns over dash separators.
- **When:** cells are short.
- **Where:** a comparison block.
- **Why:** keep source columns readable. One source line per row.

- **Sources:**

  - [P-TABLE](https://pandoc.org/demo/example33/8.9-tables.html)

## E52 Multiline table

- **How:** use top/bottom dash rules and blank-separated wrapped rows.
- **When:** table prose needs wrapping.
- **Where:** a table block.
- **Why:** avoid huge source lines. Pandoc; no spans in this form.

- **Sources:**

  - [P-TABLE](https://pandoc.org/demo/example33/8.9-tables.html)

## E53 Grid table

- **How:** use `+---+` borders and `| cells |`; `=` separates headers or a footer; omit interior borders for supported spans.
- **When:** cells contain blocks or spans.
- **Where:** a complex table.
- **Why:** retain relationships. Follow the current Pandoc grid grammar; fixed-width alignment matters.

- **Sources:**

  - [P-TABLE](https://pandoc.org/demo/example33/8.9-tables.html)

## E54 Table caption/attributes

- **How:** add `Table: Caption {#id .class}`, or `: Caption`, next to the table.
- **When:** the table needs context or a target.
- **Where:** before or after it.
- **Why:** state what it shows. Attributes follow the caption.

- **Sources:**

  - [P-TABLE](https://pandoc.org/demo/example33/8.9-tables.html)

## E55 kramdown table groups

- **How:** use pipe rows, dash separators for header/body groups, and `=` separators for the footer.
- **When:** retaining grouped tabular structure.
- **Where:** the table.
- **Why:** preserve group meaning. Cells are single-line; rules differ from GFM.

- **Sources:**

  - [KRAM](https://kramdown.gettalong.org/syntax.html)

## E56 MultiMarkdown 6 table variants

- **How:** use repeated trailing pipes for column spans, `[Caption]`, and blank-separated body groups.
- **When:** preserving existing MMD6 tables.
- **Where:** table blocks.
- **Why:** keep grouped relationships. MMD7's table chapter remains unfinished; do not infer identical support.

- **Sources:**

  - [MMD6-TABLE](https://fletcher.github.io/MultiMarkdown-6/syntax/tables.html)

## E57 Figure and image attributes

- **How:** place an image alone with a caption/ID and supported width, height, or alt attributes.
- **When:** a figure needs a caption or stable reference.
- **Where:** a figure block.
- **Why:** connect illustration and explanation. Pandoc implicit figures can use the image description as caption; keep a separate useful alt where needed.

- **Sources:**

  - [P-IMAGE](https://pandoc.org/demo/example33/8.17-images.html)
  - [QUARTO-B](https://quarto.org/docs/authoring/markdown-basics.html)

## E58 MMD link attributes

- **How:** use `[id]: image.png "title" width=20px height=30px`.
- **When:** preserving this source convention.
- **Where:** reference definitions.
- **Why:** retain asset metadata. Different from brace attributes.

- **Sources:**

  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
