# Attributes, containers, and raw content

- Read this file when the input uses attributes, spans, containers, raw output, or TeX macros.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E08 Heading and element attributes

- **How:** append supported `{#id .class key="value"}`; Pandoc heading `{-}` means `.unnumbered`, and `.unlisted` can omit a heading from contents.
- **When:** a stable anchor or known metadata is needed.
- **Where:** the supported owner element.
- **Why:** attach data precisely. Attribute support and placement are dialect-specific.

- **Sources:**

  - [P-HEAD](https://pandoc.org/demo/example33/8.3-headings.html)
  - [P-SPANS](https://pandoc.org/demo/example33/8.18-divs-and-spans.html)
  - [EXTRA](https://michelf.ca/projects/php-markdown/extra/)

## E09 kramdown attribute lists

- **How:** attach `{: #id .class}`; define `{:name: .class}` and reuse `{: name}`.
- **When:** several elements share attributes.
- **Where:** after each owner, with a reusable definition.
- **Why:** avoid drift. IAL means inline attribute list; ALD means attribute list definition. These forms differ from E08.

- **Sources:**

  - [KRAM](https://kramdown.gettalong.org/syntax.html)

## E10 Bracketed span

- **How:** use `[text]{#id .class key="value"}`.
- **When:** one phrase needs metadata.
- **Where:** inline.
- **Why:** mark exactly that phrase. Classes such as `.underline`, `.smallcaps`, and `.mark` need support from the tool that writes the output; styling is not a new core primitive.

- **Sources:**

  - [P-SPANS](https://pandoc.org/demo/example33/8.18-divs-and-spans.html)
  - [QUARTO-B](https://quarto.org/docs/authoring/markdown-basics.html)

## E11 Fenced Div

- **How:** use `::: {.class}\nblocks\n:::`; nest with clear fences.
- **When:** related blocks need a container.
- **Where:** block flow.
- **Why:** group them without raw HTML. Opening attributes are required in Pandoc.

- **Sources:**

  - [P-SPANS](https://pandoc.org/demo/example33/8.18-divs-and-spans.html)
  - [QUARTO-B](https://quarto.org/docs/authoring/markdown-basics.html)

## E12 Markdown inside HTML

- **How:** use a supported wrapper such as `<div markdown="1">`, with matching close and valid spacing.
- **When:** HTML wrapping is needed.
- **Where:** an allowed HTML region.
- **Why:** retain editable inner Markdown. Pandoc defaults differ; `markdown="block"` is dialect-specific. Obsidian does not parse Markdown inside HTML.

- **Sources:**

  - [EXTRA](https://michelf.ca/projects/php-markdown/extra/)
  - [P-RAW](https://pandoc.org/demo/example33/8.14-raw-html.html)

## E13 Native HTML containers

- **How:** use `div`/`span` markup with `native_divs`/`native_spans` enabled.
- **When:** groups must survive conversion.
- **Where:** block/inline positions.
- **Why:** keep groups in the parsed document. This differs from passing raw HTML through unchanged.

- **Sources:**

  - [P-RAW](https://pandoc.org/demo/example33/8.14-raw-html.html)

## E14 Raw output

- **How:** mark a code span or fence with `{=html}`, `{=latex}`, or the required format.
- **When:** exact target markup must pass through.
- **Where:** inline or block.
- **Why:** prevent Markdown parsing. Do not combine raw-format attributes with ordinary attributes; unsupported writers may omit it.

- **Sources:**

  - [P-RAW](https://pandoc.org/demo/example33/8.14-raw-html.html)

## E15 Raw TeX and macros

- **How:** retain TeX commands/environments and definitions such as `\newcommand{\vect}[1]{\mathbf{#1}}`.
- **When:** required publication notation uses them.
- **Where:** before use or at the intended insertion.
- **Why:** keep notation consistent. Output support varies; raw-attribute content has different expansion rules.

- **Sources:**

  - [P-RAW](https://pandoc.org/demo/example33/8.14-raw-html.html)
  - [P-MACROS](https://pandoc.org/demo/example33/8.15-latex-macros.html)
