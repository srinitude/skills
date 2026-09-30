# Build and verify the skill

- Follow create-and-update-skill's package and validation process.

## Purpose and reading route

- **Reading trigger:** Read before creating, changing, or testing this skill.
- **Prerequisites:** No other package file must be loaded first. Required companion skills must already be active.

- Before behavior tests, load [the concrete cases](../evals/behavior-cases.json).
- Case expectations are test inputs, not proof that a test passed.
- Read the [heading cases](headings.md#check-the-actual-structure), [hierarchy cases](hierarchy.md#record-and-validate-the-decisions), [disclosure cases](placement.md#check-placement-before-acceptance), [dependency cases](dependencies.md#test-the-reading-contract), and [coverage cases](coverage.md#prove-input-coverage-before-acceptance) before testing those contracts. Run them and record actual outcomes; specifications alone are not results.

- Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

### Cover required cases

- Include runnable checks for file length, local links and anchors, and dependency cycles, plus behavior cases that cover:

- Short input that needs only a few Markdown forms.
- Rich content where several supported forms help.
- Files at 149, 150, 151, 199, and 200 lines, including an edit that crosses 150.
- A child that also needs splitting, followed by a deeper file that needs the same review.
- An empty parent directory, a planned file, a broken link, and a parent with a useful file. Check the parent on disk before each new directory level; never add filler to pass.
- A file whose remaining 150-199 lines are all core or exact material.
- Direct, indirect, and self-dependency cycles, including alternate paths to one file.
- Shared references without cycles, navigation-only return links, and a required-context link mislabeled as navigation.
- Exact quotes, code, and rules with narrow exceptions.
- Source contradictions, unsupported renderer features, and missing skills.
- A file split that could lose context or leave a broken reference.
- A copied package in a different folder, with dependencies found by name and working relative links. Validate its Agent Skills metadata and run the available checks from that copy.
- Unchanged source text that is still available and should not be fetched again.
- An early read that remains relevant, and an early read whose needed text was later removed or reduced to an incomplete summary.
- Changed files, partial reads, newly relevant branches, and exact wording needed after a long gap.
- A critical rule buried among later material, plus a focused reminder that preserves its exceptions.
- A repeated low-authority instruction that must not override a higher-priority rule.
- A valid reread after a completed visit, compared with an invalid active loading cycle.
- A large file set whose files each pass the line limit but together exceed the working context.
- A required full read that must not be replaced with a summary.
- A skill package whose entry file is clear but whose catalog, examples, or child files contain unclear prose.
- Output files that read clearly alone but use conflicting terms, missing definitions, or unclear cross-file reading triggers.
- Dense catalog entries or table cells that meet line limits but remain hard to read.
- A late wording change or file split that invalidates an earlier language check.
- A reading-level score that passes while a required condition is missing, plus exact technical text that must not be simplified.
- A final review that misses a child file or substitutes a sample for the full output set.

- Meaningful titles and sections in every file, including a tiny file and a misleading heading whose label disagrees with its content.
- Ordered procedures, unordered rules, a justified paragraph, and exact fragments that cannot take headings without changing their content.
- Every catalog candidate considered, including an unknown form that must remain unresolved until checked.
- Both required skills used during intake, research, planning, drafting, handoffs, repairs, and final review; a missing skill stops dependent work.
- Rendered faults: a table without headers, color-only status, an inaccessible disclosure, clipped enlarged text, and an informative image without an alternative.
- Separate source, layout, keyboard, document-tree, assistive-tool, and reader checks. An unavailable check must stay reported as not run.

### Compare context-loading behavior

- Test the context workflow with both short and long histories, distracting material, narrow context budgets, and several runs.
- Compare a clear single statement, a focused reminder, and full repetition where it is safe to test.
- Check actual rule-following, preserved meaning, successful retrieval, read count, and text cost.
- Verify these from source and output traces rather than self-reported confidence.
- Keep mandatory checks fixed while comparing approaches.
- Do not claim universal gains or a passing case that was not run.

### Accept only checked results

- Accept the result only when required checks pass: meaning is preserved, no material logic fault remains unresolved, editable prose passes human-language review, Markdown fits the target, local links and anchors work, recursive disclosure keeps each file focused, all context needed for each action is available, rereads have a clear purpose, the complete checked dependency graph has no cycles, and every output Markdown file has at most 199 lines.
- Separate mechanical checks from semantic review and actual reader testing.

- The language and meaning acceptance checks include the final whole-set reviews defined above for the skill package and all outputs, including Markdown and non-Markdown results.
- Passing a size, syntax, link, or reading-level check alone cannot satisfy it.

- Return the created skill's location, brief usage instructions, and the checks run with their results.
- Report any unresolved limit plainly.
- Do not present a checklist or an unrun test as proof of success.
