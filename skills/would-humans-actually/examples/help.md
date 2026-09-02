# Example: help command

## User says

```text
/would-humans-actually help
```

## Executor replies

```text
Use `verdict <behavior question>` for a researched human-action verdict. The result must use LIKELY, UNLIKELY, UNCERTAIN, INSUFFICIENT EVIDENCE, or UNVALIDATED HYPOTHESIS and must define the actor, observable action, setting, costs, alternative, and window. The help command does not run research.
```

## Commands run

```text
$ mise run validate-verdict --help
usage: validate_verdict.py [-h] --input INPUT

Validate a completed human-action verdict.

Checks the public verdict headings, verdict label, and source URL rule.
Prints one JSON report to stdout.

Exit codes:
  0  verdict passes
  1  verdict is incomplete or malformed
  2  usage or input error

Example:
  mise run validate-verdict --input verdict.md

options:
  -h, --help     show this help message and exit
  --input INPUT  completed verdict markdown
exit 0
```

## Files created

None.

## What the run proves

The help path exposes the command and validation contract without claiming that research ran.
