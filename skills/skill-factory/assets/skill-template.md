---
name: {{NAME}}
description: "{{DESCRIPTION}}"
license: MIT
metadata:
  author: skill-factory
  version: "0.1.0"
---

# {{NAME}}

{{DESCRIPTION}}

SCAFFOLD-PLACEHOLDER: rewrite this whole line as two or three sentences naming the result this skill produces, then rerun `python3 scripts/check_placeholders.py .` until it prints 0 placeholders.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this command table and the frontmatter description. |
| info | Run `python3 scripts/skill_info.py` and report the JSON. |
| check | Run the full pipeline and report each job with its exit code. |

Suppose the request matches none of these. In this case stop, say what is missing, and wait. Do not guess.

## How do I run the work?

1. Pick the command from the table that matches the request.
2. Before the first real task, look for a scoping skill named starting-point in the surrounding skills directory. If its SKILL.md is present, apply it first. If absent, continue without it.
3. Run the command. Scripts live in scripts/ and run by absolute path with no prompts. Every script prints usage with --help.
4. Verify with `mise run ci` from the skill root. A job that fails names the file and the reason; fix the cause and rerun until the exit code is 0.
5. When the task runner is missing, take the degraded path below instead of skipping step 4.
6. Report the result and paste the command output as evidence, including the exit code of each command you ran.

## What runs when the task runner is missing?

`mise run ci` exits 127 with "mise: command not found" on a machine without the runner. Run these six commands from the skill root instead, in this order, and report every exit code.

```
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
python3 scripts/validate_skill.py .
python3 scripts/lint_writing.py .
python3 scripts/check_code_rules.py .
python3 scripts/check_placeholders.py .
python3 scripts/check_evals.py .
```

State the claim exactly this way: "every job in mise.toml passed as a direct command; `mise run ci` itself did not run here". Never claim `mise run ci` exited 0 when it never ran.

## What does a passing run print?

Each check prints one summary line. Compare against these.

| Command | Passing last line |
| --- | --- |
| `python3 scripts/validate_skill.py .` | `PASS {{NAME}}: 0 problems` |
| `python3 scripts/lint_writing.py .` | `checked 4 files, 0 problems` |
| `python3 scripts/check_code_rules.py .` | `checked 7 files, 0 problems` |
| `python3 scripts/check_placeholders.py .` | `checked 5 files, 0 placeholders` |
| `python3 scripts/check_evals.py .` | `eval checks: 0 problems` |

The file counts grow as the skill grows. The trailing count of problems is the part that must read 0.

## What loads when?

- Read references/generation-contract.md before growing this skill or building another one. Every new file must meet that contract.
- Read references/decisions.md when you need the reasoning behind an earlier change. Append one dated line per new decision.
- Read examples/example-first-run.md before the first run of this skill, and whenever a reply needs the shape of a complete run. Add one example per command in the table above plus one for the failure this skill is most likely to cause.
- Copy assets/eval-case-template.json when adding an eval case.
- Run the tests in scripts/tests/ through `mise run test` after any script change.
- Update evals/evals.json whenever behavior changes, and replace every seed case before shipping.

## Gotchas

- The frontmatter description is the only trigger text. Keep it under 1024 characters and keep the words "Use when" in it.
- Keep this file under 200 lines. Move detail into references/.
- Never name an agent product or a model in any file of this skill.
- The scaffold ships placeholder text on purpose. `python3 scripts/check_placeholders.py .` exits 1 until every placeholder is gone, so a scaffold cannot ship as finished work.

## When is the work done?

Done needs fresh evidence from one run: the six commands above all exit 0 (or `mise run ci` exits 0 where the runner exists), `python3 scripts/validate_skill.py .` prints PASS, the writing lint reports 0 problems, the placeholder check reports 0 placeholders, evals/evals.json holds at least 4 cases that describe this skill's real job, and examples/ holds one worked example per command with real output pasted in.
