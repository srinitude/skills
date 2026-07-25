---
name: skill-factory
description: "Use when a workflow, recipe, or capability needs to be packaged as an agent skill, or when an existing skill needs scaffolding, validation, linting, or evals. Covers requests to build, create, generate, scaffold, check, or evaluate a skill: a folder holding SKILL.md, scripts, tests, a task graph, CI, and eval cases. Applies even when the request says playbook, runbook, or reusable workflow instead of skill."
license: MIT
metadata:
  author: Kiren Srinivasan
  version: "0.1.0"
---

# Skill Factory

Skill Factory turns a request into a working agent skill: a directory with SKILL.md, scripts, tests, worked examples, a task graph, CI, and evals that all pass their checks before the work counts as done. It also validates and evaluates skills that already exist.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this table and a one line summary per command. |
| new <prompt> | Build a skill that fulfills the prompt. Main path below. |
| validate <path> | Run the structure, writing, code, and placeholder checks on a skill. |
| eval <path> | Check a skill's eval files, then run its cases. |
| doctor | Run scripts/doctor.py and report readiness. |

`--help` on any bundled script prints its flags, exit codes, and an example. Suppose the request matches no command, or a needed fact is missing and cannot be inferred. In this case stop, report exactly what is missing, and wait. Do not guess.

## How do I build a new skill?

This is the full plan. After each step, run the named check; when it fails, fix the cause and rerun that check before moving on.

1. Run `python3 scripts/doctor.py`. Exit 0 means build, in full mode or in degraded mode. Exit 1 with "ready": false means stop: report the failing required check and wait.
2. When the report says "mode": "degraded", the task runner is absent. Use the six commands in its "fallback" list wherever this plan says `mise run ci`, and take the reporting wording from examples/example-doctor.md.
3. Read references/generation-contract.md in full. Every file you write must meet it.
4. Check the registry per references/registry.md. When an installed skill already covers the request, defer to it and say so instead of duplicating it.
5. Derive a name matching `^[a-z0-9][a-z0-9._-]*$` and a description that contains "Use when". One unresolvable fact: ask one question. Anything smaller: state the assumption in the reply and continue. Unresolvable means every path of the build changes with the answer; see the closing section of examples/example-new-skill.md for one case on each side.
6. Pick the destination. Default is the skills directory that holds this factory, so the new skill sits beside starting-point. When that directory is read only or the user named a working directory, use that instead and say in the reply that the registry check inside the new skill will find nothing there.
7. Create a progress log named <name>-build-log.md next to the new skill, never inside it. Append one line after each following step.
8. Scaffold: `python3 scripts/scaffold_skill.py --name <name> --description "<description>" --dest <destination>`. It prints a JSON object with created, files, next, and blocked_until. Exit code 2 means the name or the description broke a rule; the message says which. Fix and rerun.
9. Author in TDD order: mise.toml tasks first, then the CI contract test the scaffold ships, then script tests, then scripts, then docs, then examples, then evals. Read references/code-rules.md before writing code, references/writing-rules.md before writing markdown, and references/eval-authoring.md before writing evals.
10. Replace every seeded line. The scaffold marks each one with a sentinel token in SKILL.md, evals/evals.json, evals/trigger-queries.json, and examples/example-first-run.md. The seeds are about a generic skill, so rewrite them around the user's real job rather than editing them.
11. Run `mise run ci` inside the new skill, or the six fallback commands. Exit 0 required on each. A failing job names the file and reason; fix it and rerun until green.
12. Run `python3 scripts/validate_skill.py <path>` and `python3 scripts/check_placeholders.py <path>` from this directory against the new skill. Confirm PASS and 0 placeholders.
13. Report the tree with one line of purpose per file, the assumption you made, and the fresh check output. Claims about passing checks quote the run, never memory. Model the reply on examples/example-new-skill.md.

## How do I validate or evaluate an existing skill?

For validate <path>, run scripts/validate_skill.py, scripts/lint_writing.py, scripts/check_code_rules.py, and scripts/check_placeholders.py on the path. Report every FAIL line with file and reason, then propose the fix for each; examples/example-validate.md shows the shape. For eval <path>, run scripts/check_evals.py first; when it exits 0, run the cases per references/eval-authoring.md and grade each assertion against quoted evidence, as in examples/example-eval.md.

