# Check source and rendered readability

- Judge readability in four parts: preserved meaning, readable source, usable rendered content, and a clear route through related files.

## Purpose and reading route

- **Reading trigger:** Read before drafting and before checking source or rendered output.
- **Prerequisites:** None within this package. Identify the reader and target before applying these checks.

## Define readability before editing

- Name the intended reader, task, reading language, target renderer, active extensions, output formats, and HTML policy. Use CommonMark when the target is unknown and state the untested target limits.
- Make the main point, needed context, terms, conditions, and next action easy to find and explain. A reader should be able to use the document without guessing missing steps.
- Treat complete readability as a bounded acceptance goal for the stated readers and targets. No syntax choice, score, or automated check proves readability for everyone.
- Keep grade 6 English, the H1/H2/H3 minimum, rare paragraphs, exhaustive primitive consideration, and the 150/200-line policy as this project's requirements. Do not present those exact choices as universal Markdown or accessibility standards.

## Apply checks to every primitive family

- Check the selected forms together, including their source boundaries, meaning, and accessible alternatives.

### Source structure and text

- Keep blank lines and indentation that make block boundaries clear. Check list continuation, nested code, and quote boundaries in the actual parser; do not assume one indentation width works everywhere.
- Use soft source wraps where they preserve meaning. Use hard breaks only when line endings matter, such as verse or an address. Do not force visual line lengths with repeated breaks, spaces, or nonbreaking spaces.
- Use emphasis sparingly for real stress or importance. Do not depend on bold, italics, color, emoji, strike marks, or position alone to convey a required fact or state.
- Keep edited, deleted, inserted, highlighted, superscript, and subscript meaning explicit when a reader may miss the visual distinction. Preserve equations and other exact notation.
- Use thematic breaks for real topic shifts. Check collisions with heading underlines and metadata fences; decoration must not replace a useful heading.
- Distinguish quotes from the author's rules and claims. Keep attribution and exact wording; do not use blockquotes just to indent ordinary text.
- Check escaped punctuation, entities, delimiters, and literal examples in both source and output. Verify the intended characters survive rendering and copying.

### Links, references, and supporting text

- Give links labels that explain the destination or action. Avoid labels such as “here.” Identify unexpected downloads or other link behavior when relevant.
- Keep reference definitions, citations, footnotes, glossary terms, and abbreviations complete and reachable. Keep facts tied to their sources and define needed terms before using them.
- Use notes for supporting detail. Keep prerequisites, warnings, and essential meaning in the main reading path. Check note markers, destinations, return routes, and exported output.
- After splits or heading edits, recheck relative paths, fragments, duplicate IDs, reference definitions, assets, and citations from the file that owns each link.

### Code, tables, and status

- Use inline code for exact tokens and fenced blocks for literal multiline content. Add the correct language label when known, and distinguish literal code from executable cells.
- Explain an example's purpose before its code. Keep syntax, meaningful whitespace, and copyable content intact. Provide a text explanation when complex code needs one.
- Use tables only for real row-column relationships. Supply clear headers, context, units, and meaningful cell values. Avoid layout tables and walls of prose in cells.
- Check actual header associations. A Markdown pipe table may not express complex row headers, spans, or block content; use supported accessible markup or a meaning-preserving alternative when needed.
- Keep wide tables and code reachable on narrow screens. Preserve two-dimensional layout only where its meaning needs it; keep surrounding prose able to wrap.
- Use task items only for real work states. State status in words when needed, and do not imply that a checkbox is interactive or that checking it proves completion.

### Images, diagrams, math, and media

- Match image alternatives to purpose: describe information for informative images, the action for linked images, and use empty alternatives only for decoration. Check the rendered result.
- Give complex charts and diagrams a short name plus an available text account of their important data, relationships, and conclusion. Do not rely on color alone or replace selectable text with screenshots.
- For supported Mermaid diagrams, use accessible titles and descriptions and verify that they reach the rendered output. Metadata alone does not prove that the diagram is understandable.
- Preserve math syntax, define needed symbols, and check the target's speech or other accessible math output. A visual equation or raw TeX alone does not establish accessible reading.
- Give audio and video the captions, transcripts, and descriptions needed to convey their content. Keep essential information available without sound or motion; avoid harmful flashing.

### Containers, extensions, and hidden content

- Use alerts only for information that warrants interruption. Keep labels meaningful and avoid stacks of competing alerts. Follow target-specific nesting limits.
- Give details, tabs, and other controls clear labels, keyboard access, visible focus, and correct open or selected states. Keep prerequisite warnings visible before the action they govern.
- Verify that hidden or alternate content remains reachable in the intended reading and export paths. Collapsing a block does not reduce its source lines or remove it from loaded context.
- Keep metadata, attributes, raw HTML or TeX, comments, directives, components, embeds, includes, and substitutions distinct from ordinary prose. Check their meaning and support before conversion.
- Do not place reader-required content only in comments, metadata, hover text, styling, or content that the target strips. Preserve a usable fallback when an extension cannot carry its meaning.
- Check generated content and transclusions for duplicate headings, ID collisions, changed path bases, missing context, and reading-order faults.
- Formatting does not authorize code execution, remote fetching through embeds, publishing, sending messages, or changes to unrelated sources.

## Check the rendered reading experience

- Keep source faults, host faults, and untested behavior separate in the results.

### Layout and interaction

- Where the target permits testing, check ordinary and narrow views, 200% text enlargement, and reflow at 320 CSS pixels wide for vertical scrolling, or 256 CSS pixels high for horizontal scrolling. Distinguish these checks; a narrow screenshot is not a zoom test.
- Keep ordinary prose readable without two-direction scrolling. Apply the documented exception for content that needs two-dimensional layout, without hiding or clipping its information.
- Check user text-spacing changes for lost, overlapping, or clipped content. For applicable web output, test line height 1.5, paragraph spacing 2, letter spacing 0.12, and word spacing 0.16 times the font size. Apply properties used by the writing system. These are override tests, not mandatory default styles.
- Check applicable WCAG contrast requirements in the rendered theme: normally 4.5:1 for text and 3:1 for qualifying large text, with the standard's stated exceptions. Syntax highlighting and diagram labels need checks too.
- Check linear reading order, real heading and list structure, link names, table headers, and control states through the rendered document structure. Check keyboard use and available assistive tools separately from appearance.
- Keep renderer and theme faults distinct from Markdown-source faults. Fix only within the authorized scope; report host limits that prevent a required result.

### Meaning and evidence

- Review the text in context, including hard passages that an average reading score could hide. Keep required technical terms and explain them rather than deleting meaning to lower a score.
- A reading score, parser result, screenshot, accessibility-tree check, and reader study prove different things. State which checks ran, on which versions, with which limits.
- Do not claim a screen-reader test from a document-tree inspection, or a human comprehension test from an automated review.
