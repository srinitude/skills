# Keep every Markdown file below 200 lines

- Apply a strict maximum of 199 physical lines to every Markdown file created or changed by this skill, including the skill's own Markdown files.

## Purpose and reading route

- **Reading trigger:** Read before creating files, adding content near 150 lines, or changing reading paths.
- **Prerequisites:** No other package file must be loaded first. Required companion skills must already be active.

### Count physical lines

- Count headings, blank lines, front matter, tables, and code fences.
- Count a final line even if it has no trailing newline.

## Use recursive progressive disclosure near 150 lines

- Read [placement and timing](placement.md) before choosing a route or moving detail. Keep the route under its true heading owner, after needed context and before its first active consumer.

- Progressive disclosure means keeping a file's core content in that file and moving deeper or branch-specific detail into linked Markdown files that readers load when needed.

- Begin this review during drafting, before the next planned addition would bring a file to 150 lines or more.
- Review an existing file at or above 150 lines at once.
- Do not wait for the 199-line cap.
- Apply this rule to every Markdown file created or changed, including the skill's own files.

### Create useful directories

- Before creating a nested directory, inspect its immediate parent on disk.
- That parent must already contain at least one real file directly inside it.
- A planned file, a broken link, or a file only in a deeper directory does not count.
- If the parent has no file, first save useful content there or use a fitting existing directory.
- Do not add an empty placeholder just to pass this check.
- Create one level at a time and repeat the check before each deeper level.
- This rule applies to the skill package and its output directories.

### Keep the core and move branch detail

- Define the current file's core from its own purpose and reader.
- Keep the main point, essential context, always-needed rules, main steps, and checks needed to use that file correctly.
- A child file has its own core; do not judge it only by what belongs in the root file.

- Move content outside that core into clearly named Markdown files.
- This may include long examples, detailed evidence, optional background, or instructions for a specific branch.
- Keep each topic together and give it one authoritative home.
- Reuse a fitting existing file where possible.

- Replace each moved section with a brief description, a working relative link, and a clear reading trigger such as “Read this before doing X.” Keep mandatory branch instructions mandatory when that branch applies.
- The parent must still explain what the reader needs to decide or do next.
- Moving text must not hide a duty or weaken its meaning.

- Apply the same review to every new or changed child, grandchild, and deeper file.
- Continue until each file has a clear scope, its non-core detail is placed well, and all files meet the hard cap.
- Recount after adding links, headings, and context.
- Each split must reduce the file's load of detail and create useful topic boundaries.
- Do not create endless one-child wrappers or move the same oversized block down through new files.

- Use 150 lines as a review and offloading trigger, not a second hard cap.
- A file may keep 150-199 lines only when further splitting would damage its core meaning, exact content, or readability; record the reason.
- Never meet either target by dropping meaning, removing useful spacing, hiding text, or packing unrelated ideas into long lines.
- If an indivisible exact block or fixed single-file requirement makes the 199-line cap impossible, state the conflict and request the smallest needed decision.
- Do not claim compliance.

## Keep dependencies free of cycles

- Treat A → B as a dependency whenever A requires B to be read, loaded, or included to understand or carry out its content, even if that requirement appears in prose rather than a link.
- Check the complete dependency graph for the governed file set, including dependencies reached through other files.

- Before accepting each split or new dependency, verify that it creates no self-dependency or route that leads back to its starting file.
- Repeat this check across the whole final set.
- Resolve paths consistently so alternate paths to the same file cannot hide a cycle.
- A shared reference used by several files is allowed if it creates no cycle.

- Keep return links for navigation, clearly marked as navigation only.
- They must not instruct readers or agents to reload a parent or serve as required context.
- A child must not depend on a parent that already depends on that child.
- If a link supplies required context, count it as a dependency regardless of its label.
- Restructure shared material or reading order to remove the cycle without losing meaning.

- At use time, follow the context guide loaded from the entry file.
- Track the active loading path to detect cycles, and track completed reads to avoid unnecessary repeated loading without blocking justified later rereads.
- If a cycle is found, report its exact path and stop the affected loading or delivery.
- Skipping a repeated file is not proof that the dependency graph is sound.
- Do not claim an unresolved or inaccessible dependency was checked.

- Keep every moved section reachable from the entry file through clear reading triggers.
- Verify file and heading links, meaning-ledger locations, consistent terms, and reading order after each split.
- Complete the same checks at every depth and across the final set.

## Set the reading order

- Read [dependency types and ordering](dependencies.md) before mapping reading prerequisites. Separate real reading needs from execution dependencies and navigation.

- A prerequisite supplies rules, terms, facts, or decisions needed by another file or section. State each file's prerequisites and reading trigger.
- Dependencies dictate reading order for every file, at every depth. Include rules carried by prose, imports, includes, shared content, and required external references.
- Read prerequisites before dependent content. Keep always-needed context in the entry path; load optional branches only when their triggers apply.
- Filename, link position, folder depth, and alphabetical order do not create dependencies. Choose a clear order for independent files; do not invent prerequisites.
- A router may be read first to discover the required path. Do not use its dependent instructions until the required context has been loaded.
- After each split, move, or dependency change, recheck the entire affected path, including missing files, anchors, definitions, and cycles.
