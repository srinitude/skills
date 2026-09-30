# Note links, parsing controls, and code details

- Read this file when the input uses wiki links, embeds, comments, contents, anchors, or code attributes.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E42 Wiki link

- **How:** use `[[Note]]`, and only the target's alias/fragment form.
- **When:** linking within a note collection.
- **Where:** prose/navigation.
- **Why:** use readable local names. Obsidian uses `[[Note|label]]`; Pandoc has opposite
  pipe-order options; GitLab wiki uses `[[label|slug]]`. Python wikilinks does not imply alias
  support.

- **Sources:**

  - [OBS-LINK](https://obsidian.md/help/links)
  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
  - [PY-WIKI](https://python-markdown.github.io/extensions/wikilinks/)
  - [GL](https://docs.gitlab.com/user/markdown/)

## E43 Block ID

- **How:** add `^block-id` and link with `[[Note#^block-id]]`.
- **When:** a block is the exact target.
- **Where:** its supported boundary.
- **Why:** link more precisely than a heading. Use letters, numbers, and dashes; distinct from
  kramdown's lone `^`.

- **Sources:**

  - [OBS-LINK](https://obsidian.md/help/links)

## E44 Note/media embed

- **How:** use `![[Note]]`, `![[Note#Heading]]`, `![[Note#^id]]`, or `![[file.ext]]`.
- **When:** the content itself is needed.
- **Where:** the point of use.
- **Why:** reuse source content. Transclusion creates a dependency and may load too much.

- **Sources:**

  - [OBS-EMBED](https://obsidian.md/help/embeds)

## E45 Source-only comment

- **How:** use the supported `<!--...-->`, `%%...%%`, MyST `%` line, kramdown
  `{::comment}`...`{:/comment}`, or MDX `{/*...*/}`.
- **When:** an editor needs a note.
- **Where:** source positions that parse it.
- **Why:** keep editorial notes separate. Comments are not secret storage and must not hide
  required reader context.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [OBS-SYNTAX](https://obsidian.md/help/syntax)
  - [MYST-TYPE](https://myst-parser.readthedocs.io/en/stable/syntax/typography.html)
  - [KRAM](https://kramdown.gettalong.org/syntax.html)
  - [MDX](https://mdxjs.com/docs/what-is-mdx/)

## E46 Parser control tags

- **How:** use `{::nomarkdown}`...`{:/nomarkdown}` or `{::options key="value" /}`; a lone `^` in
  column one ends a block.
- **When:** preserving required parsing behavior.
- **Where:** valid kramdown positions.
- **Why:** prevent blocks or literal content being misread. These controls are not portable
  Markdown.

- **Sources:**

  - [KRAM](https://kramdown.gettalong.org/syntax.html)

## E47 Generated contents

- **How:** use Python `[TOC]`, GitLab `[TOC]`/`[[_TOC_]]`, or MMD7 `{{TOC}}` at the desired
  position.
- **When:** headings need navigation.
- **Where:** near the start or a useful junction.
- **Why:** keep links tied to headings. GitHub's automatic outline is interface behavior, not
  `[TOC]` syntax.

- **Sources:**

  - [PY-TOC](https://python-markdown.github.io/extensions/toc/)
  - [GL](https://docs.gitlab.com/user/markdown/)
  - [MMD7](https://fletcher.github.io/MultiMarkdown-7/docs/user.html)

## E48 Heading references and anchors

- **How:** link to a verified `#slug` (a heading ID) or explicit ID; Pandoc also resolves `[Heading]`,
  `[Heading][]`, and `[label][Heading]`.
- **When:** directing readers to a section.
- **Where:** navigation or a relevant sentence.
- **Why:** avoid searching. Slug rules and duplicate suffixes vary; explicit references can
  override implicit ones. GitHub custom anchors may use `<a name="id"></a>`.

- **Sources:**

  - [P-HEAD](https://pandoc.org/demo/example33/8.3-headings.html)
  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

## E49 Code attributes

- **How:** add supported language, `{#id .class}`, title, line numbers, or highlighted-line
  options to the fence.
- **When:** code needs explanation or reference.
- **Where:** its opening fence.
- **Why:** connect discussion to exact code. Pandoc example: `{#sample .python .numberLines
  startFrom="10"}`; options differ in SuperFences.

- **Sources:**

  - [P-CODE](https://pandoc.org/demo/example33/8.5-verbatim-code-blocks.html)
  - [SUPERFENCES](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/)

## E50 Inline code attributes/highlighting

- **How:** append supported attributes to a code span; PyMdown uses a span starting `#!language`
  or `:::language` plus a space.
- **When:** a short fragment needs metadata or syntax coloring.
- **Where:** inline code.
- **Why:** add context without a whole block. No execution follows from highlighting.

- **Sources:**

  - [P-INLINE](https://pandoc.org/demo/example33/8.12-inline-formatting.html)
  - [INLINEHILITE](https://facelessuser.github.io/pymdown-extensions/extensions/inlinehilite/)
