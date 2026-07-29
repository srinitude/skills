# Example: help command

## User says

```text
/would-agents-actually help
```

## Executor replies

```text
Use `verdict <behavior question>` for a researched agent-action verdict. The result must use LIKELY, UNLIKELY, UNCERTAIN, INSUFFICIENT EVIDENCE, or UNVALIDATED HYPOTHESIS and must define the opportunity, pinned system, action, tasks, budgets, comparator, and readback. The help command does not run research.
```

## Commands run

```text
$ python3 scripts/validate_verdict.py --help
usage: validate_verdict.py [-h] --input INPUT

Validate a completed agent-action verdict.

Checks the public verdict headings, verdict label, and source URL rule.
Prints one JSON report to stdout.

Exit codes:
  0  verdict passes
  1  verdict is incomplete or malformed
  2  usage or input error

Example:
  python3 scripts/validate_verdict.py --input verdict.md

options:
  -h, --help     show this help message and exit
  --input INPUT  completed verdict markdown
exit 0
```

## Files created

None.

## What the run proves

The help path exposes the command and validation contract without claiming that research ran.
