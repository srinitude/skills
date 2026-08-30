# Example: continue a saved review

Guess this removes: asking the author to restate the blocking finding, when the saved record already names it.

Working directory for this run: `/home/user/workspace/test/t-code-review/examples-run/auth-change`.

## The user says

> Continue the review of the auth change from the record I saved earlier. I cannot remember which finding blocked it.

## Commands run, with real output

```
$ ls review-log-*.md
review-log-auth-change.md
EXIT=0

$ grep -n "^- target\|^### F-\|^- status\|^- verdict" review-log-auth-change.md
3:- target: src/auth.py
11:- verdict: block
12:- status: blocked
15:### F-001 blocker: token refresh keeps a stale role
EXIT=0
```

The record the run resumed, at `review-log-auth-change.md`:

```markdown
- target: src/auth.py
- contract: A refreshed token must drop stale roles.
- verdict: block
- status: blocked
- ### F-001 blocker: token refresh keeps a stale role
  - evidence: role admin persists after refresh in test_auth.py
  - suggestion: clear the role set before the refresh returns
- next_check: Apply the role-clear fix and rerun test_auth.py
```

## The executor replies

> Resumed from the record. F-001 blocks: a refreshed token keeps a stale admin role. Clear the role set before refresh returns, then rerun test_auth.py.
