# Image prompt and tool routing

Resource gate: run `mise run validate` before using package files named here.

Backlink: [SKILL.md](../SKILL.md). Load for every image job.

The package contains 1,000 public prompt strings across 25 domains, eight lanes, and five perspectives. Every public prompt is punctuation-normalized from byte-exact native evidence and stored uncompressed in a UTF-8 YAML record under `assets/prompts/`. The canonical prompt ID is its source path:

`prompts/<domain>/<lane>/<perspective>.md`

Each YAML record retains the source ID, SHA-256, byte count, domain, lane, perspective, and exact callable `prompt` text.

## Image job fields

Require `job_id`, purpose, audience, placement, source assets, desired change, protected invariants, rights status, output size, aspect ratio, transparency, text policy, and acceptance checks.

## Lane selection

Choose one lane:

- new concept or asset: `generate-and-render`
- modify supplied pixels: `edit-and-transform`
- crop, size, channel, or derivative set: `adapt-and-version`
- inspect and explain: `analyze-and-critique`
- comparison or selection: `compare-and-select`
- package, rights, or handoff: `deliver-and-govern`
- planning and decomposition: `plan-and-specify`
- research and evidence: `research-and-discover`

Choose the domain from the requested artifact, not the tool. Choose the perspective from the requested decision owner: `creator-operator`, `production-workflow`, `audience-user`, `assurance-quality`, or `risk-provenance`. Exact ties use UTF-8 byte order.

## Recover exact text

Run `mise run prompt-corpus verify` before selection. Run `mise run prompt-corpus get <source-path>` to recover exact bytes from the uncompressed YAML record. Verify the byte count and SHA-256 against that record. Never substitute a taxonomy label, paraphrase, or newly generated prompt.

## Tool order

Resource gate: run `mise run validate` before using package files named here.

1. An available direct image generation or editing capability for supported text-to-image or image-editing work. The configured provider and model are user-owned; do not invent or select them.
2. Flora `search_docs`, then approved Flora `execute`, when its model, canvas, project, technique, or action workflow is required.
3. ComfyUI when a local node graph, control path, or repeatable diffusion workflow is required.
4. Other available image tools named in `assets/tool-registry.json` when their trigger matches.
5. Frozen local assets when generation is unavailable or unnecessary.

Use an available pixel-inspection capability on every candidate. Check content, crop, anatomy, text, artifacts, brand fit, rights constraints, and placement at every breakpoint. Freeze selected bytes and their SHA-256. A provider request ID is not replay evidence.
