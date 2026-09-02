# Example: new line-budget skill

Guess this example removes: where a build lands, how RED becomes GREEN, and which output proves the generated skill works.

## User says

```
make me a skill that tells me whether a markdown file is over a line budget, and which section is the fattest
```

## Executor replies

```
Built `line-budget` at `/home/user/work/line-budget`. Its budget task reads one Markdown file and returns total lines, the overage, and the largest heading section. The full CI and invocation receipts pass.

$ mise run budget -- --input evals/files/long-note.md --max 10
{"file":"evals/files/long-note.md","lines":14,"max":10,"over":true,"over_by":4,"longest_section":{"heading":"Long note","lines":14}}
exit 1

$ mise run ci
Finished successfully
exit 0
```

## Commands run

```
$ mise run new -- --name line-budget --description "Use when Markdown line budgets or largest sections must be measured." --dest /home/user/work
{"created":"/home/user/work/line-budget","next":"run mise run ci inside the new skill","blocked_until":"every scaffold placeholder is replaced"}
exit 0

$ mise run test
FAILED (failures=3)
exit 1

$ mise run test
Ran 18 tests
OK
exit 0

$ mise run domain-research-policy
domain research: 0 problems
exit 0

$ mise run use-case-policy
use-case contract: 0 problems
exit 0

$ mise run task-graph-policy
task graph: 0 problems
exit 0

$ mise run decision-policy
decision records: 0 problems
exit 0

$ mise run ci
Finished successfully
exit 0
```

## Files created

The package contains SKILL.md, mise.toml, one CI workflow, domain references, machine-readable assets, private implementation and behavior tests, real examples, and eval fixtures. Markdown names only Mise task interfaces; `mise.toml` owns private implementation paths.

## What the run proves

The first test run proves RED before implementation. The second proves the behavior contract, while the policy tasks prove current research coverage, domain-specific primitives, one acyclic task path, and motivated decisions. The fixture run proves the user-visible overage result. CI proves the integrated package but not the semantic truth of its domain claims; source review supplies that judgment.
