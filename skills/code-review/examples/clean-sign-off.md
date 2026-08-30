# Example: a clean sign-off

Guess this removes: that a passing suite alone is merge ready, when the contract also names a check the suite covers and the handoff is unverified.

Working directory for this run: `/home/user/workspace/test/t-code-review/examples-run/parser-refactor`.

## The user says

> The change is clean. Sign it off and hand the review to the next reviewer.

## Commands run, with real output

```
$ python3 -m pytest tests/test_parser.py -q
4 passed in 0.03s
EXIT=0

$ cp "$SKILL_DIR/assets/review-checklist.json" ./CHECKLIST.json
EXIT=0

$ python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json
{"errors": [], "status": "PASS"}
EXIT=0
```

The filled checklist the run created, at `./CHECKLIST.json`:

```json
{
  "target": "src/parser.py",
  "contract": "The parser must round-trip every fixture.",
  "verdict": "sign-off",
  "findings": [],
  "decisions": [],
  "next_check": "None; review finalized.",
  "status": "finalized"
}
```

The record entry the run appended, at `review-log-parser-refactor.md`:

```markdown
- verdict: sign-off
- status: finalized
- findings: none blocking; one minor nit (F-001) left open
```

## The executor replies

> Signed off. Zero open blocking findings; one minor nit stays open. The checklist validates at exit 0.
