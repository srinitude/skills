# Tool profile

Read this file before writing or reviewing a descriptor. The profile records facts about one callable tool and never contains desired user behavior.

## Identity

Required fields are `origin_class`, `provider_or_owner`, `runtime_or_server`, `namespace`, `callable_name`, and `discovery_route`. Preserve the exact callable name. Record `version` when verified; otherwise bind the identity to the stable SHA-256 contract hash emitted by the script.

`origin_class` is exactly one of `established-mcp`, `owned-mcp`, `native`, or `custom`. A server, application, namespace, plugin, SDK, registry, or collection is invalid as the callable target.

## Contract

Record the live `input_schema`, available `output_schema`, and capability facts for read-only behavior, state changes, approvals, idempotency, progress, cancellation, readback, state handles, partial results, rate limits, known failures, and safe retry conditions. Use explicit false values only when a source proves absence. Use null or `unknown` when the fact is not proved; a safety-relevant unknown blocks generation.

## Sources and status

Each source entry records `locator`, `owner`, retrieval date, version or revision, claim, kind, and `status`. Use `verified`, `not applicable`, `unknown`, `stale`, `unavailable`, or `conflicted`. At least one current `verified` source is required. For a private tool, use authorized local source and a confined probe without copying private payloads to an external destination.

## Origin routes

- For `established-mcp`, start with the connected tool listing and exact schema, then use the current protocol rules and the server owner's primary references.
- For `owned-mcp`, inspect registration source, schema, handler, tests, and a confined live listing or call when safe.
- For `native`, inspect the current host registry entry and callable schema. Do not add protocol rules that the native contract does not expose.
- For `custom`, inspect the authorized registry, source, types, tests, or supplied descriptor and the actual transport only when it affects the call.

## Contradictions

Use the live schema for what can be invoked now. Use canonical source for intended semantics. Record both claims and the discrepancy. Do not fill an unknown with a familiar default.
