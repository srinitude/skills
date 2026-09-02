# Changelog

All notable changes to this project are recorded here.

## Unreleased

## GitHub release 0.1.5

- Made the canonical catalog the single inventory owner for Aider, Hermes Agent, the Python plugin, integration validation, client smoke checks, and MCP resource assertions.
- Hardened the six-tool read-only MCP contract with exact resource-byte checks, strict invalid-input errors, symlink and path-escape rejection, stdio channel checks, and identical consecutive bundle builds.
- Routed local and GitHub verification through one non-circular Mise graph whose complete `ci` frontier includes dependency audit, source tests, MCP tests, canonical skill validation, offline evals, benchmarks, integration checks, and archive inspection.
- Hardened the release archive against bytecode, caches, skill test fixtures, source maps, local settings, symlinks, duplicate or unsafe entries, and bulky source-evidence packets that clients do not consume.
- Replaced the false OpenClaw-native manifest claim with the portable Agent Plugins bundle and tightened route-specific documentation for every supported client.
- Added a release audit that records one current disposition and content digest for every repository-owned file outside `skills/`.

- Added the `only-one-interpretation` Agent Skill at `metadata.version: "0.1.0"` with a two-branch ambiguity gate, private interpretation ledger, semantic round trip, alternate-reading attacks, constraint tracing, fourteen behavior cases, twenty trigger cases, three deterministic result fixtures, and skill-local CI.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `only-one-interpretation`.
- Added the `by-design` Agent Skill at `metadata.version: "0.1.0"` with a library of 16,112 execution-time design questions across 35 categories, a gate that ends a non-design turn in one command, coordinate ranking measured over 26 discipline fixtures, a benchmark that refuses any measure below its recorded baseline, thirteen worked examples whose 85 pasted command outputs were replayed against the shipped scripts, skill-local CI, and the full repository evaluation artifact set.
- Conformed the `by-design` question corpus to the repository writing rules by splitting each citation into `source_publisher` and `source_title`, replacing long dashes in authored text with a colon, a comma, or a parenthetical, and describing what a user has done rather than labeling their ability. A hundred and two questions were dropped rather than misquoted: twelve whose cited page or title could not be written without a banned word, and ninety whose citation named an agent product, a model, or its vendor, which no file under `skills/` may do.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `by-design`.
- Fixed the bundled standard-library YAML reader in `by-design` so a block ends at the next top level key. Without an installed parser the gate had been reading its weak nouns as design surfaces, which let a document extraction request through.
- Added an Agent Plugins 1.0.0 portable core with root `plugin.json`, root `mcp.json`, canonical Agent Skills discovery, and the existing read-only stdio server.
- Added offline canonical-schema validation with source digests, path and symlink containment tests, a real portable MCP startup check, archive assertions, and public install and security guidance.
- Added the `mobile-first-website-design` Agent Skill at `metadata.version: "0.1.0"` with a byte-exact 228-file native evidence packet, complete 12,029-line source mapping, all eight native cases, deterministic punctuation normalization for public prompt scalars, three worked examples, skill-local CI, and repository evaluation coverage.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `mobile-first-website-design`.
- Added the `prompt-enhancer` Agent Skill at `metadata.version: "0.1.0"` with all sixteen native behavior cases, five packaged validation scripts, worked examples with real script output, complete nonblank-line coverage of the eight-file native source packet under `evidence/ports/`, package-local CI, and repository evaluation coverage.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `prompt-enhancer`.
- Raised `timebox` to `0.1.1`, restored its native hard-acceptance, admission, incomplete-work, verification, and evaluation-owner semantics, replaced count-only source mapping with executable public-target assertions, and aligned the published evaluation-manifest schema with the live parser and all 15 manifests.
- Closed final review follow-ups by splitting oversized validation code and regressions, documenting `target-scaffolding`, and labeling mixed visual-design source evidence explicitly.
- Refreshed the visual-design live-font fixture and raised that skill to `0.2.1` after catalog drift invalidated its recorded ranks.
- Closed repository-wide logic gaps in evaluation completeness, fixture claim scope, source evidence verification, public-file lineage coverage, special-entry rejection, catalog identity, empty trigger rejection, and dependency audit state.
- Added committed source-evidence manifests for all published skills. Historical native packets stay byte-bound where available; legacy packages without recoverable source bytes now declare a complete `repository_baseline` instead of unverifiable historical hashes.
- Added `timebox` at `metadata.version: "0.1.0"` with byte-exact native evidence, complete source-line coverage, all six source eval cases, deadline-bound validation, package-local CI, and collection integration.
- Added `meaning-preserving-rewrite`, `simplify-skill`, and `goal-prompt` at `metadata.version: "0.1.0"` with byte-exact native evidence, complete source mappings, portable dependency reconciliation, package-local CI, and repository evaluation coverage.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for the three dependency-campaign units.
- Added a regression that requires the Python plugin to register every canonical skill with its current frontmatter description.
- Added the `dedupe` Agent Skill at `metadata.version: "0.1.0"` with six adapters, eight native behavior cases, sixteen trigger cases, complete nonblank-line coverage, and a byte-exact 36-file native source packet under `evidence/ports/`.
- Updated Python plugin, skills.sh, Aider, package, repository, and MCP discovery routes for `dedupe`.
- Renamed the prior date-only skill to `always-current-datetime` at `metadata.version: "0.1.0"`, added the acquired local time to every visible reply prefix, preserved the fail-closed clock helper, and expanded native lineage to all twelve date-time pressure cases.
- Updated every published skill body and active collection discovery surface to use `always-current-datetime`; raised `logic-audit` to `metadata.version: "0.1.1"` for its renamed dependency.
- Rebuilt the byte-exact native evidence packet, source lineage, examples, offline evals, package registration, adapters, and MCP catalogs for `always-current-datetime`.
- Added the `logic-audit` Agent Skill at `metadata.version: "0.1.0"` with capability-neutral web evidence, all ten native pressure cases, complete nonblank-line coverage, and a byte-exact native source packet under `evidence/ports/`.
- Updated Python plugin, skills.sh, Aider, Hermes Agent, package, repository, and MCP discovery routes for `logic-audit`.
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
