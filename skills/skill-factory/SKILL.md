---
name: skill-factory
description: "Use when a workflow, recipe, or capability needs to be packaged as an agent skill, or when an existing skill needs scaffolding, validation, linting, or evals. Covers requests to build, create, generate, scaffold, check, or evaluate a skill: a folder holding SKILL.md, scripts, tests, a task graph, CI, and eval cases. Applies even when the request says playbook, runbook, or reusable workflow instead of skill."
license: MIT
metadata:
  author: Kiren Srinivasan
  version: "0.1.0"
---

# Skill Factory

Skill Factory turns a request into a working agent skill: a directory with SKILL.md, scripts, tests, a task graph, CI, and evals that all pass their checks before the work counts as done. It also validates and evaluates skills that already exist.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this table and a one line summary per command. |
| new <prompt> | Build a skill that fulfills the prompt. Main path below. |
| validate <path> | Run the structure, writing, and code checks on a skill. |
| eval <path> | Check a skill's eval files, then run its cases. |
| doctor | Run scripts/doctor.py and report readiness. |

`--help` on any bundled script prints its flags, exit codes, and an example. Suppose the request matches no command, or a needed fact is missing and cannot be inferred. In this case stop, report exactly what is missing, and wait. Do not guess.

## How do I build a new skill?

This is the full plan. After each step, run the named check; when it fails, fix the cause and rerun that check before moving on.

1. Run `python3 scripts/doctor.py`. Proceed only when it prints "ready": true. Otherwise report the failing check and stop.
2. Read references/generation-contract.md in full. Every file you write must meet it.
3. Check the registry per references/registry.md. When an installed skill already covers the request, defer to it and say so instead of duplicating it.
4. Derive a name matching `^[a-z0-9][a-z0-9._-]*$` and a description that contains "Use when". One unresolvable fact: ask one question. Anything smaller: state the assumption and continue.
5. Create a progress log named <name>-build-log.md next to the new skill. Append one line after each following step.
6. Scaffold: `python3 scripts/scaffold_skill.py --name <name> --description "<description>" --dest <skills directory>`. Verify it prints "created". Exit code 2 means the name or the description broke a rule; the message says which. Fix and rerun.
7. Author in TDD order, replacing scaffold seeds where the request needs more: mise.toml tasks first, then CI contract tests, then script tests, then scripts, then docs, then evals. Read references/code-rules.md before writing code, references/writing-rules.md before writing markdown, and references/eval-authoring.md before writing evals.
8. Run `mise run ci` inside the new skill. Exit 0 required. A failing job names the file and reason; fix it and rerun until green.
9. Run `python3 scripts/validate_skill.py <path>` and confirm the last line starts with PASS.
10. Report the tree, each file's purpose, and the check output. Claims about passing checks quote the fresh run, never memory.

## How do I validate or evaluate an existing skill?

For validate <path>, run scripts/validate_skill.py, scripts/lint_writing.py, and scripts/check_code_rules.py on the path. Report every FAIL line with file and reason, then propose the fix for each. For eval <path>, run scripts/check_evals.py first; when it exits 0, run the cases per references/eval-authoring.md and grade each assertion against quoted evidence.

## What loads when?

- references/generation-contract.md: read before generating any file of a new skill. It is the recursive contract generated skills carry.
- references/writing-rules.md: read before writing or editing any markdown file.
- references/code-rules.md: read before writing any script or test.
- references/eval-authoring.md: read when authoring or grading evals.
- references/registry.md: read before any build, to reuse instead of rebuild.
- assets/: templates the scaffolder fills. Read assets/skill-template.md when you need to see what a generated SKILL.md contains.
- scripts/: the executable commands. Run them; read their source only when a check message stays unclear after one rerun.
- scripts/tests/: run through `mise run test` after changing any script.
- evals/: this skill's own cases and trigger queries, plus the registry eval artifact set described in references/eval-authoring.md. Read when measuring the factory itself.

## Which task runs which job?

Every job has one command. `mise run ci` runs the whole pipeline and is the only entry point CI uses. The pieces: test-ci, test, validate, lint-writing, lint-code, evals, doctor, and new. Remote CI comes from assets/ci/ci.yml; copy that file to .github/workflows/ci.yml in the hosting repository.

## Gotchas

- The scaffolder refuses descriptions without "Use when" and names with capitals. That is the contract working, never a bug.
- The writing lint bans em dashes plus a word list kept inside scripts/lint_writing.py. Rewrite flagged sentences; a close synonym of a banned word usually trips another rule.
- The writing lint also enforces the one line layout: every paragraph or list item is one physical line with no hard breaks and no maximum length. See references/writing-rules.md.
- Generated skills carry their own copies of the checker scripts, so they verify themselves with `mise run ci` and keep no path back to this directory.
- No file in any skill may name an agent product or a model. The test suite scans generated output for such names and fails on a hit.
- A new skill may reach the executor's index only on the next session. The files land immediately even when the index lags.

## When is the work done?

Done means all of these from fresh runs inside the new skill: `mise run ci` exits 0, validate_skill.py prints PASS, the writing lint reports 0 problems, evals hold at least four cases with both trigger labels, and the build log records every step.
