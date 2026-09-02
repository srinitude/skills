# Voice check

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Writing standard.

Scan prose only. Skip exact source quotes, owner-only backups, raw command output, inline code, and code fences that must remain exact.

Fail on:

- banned terms or phrases from the active writing rules
- em or en dash characters
- stiff or unclear prose
- hidden subjects or weakened requirement strength
- pointers without a clear local referent
- voice applied only to the plan while planned artifacts remain inconsistent
- unreadable spacing or list-like sentence compression

Do not run a global replacement across mixed prose and code. Patch the exact prose occurrence, then recheck nearby code examples and syntax.

Record the scanned paths, excluded regions, finding count, contraction check when relevant, and `PASS` or `BLOCKED`. Include final report strings in the last scan. Rescan any prose changed after that point.
