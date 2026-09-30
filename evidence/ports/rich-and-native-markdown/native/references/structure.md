# Choose clear document structure

- Give every Markdown file a clear title and meaningful sections beneath it. Use `#` for the title, `##` for its sections, and deeper levels when a section has real subsections.

## Purpose and reading route

- **Reading trigger:** Read before choosing headings, lists, or standalone paragraphs.
- **Prerequisites:** None within this package. Follow the active language and meaning skills.

## Rules

- Read the [heading and content contract](headings.md) before choosing or checking headings. Every Markdown file needs H1, H2, and H3; use H4-H6 wherever its real section tree requires them. Give every heading useful owned content before another heading or EOF.

### Headings in every file

- Keep heading levels in order. Make each child heading describe content owned by its parent. Use descriptive, distinct labels; do not use bold text as a substitute for a heading.
- Check the outline both per file and in assembled output, where a host may add a title. Avoid duplicate heading IDs and broken anchors.
- Apply this hierarchy to each linked file on its own. Do not add empty sections, invented content, or deeper headings merely to increase nesting.
- If an exact fragment or required output format cannot accept headings without changing meaning or breaking its use, identify the conflict. Do not silently exempt it or claim full compliance.

### Ordered steps and unordered lists otherwise

- Use ordered lists for steps in a procedure. Keep their required order, prerequisites, branches, and stopping conditions explicit.
- Use unordered lists for all other editable rules, conditions, exceptions, prohibitions, checks, and list content.
- Keep one action per step and one rule per bullet where possible. Keep each condition and narrow exception with its action or rule.
- Use nested lists only for real parent-child relationships. Number child steps; use bullets for child conditions or notes.
- Preserve meaningful ranks and identifiers as explicit text when using unordered lists. Preserve exact quoted rules and literal examples in their required form.

### Rare, justified paragraphs

- Make headings and lists the default for editable guidance: ordered lists for steps, unordered lists otherwise.
- Keep a prose paragraph only when it serves a specific purpose that bullets would weaken, such as a connected explanation or required narrative passage.
- Record the file, passage, and concrete reason for each retained paragraph in the review evidence. Name the meaning or reading task that would suffer if it became a list.
- Keep necessary tables, code, quotations, images, and other supported forms when their role warrants them. These are not prose exceptions, and they must not hide editable rules outside ordered steps or unordered rule lists.
- This paragraph exception concerns authored prose, not paragraph elements that a renderer may create inside list items.
- Use natural, complete wording. Do not turn paragraphs into long bullets that hide several rules or remove spacing to shorten files.

