# Generation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before changing package structure, native lineage, examples, or evaluation files.

## Purpose

Keep the portable skill complete, testable, and traceable to its native source without putting host-product or model names in the canonical skill body.

## Required structure

The package keeps one canonical `SKILL.md` plus `references/`, `scripts/`, `scripts/tests/`, `assets/`, `examples/`, `evals/`, `mise.toml`, and `.github/workflows/ci.yml`. `mise run ci` is the single local and hosted entry point.

## Lossless source packet

The repository keeps byte-exact native source files under `evidence/ports/logic-audit/`. `manifest.json` binds every source file by relative path, byte count, line count, nonblank-line count, and SHA-256. Formatting tools ignore the evidence owner so native bytes cannot change.

`evals/source-lineage.json` binds the native manifest, native version, public version, source file hashes, native case IDs, and every public file to its source paths. `evals/source-mapping.json` has one approved entry for every nonblank source line and maps every native case slug to one lineage ID and one public ID. Allowed line actions are `keep`, `split`, `move`, and `clarify`; `drop` is forbidden.

## Portability adaptations

- Replace native host metadata with portable frontmatter while preserving every original byte in evidence.
- Express web tools as search, source extraction, rendered browser, social-source, academic, and domain-source capabilities. Keep the original tool-specific contract in evidence and preserve every use condition, fallback rule, and proof limit.
- Keep `always-current-date`, `starting-point`, and `outcome-bounded-work` as named skill dependencies because they own required behavior rather than one host implementation.
- Map native case slugs to lineage IDs `NLA-001` through `NLA-010` and public IDs `LA-001` through `LA-010`. Preserve every native prompt, required behavior, and veto.
- Add package scaffolding, examples, and evaluations only as proof and distribution support. They do not replace native meaning.

## Example contract

This skill has no command grammar and performs no shell action during an ordinary audit. Each example still shows the user's words, the complete visible reply, every command, every exit code, and every created file. State `None` when the run used no command or created no file.

## Evaluation contract

Test positive activation, hard rejection, near-neighbor routing, required behavior, forbidden behavior, source failure, recovery, with-skill and without-skill conditions, and cold and warm speed. Every native expectation remains required and every native prohibition remains a veto. Target-only cases may add proof but may not replace native cases.

## Completion proof

A structural PASS is not enough. Completion requires byte-exact source hashes, complete source-file and nonblank-line coverage, complete native-case coverage, no unreviewed clarification, passing script tests, passing skill-local CI, passing package checks, two clean root `mise run ci` passes, and passing remote CI for the pushed commit.
