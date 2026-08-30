# Example: hold an unverified suspicion as a question

Guess this removes: turning an unverified suspicion into a blocker, when no evidence confirms it yet.

Working directory for this run: `/home/user/workspace/test/t-code-review/examples-run/retry-loop`.

## The user says

> I think the retry loop leaks a connection, but I have not checked. Is that a blocker?

## Commands run, with real output

```
$ python3 -m pytest tests/test_retry.py -q
3 passed in 0.02s
EXIT=0

$ python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json
{"errors": [], "status": "PASS"}
EXIT=0
```

The checklist the run created records the suspicion as unverified, not as a blocker:

```json
{
  "target": "src/retry.py",
  "contract": "Retries must not leak open connections.",
  "verdict": "",
  "findings": [
    {
      "id": "F-001",
      "severity": "minor",
      "file": "src/retry.py",
      "line": "unverified",
      "clause": "question",
      "evidence": "no run observed; user reports a suspicion only",
      "suggestion": "Run the retry suite under a connection tracker and count open handles after the loop.",
      "state": "unverified"
    }
  ],
  "decisions": [],
  "next_check": "Run a connection tracker over the retry loop.",
  "status": "active"
}
```

## The executor replies

> Not a blocker. F-001 is unverified: no run shows a leak. Track open connections across the loop; a leak there becomes F-001 blocker, otherwise it resolves.
