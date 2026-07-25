# Example: eval <path>, schema check then graded cases

Guess this example removes: what the eval checker prints, what a real case file looks like next to a seeded one, and how a case gets graded with evidence.

## User says

```
my line-budget skill has evals now, check them and run a couple of cases against the real script
```

## Executor replies

```
Schema is clean and both cases I ran hold.

$ python3 scripts/check_evals.py .
eval checks: 0 problems
exit 0

Case 2, "check evals/files/long-note.md against a 10 line budget and tell me how far over it is". Assertion one, the reply quotes over_by: held, the run printed "over_by": 4. Assertion two, exit code 1 is reported as the over-budget signal rather than a crash: held, the command exited 1 with a complete JSON object on stdout.

Case 3, "run the budget check on notes/missing.md, i think i deleted it". Assertion one, the reply names the missing path: held, stderr read "error: no such file: notes/missing.md". Assertion two, exit code 2 and no line count: held, stdout was empty.

The file counts to watch: 4 cases is the floor the checker enforces, and 16 trigger queries ship here against the floor of 4. The reference asks for about 20, half positive and half negative, so treat the checker floor as the minimum and the reference number as the shipping bar.
```

## Commands run

```
$ python3 scripts/check_evals.py .
eval checks: 0 problems
exit 0

$ python3 scripts/check_budget.py --input evals/files/long-note.md --max 10
{"file": "evals/files/long-note.md", "lines": 14, "max": 10, "over": true, "over_by": 4, "longest_section": {"heading": "Long note", "lines": 14}}
exit 1

$ python3 scripts/check_budget.py --input notes/missing.md --max 200
error: no such file: notes/missing.md
exit 2

$ python3 scripts/check_evals.py /home/user/workspace/test/t-factory/work-examples/broken/broken-skill
evals.json: needs at least 4 cases
missing evals/trigger-queries.json
eval checks: 2 problems
exit 1
```

## What a real case file holds

The four shipped cases, one line of purpose each: a common request, a fixture-backed request with a countable answer, an edge case on a missing file, and a request the skill must refuse. The refusal case, in full:

```
{
  "id": 4,
  "prompt": "trim my 400 line SKILL.md down to 150 lines for me",
  "expected_output": "A refusal to rewrite prose, the measurement offered instead, and the longest sections named as edit candidates.",
  "assertions": [
    "The reply states that this skill measures and does not rewrite.",
    "The reply offers the longest section list as the next step."
  ],
  "files": []
}
```

The negative trigger queries are near misses, meaning requests that share the vocabulary and need a different skill:

```
{"query": "count the words in docs/onboarding.md", "should_trigger": false},
{"query": "reformat README.md to 80 column wrapping", "should_trigger": false},
{"query": "split docs/spec.md into three files", "should_trigger": false},
{"query": "check the python line length limits in scripts/", "should_trigger": false}
```

## Files created

None. The eval command reads, runs, and grades.

## What the run proves

The schema check prints one summary line, "eval checks: N problems", and names each defect above it when N is not zero. Grading is separate from the schema check: every assertion above is answered with a quoted line from a command that ran, and an assertion with no quotable evidence is a fail.
