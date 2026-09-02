# External integrations

Resource gate: run `mise run validate` before using package files named here.

Backlink: [SKILL.md](../SKILL.md). Load for research, generation, and judgement.

Check each route independently. Allowed statuses are `PASS`, `UNAVAILABLE_AUTH`, `UNAVAILABLE_TRANSPORT`, `UNAVAILABLE_SCHEMA`, `UNAVAILABLE_SKILL`, `UNAVAILABLE_DISABLED`, and `NO_MATCH`.

## Refero

- Canonical endpoint: `https://refero.design/mcp`.
- Search by section job and site type. Record source ID, screen or flow, visible mechanism, relevance, and adaptation.
- Do not silently substitute `https://api.refero.design/mcp`.
- Fallback: Mobbin, Lazyweb, then direct first-party web.

## Mobbin

Use the host's available capability-discovery mechanism, inspect the current input contract, and invoke matching Mobbin operations:

- section search for page sections
- screen search for single states
- flow search for multi-step behavior

Use fixed result limits. Inspect returned pixels with an available pixel-inspection capability. Fallback: Refero, Lazyweb, then direct first-party web.

## Lazyweb

Use the configured Lazyweb MCP only when enabled and authenticated. Query the exact section job and current marketing pattern. Record the returned source and date. Fallback: direct first-party web.

## Flora

- Canonical endpoint: `https://agents.flora.ai/mcp`.
- Transport: native HTTP OAuth.
- Top-level tools: `search_docs` and `execute`.
- Use `search_docs` before execution when any SDK signature, model input, cost, artifact, callback, stream, polling, or canvas patch is uncertain.
- Use `execute` for one isolated TypeScript `async run(client)` operation. Prefer one complete call over a sequence of partial calls.
- Never use `execute` only to test connectivity.
- Any charged generation needs explicit approval naming cost, batch, workspace, and export effects.
- Never retry permission or billing failures as transient.
- Use bounded polling for asynchronous work inside the MCP `execute` route, then verify the returned artifact bytes. Do not assume that public REST `callback_url` webhooks or operation-specific technique-run stream modes apply inside one isolated MCP run. Use those only when current operation-specific documentation and the active receiver prove support.
- Canvas updates are add-only Mermaid patches. Technique creation, editing, or publishing stays in the app unless current official documentation proves an API route.
- Fallback: an available direct image generation or editing capability, ComfyUI, or an approved frozen local asset.

## Impeccable and TasteSkill

Load and run every available validator against the same frozen bytes. Keep each verdict, findings, revision, and evidence hash separate. When unavailable, run native checks from [judgement.md](judgement.md) and never label that output as the missing validator.

## Capability floor

Research needs one current source per section. Visual work needs a rendered capture and native pixel inspection at every breakpoint. Judgement needs all available external validators plus native checks. Performance needs lab metrics at every breakpoint. Unavailability is acceptable only when these floors still pass; otherwise return `BLOCKED_CAPABILITY_FLOOR`.
