# Writing style

Read this file before changing any Markdown in this skill. Step 24 checks every Markdown file against these rules with `mise run lint-writing` and a full human readback.

## Structure

Use one H1, ordered H2 sections, no skipped heading level, and a blank line after each heading. State the file purpose and load condition before detailed rules.

## Language

Use common words, active voice, literal language, and direct error text. Define a required uncommon term on first use. Keep one action per sentence and one idea per paragraph. Do not use a metaphor as an instruction or an example as the only statement of a rule.

## Lists and tables

Use lists for ordered actions or equal items. Use tables for commands, mappings, schemas, and comparisons. Keep tables at four columns or fewer when practical. Commands belong in a table.

## Links and code

Use meaningful relative links. State when to read or run the target. Use fenced code only for exact data, commands, or examples. Do not hide a required route in generic wording.

## Line breaks

Use real blank lines between blocks. Do not use HTML break tags. If a table cell would need a line break, shorten the cell and move its detail to a linked procedure where every item can use its own Markdown line.

## Density and ownership

Keep `SKILL.md` under 200 lines. Review a support file at 150 lines and split before 200 when the procedure stays clear. One file owns each rule. Other files link to it.

## Human readback

Confirm headings expose the file shape, steps scan in order, tables do not carry dense prose, labels stay consistent, examples resolve a real ambiguity, and the page does not feel crowded. A parser cannot settle this check.
