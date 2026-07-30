# Generation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before changing package structure, native lineage, examples, or evaluation files.

## Purpose

Keep the portable skill complete, testable, and traceable to its native source without putting agent-product or model names in the canonical skill body.

## Required structure

The package keeps one canonical `SKILL.md` plus `references/`, `scripts/`, `scripts/tests/`, `assets/`, `examples/`, `evals/`, `mise.toml`, and `.github/workflows/ci.yml`. `mise run ci` is the single local and hosted entry point.

## Lossless source packet

The repository keeps byte-exact native source files under `evidence/ports/outcome-bounded-work/`. `manifest.json` binds every source file by relative path, byte count, line count, nonblank-line count, and SHA-256. Formatting tools ignore the full evidence owner so native bytes cannot change.

`evals/source-lineage.json` binds the native manifest, native version, public version, source file hashes, repository-compliant lineage case IDs, and every public file to its source paths. `evals/source-mapping.json` contains one approved entry for each nonblank source line and maps every native slug to one lineage ID and one public ID. Allowed line actions are `keep`, `split`, `move`, and `clarify`; `drop` is forbidden.

## Portability adaptations

- Replace the native version and host metadata with portable frontmatter while preserving them in evidence and lineage.
- Replace the product-specific phrase for skill simplification with capability-neutral skill-package wording. Keep the dedicated simplification owner and every routing boundary.
- Express skill loading through the host's available skill-loading capability. Keep `starting-point` first.
- Map native case slugs to lineage IDs `NOBW-001` through `NOBW-010` and public IDs `OBW-001` through `OBW-010`. Keep every native slug in the source mapping and byte-exact evidence.
- Add package scaffolding, examples, and evaluations only as proof and distribution support. They do not replace native meaning.

## Example contract

This skill has no command grammar and performs no shell action during ordinary classification. Each example must still show the user's words, the complete visible reply, all commands, all exit codes, and every created file. State `None` when the run used no command or created no file. Include the simple-request bypass because unnecessary contract work is the most likely failure.

## Evaluation contract

Keep all ten native cases under their native slugs, lineage IDs, and public IDs. Test positive activation, hard rejection, near-neighbor routing, required behavior, forbidden behavior, failure handling, recovery, with-skill and without-skill conditions, and cold and warm speed.

Every native `must` remains required and every native `must_not` remains a veto. Target-only cases may add proof but may not replace native cases.

## Completion proof

A structural PASS is not enough. Completion requires byte-exact evidence hashes, complete source-file and nonblank-line coverage, complete native-case coverage, no unreviewed clarification, passing script tests, passing skill-local CI, passing Agent Skills validation, passing package checks, two clean root `mise run ci` passes, and passing remote CI for the pushed commit.
