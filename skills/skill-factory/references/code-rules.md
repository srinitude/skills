# Code rules

These caps bind every code file in this skill and in every generated skill. The checker is scripts/check_code_rules.py, and `mise run lint-code` runs it over the whole tree.

## Size and shape

- 200 lines of code per file at most. Blank lines and comments do not count.
- 30 lines of code per function or class, counting its own lines and skipping nested definitions.
- Block nesting caps at depth 3 inside any function. Test functions count depth from the test declaration.
- No work markers, mocks, stubs, or placeholder branches. Every code path does real work. Split a file before it hits a cap.

## Script interface

Every script under scripts/ meets one interface:

- prints usage, exit codes, and an example with --help
- takes input from flags or stdin, never from an interactive prompt
- sends data to stdout and diagnostics to stderr
- exits 0 on success, 1 on a failed check or action, 2 on a usage or input error
- behaves the same on a rerun, so retries are safe
- prefers the standard library; document any needed dependency in the skill body

## What order do I build in?

The order is fixed and test-first:

1. mise.toml, so every job has its one command.
2. The CI workflow plus the tests that pin the task graph.
3. Tests for each script, written against the real interface.
4. The scripts, until those tests pass.
5. Docs, checked by the writing lint.
6. Evals.

Red before green: a new behavior starts as a failing test. Tests exercise what users touch (flags, exit codes, file outputs, the boundaries between parts), never private internals. A test that breaks when a private helper gets renamed is testing the wrong thing.
