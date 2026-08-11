# Task 1 baseline and ledger acceptance

Use before any rewrite of SOUL, AGENTS, standards notes, or similar policy files.

## Artifacts to create

| Artifact | Typical path |
|---|---|
| Baseline | `.hermes/reports/<task>/baseline.json` |
| Meaning ledger | `.hermes/reports/<task>/meaning-ledger.json` |
| SOUL backup | owner-only fixed path under profile/home backups |
| AGENTS backup | owner-only fixed path under workspace `.hermes/backups/` |

Do not create rewrites, vault notes, plan edits, git commits, or config changes in Task 1.

## Baseline must record

- Absolute paths for each governed source and future target
- `status`: `present` or `absent`
- For present files: `sha256`, `bytes`, `lines`, `headings`, `mode`
- `headings` records every physical ATX heading line matching `^#{1,6} ` in source order, including lines inside fenced templates or examples. Give each byte-identical backup the same heading array.
- Expected plan hashes when the plan pins them; abort on drift
- Backup metadata with post-copy sha256 and mode (`0600` when required)
- Current Hermes source commit
- Git inventory for source root + workspace worktrees: head, branch, clean/dirty, AGENTS/mise file hits
- Remote **names** only. Never record credential-bearing remote URLs
- Explicit `future_note` / future path absence when the plan names a not-yet-created note

## Ledger must record

- Wrapper: `task`, `source_files`, optional `future_files`, `coverage_required` (1.0), `coverage_method`, `entries`
- Every SOUL multi-rule paragraph split into separate IDs
- Every SOUL and AGENTS bullet from a line walk of the live file
- Every new plan/user voice rule, plus the meta rule that the same voice covers the plan and all planned artifacts
- Fields per entry: `id`, `source_file`, `original`, `meaning`, `strength`, `new_file`, `new_section`, `new_text`, `action`, `review`
- Allowed `strength`: `must`, `must_not`, `may`, `prefer`
- Allowed `action`: `keep`, `split`, `move`, `clarify` (never `drop`)
- Allowed `review` before rewrite proceeds: `same_meaning`

## Builder pitfalls

- Keep map/tuple pack and unpack arity identical when generating entries in code.
- After writing JSON, parse with a real JSON parser; do not trust print-side success alone.
- Re-hash live sources after report writes; they must still match the plan/baseline expected hashes.
- Remove temporary `_build_*.py` (or similar) scripts from the report directory before finishing.

## Focused acceptance checks (ad-hoc)

Run a temporary probe, not a full suite. If the environment asks for a disposable verifier, prefer an OS tempfile with a `hermes-verify-` prefix, then delete it.

1. `json.loads` on baseline and ledger.
2. Unique entry IDs; required fields present on every entry.
3. Strength/action/review values in the allowed sets.
4. Entry count matches enumerated clauses (paragraph splits + bullets + voice rules + meta voice rule).
5. Source hashes unchanged vs expected.
6. Backups byte-identical to sources and mode `0600` when required.
7. Direct ATX heading scan matches the source and byte-identical backup heading arrays exactly.
8. Future note path recorded as `absent` when not created yet.
9. No leftover temporary builder script in the report dir.

Label the result **ad-hoc verification**, not full-suite green.
