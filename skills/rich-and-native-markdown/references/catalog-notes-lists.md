# Notes, terms, and list forms

- Read this file when the input uses footnotes, term definitions, abbreviations, or extended lists.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E01 Footnote

- **How:** use `text[^n]` and `[^n]: Note`; indent continued note blocks.
- **When:** support would interrupt the main thought.
- **Where:** marker by the claim, definition outside core prose.
- **Why:** preserve reading flow. Not core CommonMark; GitHub wikis do not support it.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [P-NOTES](https://pandoc.org/demo/example33/8.19-footnotes.html)
  - [EXTRA](https://michelf.ca/projects/php-markdown/extra/)

## E02 Inline note

- **How:** use `text^[Short note]`.
- **When:** a short note needs no separate key.
- **Where:** inline.
- **Why:** keep its source nearby. Pandoc only; no multiparagraph note.

- **Sources:**

  - [P-NOTES](https://pandoc.org/demo/example33/8.19-footnotes.html)

## E03 Definition list

- **How:** write `Term` followed by `: Definition`; Pandoc also permits `~` as marker.
- **When:** terms need paired meanings.
- **Where:** a glossary or reference section.
- **Why:** pair each term with its meaning. Preserve each dialect's blank lines and indentation.

- **Sources:**

  - [EXTRA](https://michelf.ca/projects/php-markdown/extra/)
  - [P-LISTS](https://pandoc.org/demo/example33/8.7-lists.html)

## E04 Abbreviation

- **How:** define `*[API]: Application programming interface`, then use API.
- **When:** a short form repeats.
- **Where:** definitions and prose.
- **Why:** make its expansion available. PHP Extra, kramdown, and Python-Markdown `abbr` support this family; Pandoc's compatibility extension skips definitions rather than making the full name available.

- **Sources:**

  - [EXTRA](https://michelf.ca/projects/php-markdown/extra/)

## E05 Fancy list

- **How:** use supported `a.`, `A.`, `i.`, `(i)`, `1)`, or `#.` markers.
- **When:** a required label style matters.
- **Where:** ordered lists.
- **Why:** preserve sequence labels. Pandoc uppercase letters followed by a period need two spaces; extension support varies.

- **Sources:**

  - [P-LISTS](https://pandoc.org/demo/example33/8.7-lists.html)
  - [PYMDOWN](https://facelessuser.github.io/pymdown-extensions/)

## E06 Numbered example list

- **How:** use `(@id) Example`, refer with `(@id)`, and reset with `(1@id)`.
- **When:** examples continue across prose.
- **Where:** teaching or research text.
- **Why:** keep stable numbered references. Pandoc syntax.

- **Sources:**

  - [P-LISTS](https://pandoc.org/demo/example33/8.7-lists.html)

## E07 Line block

- **How:** start each line with `|` and a space; indent continuation lines.
- **When:** line layout carries meaning.
- **Where:** verse or addresses.
- **Why:** preserve lines and leading spaces while allowing inline markup. Pandoc; no nested block structures.

- **Sources:**

  - [P-LINE](https://pandoc.org/demo/example33/8.6-line-blocks.html)
