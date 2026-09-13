# Writing rules for markdown files

Two rule sets apply together. Plain language makes any reader act correctly on the first pass. Human prose keeps the text free of the machine tells the lint flags.

## Plain language

- Write for the reader you have. Purpose and bottom line first, background last.
- One idea per sentence. One topic per paragraph, topic sentence first, under 150 words.
- Active voice, present tense. "Run the check", never "the check should be run".
- Verbs over noun forms: "we decide", never "we make a decision".
- Steps in the order the reader performs them, numbered.
- Question headings where they fit, statement headings otherwise, and never more than three heading levels.
- One term per concept for the whole document. No synonym rotation.
- Full words: "for example" and "that is", never the Latin shorthand.
- Numbers, file names, and commands beat adjectives. "Exits 0" beats "works correctly".
- Every list gets a lead-in sentence and parallel items. Prose wins when the items flow as one thought.

## Reasoning simplicity

- Use the smallest coherent structure that preserves every required rule and accepted behavior.
- Keep one canonical owner per rule and link to it instead of restating it. Define a repeated link target once per document, following [reference-link syntax](https://spec.commonmark.org/0.31.2/#link-reference-definitions). A definition cannot interrupt an open paragraph.
- Link specific implementation owners descriptively while naming their public `mise run` route in the same block or section. A link identifies the owner; execution still uses the public task. Bare script commands remain forbidden in operative Markdown. The lint checks bounded spellings and layout, not semantic intent, all Markdown syntax, target validity or actual resource consumption.
- Use one stable term per concept. Define it once, then keep it exact.
- Keep one material decision per branch. Remove choices that lead to the same action or result.
- Keep the causal chain visible: outcome, reason, evidence, action, readback, and completion.
- Remove decorative headings, duplicate checklists, needless load hops, and examples that teach nothing new.
- Keep essential domain complexity visible. Fewer words or files do not prove simpler work.

## Human prose

- The `mise run lint-writing` task owns the banned word and frame checks. Run it before drafting when prior output is available, then rerun it on the finished Markdown; it prints file and line for every hit.
- No em or en dashes anywhere. Use a comma, a period, or parentheses.
- Vary sentence length on purpose. A four word sentence lands. Then let a longer one carry the detail that needs the room.
- Cut hedges: somewhat, fairly, arguably, very, quite.
- No closers that restate the section above.
- Emphasis is bold or italics, rarely. Never full capitals.
- Pick a structure that fits the content instead of reusing one skeleton for every document.

## Line layout

- Wrap paragraphs and list items where this helps reading. Keep proper list indentation.
- Use blank lines to keep headings, lists, tables and code clear.
- A link definition cannot start inside an open paragraph. Add a blank line first.
- Keep each Markdown file within 200 physical lines, including blanks and comments.
- Do not use huge lines or dense tables to fit the cap. Keep core rules in SKILL.md.

## Reading and meaning checks

Use the full writing review in this order:

1. `mise run markdown:inventory`: capture the files and their rules.
2. `mise run markdown:mechanical`: report facts and all check failures.
3. `mise run markdown:review-request`: give the model the exact review inputs.
4. `mise run markdown:macro-review`: judge the whole file first.
5. `mise run markdown:micro-review`: judge its sections and blocks next.
6. `mise run markdown:line-review`: polish lines after the first two reviews pass.
7. `mise run markdown:review-check`: check the replies and full-file readback.
8. `mise run markdown:accept`: check all required proof before acceptance.

Set `SKILL_MARKDOWN_REQUEST` to the request file and `SKILL_MARKDOWN_STATE`
to a private state folder outside the reviewed roots. Use absolute paths.
Each task names its prerequisite. At exit 3, the model reads the pending review.
Set `SKILL_MARKDOWN_REPLY` to its bound reply file, then rerun that same task.
Keep the request and state paths fixed. Missing or stale proof blocks the next task.
Early quality failures inform whole-file review; they still block acceptance.
Mastra calls the same check owners, never nested Mise. Keep human proof separate.

Write English prose at a sixth-grade level. Use short words and clear steps.
Keep each rule, condition, exception and proof duty. Define needed terms.
The pinned grade check must report a score of 6.0 or less. Keep its exact input,
method and exclusions. Short text still needs direct review. A low score alone
cannot show that a reader will know what to do.

The model must read the full text, source rules, linked context, check results
and rendered page. It must judge meaning, clear actions, terms, structure,
first-load rules, file roles and honest score exclusions. Each finding needs
a cited span, a reason and any needed repair. Bind it to the same run and files.
Missing, stale or failed reviews block acceptance. Keep human review separate.
Do not claim that a schema or model review proves real readers understood.

## How do I choose each Markdown form?

Use the full [CommonMark spec](https://spec.commonmark.org/0.31.2/),
[GFM spec](https://github.github.com/gfm/) and the target's current docs.
The list below is a guide, not a claim that a renderer passed each spec test.
Keep a source-to-feature map with versions, variants, support and test results.
Missing or untested features stay open. Do not infer support from this guide.

For each feature, answer six questions in the existing Markdown review:

1. What does it mean, and what is its syntax?
2. Which form fits this content better than the other choices?
3. When does it help, and when should it be avoided?
4. How is it written, nested, escaped, rendered and checked?
5. Why does it help this reader without changing a rule?
6. Who writes it, checks it, judges it and gives any required approval?

The author or model chooses and writes each form. Generators follow that choice.
Mise and Mastra check bound inputs, syntax and review coverage.
The model judges meaning, fit and clarity from the full text and render.
The named human keeps any required approval. A task cannot grant it.
These roles apply to every form below, including forms a generator writes.

### CommonMark forms and syntax rules

- **Text and paragraphs:** Write one thought in plain text. Use a new paragraph for a new idea, not a table for prose.
- **Blank lines:** Separate blocks so the reader can see their roles. Check that spacing keeps lists and code in the right block.
- **Characters and lines:** Keep the source encoding and line endings. Check Unicode, tabs and control characters with the named parser.
- **Tabs:** Tabs affect block indentation. Prefer clear spaces for new text; do not alter protected tabs. Check the actual parsed block.
- **Unsafe characters:** Let the parser apply its defined handling of null characters. Never alter protected source bytes to hide a failure.
- **Escapes:** Use a backslash before punctuation, such as `\*`, when the reader needs a literal mark instead of emphasis.
- **Entities:** Use named or numeric character references only when needed. Check the rendered character; code spans treat them as literal text.
- **Block and inline rules:** A block holds content; inline marks sit within it. Check precedence before nesting forms, since appearance alone can mislead.
- **Thematic breaks:** Use three matching `*`, `-` or `_` marks for a real topic break. Prefer a heading when the next topic needs a name.
- **ATX headings:** Use one to six hash marks and a space. Choose the level from the section's parent, not the desired font size.
- **Setext headings:** Put an equals or hyphen underline below a title for levels one or two. Prefer ATX for a deeper hierarchy; check confusion with breaks.
- **Indented code:** Four spaces mark a code block. Use it for simple literal text only when it cannot be mistaken for list nesting.
- **Fenced code:** Use matching backtick or tilde fences, long enough to contain literal fences. Add a language tag for code; never hide prose in code.
- **HTML blocks:** Use supported HTML only for a needed result native Markdown cannot express. Check sanitizing, visible prose and accessible fallback text.
- **Reference definitions:** Define a reused link target once outside an open paragraph. Check duplicate labels and the parser's first-definition rule.
- **Blockquotes:** Prefix quoted text with >. Use them for attributed quotes, not to give an ordinary rule false authority.
- **List items:** Keep each item's child blocks under that item. Check indentation, blank lines and lazy continuation so instructions stay with their parent.
- **Unordered lists:** Use bullets for parallel facts. Choose prose when the items form one thought; nesting must show a real relationship.
- **Ordered lists:** Use numbers for a sequence. Check the first number and nested items; a numbered list does not enforce task execution order.
- **Tight and loose lists:** Blank lines can change list layout. Choose spacing for reading and check which paragraphs remain inside the list.
- **Code spans:** Put exact tokens in backticks. Use longer delimiters to show backticks; check normalized spaces before quoting exact bytes.
- **Emphasis:** Use a pair of `*` or `_` marks for stress. Keep the text clear without it; check word-boundary and nesting rules.
- **Strong emphasis:** Use a double pair for a key point. Use headings for structure; bold text cannot replace a section's name.
- **Inline links:** Use a label and a parenthesized target. Choose a clear label, verify the destination and escape delimiters as the parser requires.
- **Reference links:** Use full, collapsed or shortcut labels for shared targets. Match the definition and check unresolved labels, titles and nested marks.
- **Images:** Use image syntax with useful alt text and a valid target. Use prose for required rules; an image cannot carry hidden first-load duties.
- **Autolinks:** Put a URI or email in angle brackets when its exact address is the useful label. Prefer a named link for long or unclear targets.
- **Raw inline HTML:** Use a supported tag only for a needed inline result. Check filtering and accessibility; visible words still need prose review.
- **Hard breaks:** Use a backslash or two trailing spaces when a line break carries meaning. Prefer a paragraph for a new thought.
- **Soft breaks:** A normal newline may render as a space. Wrap prose for source reading and test targets that treat line breaks differently.

### GFM extensions

GFM has its own version and CommonMark base. Do not label every GitHub feature GFM.

- **Tables:** Use header and delimiter rows for short comparisons. Align columns when useful; escape literal pipes and keep long prose outside cells.
- **Task list items:** Use [ ] or [x] after a list marker for real work states. A checked box needs evidence and is not approval by itself.
- **Strikethrough:** Use paired tildes for removed wording where the target supports it. Keep the current rule clear; preserve protected quotes unchanged.
- **Extended autolinks:** GFM can link bare addresses. Check punctuation and boundaries; use an explicit link if the inferred target is unclear.
- **Disallowed HTML:** GFM filters named raw tags. Test the target's further sanitizing too; never use HTML to bypass a content or safety check.

### Target extensions and host features

Use the target's [documented formatting](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting)
and [basic writing guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
Record the exact surface: a repository file, issue, pull request or another host.
A host feature is not native CommonMark merely because GitHub renders it.

- **Section links and anchors:** Link to a stable heading or supported anchor. Check duplicate headings and changed titles; use file links for another document.
- **Relative links and image paths:** Use them for portable local targets. Resolve from the current file and check fragments, case and moved files.
- **Footnotes:** Use them for optional source detail. Keep required actions inline; test the target's labels, return links and nesting limits.
- **Alerts:** Use the documented alert marker for a real warning or note. Keep its content readable without color or an icon.
- **Collapsible details:** Use supported details and summary tags for optional depth. Never collapse first-load rules, required warnings or current blockers.
- **Math:** Use supported inline or block math for exact formulas. Define symbols, check rendering and give a readable text form where needed.
- **Mermaid and other diagrams:** Use the target's documented fence and renderer. Verify graph content, labels and fallback access; follow the file-graph contract.
- **Maps and 3D figures:** Use documented GeoJSON, TopoJSON or STL support only for relevant spatial data. Test the surface and retain an accessible explanation.
- **Syntax highlighting:** Select the right fenced-code language. Color can help reading but cannot prove that a command is valid or safe.
- **Subscript, superscript and inserted text:** Use supported HTML tags only when those meanings matter. Verify the target; use plain words if support is absent.
- **Comments:** Use supported HTML comments for non-user notes only. Never hide required instructions, secrets or unreviewed prose in comments.
- **Emoji:** Use a supported code or Unicode symbol only when it helps. Words must carry the meaning without the symbol.
- **Mentions and references:** Use supported user, team, issue, commit or pull-request references only within authority. Check link and notification effects before posting.
- **Automatic links and color previews:** Check the exact host surface and pattern. Use plain text when the feature is absent; do not claim previews work in every file.
- **Attachments and code permalinks:** Use verified links to relevant content. Check access and revision; a host preview cannot replace required source reading.
- **Front matter:** Treat supported front matter as metadata. Preserve its schema and keep explanatory rules in the visible body.

Do not force these forms into every file. Extend the map for each documented
feature or material variant not yet covered. Trace official examples and mixed
forms to tests; record gaps instead of claiming full coverage from this list.
Use the six questions for every entry, including a choice not to use a feature.

## How do I avoid the banned list on the first draft?

Run `mise run lint-writing` and use its current diagnostics rather than copying its policy into prose. Draft, rerun the task, then fix each reported line. Typical rewrites keep the concrete word: "checked" or "tested" for a quality claim, "use" for a verb of applying something, "with no extra step" for a smoothness claim.

## How do I check a document?

Run `mise run lint-writing` from the skill root. Exit 0 means the bounded lint checks passed. It does not prove reading level, meaning or rendered clarity. On failure the output names file, line, and rule. Rewrite the sentence; swapping one flagged word for a close synonym of it usually trips another rule.
