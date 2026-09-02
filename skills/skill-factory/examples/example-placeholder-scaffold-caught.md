# Example: the failure this skill causes most, a scaffold shipped as finished work

Guess this example removes: whether a fresh scaffold that passes the structure, writing, code, and eval checks counts as a delivered skill.

## User says

```
make me a skill that turns a messy meeting transcript into a decision log
```

## The failing reply, and why it is wrong

```
Built it. decision-log is at ./work/decision-log and every check is green: PASS decision-log: 0 problems, checked 3 files 0 problems, checked 6 files 0 problems, eval checks: 0 problems, 2 tests OK.
```

That reply is true about the checks and false about the skill. Nothing in the tree reads a transcript. The intro line still carries the scaffold sentinel, the four eval cases still describe a generic request, and the worked example is a stub. Four green checks plus a build log satisfied the old completion criteria, so the laziest possible run was reportable as done.

## What the checks print on an untouched scaffold now

```
$ mise run validate
PASS line-budget: 0 problems
exit 0

$ mise run lint-writing
checked 4 files, 0 problems
exit 0

$ mise run lint-code
checked 8 files, 0 problems
exit 0

$ mise run evals
eval checks: 0 problems
exit 0

$ mise run lint-placeholders
SKILL.md:14: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
evals/evals.json:6: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
evals/evals.json:7: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
evals/evals.json:9: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
evals/evals.json:10: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
evals/trigger-queries.json:2: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
examples/example-first-run.md:5: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
examples/example-first-run.md:15: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
examples/example-first-run.md:23: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
examples/example-first-run.md:33: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
examples/example-first-run.md:37: scaffold sentinel SCAFFOLD-PLACEHOLDER still present
checked 6 files, 26 placeholders
exit 1
```

The `mise run lint-placeholders` listing above is trimmed in the middle: the real run printed 26 lines, 17 of them from evals/evals.json. The four other checks still pass, which is the point. Structure, writing, code shape, and eval schema say nothing about whether the skill does the requested job, so one more check carries that weight.

## The same tree after the build

```
$ mise run lint-placeholders
checked 7 files, 0 placeholders
exit 0
```

## What the executor must say when the gate is red

```
Not done. The scaffold exists and four checks pass, and `mise run lint-placeholders` exits 1 with 26 hits across SKILL.md, evals/evals.json, evals/trigger-queries.json, and examples/example-first-run.md. Those files still hold seeded text, so the skill does not do the job yet. Next: write the transcript scan, its tests, the real eval cases, and the worked example, then rerun.
```

## Files created

None by the failing path. The scaffold already exists; the work is the rewrite.

## What the run proves

A fresh scaffold now exits 1 on the pipeline, so "every check is green" cannot be said about untouched boilerplate. The gate clears only when every seeded line in SKILL.md, the evals, and the worked example is replaced with content about the requested job.
