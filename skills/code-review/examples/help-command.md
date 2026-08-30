# Example: the help command

Guess this removes: what `help` prints, and how the executor reports the state of a record it did not create in this session.

Working directory for this run: `/home/user/workspace/test/t-code-review/examples-run/parser-refactor`.

## The user says

> help

## Commands run, with real output

```
$ ls review-log-*.md
review-log-parser-refactor.md
EXIT=0

$ grep -n "^- target\|^- verdict\|^- status\|^### F-" review-log-parser-refactor.md
3:- target: src/parser.py
4:- verdict: sign-off
11:- status: finalized
15:### F-001 minor: trailing comma not handled in nit path
EXIT=0
```

The script help text is part of the same answer when the user asks about the handoff step.

```
$ python3 "$SKILL_DIR/scripts/validate_checklist.py" --help
usage: validate_checklist.py [-h] checklist

Validate a saved code review checklist.

The input is a JSON object holding the review record fields: target,
contract, verdict, and next_check strings, findings and decisions lists,
and a status of active, blocked, or finalized. Each findings entry is an
object with id, severity, file, line, clause, evidence, suggestion, and
state. Each decisions entry is an object with id, finding, choice, reason,
and reversible. Pass - to read the object from stdin. The report is JSON
on stdout.

Exit codes:
  0  the checklist passes
  1  the checklist is invalid or cannot be read
  2  command usage is invalid, including a wrong script path

Example:
  SKILL_DIR=/path/to/skills/code-review
  python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json

positional arguments:
  checklist   JSON file path, or - for stdin

options:
  -h, --help  show this help message and exit
EXIT=0
```

## The executor replies

> Five commands, and one record already open in this directory.
