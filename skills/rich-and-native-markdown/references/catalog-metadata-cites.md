# Metadata, citations, and term references

- Read this file when the input uses document metadata, citations, glossaries, or MMD abbreviations.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

- Examples below are literal syntax. Use the named dialect and its stated limits.

## E59 YAML metadata

- **How:** place valid key/value data between `---` and `---` or `...` as supported.
- **When:** document metadata is needed.
- **Where:** normally the start.
- **Why:** keep data separate from prose. Pandoc Markdown allows later blocks; its CommonMark-family readers accept one at the start.

- **Sources:**

  - [P-META](https://pandoc.org/demo/example33/8.10-metadata-blocks.html)
  - [QUARTO-B](https://quarto.org/docs/authoring/markdown-basics.html)

## E60 Other metadata

- **How:** use Pandoc `% Title`, `% Author`, and `% Date` lines; MMD-style `Title: Value`; or GitLab `+++` TOML and `;;;` JSON fences.
- **When:** preserving the target's metadata form.
- **Where:** file start.
- **Why:** retain structured document facts. Python meta accepts YAML-like fences but does not parse YAML; keep the formats distinct.

- **Sources:**

  - [P-META](https://pandoc.org/demo/example33/8.10-metadata-blocks.html)
  - [P-EXT](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
  - [PY-META](https://python-markdown.github.io/extensions/meta_data/)
  - [GL](https://docs.gitlab.com/user/markdown/)

## E61 Bibliographic citation

- **How:** use `[@key, p. 4; @other]`, `@key [p. 4]`, or `[-@key]`; complex keys may use `@{...}`.
- **When:** attributing sourced claims.
- **Where:** beside the claim.
- **Why:** preserve source and locator. To format references, set up a bibliography (source list), `citeproc` (citation processor), and CSL (Citation Style Language) style; do not invent entries.

- **Sources:**

  - [P-CITE](https://pandoc.org/demo/example33/8.20-citation-syntax.html)

## E62 MMD6 citation

- **How:** use `[p. 7][#key]` with `[#key]: Reference`; `[#Reference]` is inline, `[Not cited][#key]` includes an uncited item.
- **When:** retaining MMD6 attribution.
- **Where:** claims and reference definitions.
- **Why:** keep existing source links. Not Pandoc `@` syntax; MMD7 chapter unfinished.

- **Sources:**

  - [MMD6-CITE](https://fletcher.github.io/MultiMarkdown-6/syntax/citation.html)

## E63 MMD6 glossary

- **How:** use `[?term]` and `[?term]: Definition`, or `[?(term) Definition]`.
- **When:** terms need a glossary.
- **Where:** term uses and definitions.
- **Why:** connect terms to meaning. Version-bound; MMD7 chapter unfinished.

- **Sources:**

  - [MMD6-GLOSS](https://fletcher.github.io/MultiMarkdown-6/syntax/glossary.html)

## E64 MMD6 abbreviation

- **How:** use `[>ABC]` and `[>ABC]: Expanded name`, or `[>(ABC) Expanded name]`.
- **When:** preserving abbreviation expansion.
- **Where:** prose/definitions.
- **Why:** retain short/full-name links. Not the Extra syntax; MMD7 chapter unfinished.

- **Sources:**

  - [MMD6-ABBR](https://fletcher.github.io/MultiMarkdown-6/syntax/abbreviations.html)
