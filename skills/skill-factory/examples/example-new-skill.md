# Example: new <prompt>, a complete build

Guess this example removes: how much of a scaffold gets deleted, where the new skill and its build log land, what red then green looks like, and which output lines count as proof.

## User says

```
make me a skill that tells me whether a markdown file is over a line budget, and which section is the fattest
```

## Executor replies

```
Built it. The skill is line-budget, at /home/user/workspace/test/t-factory/work-examples/line-budget, and every check is green.

How it works: scripts/check_budget.py reads one markdown file, counts physical lines, groups them under the nearest heading, and prints one JSON object. Exit 0 means inside the budget, exit 1 means over it, exit 2 means the path does not exist. The exit code is the gate, so a hook can call it without parsing the JSON.

$ python3 scripts/check_budget.py --input evals/files/long-note.md --max 10
{"file": "evals/files/long-note.md", "lines": 14, "max": 10, "over": true, "over_by": 4, "longest_section": {"heading": "Long note", "lines": 14}}
exit 1

Build order was test first: mise.toml, then scripts/tests/test_check_budget.py (red, 3 failures), then scripts/check_budget.py (green, 13 tests OK), then SKILL.md and the worked example, then the evals.

Checks, all from one fresh run inside the new skill: 13 tests OK, PASS line-budget: 0 problems, checked 5 files, 0 problems, checked 10 files, 0 problems, checked 7 files, 0 placeholders, eval checks: 0 problems. Every job in mise.toml passed as a direct command; mise run ci itself did not run here, since the task runner is absent in this environment.

One assumption I made without asking: the budget is a flag with a default of 200, not a value stored in a config file. Say the word if you want it read from a file.
```

## Commands run

```
$ python3 scripts/scaffold_skill.py --name line-budget --description "Use when a markdown file or a set of markdown files must stay under a line budget, or when a document needs its longest sections found before an edit." --dest /home/user/workspace/test/t-factory/work-examples
{"created": "/home/user/workspace/test/t-factory/work-examples/line-budget", "files": 17, "next": "run mise run ci inside the new skill", "blocked_until": "every SCAFFOLD placeholder is replaced; check_placeholders.py exits 1 until then"}
exit 0

$ python3 -m unittest discover -s scripts/tests -p 'test_*.py'
FAIL: test_help_documents_usage_and_exit_codes (test_check_budget.TestBudgetCli.test_help_documents_usage_and_exit_codes)
AssertionError: 2 != 0
FAIL: test_file_over_budget_exits_one (test_check_budget.TestBudgetReport.test_file_over_budget_exits_one)
AssertionError: 2 != 1
FAIL: test_file_within_budget_exits_zero (test_check_budget.TestBudgetReport.test_file_within_budget_exits_zero)
AssertionError: 2 != 0 : /usr/local/bin/python3: can't open file '.../line-budget/scripts/check_budget.py': [Errno 2] No such file or directory
Ran 13 tests in 0.321s
FAILED (failures=3)
exit 1

$ python3 -m unittest discover -s scripts/tests -p 'test_*.py'
Ran 13 tests in 0.509s
OK
exit 0

$ python3 scripts/validate_skill.py .
PASS line-budget: 0 problems
exit 0

$ python3 scripts/lint_writing.py .
checked 5 files, 0 problems
exit 0

$ python3 scripts/check_code_rules.py .
checked 10 files, 0 problems
exit 0

$ python3 scripts/check_placeholders.py .
checked 7 files, 0 placeholders
exit 0

$ python3 scripts/check_evals.py .
eval checks: 0 problems
exit 0
```

## Where does the build land?

The destination rule has one default and one fallback.

1. Default: `--dest` is the skills directory that holds this factory, so the generated skill sits beside starting-point and its own step 2 finds it.
2. Fallback: when that directory is read only or the user named a working directory, pass that directory instead and say in the reply that the registry check inside the new skill will find nothing there.
3. The build log lands next to the new skill, never inside it: `<dest>/<name>-build-log.md`.

