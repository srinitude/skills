# Validation and replay

Resource gate: run `mise run validate` before using package files named here.

Backlink: [SKILL.md](../SKILL.md). Load at every stage gate and before release.

## Evidence record

Every check records stable check ID, input hashes, route, tool and version, viewport, status, raw artifact path or ID, findings, and output hash. Canonicalize JSON with sorted keys and compact separators.

## Required checks

1. Package links, line limits, syntax, source locks, and active load.
2. Full and degraded deterministic fixtures, each replayed twice.
3. Named negative fixtures for style leakage, breakpoint order, capability floor, prompt hash, Flora routing, and performance.
4. Parse every uncompressed public YAML prompt shard; verify manifest file hashes, prompt count, path order and uniqueness, exact UTF-8 byte counts, and every public prompt SHA-256; verify native evidence remains byte-exact; reject any compressed tar or encoded prompt index.
5. Explicit capability triggers and fallbacks for direct image generation or editing, pixel inspection, Flora `search_docs`, and Flora `execute`.
6. Research evidence from every available Refero, Mobbin, Lazyweb, and direct web route.
7. External Impeccable, TasteSkill, and applicable Emil verdicts or named unavailability.
8. Browser capture, native vision, keyboard, accessibility, and lab metrics at every breakpoint.
9. Integer all-width sweep plus boundary checks.
10. Field data where available, otherwise `UNAVAILABLE_FIELD_DATA`.
11. Frozen artifact replay with no provider rerun.

## Repair

Permit at most two repair passes per failing stage. Fix the smallest root cause. Reset the changed stage and all dependents. A second failure with the same cause blocks. Authentication, permission, billing, or human gates are not retryable as transient.

## Release states

- `PASS_RELEASE`: all integrations and gates pass.
- `PASS_RELEASE_DEGRADED`: named integrations are unavailable, every fallback ran, and all capability floors pass.
- `BLOCKED_CAPABILITY_FLOOR`: required evidence or capability is absent.
- `BLOCKED_DETERMINISM`: replay differs or source bytes drift.
- `BLOCKED_VALIDATION`: any remaining veto or threshold failure.

## Replay

Recompute every local hash, rerun deterministic validators, and compare canonical report bytes. Generated assets replay from frozen bytes. External providers may be rechecked for availability, but a new generation is not replay evidence.
