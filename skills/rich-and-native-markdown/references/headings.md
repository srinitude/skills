# Heading structure and content

- Read this file before choosing headings or checking section boundaries. It governs the skill package and every Markdown output.

## Apply the heading rules in every file

- Prerequisites: the source text, reader, target, topic map, and active language and meaning rules. Read the nested-relationship analysis linked below before applying these rules.
- Use each level to show the source topic tree; font size and visual emphasis do not determine depth.

### Required levels

- Every Markdown file must contain exactly one H1 (`#`), at least one H2 (`##`), and at least one H3 (`###`). These are the minimum required levels. Do not use a heading level beyond H6.
- H4 (`####`), H5 (`#####`), and H6 (`######`) are required whenever the content has distinct nested sections at those depths. A child section under H3 must use H4; under H4, H5; and under H5, H6. Do not treat these levels as optional or flatten, merge, or disguise real section relationships to avoid using them.
- On every invocation, analyze the whole input for nested relationships from H1 through H6 before drafting. Explicitly check for needed H4, H5, and H6 sections, add each supported heading, and record evidence when a level is not needed or remains unresolved. Follow the [nested-relationship analysis](hierarchy.md#analyze-nested-relationships) and use every relevant available web capability, skill, and tool to resolve or validate those decisions.
- Make the H1 the file's title and first heading. Each H2 opens a section under it; each H3 opens a real subsection under its current H2. This minimum applies per file, not to every section: an H2 need not contain an H3 if another section supplies the file's required H3.

### Parent and sibling relationships

- Apply the same parent rule through H6: H2 requires H1, H3 requires H2, H4 requires H3, H5 requires H4, and H6 requires H5. Every ancestor in that chain must appear before the child and still be active in the same file.
- A heading's parent is the nearest preceding active heading exactly one level shallower. A new heading closes the previous section at its own level and all deeper levels. A heading in a closed sibling section cannot serve as a parent.
- Move deeper by only one level at a time. `H1 -> H3`, `H2 -> H4`, and `H3 -> H5` are invalid. The same rule applies to every skipped level.
- Repeating a level for sibling sections or returning to a shallower level is valid when the required parent remains active. `H1 -> H2 -> H3 -> H4 -> H2 -> H3` is valid; `H1 -> H2 -> H3 -> H2 -> H4` is invalid.

### Meaning, conflicts, and rechecks

- Make each heading describe the content it owns. Use clear, distinct labels and real Markdown headings; bold text, visual styling, or heading-like text inside literal examples does not meet the requirement.
- Apply the full H1/H2/H3 minimum and parent chain to every linked child file at every depth. A parent file's headings cannot supply another file's missing levels.
- Reorganize existing content into useful sections and subsections. Do not add empty headings, filler, invented content, or needless H4-H6 levels just to satisfy a count.
- If a tiny file, exact fragment, or required format cannot meet the minimum without changing meaning or breaking its use, report the specific conflict and stop acceptance of that file until it is resolved. Do not silently waive the minimum or claim compliance.
- Check each file's parsed heading order and the assembled output, where a host may add a title. Reconcile host-added headings without losing the source-file minimum; if the target prevents that, report the conflict. Avoid duplicate heading IDs and broken anchors.
- After splits, moves, or heading edits, check the full affected heading tree, links, anchors, and reading order again. Every retained heading level must have its complete active parent chain.

## Require content before the next heading

- Every heading must have meaningful non-heading content that it directly owns before any next heading, at any level. The final heading must also have content before the file ends.

### What counts as content

- Use a useful rule, scope statement, prerequisite, short explanation, step, or other warranted Markdown block. Keep rules in bullets and steps in ordered lists. Preserve the rare-paragraph rule.
- Blank lines, comments, metadata, invisible anchors, empty list items, thematic breaks, and decorative-only content do not count. Do not repeat the heading in a sentence, add filler, invent facts, or use a meaningless link only to pass this check.
- A parent's content must appear before its first child heading. Content under a child does not fill the parent's empty opening. A deeper heading cannot count as non-heading content.
- Keep exact fragments, quotes, and code intact. Heading-like text inside literal code is not a document heading. If a protected format prevents compliance, name the conflict and withhold acceptance of that file.

### Check the actual structure

1. Parse Markdown with the target's rules, including supported Setext or HTML headings and headings inside editable containers. Inspect rendered headings when available; do not rely on a line-prefix search alone.
2. Check every heading-to-heading interval and the final heading-to-end interval for directly owned, meaningful content. Then review whether that content belongs there and preserves the source meaning.
3. Test adjacent parent-child headings, adjacent siblings, blank-line-only separation, comments, empty items, decoration, an empty last section, literal heading examples, and valid rules between headings. Reject filler even when a parser accepts it.
4. Recheck the entire file set after every heading, content, or split repair. Treat this as a project requirement, not a universal CommonMark or accessibility rule.

- The [skill entry](../SKILL.md) is a navigation-only return route.

- Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.
