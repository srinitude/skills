# Generation contract

Every skill this factory creates must meet every rule in this file. The rule set is recursive: a generated skill that builds another skill passes this same contract on, unchanged, through its own copy of this file. No skill is exempt, the factory included.

## Layout

A skill is one directory whose name equals the frontmatter name. Through `mise run validate`, it keeps SKILL.md at the root plus `references/`, `assets/`, `examples/`, `evals/`, private implementation, and tests. Generated skills also carry mise.toml and a CI workflow at `.github/workflows/ci.yml` through `mise run ci`. Relative paths stay close to the skill root.

## Frontmatter

The file opens with three dashes at byte 0 and the fence closes on its own line. Allowed top-level fields, and no others: name, description, license, compatibility, metadata, allowed-tools.

- name: 1 to 64 characters matching `^[a-z0-9][a-z0-9._-]*$`, equal to the directory name.
- description: quoted, 1 to 1024 characters, says what the skill does and when it applies, contains "Use when", and carries the keywords a user would type.
- license: MIT unless the user directs otherwise.
- metadata: author and a quoted version string.

## Body

Keep the body under 200 lines and the file under 100000 characters. Order: title, short intro, command grammar, numbered procedure, load conditions per directory, gotchas, completion criteria. The command grammar starts with help and adds the subcommands the skill needs. Write for the least capable executor:

- Numbered steps, one action and one observable result per step.
- The full plan visible upfront, never improvised midway.
- A mechanical check after each consequential step, with an explicit branch for failure.
- A stop-and-report branch wherever required information can be missing. Guessing is the failure mode, stopping is the contract.
- One default path per job, no menus of equal options.
- Progress written to an external log file after each step.
- Completion claims backed by fresh command output, never memory.

## Ordered workflow

Every generated skill body contains one numbered workflow in the order the domain work must execute. Each step names an actual `mise run <task>` call, model-only logic, or both. A task exit proves only its deterministic contract; the model still owns meaning, causal interpretation, creative work, exceptions, and direct human-sense judgment.

Use plain control words only when they change execution. `Branch` selects one domain operation. `If` guards missing inputs, authority, failed evidence, or acceptance. `For each` processes a bounded named collection. `Repeat` returns to the lowest failed owner and states its exit condition. `Stop` names the accepted terminal state or the exact blocker. Never add decorative control flow, an unbounded loop, or a Mise pass that pretends to settle model-only judgment.

The workflow locks accepted lower owners before higher dependents. A changed lower owner invalidates affected downstream evidence. Run the narrowest current check after each consequential step, then run the integrated domain proof before completion.

## Simplicity and language

Preserve every accepted behavior with the smallest coherent structure. Keep one canonical owner per rule, one stable term per concept, one default path per job, and one explicit branch for each material failure. Remove duplicate rules and choices that do not change behavior. Do not hide required domain detail, evidence, safety, authority, or visual judgment to reduce words or files.

Use plain and direct language. Put the result first, use common words and active verbs, keep one idea per sentence, and place steps in execution order. Mechanical lint proves only its stated checks. Same-meaning human review must confirm that the skill stays clear and complete.

## Deterministic and model-owned boundary

Mise owns every deterministic command. Put schemas, parsing, validation, file generation, state transitions, task ordering, receipts, measurements, comparisons, and repeatable rollback checks in tested scripts behind one owning Mise task. The model-owned boundary keeps semantic interpretation, causal reasoning, creative work, and direct human-sense review. Machine checks cannot prove meaning or visual quality.

Choose data structures, formats, indexes, batching, and cache keys from measured access and mutation patterns. Read `references/resource-and-experiment-design.md` before making those choices. Do not cache mutable remote state, live judgment, side effects, or randomness without a captured seed. Use `mise run token-packet -- <args>` for this routed resource.

## Markdown layout

Every markdown file lays wrappable prose out as one physical line per block: a paragraph, or a list item plus its continuation lines, never holds an internal hard line break, and no maximum line length applies. Blank lines between elements stay exactly as markdown readability requires. YAML frontmatter, headings, table rows, code fences and their content, indented code, and blank lines are exempt. The writing lint enforces this rule on every markdown file.

## Examples

Every skill ships examples/ with at least one worked example per command in its grammar, and one more for the failure the skill is most likely to cause. An example is a complete run, not a fragment: the user's words, the executor's visible reply, every command with its real output and exit code, and every file the run created with its full contents. Each example names the guess it removes at the top and stays consistent with SKILL.md, so a rule change that outdates an example changes the example in the same commit. SKILL.md points at examples/ with a load condition, and the writing lint and structure validator both cover the directory. Use `mise run token-packet -- <args>` for this routed resource.

## Code

Caps for every code file: 200 lines of code per file, 30 per function or class counting its own lines, block nesting depth 3 inside any function, measured from the test declaration in tests. No work markers, mocks, stubs, or placeholder branches. Real behavior only. Prefer the standard library.

Every script supports --help with usage, exit codes, and an example. Scripts take input from flags or stdin, never from a prompt. Data goes to stdout, diagnostics to stderr. Exit 0 on success, 1 on a failed check, 2 on bad usage. Reruns are safe.

## Tests, tasks, CI

Build order is fixed and test-first: mise.toml, then the CI workflow and the tests that pin the task graph, then script tests, then scripts, then docs, then evals. A behavior starts as a failing test. Local runs and remote CI use one command, `mise run ci`. Tests cover contracts users touch: flags, exit codes, file outputs, integration boundaries. Never private internals. Use dependency edges so Mise can run independent read-only checks together. Keep mutating and live-evidence tasks outside deterministic caches.

## Evals

evals/evals.json holds at least four realistic cases with prompts, expected output, and verifiable assertions. evals/trigger-queries.json holds positive and negative trigger queries, near misses included. A skill destined for the srinitude/skills registry also emits the registry eval artifact set described in references/eval-authoring.md: manifest.json, cases.json, trigger-cases.json, contract.md, rubric.md, speed-budgets.json, and source-lineage.json carrying real sha256 hashes of the source files. Use `mise run token-packet -- <args>` for this routed resource.

An optional skill-improvement trial starts only after required work passes. Freeze the accepted baseline, evaluator, fixtures, environment, time budget, repetitions, and applicable resource measures before viewing a candidate. Change one named dimension at its smallest owner. Accept only a Pareto improvement where that dimension improves materially and no protected dimension regresses. Restore the last accepted version after a worse, invalid, or unknown result, then verify its digest.

## Reuse before building

Check for installed registry skills before writing anything new, starting with starting-point from https://github.com/srinitude/skills. Look for skills/starting-point/SKILL.md in the surrounding skills directory; the raw fallback is https://raw.githubusercontent.com/srinitude/skills/main/skills/starting-point/SKILL.md. Defer to an installed skill for the jobs its description names. Use `mise run token-packet -- <args>` for this routed resource.

## Prohibited content

No file names an agent product, an agent harness, or a company that ships one. The generic word `model` is permitted only when assigning model-only judgment or requiring a strong vision-capable model. Elsewhere use executor and describe the required action: run in a terminal, read the file, search the tree. Skills stay portable across executors, so nothing may assume host state beyond declared needs.
