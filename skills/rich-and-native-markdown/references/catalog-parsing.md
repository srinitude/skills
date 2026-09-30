# Parsing rules and settings

- Read this file when HTML grammar or parser settings affect the source. A setting changes how text is read; it is not another visible Markdown form.

## Reading this file

- Prerequisites: the supplied text and its target format; no other catalog file is a required read.

### Terms and syntax

- A dialect is a syntax rule set; a renderer makes its view. A parser reads the syntax.
- Related entry IDs are labels, not required reading links. Check any real content dependency before using it.

## HTML forms within C15 and C24

- These forms include opening and closing tags, `<!-- comments -->`, `<? processing instructions ?>`, declarations such as `<!DOCTYPE html>`, and `<![CDATA[sections]]>`.

- **How:** keep valid syntax only where required.
- **When:** preserving supported embedded markup.
- **Where:** its valid inline or block position.
- **Why:** avoid corrupting the source.

- CommonMark has seven classes that can start an HTML block:

  - Class 1: `pre`, `script`, `style`, or `textarea` tags.
  - Class 2: Comments.
  - Class 3: Processing instructions.
  - Class 4: Declarations.
  - Class 5: CDATA sections, which hold character data.
  - Class 6: Listed block tags.
  - Class 7: Other complete tags on their own line.

- These classes control parsing. They are not a recommendation to add scripts.

- Tabs, line endings, Unicode handling, NUL replacement, lazy continuations, delimiter matching, and precedence are parsing rules. Apply them when reading or checking syntax; do not inflate the primitive count by treating each rule as a new visual form.

## Parser and compatibility settings

- These settings change how existing forms work. They add no visible forms.

- **How:** enable only the target's required setting.
- **When:** importing or producing that dialect.
- **Where:** parser or output-tool settings.
- **Why:** preserve meaning when syntax rules differ.

- Newlines: `escaped_line_breaks` is C05; `hard_line_breaks`/`nl2br` force breaks; `ignore_line_breaks` removes paragraph newlines; `east_asian_line_breaks` handles wide-character boundaries. These policies are not interchangeable.

- Boundaries: `blank_before_header`, `space_in_atx_header`, `blank_before_blockquote`, `lists_without_preceding_blankline`, `four_space_rule`, `sane_lists`, and `spaced_reference_links` change recognition/continuation.

- Literal parsing: `all_symbols_escapable`, `angle_brackets_escapable`, `intraword_underscores`, legacy emphasis/attribute modes, quote parsing, and escape extensions change how existing delimiters work. Pandoc backslash-space can mean a nonbreaking space.

- IDs and paths: `auto_identifiers`, `ascii_identifiers`, `gfm_auto_identifiers`, `mmd_header_identifiers`, `implicit_header_references`, and `rebase_relative_paths` control targets and path lookup. MMD heading ID syntax can be `# Heading [id] #`. Preserve the correct source-file path base.

- Existing forms: `startnum`, `shortcut_reference_links`, `autolink_bare_uris`, `fenced_code_blocks`, `backtick_code_blocks`, `fenced_code_attributes`, `inline_code_attributes`, `link_attributes`, `raw_html`, `raw_tex`, `native_divs`, `native_spans`, `markdown_in_html_blocks`, `markdown_attribute`, `footnotes`, `inline_notes`, `citations`, `alerts`, `mark`, `emoji`, and math flags enable the matching catalog entries.

- Python bundles: Extra groups `abbr`, `attr_list`, `def_list`, `fenced_code`, `footnotes`, `md_in_html`, and `tables`. Other named features include `admonition`, `codehilite`, `meta`, `toc`, `wikilinks`, `smarty`, and legacy compatibility settings. Bundle names are not new syntax.

- `sourcepos` adds source-location metadata; `gutenberg` affects plain-text output. Neither is an extra authored Markdown structure. Templates, filters, CSS classes, syntax highlighters, citation styles, and output layouts are separate processing layers.

## Sources

- [CommonMark](https://spec.commonmark.org/0.31.2/)
- [Pandoc extensions](https://pandoc.org/demo/example33/8.21-non-default-extensions.html)
- [Python-Markdown extensions](https://python-markdown.github.io/extensions/)
