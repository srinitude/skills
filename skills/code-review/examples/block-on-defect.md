# Example: block on a real defect

Guess this removes: hiding a broken change behind a sign-off, when a check the contract names fails.

Working directory for this run: `/home/user/workspace/test/t-code-review/examples-run/parser-refactor`.

## The user says

> Review the change. The round-trip test is the acceptance contract.

## Commands run, with real output

```
$ python3 -m pytest tests/test_parser.py -q
tests/test_parser.py ..F.
1 failed, 3 passed in 0.04s
EXIT=1

$ python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json
{"errors": ["findings[1] open blocker conflicts with sign-off verdict"], "status": "FAIL"}
EXIT=1
```

The blocked checklist the run first tried, at `./CHECKLIST.json`, before the validator caught the inconsistent verdict:

```json
{
  "target": "src/parser.py",
  "contract": "The parser must round-trip every fixture.",
  "verdict": "sign-off",
  "findings": [
    {
      "id": "F-001",
      "severity": "blocker",
      "file": "src/parser.py",
      "line": "42",
      "clause": "round-trip",
      "evidence": "fixture quoted.csv fails on trailing comma",
      "suggestion": "Strip the trailing comma before split.",
      "state": "open"
    }
  ],
  "decisions": [],
  "next_check": "Apply the trailing-comma fix and rerun.",
  "status": "finalized"
}
```

The corrected blocked record after the verdict is fixed to `block`:

```json
{
  "target": "src/parser.py",
  "contract": "The parser must round-trip every fixture.",
  "verdict": "block",
  "findings": [
    {
      "id": "F-001",
      "severity": "blocker",
      "file": "src/parser.py",
      "line": "42",
      "clause": "round-trip",
      "evidence": "fixture quoted.csv fails on trailing comma",
      "suggestion": "Strip the trailing comma before split.",
      "state": "open"
    }
  ],
  "decisions": [],
  "next_check": "Apply the trailing-comma fix and rerun.",
  "status": "blocked"
}
```

## The executor replies

> Blocked. F-001 fails the round-trip contract at line 42. Fix the trailing comma, then resume; the validator rejects a sign-off over an open blocker.
