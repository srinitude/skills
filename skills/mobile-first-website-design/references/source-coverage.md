# Source coverage and authority

Resource gate: run `mise run validate` before using package files named here.

Backlink: [SKILL.md](../SKILL.md). Load for audits, source drift, or integration changes.

## Authority order

1. Current user instruction and live first-party documentation.
2. Locked first-party SDK or repository source for implementation shape.
3. Installed host source for local implementation shape only.
4. External skill revisions for procedure and judgement.
5. Supplemental X posts for dated announcement evidence.

Do not let supplemental evidence override current official documentation.

## Locked coverage

Resource gate: run `mise run validate` before using package files named here.

`assets/source-lock.json` records:

- all 1,055 source files and all 1,000 byte-exact native prompt strings at the locked image-prompt revision
- Impeccable, TasteSkill, Refero skill, and Emil revisions
- 195 official Flora user and developer pages, their exact URL-bound document audits, the resolved operation-scope contracts, and the Flora TypeScript SDK revision
- 206 source-host documentation pages and the reviewed source-host revision
- current Web Vitals first-party sources
- exact Refero and Flora endpoints

The Flora audit lock proves that each retained official URL has a document-level audit bound to the exact retained source hash. Its resolved contracts scope asynchronous behavior by route: MCP `execute` uses bounded polling; public REST `callback_url` and schema-specific stream modes are not inherited by MCP and require current operation-specific proof.

The public prompt corpus is stored uncompressed in deterministic UTF-8 YAML shards under `assets/prompts/`. It is punctuation-normalized from the byte-exact native corpus retained in committed evidence. `assets/prompt-manifest.json` lists every shard, ordered source-path range, count, byte count, and SHA-256. Parse each shard as YAML, read each exact public `prompt` scalar, then verify its UTF-8 byte count and SHA-256 before use. No tar, compression, or encoded prompt index is part of the package.

## Host compatibility

Use user-local skill directories only. Progressive files stay under `references`, `assets`, or `scripts`. Load through the host's skill capability. Discover deferred tools through the host registry, inspect their schemas, then invoke them. MCP tool names follow `mcp__<server>__<tool>`. Disabled MCP servers are unavailable, not passing. The user chooses the image provider and model.

## Drift

If any lock changes, stop selection, rerun complete coverage and compatibility review, regenerate derived assets, and bump the skill version. Never infer a missing revision. Record unreachable pages, unavailable X evidence, disabled servers, and absent field data explicitly.

## Privacy

Source locks may contain public URLs and hashes. They must not contain credentials, authorization codes, tokens, cookies, private configuration values, or secret-bearing URLs.
