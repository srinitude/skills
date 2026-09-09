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
- Keep one canonical owner per rule and link to it instead of restating it.
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

- Every wrappable block is exactly one physical line. A paragraph, or a list item together with what would have been its continuation lines, holds no internal hard line breaks.
- There is no maximum line length. Text fills every column naturally because nothing is manually wrapped, exactly like the one line frontmatter description in SKILL.md.
- Blank lines between markdown elements (headings, paragraphs, lists, code fences, tables) stay exactly as normal markdown readability requires.
- Exempt from the one line rule: YAML frontmatter, headings, table rows, code fence delimiters and everything inside fences, indented code blocks, and blank lines.
- The lint reports any block spanning more than one physical line as path:line; join the block into one line with single spaces.

## How do I avoid the banned list on the first draft?

Run `mise run lint-writing` and use its current diagnostics rather than copying its policy into prose. Draft, rerun the task, then fix each reported line. Typical rewrites keep the concrete word: "checked" or "tested" for a quality claim, "use" for a verb of applying something, "with no extra step" for a smoothness claim.

## How do I check a document?

Run `mise run lint-writing` from the skill root. Exit 0 means every markdown file passed. On failure the output names file, line, and rule. Rewrite the sentence; swapping one flagged word for a close synonym of it usually trips another rule.
