# Quotes, placeholders, and shared content

- Read this file when the input uses GitLab quotes or placeholders, literate Haskell, snippets, includes, or shortcodes.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## A10 GitLab multiline quote

- **How:** enclose the quote between `>>>` lines.
- **When:** a long pasted quote needs blocks.
- **Where:** quote flow.
- **Why:** avoid prefixing each line. An alert marker can follow the opening fence.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A11 GitLab placeholder

- **How:** use an enabled `%{PLACEHOLDER}`, such as `%{project_name}`.
- **When:** a documented changing project value belongs in prose.
- **Where:** supported text.
- **Why:** reduce stale copied values. Experimental and off by default in the inspected docs;
  never assume it is active.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A12 Literate Haskell

- **How:** enable `+lhs`; use `>` code lines or code environments as documented.
- **When:** editing real literate Haskell.
- **Where:** its mixed code/prose file.
- **Why:** retain executable source structure. This changes heading/quote parsing and is not an
  ordinary blockquote use.

- **Sources:**

  - [P-LHS](https://pandoc.org/demo/example33/7.5-literate-haskell-support.html)

## A13 PyMdown snippet

- **How:** use `--8<-- "file.md"` or paired `--8<--` lines around filenames, with supported
  section/line selectors.
- **When:** reusing an exact excerpt.
- **Where:** the insertion point.
- **Why:** keep one text owner. Preprocessing also runs inside code fences; escape
  demonstrations as documented and check dependencies.

- **Sources:**

  - [SNIPPETS](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)

## A14 GitLab include

- **How:** use `::include{file=chapter.md}` at line start.
- **When:** inserting approved shared text.
- **Where:** supported files/wiki pages.
- **Why:** reuse a source. Nested includes are ignored; recursive authoring disclosure must not
  depend on recursive GitLab expansion.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A15 MMD6 transclusion

- **How:** use `{{file.md}}` or output-specific `{{file.*}}`.
- **When:** combining shared sources.
- **Where:** the insertion point.
- **Why:** avoid copies. Resolve the configured path base and cycles; MMD7's syntax chapter is
  unfinished.

- **Sources:**

  - [MMD6-INCLUDE](https://fletcher.github.io/MultiMarkdown-6/syntax/transclusion.html)

## A16 Quarto shortcode

- **How:** use `{{< name args >}}`.
- **When:** a built-in or registered function is required.
- **Where:** its supported inline/block position.
- **Why:** express a document operation clearly. Built-ins: version, var, meta, env, pagebreak,
  kbd, video, include, embed, placeholder, lipsum, contents. Names/arguments are extension data,
  not separate universal primitives.

- **Sources:**

  - [QUARTO-S](https://quarto.org/docs/authoring/shortcodes.html)

## A17 Quarto include/embed

- **How:** put `{{< include _part.qmd >}}` on its own blank-separated line; use documented embed
  for approved computed content.
- **When:** a shared source/output belongs here.
- **Where:** the insertion point.
- **Why:** retain ownership. Included paths resolve from the main document; metadata and
  executable cells can affect the whole document.

- **Sources:**

  - [QUARTO-I](https://quarto.org/docs/authoring/includes.html)
  - [QUARTO-S](https://quarto.org/docs/authoring/shortcodes.html)
