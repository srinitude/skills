# Final validation and independent review

Use after policy/plan rewrites under `meaning-preserving-rewrite`. This is focused ad-hoc validation, not full-suite CI.

## Artifacts

Under `.hermes/reports/<task>/` (names may match the plan):

| File | Role |
|---|---|
| `baseline.json` | Pre-edit hashes, backups, git inventory |
| `meaning-ledger.json` | Clause map and same-meaning reviews |
| `codebase-inventory.json` | Read-only repo/worktree audit when required |
| `context-check.json` | Fresh-session context load when required |
| `voice-scan.json` | Prose scanner result with scope list and findings |
| `independent-review.json` | Read-only reviewer verdict |
| `review-packet.json` | Frozen file list and claims sent to review when used |
| `packet-integrity.json` | SHA of the frozen packet and per-file hashes when used |
| `final-validation.json` | Machine PASS/BLOCKED with separate subtask vs whole-change fields |
| `VALIDATION.md` | Human table with evidence and hashes |

## Independent review

1. Build a source packet from live files only: original profile note (if required), backups, live SOUL/AGENTS, Obsidian standards, skill files when those are rewrite targets, active plan, baseline, ledger, inventory, context check, voice scan, human and machine validation as they stand before review closeout.
2. When using a frozen packet, write `review-packet.json` and `packet-integrity.json` with the packet SHA and per-file hashes before dispatch. Put every `required_check` name and every in-scope path in the packet so the reviewer has an explicit work order.
3. Dispatch a reviewer with **read-only** tools only. Prefer toolset `search` (or equivalent read/search tools). Do **not** give write, patch, terminal mutation, skill_manage, or other mutation tools.
4. Require the reviewer to check plan completion, ledger coverage, same meaning, voice, scratch exception, durable controls, AGENTS behavior, history preservation, secret safety, worktree safety, validation labels, and clarity.
5. Tell the reviewer to **re-count** ledger entries and any fixture or validator-case matrix from disk, not from summary claims. Ledger size is the count of stable entry IDs (`"id": "PREFIX-###"`), not the count of `"source_file"` keys alone. When a completion-report validator is in scope, also re-count PASS/FAIL cases and the exit-code distribution, and probe fail-closed classes in live validator code (see `hermes-skill-lifecycle` → `references/skill-mutation-validation.md`, Acting as the independent reviewer).
6. Save `independent-review.json` with at least:
   - `status`: `PASS` or `BLOCKED`
   - `reviewer_toolset` and boolean flags proving mutation/skill-writing tools were unavailable
   - `packet_chars` or packet hash
   - `checks` map keyed by each `required_check` name
   - `failed` and `required_fixes` arrays (empty on PASS)
   - Optional empty `security_concerns`, `logic_errors`, and `suggestions` arrays on PASS so the shape stays stable across review rounds
7. On any fail: fix in the main session, re-run focused checks, rebuild and re-hash the frozen packet when used, then re-run independent review. Do not self-approve while mutation tools were available to the reviewer. Stale packet metadata after a fix is BLOCKED even if live files are already correct.

## Closeout order

1. Land independent review PASS first.
2. Update `final-validation.json`: overall `status`, each check including `independent_review`, separate subtask vs whole-change fields, and the SHA-256 of `independent-review.json` (and packet integrity when used).
3. Update `VALIDATION.md` to match: overall PASS, independent-review row, machine-report hash, voice-scan evidence counts.
4. Run the **final** voice scan over the full governed set, including `VALIDATION.md`, `final-validation.json` string fields, and `independent-review.json` string fields when those files exist.
5. Run a deterministic cross-check: human report starts with PASS, machine report all checks PASS, review PASS, voice PASS, plan hash still baseline, ledger targets live, packet integrity matches the latest live packet when used, no credential hits, no leftover `hermes-verify-*` after cleanup.
6. If you edit any scanned prose after the final voice scan (for example fixing an evidence count from 10 to 11), recheck that prose and re-run the consistency check. Do not leave human evidence text stale against the real scan scope.

## Side effects

- Prove no forbidden side effects: no new profiles, durable plugin/project repos, commits, pushes, source tree edits, or worktree removals unless the plan allows them.
- `hermes config check` and `hermes doctor` may run when the plan requires them. Do not run `hermes doctor --fix` on a no-side-effects task unless the plan says so. Note unrelated advisories (for example a large session WAL) without auto-fixing.

## Honest labels

- Call focused JSON/hash/prose checks **focused ad-hoc validation**.
- Call the independent review separate from the focused suite.
- Keep subtask evidence separate from whole-rewrite completion.
- Never claim full test-suite green when none ran.
