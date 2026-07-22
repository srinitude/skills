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

This skill was scaffolded by a skill factory. Replace this paragraph with two or three sentences on the result the skill produces.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this command table and the frontmatter description. |
| info | Run `python3 scripts/skill_info.py` and report the JSON. |
| check | Run `mise run ci` from the skill root and report each job. |

Suppose the request matches none of these. In this case stop, say what is missing, and wait. Do not guess.

## How do I run the work?

1. Pick the command from the table that matches the request.
2. Before the first real task, look for a scoping skill named starting-point in the surrounding skills directory. If its SKILL.md is present, apply it first. If absent, continue without it.
3. Run the command. Scripts live in scripts/ and run by absolute path with no prompts. Every script prints usage with --help.
4. Verify with `mise run ci`. A job that fails names the file and the reason; fix the cause and rerun until the exit code is 0.
5. Report the result and paste the command output as evidence.

## What loads when?

- Read references/generation-contract.md before growing this skill or building another one. Every new file must meet that contract.
- Read references/decisions.md when you need the reasoning behind an earlier change. Append one dated line per new decision.
- Copy assets/eval-case-template.json when adding an eval case.
- Run the tests in scripts/tests/ through `mise run test` after any script change.
- Update evals/evals.json whenever behavior changes.

## Gotchas

- The frontmatter description is the only trigger text. Keep it under 1024 characters and keep the words "Use when" in it.
- Keep this file under 200 lines. Move detail into references/.
- Never name an agent product or a model in any file of this skill.

## When is the work done?

Done needs fresh evidence, all four checks in one run: `mise run ci` exits 0, `python3 scripts/validate_skill.py .` prints PASS, the writing lint reports 0 problems, and evals/evals.json holds at least 4 cases.
