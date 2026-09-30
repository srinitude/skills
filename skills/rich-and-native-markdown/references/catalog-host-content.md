# Embedded views and host references

- Read this file when the input uses diagrams, maps, meshes, responsive images, mentions, or host work references.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## A01 Diagram fence

- **How:** put valid diagram source in a `mermaid` fence; configured GitLab targets can use `plantuml` or Kroki-supported languages.
- **When:** relationships are clearer visually.
- **Where:** beside the explanation.
- **Why:** show structure. The embedded diagram language has its own grammar and version; preserve accessible descriptions.

- **Sources:**

  - [GH-DIAGRAM](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
  - [GL](https://docs.gitlab.com/user/markdown/)

## A02 Map fence

- **How:** use `geojson` or `topojson` fences containing valid corresponding data.
- **When:** geographic shapes are the content.
- **Where:** supported GitHub surfaces.
- **Why:** show spatial relationships. These are embedded formats, not separate primitives for each shape.

- **Sources:**

  - [GH-DIAGRAM](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)

## A03 3D mesh fence

- **How:** put ASCII STL in an `stl` fence.
- **When:** inspecting supplied geometry.
- **Where:** supported GitHub surfaces.
- **Why:** show its shape. This is a host view of embedded data.

- **Sources:**

  - [GH-DIAGRAM](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)

## A04 Responsive image

- **How:** use permitted `picture`/`source` elements plus `img` with useful alt text.
- **When:** visual conditions need different assets.
- **Where:** supported HTML.
- **Why:** show a fitting image. Ordinary image Markdown remains the fallback.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

## A05 Color preview

- **How:** put a supported hex/rgb/hsl value in an inline code span.
- **When:** exact color matters.
- **Where:** supported host surfaces.
- **Why:** pair value with swatch. GitHub limits this to issues, pull requests, and discussions; it does not color arbitrary text.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [GL](https://docs.gitlab.com/user/markdown/)

## A06 Mention

- **How:** use `@user` or a valid team/group form.
- **When:** an authorized message needs that recipient.
- **Where:** host conversations.
- **Why:** identify the owner. Mentions may notify people; formatting is not permission to publish or contact anyone.

- **Sources:**

  - [GH-B](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
  - [GL](https://docs.gitlab.com/user/markdown/)

## A07 Work/history reference

- **How:** use a real host ID, commit, or URL; GitHub examples include `#123`, `GH-123`, `owner/repo#123`, and `owner/repo@SHA`.
- **When:** connecting prose to tracked work/history.
- **Where:** supported host text.
- **Why:** make claims traceable. GitHub shorthand behavior differs in repository files and wikis.

- **Sources:**

  - [GH-AUTO](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls)
  - [GL](https://docs.gitlab.com/user/markdown/)

## A08 Label/external autolink

- **How:** use a supported label URL or configured tracker prefix.
- **When:** connecting to an actual label/ticket.
- **Where:** the configured repository.
- **Why:** avoid ambiguous references. Do not infer an integration from the token alone.

- **Sources:**

  - [GH-AUTO](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls)

## A09 GitLab reference variants

- **How:** use the registered token: `!123`, `$123`, `&123`, `~label`, `%milestone`, `namespace/project>`, commit/range, `^alert#123`, `*iteration:"title"`, or `[type:value]`.
- **When:** linking the matching object.
- **Where:** supported GitLab text, not Markdown snippet files.
- **Why:** target the right record. Named types include issue, `work_item`, epic, cadence, vulnerability, `feature_flag`, contact, and `wiki_page`; `+` adds a title and `+s` a supported summary.

- **Sources:**

  - [GL](https://docs.gitlab.com/user/markdown/)
