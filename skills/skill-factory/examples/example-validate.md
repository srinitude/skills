# Example: validate <path>, one passing skill and one failing skill

Guess this example removes: the exact shape of a PASS line, the shape of a FAIL block, and which of the four checks catches which defect.

## User says

```
can you check whether the skill at work-examples/broken/broken-skill meets the contract? someone wrote it by hand
```

## Executor replies

```
Nine structure problems, two writing problems, one code problem, two eval problems. Every line below is from a run just now, and each one has a fix.

Structure, from validate_skill.py:
- description must state "Use when": add the trigger phrase to the frontmatter description.
- references/, assets/, examples/, evals/, scripts/tests/ are missing: create them and reference each from the body with a load condition.
- body never references scripts/: add the load condition line for scripts/.
- missing evals/evals.json and missing mise.toml: copy the templates from assets/ and fill them.

Writing, from lint_writing.py:
- SKILL.md:9 heading nested past three levels: promote it to a level three heading.
- SKILL.md:12 hard line break inside a wrappable block: join the two physical lines into one.

Code, from check_code_rules.py:
- scripts/deep.py:1 walk nesting is 4: pull the inner loop into its own function.

Evals, from check_evals.py:
- evals.json needs at least 4 cases and trigger-queries.json is missing: write four real cases plus positive and negative queries.

For comparison, here is the same set of checks on a skill that passes.
```

## Commands run

```
$ python3 scripts/validate_skill.py /home/user/workspace/test/t-factory/work-examples/broken/broken-skill
FAIL description must state "Use when" the skill applies
FAIL missing required directory: references/
FAIL missing required directory: assets/
FAIL missing required directory: examples/
FAIL body never references scripts/
FAIL missing required directory: evals/
FAIL missing required directory: scripts/tests/
FAIL missing evals/evals.json
FAIL missing mise.toml task graph
FAIL broken-skill: 9 problems
exit 1

$ python3 scripts/lint_writing.py /home/user/workspace/test/t-factory/work-examples/broken/broken-skill
/home/user/workspace/test/t-factory/work-examples/broken/broken-skill/SKILL.md:9: heading nested past three levels
/home/user/workspace/test/t-factory/work-examples/broken/broken-skill/SKILL.md:12: hard line break inside a wrappable block; join the block into one line
checked 1 files, 2 problems
exit 1

$ python3 scripts/check_code_rules.py /home/user/workspace/test/t-factory/work-examples/broken/broken-skill
/home/user/workspace/test/t-factory/work-examples/broken/broken-skill/scripts/deep.py:1: walk nesting is 4; cap is 3
checked 1 files, 1 problems
exit 1

$ python3 scripts/check_evals.py /home/user/workspace/test/t-factory/work-examples/broken/broken-skill
evals.json: needs at least 4 cases
missing evals/trigger-queries.json
eval checks: 2 problems
exit 1

$ python3 scripts/validate_skill.py /home/user/workspace/test/t-factory/work-examples/line-budget
PASS line-budget: 0 problems
exit 0

$ python3 scripts/lint_writing.py /home/user/workspace/test/t-factory/work-examples/line-budget
checked 5 files, 0 problems
exit 0

$ python3 scripts/check_code_rules.py /home/user/workspace/test/t-factory/work-examples/line-budget
checked 10 files, 0 problems
exit 0

$ python3 scripts/check_placeholders.py /home/user/workspace/test/t-factory/work-examples/line-budget
checked 7 files, 0 placeholders
exit 0
```

## Files created

None. Validation reads and reports.

## What the run proves

A passing run prints one line: PASS, the directory name, and a zero count. A failing run prints one FAIL line per problem and then the same summary line with the count, so the last line is enough to decide and the lines above it are enough to fix. The writing lint and the code checker print path and line instead, and both end with a "checked N files, M problems" summary.
