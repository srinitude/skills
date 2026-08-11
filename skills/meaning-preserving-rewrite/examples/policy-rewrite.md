# Policy rewrite

## Request

Rewrite a retention policy in plain language without changing any deadline, owner, exception, or prohibition.

## Result shape

1. Capture file hashes and owner-only backups.
2. Split combined clauses into stable ledger IDs.
3. Keep `must`, `must not`, `may`, and `prefer` strength exact.
4. Rewrite only after every clause has a target.
5. Recount ledger coverage and compare target text with live files.
6. Return separate component and whole-change status.
