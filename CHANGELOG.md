# Changelog

All notable changes to this project are recorded here.

## Unreleased

- Renamed the prior date-only skill to `always-current-datetime` at `metadata.version: "0.1.0"`, added the acquired local time to every visible reply prefix, preserved the fail-closed clock helper, and expanded native lineage to all twelve date-time pressure cases.
- Updated every published skill body and active collection discovery surface to use `always-current-datetime`; raised `logic-audit` to `metadata.version: "0.1.1"` and `prime-vector` to `metadata.version: "0.2.4"` for their renamed dependency.
- Rebuilt the byte-exact native evidence packet, source lineage, examples, offline evals, package registration, adapters, and MCP catalogs for `always-current-datetime`.
- Added the `logic-audit` Agent Skill at `metadata.version: "0.1.0"` with capability-neutral web evidence, all ten native pressure cases, complete nonblank-line coverage, and a byte-exact native source packet under `evidence/ports/`.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `logic-audit`.
- Re-audited `prime-vector` at `metadata.version: "0.2.3"`: hashed the 3,927.774-second source media, sampled and OCR-scanned one frame for every one of 3,928 whole video seconds, manually reviewed 300 periodic or high-change frames, classified the four post-transcript outro seconds as branding context, and confirmed zero visual instructions beyond the 25 mapped transcript learnings.
- Regenerated `prime-vector` at `metadata.version: "0.2.2"`: removed its two external behavior-proof routes, replaced them with separate local human-action and automated-action evidence contracts, rebound the unchanged source transcript and all 25 learning clusters, classified all 3,924 video seconds and 1,848 timestamped segments, expanded 15 incomplete material windows, and retained only 39 reviewed context-only segments with zero uncovered material segments.
- Corrected `prime-vector` at `metadata.version: "0.2.1"`: workflow states and response statuses are now distinct, strategy selection compares explicit criteria and alternatives, human and agent action claims route to their evidence owners, accepted uncertainty no longer masquerades as proof, scaling waits for observed acceptance and failure handling, worked examples no longer claim missing writes or request contradictory questionnaires, and lineage plus dual-format evals have regression coverage.
- Refocused `prime-vector` at `metadata.version: "0.2.0"` on the 25 source-traced video learnings, ordered `starting-point`, `always-current-datetime`, and `outcome-bounded-work` bindings, one deterministic strategy state machine, and explicit authorized-loss evidence for removed profile-generic behavior.
- Added the `prime-vector` Agent Skill at `metadata.version: "0.1.0"` with a self-contained strategy loop, 22 behavior cases, all 25 material video-learning clusters classified, complete nonblank-line coverage, and a byte-exact source packet under `evidence/ports/`.
- Updated Python plugin, skills.sh, Aider, package, and repository discovery routes for `prime-vector`.
- Fixed the date-only predecessor at `metadata.version: "0.1.1"` so the clock runs from the concrete skill working directory without relying on a shell variable, and added a regression case for loaders that supply no directory variable.
- Added the `outcome-bounded-work` Agent Skill at `metadata.version: "0.1.0"` with portable conversation and artifact-audit modes, all ten native pressure cases, complete nonblank-line coverage, and a byte-exact native source packet under `evidence/ports/`.
- Updated Python plugin, skills.sh, Aider, and Hermes Agent discovery routes for `outcome-bounded-work`.
- Added the date-only predecessor at `metadata.version: "0.1.0"` with a portable timezone script, the full registry eval artifact set, source-lineage hashes, a complete semantic mapping, and a byte-exact native source packet under `evidence/ports/`.
- Updated package, Python plugin, MCP, skills.sh, Aider, Continue, and Hermes Agent discovery routes for the date-only predecessor.
- Excluded the local Claude settings file and frozen source packets from Prettier so local CI does not inspect private machine settings or rewrite source evidence.

## GitHub release 0.1.4

