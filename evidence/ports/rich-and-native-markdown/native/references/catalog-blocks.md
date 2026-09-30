# Quotes, lists, and code blocks

- Read this file when the input uses quotes, lists, nested blocks, or literal blocks.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## C09 Blockquote

- **How:** prefix quoted lines with `>`; repeat for nested quotes.
- **When:** quoting another voice.
- **Where:** a quote block.
- **Why:** distinguish quotation from the author's own claims.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C10 Bullet list

- **How:** use `- item`, `+ item`, or `* item`.
- **When:** items are peers.
- **Where:** a list block.
- **Why:** expose a set without implying order.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C11 Ordered list

- **How:** use `1. item` or `1) item`; keep the same mark after each number.
- **When:** order matters.
- **Where:** steps or ranked items.
- **Why:** show the sequence. Preserve the intended starting number.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C12 List item and nesting

- **How:** indent child blocks to the item's content column, where its text starts; use blank
  lines for loose lists, which give paragraphs more space.
- **When:** an item owns substeps or paragraphs.
- **Where:** inside that item.
- **Why:** retain parent-child meaning. Do not assume one fixed indentation works in every
  container.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C13 Indented code

- **How:** indent four spaces beyond the containing block.
- **When:** a literal block suits this source style.
- **Where:** after a block boundary.
- **Why:** keep text literal. Container indentation is additional.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C14 Fenced code

- **How:** use at least three backticks or tildes; close with the same mark and at least the
  opening length.
- **When:** showing multiline literal text.
- **Where:** a block.
- **Why:** preserve code or data. Use a longer fence than contained fences. Text after the opening fence, called the info string, may
  name a language; coloring is a renderer feature.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C15 HTML block

- **How:** use allowed block HTML with valid boundaries.
- **When:** needed meaning lacks native syntax.
- **Where:** a host that permits HTML.
- **Why:** fill that gap. HTML may suppress Markdown parsing or be removed by the host.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C16 Link definition

- **How:** write `[key]: URL "optional title"`.
- **When:** destinations repeat.
- **Where:** a definitions area in the same file.
- **Why:** give the destination one owner; the definition itself is not visible prose.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)
