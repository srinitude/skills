# Text and headings

- Read this file when the input uses paragraphs, line breaks, headings, or section breaks.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## C01 Plain text

- **How:** write ordinary words.
- **When:** no special role applies.
- **Where:** where the target allows text.
- **Why:** keep prose easy to read.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C02 Paragraph

- **How:** separate related groups of sentences with a blank line.
- **When:** developing one idea.
- **Where:** normal document flow.
- **Why:** keep reasoning connected.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C03 Blank line

- **How:** use an empty source line.
- **When:** separating blocks or paragraphs.
- **Where:** between blocks; inside loose lists when needed.
- **Why:** make boundaries clear. This is a separator, not a visible content object.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C04 Soft break

- **How:** use one ordinary newline within a paragraph.
- **When:** wrapping source text.
- **Where:** prose.
- **Why:** keep source lines readable without demanding a visible break.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C05 Hard break

- **How:** end a line with two spaces or a backslash before the newline.
- **When:** the line boundary matters.
- **Where:** verse, addresses, or similar text.
- **Why:** preserve intended lines.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C06 ATX heading

- **How:** use one to six `#` marks, a space, then the title.
- **When:** naming a section.
- **Where:** the start of that section.
- **Why:** show how sections fit together; choose levels by meaning.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C07 Setext heading

- **How:** put `===` or `---` below the title.
- **When:** retaining that heading style.
- **Where:** level 1 or 2 headings only.
- **Why:** preserve a readable source convention.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C08 Thematic break

- **How:** put at least three matching `*`, `-`, or `_` marks on a separate line.
- **When:** a real topic or scene break occurs.
- **Where:** between blocks.
- **Why:** mark that break. Separate `---` from preceding prose to avoid a Setext heading.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)
