# Structured blocks and MyST

- Read this file when the input uses generic definitions, HTML wrappers, captions, or MyST roles and directives.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E33 Generic definition

- **How:** put a term paragraph and a list of definitions inside `/// define`.
- **When:** definitions are long.
- **Where:** reference content.
- **Why:** keep term groups together. Do not enable it with legacy `def_list`.

- **Sources:**

  - [PY-DEFINE](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/definition/)

## E34 Generic HTML wrapper

- **How:** use `/// html | div.class` around Markdown.
- **When:** a supported wrapper is needed.
- **Where:** block boundaries.
- **Why:** keep wrapper and prose clear. Parsing modes and HTML filtering still apply.

- **Sources:**

  - [PY-HTML](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/html/)

## E35 Caption block

- **How:** place `/// caption\nCaption\n///` after the object.
- **When:** an image, table, or block needs a label.
- **Where:** adjacent to it.
- **Why:** bind explanation to its object. PyMdown `blocks.caption`, added in 10.12.

- **Sources:**

  - [PY-CAPTION](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/caption/)

## E36 MyST role

- **How:** put `{role-name}` immediately before backtick-delimited text.
- **When:** a span needs a named semantic role.
- **Where:** inline.
- **Why:** express math, references, or other registered roles. A name only works when its role exists.

- **Sources:**

  - [MYST-ROLE](https://myst-parser.readthedocs.io/en/stable/syntax/roles-and-directives.html)

## E37 MyST directive

- **How:** fence `{name}` arguments with backticks, add `:option: value`, a blank line, and body.
- **When:** a named block needs options or content.
- **Where:** block flow.
- **Why:** express figures, math, tables, code, notes, or document structure. Optional `:::{name}` uses colon fences; nested outer fences must be longer.

- **Sources:**

  - [MYST-ROLE](https://myst-parser.readthedocs.io/en/stable/syntax/roles-and-directives.html)

## E38 MyST field list

- **How:** use `:name: value` with valid continuation blocks.
- **When:** fields or parameters need labels.
- **Where:** API/reference text.
- **Why:** pair each field and value. Enable `fieldlist`.

- **Sources:**

  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)

## E39 MyST substitution

- **How:** define values in configuration/front matter and use `{{ key }}`.
- **When:** a shared value changes.
- **Where:** supported prose, not ordinary code fences.
- **Why:** keep one value owner. This uses Jinja; count dependencies and reject circular substitution.

- **Sources:**

  - [MYST-OPT](https://myst-parser.readthedocs.io/en/stable/syntax/optional.html)

## E40 MyST target and reference

- **How:** put `(label)=` before a block and refer with a supported link or role such as `{ref}`.
- **When:** a stable cross-file target matters.
- **Where:** target and referring text.
- **Why:** avoid dependence on changing titles.

- **Sources:**

  - [MYST-REF](https://myst-parser.readthedocs.io/en/stable/syntax/cross-referencing.html)

## E41 MyST document assembly

- **How:** use registered `{include} file.md` or `{toctree}` directives with document entries.
- **When:** reusing text or declaring a document tree.
- **Where:** insertion/navigation blocks.
- **Why:** preserve source ownership and reading structure. Includes may load eagerly; they are not selective context loading.

- **Sources:**

  - [MYST-DOC](https://myst-parser.readthedocs.io/en/stable/syntax/organising_content.html)