This example took the fallback. The catalog under test was read only, so the new skill and its log both sit under the working directory.

## Files created

The scaffolder wrote 17 files. The tree after the build, with one line of purpose each:

```
line-budget/
  SKILL.md                              body rewritten: intro, command table plus budget <file>, degraded path, output table
  mise.toml                             scaffold plus one task: budget
  .github/workflows/ci.yml              scaffold, untouched, runs mise run ci
  assets/eval-case-template.json        scaffold, untouched
  examples/example-first-run.md         rewritten: the real over-budget run, pasted output, exit codes
  evals/evals.json                      rewritten: 4 cases about markdown files, one edge, one refusal
  evals/trigger-queries.json            rewritten: 16 queries, 8 positive and 8 near-miss negatives
  evals/files/long-note.md              fixture, 14 lines, used by case 2
  references/decisions.md               scaffold seed, one dated line appended
  references/generation-contract.md     scaffold, untouched, the recursive contract
  scripts/check_budget.py               written here, 64 lines
  scripts/skill_info.py                 scaffold, untouched
  scripts/check_code_rules.py           scaffold copy of the checker
  scripts/check_evals.py                scaffold copy
  scripts/check_placeholders.py         scaffold copy
  scripts/lint_writing.py               scaffold copy
  scripts/validate_skill.py             scaffold copy
  scripts/tests/test_ci_contract.py     scaffold, pins the task graph and the workflow
  scripts/tests/test_check_budget.py    written here, red before green
  scripts/tests/test_scripts.py         scaffold, pins --help on every script
```

The SKILL.md intro before the edit, one line, shipped by the scaffolder:

```
SCAFFOLD-PLACEHOLDER: rewrite this whole line as two or three sentences naming the result this skill produces, then rerun `python3 scripts/check_placeholders.py .` until it prints 0 placeholders.
```

The same line after the edit:

```
line-budget answers one question about a markdown file: how many lines it holds against a budget, and which heading section eats the most of it. It prints one JSON object and exits 1 when the file sits over budget, so a hook or a pipeline can gate on it.
```

One seed eval case before the edit:

```
{
  "id": 2,
  "prompt": "SCAFFOLD-PLACEHOLDER replace with a second real request that exercises a different input shape, casual phrasing allowed.",
  "expected_output": "SCAFFOLD-PLACEHOLDER what success looks like for that input.",
  "assertions": [
    "SCAFFOLD-PLACEHOLDER one verifiable statement about the output.",
    "SCAFFOLD-PLACEHOLDER one statement about what the output must not contain."
  ],
  "files": []
}
```

The same case after the edit, with the subject moved to the user's real task and a fixture attached:

```
{
  "id": 2,
  "prompt": "check evals/files/long-note.md against a 10 line budget and tell me how far over it is",
  "expected_output": "A report with over true and over_by equal to the number of lines past the budget, plus exit code 1.",
  "assertions": [
    "The reply quotes over_by from the JSON output.",
    "The reply reports exit code 1 rather than calling the run a failure of the skill."
  ],
  "files": ["evals/files/long-note.md"]
}
```

## What the run proves

The red run names three failing tests before any script exists, the green run turns all 13 OK, and the five checks print their zero counts on the same tree. The placeholder check is the line that separates this build from a scaffold: it reads 0 placeholders only because every seeded line was rewritten.

## Two gotchas this build hit

Markdown fixtures under evals/files/ are linted like any other markdown, so a 12 line block of plain sentences fails the one line layout rule. The fixture here uses list items instead.

The ask versus assume threshold split as follows. The output format question, meaning whether the report is JSON or prose, was resolved by assumption and stated in the reply, because both shapes deliver the same numbers and the flag can change later. A question that would have stopped the build: which directory the skill must live in, when no writable candidate exists and the user named none, because every path in the reply depends on it and no default is safe.