- Made `examples/` a required directory in every skill: `AGENTS.md` gains an Examples section, the generation contract adds `examples/` to the required layout, and `scripts/validate_skill.py` fails a skill whose `examples/` directory is missing or never referenced from its `SKILL.md`.
- Added 39 worked examples across the four skills, each one a complete run with the user's words, the reply, real command output, exit codes, and the files the run created.
- Invoked every skill the way a user would before and after the change, and fixed what those runs exposed.
- `skill-factory`: the scaffolder emits `examples/`; the new `scripts/check_placeholders.py` gate fails a boilerplate scaffold that previously passed every check; `scripts/doctor.py` reports a degraded mode with fallback commands instead of blocking when the task runner is absent; seed evals describe the requested skill instead of the scaffolder. Tests grew from 72 to 94.
- `reify`: one brief schema shared by the asset, the record reference, and the validator; a validator invocation that works from a user working directory, with branches for exit 0, 1, and 2; a fixed decision ID format and defined revert moves; a reply budget matching the evals; a rule against inventing first-person biographical detail.
- `starting-point`: a description that can fail to match and routes vague requests to `reify`; the new `references/constraint-classes.md`; proof thresholds by task type; a limit on how much analysis reaches the user; the handoff to nonexistent workflows removed.
- `visual-design-system-extractor`: font ranking on fit and legibility first with rarity only breaking ties inside a band; a set-level pairing check across seven dimensions that can veto a winner; a rarity measure that no longer saturates across the rare tail; a binding `meta.rarity_floor`; and a render, screenshot, and visual judgement loop that gates completion at `meta.viability`.
- Raised `visual-design-system-extractor` to `metadata.version: "0.2.0"`. Kept `reify`, `skill-factory`, and `starting-point` at `metadata.version: "0.1.0"`.

## GitHub release 0.1.3

- Added the `skill-factory` Agent Skill at `metadata.version: "0.1.0"` with the full registry eval artifact set and source-lineage hashes.
- Unified the repository rules and the skill-factory generation contract in `AGENTS.md`.
- Raised the skill description limit to the 1024-character agentskills.io specification limit; descriptions still start with `Use when`.
- Adopted the one-line markdown layout for skill markdown and applied it to `starting-point`.
- Kept `starting-point` at `metadata.version: "0.1.0"`.
- Added the platform-neutral `reify` skill with frozen source lineage.
- Added trigger, behavior, failure, recovery, and speed evaluations for `reify`.
- Updated package, plugin, MCP, skills.sh, Aider, Continue, and Hermes Agent discovery routes.
- Added the `visual-design-system-extractor` Agent Skill at `metadata.version: "0.1.0"`, retrofitted from the standalone `srinitude/visual-design-system-extractor` package with frozen source lineage.
- Required every typeface the extractor selects to be a Google Fonts family whose rarity is measured against the live `fonts.google.com/metadata/fonts` feed during the run, recorded with rank, family count, percentile, trending rank, date added, source, and retrieval date.
- Added `scripts/rare_google_fonts.py` with `catalog`, `discover`, and `verify` commands, plus a live comparison inside the extraction validator that fails on stale ranks and absent families.
- Replaced the prose extraction schema with the machine readable `references/extraction-schema.yaml` contract, which now drives section order, confidence labels, evidence buckets, and the font rules from one file.

## GitHub release 0.1.2

- Allowed verified zero-cost routes through the full ledger path.
- Added durable pending records that block automatic repayment after an ambiguous failure.
- Released rejected-request reservations only when route metadata proves no provider attempt occurred.
- Blocked unknown-price requests before creating a ledger reservation.
- Kept every skill version unchanged.

## GitHub release 0.1.1

- Added a fixed-route, capped, resumable OpenRouter sweep runner.
- Added manifest-bound user approval and first-party route and cost checks.
- Removed repository validation that tied skill versions to the package version.
- Kept `starting-point` at `metadata.version: "0.1.0"`.

## 0.1.0

Initial public package.

- Added the `starting-point` Agent Skill with source-lineage evidence.
- Added positive, rejection, behavior, failure, recovery, and speed evaluations.
- Added strict validators and JSON Schemas.
- Added a bundled read-only MCP server.
- Added plugin or adapter routes for ten clients.
- Added deterministic package and copy checks.