## What does a passing check print?

Compare every run against these lines. The file counts grow with the skill; the trailing count of problems is the part that must read 0.

| Command | Passing last line | Exit |
| --- | --- | --- |
| `python3 scripts/validate_skill.py .` | `PASS skill-factory: 0 problems` | 0 |
| `python3 scripts/lint_writing.py .` | `checked 17 files, 0 problems` | 0 |
| `python3 scripts/check_code_rules.py .` | `checked 19 files, 0 problems` | 0 |
| `python3 scripts/check_placeholders.py .` | `checked 21 files, 0 placeholders` | 0 |
| `python3 scripts/check_evals.py .` | `eval checks: 0 problems` | 0 |
| `python3 scripts/doctor.py` | JSON with `"ready": true` and a `"mode"` of full or degraded | 0 |

Failure shapes: validate_skill.py prints one `FAIL <reason>` line per problem before its summary, the two lints print `path:line: message`, check_evals.py prints one message per defect, and every one of them ends with the same summary line carrying a count above zero. Full transcripts of both sides live in examples/.

## What loads when?

- references/generation-contract.md: read before generating any file of a new skill. It is the recursive contract generated skills carry.
- references/writing-rules.md: read before writing or editing any markdown file.
- references/code-rules.md: read before writing any script or test.
- references/eval-authoring.md: read when authoring or grading evals.
- references/registry.md: read before any build, to reuse instead of rebuild.
- examples/example-new-skill.md: read before the first build of a session, and whenever the reply for a build needs its shape.
- examples/example-placeholder-scaffold-caught.md: read when a check reports placeholders, or before claiming any build is done.
- examples/example-doctor.md: read when the doctor reports degraded mode or exits 1.
- examples/example-validate.md and examples/example-eval.md: read when running the validate or eval commands.
- examples/example-help.md: read when answering "what can this do".
- assets/: templates the scaffolder fills. Read assets/skill-template.md when you need to see what a generated SKILL.md contains.
- scripts/: the executable commands. Run them; read their source when a check message stays unclear after one rerun, or when drafting markdown against the word lists in scripts/lint_writing.py.
- scripts/tests/: run through `mise run test` after changing any script.
- evals/: this skill's own cases and trigger queries, plus the registry eval artifact set described in references/eval-authoring.md. Read when measuring the factory itself.

## Which task runs which job?

Every job has one command. `mise run ci` runs the whole pipeline: test-ci, test, validate, lint-writing, lint-code, lint-placeholders, evals. The doctor and new tasks sit outside it. Remote CI comes from assets/ci/ci.yml; copy that file to .github/workflows/ci.yml in the hosting repository. Where the task runner is absent, run the six commands the doctor prints and say so in the report.

## Gotchas

- A fresh scaffold fails on purpose. It passes structure, writing, code, and eval schema checks while `check_placeholders.py` exits 1, so boilerplate cannot ship as finished work.
- The scaffolder refuses descriptions without "Use when" and names with capitals. That is the contract working, never a bug.
- The writing lint bans em dashes plus a word list kept inside scripts/lint_writing.py. Rewrite flagged sentences; a close synonym of a banned word usually trips another rule. references/writing-rules.md says where the two lists live and when reading them beats guessing.
- The writing lint reads every markdown file in the tree, eval fixtures under evals/files/ included, so a fixture also obeys the one line layout.
- Generated skills carry their own copies of the checker scripts, so they verify themselves and keep no path back to this directory.
- No file in any skill may name an agent product or a model. The test suite scans this scaffolder's output for such names, which covers the generated bytes at creation time and not what an author adds later.
- A new skill may reach the executor's index only on the next session. The files land immediately even when the index lags.

## When is the work done?

Done means all of these from fresh runs inside the new skill: every job passes with exit 0 (`mise run ci` where the runner exists, otherwise the six fallback commands, reported as such), validate_skill.py prints PASS, the writing lint reports 0 problems, check_placeholders.py reports 0 placeholders, evals hold at least four cases written around the user's real job, examples/ holds one worked example per command in the new skill's grammar plus one for its likely failure, and the build log records every step.
