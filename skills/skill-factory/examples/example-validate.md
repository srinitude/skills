# Example: validate one passing and one failing skill

Guess this example removes: the difference between a target-validation failure and a passing package.

## User says

```
check whether the skill at work/broken-skill meets the factory contract
```

## Executor replies

```
The target fails. Its trigger omits "Use when", required package owners are absent, one implementation construct exceeds the nesting cap, and its eval set is incomplete. The passing comparison reports zero problems from every selected checker.
```

## Commands run

```
$ mise run validate-target -- /home/user/work/broken-skill
[validate_skill]
FAIL description must state "Use when" the skill applies
FAIL missing required directory: references/
FAIL missing required directory: assets/
FAIL missing required directory: examples/
FAIL missing required directory: evals/
FAIL missing evals/evals.json
FAIL missing mise.toml task graph
FAIL broken-skill: 7 problems
[lint_writing]
checked 1 files, 2 problems
[check_code_rules]
[private implementation file]:1: walk nesting is 4; cap is 3
checked 1 files, 1 problems
[check_evals]
evals.json: needs at least 4 cases
missing evals/trigger-queries.json
eval checks: 2 problems
exit 1

$ mise run validate-target -- /home/user/work/line-budget
[validate_skill]
PASS line-budget: 0 problems
[lint_writing]
checked 8 files, 0 problems
[check_code_rules]
checked 14 files, 0 problems
[check_placeholders]
checked 9 files, 0 placeholders
[check_domain_research]
domain research: 0 problems
[check_use_case_contract]
use-case contract: 0 problems
[check_task_graph]
task graph: 0 problems
[check_decision_records]
decision records: 0 problems
exit 0
```

## Files created

None. Validation reads and reports.

## What the run proves

The target task selects the same factory checks for both packages. A zero exit proves only those stated contracts. The failed output identifies the lowest owning class for each repair without exposing private implementation paths in Markdown.
