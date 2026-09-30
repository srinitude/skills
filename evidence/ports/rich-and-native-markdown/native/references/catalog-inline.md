# Inline text, links, and images

- Read this file when the input uses inline code, emphasis, links, images, or escaping.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## C17 Inline code

- **How:** use matching backtick runs, longer when needed around literal backticks.
- **When:** naming exact tokens.
- **Where:** a sentence.
- **Why:** distinguish code, paths, and commands. Code spans can normalize whitespace; use a
  block for exact line layout.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C18 Emphasis

- **How:** use `*text*` or `_text_`.
- **When:** a word needs stress.
- **Where:** inline.
- **Why:** express emphasis.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C19 Strong emphasis

- **How:** use `**text**` or `__text__`.
- **When:** a short key point needs stronger stress.
- **Where:** inline.
- **Why:** mark importance. `***text***` and mixed nesting combine existing forms.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C20 Inline link

- **How:** use `[clear label](destination "optional title")`.
- **When:** a source or next destination helps.
- **Where:** beside its claim or action.
- **Why:** make the connection clear. Absolute, relative, fragment, and mailto destinations are
  uses of this form; do not nest links.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C21 Reference link

- A link definition maps a key to a destination in the same file: `[key]: URL "optional title"`. C16 names that form.

- **How:** use `[label][key]`, `[key][]`, or `[key]` with C16.
- **When:** long or repeated URLs clutter prose.
- **Where:** inline.
- **Why:** keep prose and destinations easy to maintain.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C22 Image

- **How:** use `![alt text](path)`, or `![alt][key]`, `![key][]`, `![key]` with a definition.
- **When:** an image adds meaning.
- **Where:** near its discussion.
- **Why:** give visual information a text equivalent. `[![alt](image)](target)` combines image
  and link.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C23 Angle autolink

- **How:** use `<https://example.com>` or `<reader@example.com>`.
- **When:** the address itself matters.
- **Where:** inline.
- **Why:** make that address actionable.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C24 Inline HTML

- **How:** use permitted inline tags.
- **When:** required inline meaning has no native form.
- **Where:** supported prose.
- **Why:** retain that meaning. Respect the host's HTML filter.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C25 Escape

- **How:** put a backslash before active ASCII punctuation.
- **When:** syntax must appear literally.
- **Where:** normal parsed text.
- **Why:** prevent unwanted formatting. Code, autolinks, and raw HTML have different escape
  rules.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)

## C26 Character reference

- **How:** use a named entity such as `&amp;` or numeric forms such as `&#35;` and
  `&#x23;`.
- **When:** a literal character needs that spelling.
- **Where:** supported text contexts.
- **Why:** disambiguate the character; code shows these forms literally.

- **Sources:**

  - [CM](https://spec.commonmark.org/0.31.2/)
  - [ORIG](https://daringfireball.net/projects/markdown/syntax)
