# Markdown catalog

- Use this guide to choose syntax that fits the content and its destination.

## Purpose and reading route

- **Reading trigger:** Read before choosing Markdown forms.
- **Prerequisites:** No other package file must be loaded first. Required companion skills must already be active.

### Context and topic detail

- Use the topic links below for the input and target.
- You do not need to reread the entry file to use this guide.
- Read the complete [primitive inventory](catalog-inventory.md) before choosing a form. Load topic detail when needed for a sound decision; a small edit does not always need every topic.
- The whole-set review still covers every file when that review is due.

## Scope and terms

- The supplied research was checked on 2026-09-17.
- This catalog has 136 entries: all named CommonMark block and inline forms, the five formal GFM extensions, and the listed forms from GitHub, GitLab, Pandoc, MultiMarkdown, PHP Markdown Extra, kramdown, Python-Markdown, PyMdown, Material, MyST, Obsidian, Quarto, Markdoc, and MDX.

- There is no final list of every Markdown feature.
- People can add plugins, roles, directives, components, and shortcodes.
- Identify the owner of an unknown form before changing it.
- Never silently remove or reinterpret it.

- A **dialect** is a named set of syntax rules. A **renderer** makes its view.
- A **parser** reads syntax and decides its structure.
- **Core syntax** is the shared baseline. An **extension** adds forms or rules.
- A **host feature** belongs to an app. An **embedded language** has its own rules.
- An **attribute** attaches data to one item; a **span** groups inline text.
- A **container** groups blocks. **Raw content** passes through without normal parsing.
- An **include**, **partial**, or **transclusion** brings in text from another owner.
- **GFM** means GitHub Flavored Markdown. **MMD6** and **MMD7** mean MultiMarkdown versions 6 and 7.

- These are different layers.
- CommonMark is the portable baseline here, subject to actual target support.
- The usage advice is editing guidance, not measured proof of reading ease.
- The catalog is source guidance; it does not certify that every named renderer or form has passed a render test.

- In examples, `\n` means a real newline to emit.
- Described indentation means real spaces.
- A fence has a matching opening and closing line.
- Examples are shown as literal text so they do not run or change the guide's layout.

## Choose the target first

- Find the destination, dialect, active extensions, output type, and HTML policy in the request or its files.
- Use only supported forms.
- If they are unknown, state the CommonMark baseline.
- Preserve unsupported forms literally or use a fallback with the same meaning.
- Prefer native syntax when it does the job.

- Check current owner docs before claiming complete feature support.
- Test the actual reading of ambiguous marks: `---`, `~`, `^`, `$`, braces, blank lines, indentation, and fence length can each change meaning.

- Check these common collisions in the chosen target:

- `---`: thematic break, heading underline, or metadata fence.
- `~`: strikethrough or subscript.
- `^`: superscript, block ID, or block ending.
- `$`: currency, math, or a host reference.
- Braces: attributes, data, or executable expressions.

- Keep alt text useful, heading order clear, table headers meaningful, link labels specific, and reading order sensible.
- Keep exact code, equations, identifiers, and citations.
- Do not invent facts, states, citations, image details, or support for syntax.
- Formatting does not grant permission to publish, notify people, fetch remote embedded content, or run code.

- Details, tabs, comments, footnotes, and eager includes do not remove source lines or automatically save context.
- Use linked files with reading triggers for real progressive disclosure.
- Count includes, imports, partials, transclusions, substitutions, and required cross-references as dependencies when they supply needed content.
- Keep navigation-only links distinct.

## Check a chosen form

- Reading a manual is not a render test.
- Check representative syntax against each renderer claimed as supported.
- Check source and rendered meaning, escaping, fallbacks, nested containers, math versus currency, reference definitions after splits, and literal versus executable fences.
- Label untested dialect support.
- Later checks may verify versions and correct proven source changes; the supplied catalog must stay built into the skill.

## Consider every candidate

- For each formatting decision, consider every catalog entry, known target-specific forms, and unfamiliar forms found in the input. Do not rule out an unread or unknown form just because context is missing.
- A decision covers one passage or passages with the same purpose, meaning, and target constraints. Reuse it only while those facts remain unchanged.
- Check meaning, reader value, support, accessibility, syntax, and fit with the requested heading and list rules.
- Record each candidate as use, rule out, or unresolved, with a reason. Shared reasons may cover named entries; an unchecked group does not count as considered.
- Consideration is not selection. Do not force every form into the output or replace a required list just for variety.
- The catalog describes syntax capabilities. This skill's selection rules are stricter: ordered lists for procedure steps, unordered lists for other editable rules, and justified standalone paragraphs only.
- Keep all 136 entries, How, When, Where, Why, exact syntax, source links, and dialect limits. Verify additions against their owners before claiming coverage.

## Load catalog topics when needed

- Each link below is required only when its reading trigger applies.

- Read [text and headings](catalog-text.md) for prose, breaks, and headings: C01-C08.
- Read [quotes, lists, and code blocks](catalog-blocks.md) for blocks: C09-C16.
- Read [inline text, links, and images](catalog-inline.md) for inline forms: C17-C26.
- Read [formal GFM extensions](catalog-gfm.md) for tables, tasks, strike text, links, and filtering: G01-G05.
- Read [notes, terms, and lists](catalog-notes-lists.md) for extended notes or lists: E01-E07.
- Read [attributes, containers, and raw content](catalog-containers.md) for these forms: E08-E15.
- Read [math and edit marks](catalog-math-edits.md) for math, marks, edits, emoji, or keys: E16-E24.
- Read [asides and tabs](catalog-asides.md) for alerts, folding, and alternatives: E25-E32.
- Read [structured blocks and MyST](catalog-myst.md) for typed blocks and MyST: E33-E41.
- Read [note links and code details](catalog-links-code.md) for links, embeds, parsing, or code: E42-E50.
- Read [tables and figures](catalog-tables-media.md) for extended tables and images: E51-E58.
- Read [metadata and citations](catalog-metadata-cites.md) for metadata and source or term links: E59-E64.
- Read [text transforms and theme features](catalog-theme.md) for display helpers: E65-E71.
- Read [embedded views and host references](catalog-host-content.md) for diagrams and host objects: A01-A09.
- Read [shared content](catalog-includes.md) for quotes, placeholders, includes, or shortcodes: A10-A17.
- Read [Quarto and Markdoc](catalog-quarto-markdoc.md) for those systems: A18-A26.
- Read [MDX and media](catalog-mdx-media.md) for MDX, record tables, media, or page breaks: A27-A34.
- Read [parser settings](catalog-parsing.md) when configuration or HTML grammar changes the reading.
- Read [source details](catalog-sources.md) when checking evidence, versions, or a source key.
