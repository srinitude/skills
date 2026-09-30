# Readability evidence and limits

- These sources were accessed on September 17, 2026. Publication and update dates below are separate from that access date.

## Purpose and reading route

- **Reading trigger:** Read when checking supplied findings, target support, or the strength of a readability claim.
- **Prerequisites:** None within this package. Check the target and version before applying a source-specific rule.
- The operating rules are in the readability guide linked by the entry file. This file holds their evidence, not a second set of competing rules.

## Sources and findings

- Check dates and target versions before using a source to support a current claim.

### Recent owner guidance

- [Cloudflare accessibility guide](https://developers.cloudflare.com/style-guide/style-and-grammar/accessibility/), updated August 20, 2026: plain wording, logical sections, useful links, alternatives, and checks. Publisher style advice is distinct from standards.
- [WAI content structure](https://www.w3.org/WAI/tutorials/page-structure/content/), updated April 8, 2026: semantic headings, paragraphs, lists, quotes, and figures. Rare paragraphs remain the user's project rule.
- [WAI images](https://www.w3.org/WAI/tutorials/images/), updated April 8, 2026: alternatives depend on an image's purpose; complex images need more than a short label.
- [Google accessible documentation](https://developers.google.com/style/accessibility), updated April 21, 2025: source formatting and rendered semantics both matter.

### Current standards and implementation guidance

- [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/), January 28, 2024; still listed as latest on the specification site when checked: core syntax baseline. This is syntax guidance, not a full parser conformance audit.
- [GFM specification](https://github.github.com/gfm/): pipe tables have a header row and inline cell content; support for more complex tables must be checked separately.
- [GitHub writing syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax): alerts, footnotes, comments, and other host features have target-specific rules.
- [WAI tables](https://www.w3.org/WAI/tutorials/tables/), updated February 16, 2023: use tables for data relationships and preserve header associations.
- [WAI headings](https://www.w3.org/WAI/tutorials/page-structure/headings/), updated May 4, 2017: use meaningful heading structure. A current source need not have a recent publication date.
- [WCAG reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): check 320 CSS pixel width or 256 CSS pixel height for the relevant scrolling direction, with the defined two-dimensional-layout exception.
- [WCAG text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html): test supported spacing overrides without loss; these are not required default styles.
- [WCAG contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): normal and qualifying large text have different ratios and stated exceptions.
- [WCAG reading level](https://www.w3.org/WAI/WCAG22/Understanding/reading-level.html): its AAA criterion does not establish grade 6 as a universal requirement.
- [WCAG meaningful sequence](https://www.w3.org/WAI/WCAG22/Understanding/meaningful-sequence.html): preserve order when it changes meaning. The user's file dependency graph is a project rule.
- [ARIA disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/): check names, keyboard action, and exposed state.
- [Mermaid accessibility](https://mermaid.js.org/config/accessibility.html): titles and descriptions can reach the rendered SVG. Their presence alone does not prove comprehension.
- [MathJax accessibility](https://docs.mathjax.org/en/latest/basic/accessibility.html), version 4 documentation: accessible math behavior varies by version; do not prescribe older hidden-MathML behavior for every target.
- [WAI evaluation guidance](https://www.w3.org/WAI/test-evaluate/): automated tools alone cannot determine accessibility.
- Undated pages above have no claimed publication date. Access date is separate from publication date.


### Context retrieval and repetition

- [Recent context guidance](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models), published July 24, 2026: the publisher reports removing repeated instructions without loss in its coding tests and using detail loaded at the point of need. This is evidence against a universal repetition rule, not proof for every task.
- [Recoverable session context](https://www.anthropic.com/engineering/managed-agents), published April 8, 2026: shortened history can discard details later needed. Stored source records allow a focused return to earlier context before an action. Storage alone does not mean the text is currently loaded.
- [Prompt repetition experiment](https://arxiv.org/html/2512.14982v1), published December 17, 2025, with tests from February and March 2025: repetition improved many tested cases, while another tested setting had mostly neutral results and one loss. Long requests could cost more time. The study did not test this skill's file-loading workflow or establish that repetition changes rule authority.
- These findings support testing reminders and restoring missing context. They do not support rereading every file on a timer, treating older text as weaker, or assuming repetition always helps. The context guide keeps the same need-based checks in every setting.

## What these sources do not prove

- Grade 6 English, rare standalone paragraphs, consideration of every catalog entry, and the 150/200-line policy are project rules. They are not universal accessibility requirements.
- Markdown source, rendered semantics, keyboard access, visual layout, assistive-tool behavior, and reader understanding need different checks.
- A document-tree inspection found a title, description, and ARIA links in one rendered Mermaid example. It did not test screen-reader use or comprehension.
- Keep old sources when they remain authoritative. Prefer recent primary evidence of equal fit; do not replace a current standard with a newer unrelated article.
- Recheck the owner when target support or version changes. No finite catalog covers every possible extension.

- [Agent Skills specification](https://agentskills.io/specification), accessed September 17, 2026: required frontmatter, folder naming, and optional package resources. No page update date was established.
- The [dependency research notes](dependencies.md#research-basis-and-limits) retain the supplied first-party sources, dates, and limits for reading-order decisions. Read them when checking that evidence.
