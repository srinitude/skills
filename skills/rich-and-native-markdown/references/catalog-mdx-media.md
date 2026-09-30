# MDX, structured records, and media

- Read this file when the input uses MDX, GitLab record tables or media, source embeds, or Quarto page breaks and media.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## A27 MDX JSX

- **How:** use `<Component prop="value" />`, paired elements, or `<>` fragments.
- **When:** an authorized defined component is needed.
- **Where:** MDX.
- **Why:** combine prose and reusable UI. JSX replaces raw HTML; component definitions must exist.

- **Sources:**

  - [MDX](https://mdxjs.com/docs/what-is-mdx/)

## A28 MDX expression

- **How:** use `{expression}`; comments use `{/*...*/}`.
- **When:** a computed value is needed.
- **Where:** supported inline/block positions.
- **Why:** connect text and data. This is JavaScript syntax; do not execute untrusted input merely to format it.

- **Sources:**

  - [MDX](https://mdxjs.com/docs/what-is-mdx/)

## A29 MDX module statement

- **How:** retain valid `import`/`export` statements.
- **When:** content depends on modules or exported values.
- **Where:** module-level MDX.
- **Why:** declare those dependencies. MDX lacks ordinary indented code blocks and angle autolinks; do not apply CommonMark blindly.

- **Sources:**

  - [MDX](https://mdxjs.com/docs/what-is-mdx/)

## A30 GitLab JSON table

- **How:** use a `json:table` fence with a valid object such as `{"items":[{"name":"A"}]}`; fields and caption are optional.
- **When:** supplied records need a table.
- **Where:** a supported block.
- **Why:** keep structured data intact. This is an embedded schema; `markdown:true` affects supported cells/caption, not fields.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A31 GitLab audio/video

- **How:** use `![description](clip.mp4)` or `![description](clip.mp3)`; supported dimensions may follow in braces.
- **When:** supplied media carries the content.
- **Where:** its point of discussion.
- **Why:** make it directly usable. Host behavior on image syntax; provide needed captions/transcripts and preserve actual format support.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A32 Code permalink embed

- **How:** put a same-instance file permalink with a full commit SHA and `#Lstart-end` alone in a paragraph.
- **When:** exact source lines are evidence.
- **Where:** beside the claim.
- **Why:** bind the excerpt to a revision. Host limits and reader access apply; a link alone is not proof everyone sees the embed.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)

## A33 Quarto page break

- **How:** put `{{< pagebreak >}}` on its own line.
- **When:** a print/export page boundary is intended.
- **Where:** between blocks.
- **Why:** control pagination. It is not a thematic break.

- **Sources:**

  - [QUARTO-S](https://quarto.org/docs/authoring/shortcodes.html)

## A34 Quarto keys/media

- **How:** use `{{< kbd Ctrl-C >}}` or `{{< video clip.mp4 >}}`.
- **When:** explaining input or showing supplied video.
- **Where:** the action/media position.
- **Why:** present the content clearly. Output support and accessibility still apply.

- **Sources:**

  - [QUARTO-S](https://quarto.org/docs/authoring/shortcodes.html)
