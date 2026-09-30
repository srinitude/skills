# Quarto and Markdoc

- Read this file when the input uses Quarto callouts, cross-references, cells, or Markdoc tags and partials.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## A18 Quarto callout

- **How:** use `::: {.callout-note}\nbody\n:::`; types include note, tip, warning, caution,
  important.
- **When:** a typed aside helps.
- **Where:** its relevant section.
- **Why:** show purpose. `collapse=true`/`collapse=false` and appearance depend on output.

- **Sources:**

  - [QUARTO-C](https://quarto.org/docs/authoring/callouts.html)

## A19 Quarto cross-reference

- **How:** assign `#fig-id`, `#tbl-id`, `#eq-id`, or `#sec-id` as appropriate and refer with `@fig-id`,
  etc.
- **When:** referring to a numbered object.
- **Where:** object and referring sentence.
- **Why:** keep references tied to content. Use proper captions and reserved prefixes.

- **Sources:**

  - [QUARTO-X](https://quarto.org/docs/authoring/cross-references.html)

## A20 Executable cell

- **How:** use a registered `{python}` or `{r}` fence and supported `#|` options.
- **When:** an authorized computation belongs to a reproducible document.
- **Where:** a cell block.
- **Why:** connect source and output. This differs from highlighted literal code; rewriting
  alone grants no permission to execute it.

- **Sources:**

  - [QUARTO-B](https://quarto.org/docs/authoring/markdown-basics.html)

## A21 Markdoc tag

- **How:** use `{% name key="value" %}body{% /name %}`, or `{% name /%}`.
- **When:** a defined block or inline element is needed.
- **Where:** valid tag positions.
- **Why:** give content defined behavior. Built-in tags include if, else, table, partial; custom
  names require definitions.

- **Sources:**

  - [MARKDOC-T](https://markdoc.dev/docs/tags)

## A22 Markdoc annotation

- **How:** attach `{% #id %}` or `{% key="value" %}` to the supported node.
- **When:** a node needs attributes.
- **Where:** immediately at its owner.
- **Why:** attach data precisely. Quote strings with double quotes.

- **Sources:**

  - [MARKDOC-A](https://markdoc.dev/docs/attributes)

## A23 Markdoc variable/function

- **How:** use `{% $page.title %}` or `{% default($title, "Untitled") %}`.
- **When:** supplied data or a registered expression is needed.
- **Where:** supported expression positions.
- **Why:** reuse data. Built-ins include equals, and, or, not, default, debug; variables cannot
  simply be inserted into a Markdown link destination.

- **Sources:**

  - [MARKDOC-V](https://markdoc.dev/docs/variables)
  - [MARKDOC-F](https://markdoc.dev/docs/functions)

## A24 Markdoc condition

- **How:** use `{% if $show %}`...`{% else /%}`...`{% /if %}`.
- **When:** readers should receive the applicable branch.
- **Where:** around conditional content.
- **Why:** select relevant text. Keep required shared rules outside optional branches.

- **Sources:**

  - [MARKDOC-T](https://markdoc.dev/docs/tags)

## A25 Markdoc table

- **How:** use `{% table %}\n* Name\n* Value\n---\n* A\n* 1\n{% /table %}`; `---`
  separates rows, and cells may carry `{% colspan=2 %}` or `{% align="right" %}`.
- **When:** a structured table needs rich cells.
- **Where:** a table block.
- **Why:** keep cell content grouped. This differs from pipe-table grammar.

- **Sources:**

  - [MARKDOC-T](https://markdoc.dev/docs/tags)

## A26 Markdoc partial

- **How:** use `{% partial file="part.md" /%}` with a registered partial.
- **When:** reusing shared content.
- **Where:** the insertion point.
- **Why:** preserve one owner. Count the partial in dependency and context checks.

- **Sources:**

  - [MARKDOC-P](https://markdoc.dev/docs/partials)
