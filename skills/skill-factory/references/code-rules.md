# Code rules

These caps bind every code file in this skill and in every generated skill. `mise run lint-code` owns the complete tree check.

## Size and shape

- 200 lines of code per file at most. Blank lines and comments do not count.
- 30 lines of code per function or class, counting its own lines and skipping nested definitions.
- Block nesting caps at depth 3 inside any function. Test functions count depth from the test declaration.
- No work markers, mocks, stubs, or placeholder branches. Every code path does real work. Split a file before it hits a cap.

## Native checker boundary

`mise run lint-code` checks owned Python, shell, JavaScript and TypeScript files. Its `check-runtime` prerequisite first installs the native lock through `mise run setup-runtime`, then checks owned TypeScript with the declared compiler. The source parser counts actual syntax, excludes comments from code lines, and retains multiline literal content. Installed dependencies, caches, bytecode and tool state remain outside owned-file checks; owned symlinks fail.

The managed environment pins Node and npm, with exact compiler/schema dependencies in package.json and package-lock.json. `mise run check-runtime` uses strict application checking with `skipLibCheck`, matching the verified upstream and repository configuration. It does not prove that every dependency declaration is sound, nor that application runtime behavior is correct. Keep failed dependency checks and actual runtime/API probes as separate evidence. The source parser enforces code shape; domain and human proof remain required.

Scaffolding copies the same runtime contract and code-check owners. `mise run standardize-target` replaces only a recognized prior checker or the current exact checker. Conflicting runtime manifests, tool pins or unreviewed checker customizations require explicit reconciliation before that migration; rejection preserves the original target.

## Script interface

Every implementation command behind a Mise task meets one interface:

- prints usage, exit codes, and an example with --help
- takes input from flags or stdin, never from an interactive prompt
- sends data to stdout and diagnostics to stderr
- exits 0 on success, 1 on a failed check or action, 2 on a usage or input error
- behaves the same on a rerun, so retries are safe
- prefers the standard library; document any needed dependency in the skill body

## What order do I build in?

The order is fixed and test-first:

1. mise.toml, so every job has its one command.
2. The CI workflow plus the behavior tests that pin the task graph: every required task exists, CI invokes every check job in order, every task carries a description, and the workflow runs the single entry point.
3. Tests for each script, written against the real interface.
4. The scripts, until those tests pass.
5. Docs, checked by the writing lint.
6. Evals.

Red before green: a new behavior starts as a failing test. Tests exercise what users touch (flags, exit codes, file outputs, the boundaries between parts), never private internals. A test that breaks when a private helper gets renamed is testing the wrong thing.
