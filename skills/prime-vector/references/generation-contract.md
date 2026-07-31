# Generation contract

This file governs maintenance of the portable package. It does not add runtime dependencies.

## Canonical layout

```text
prime-vector/
├── SKILL.md
├── .github/workflows/ci.yml
├── mise.toml
├── references/
├── assets/
├── examples/
├── scripts/
│   └── tests/
└── evals/
```

`SKILL.md` is the only runtime entry point. It must stay below 200 physical lines, link every optional resource it expects a reader to load, and remain useful when no optional resource is opened.

The skill must not require another skill, a specific host, a named model, a plugin, a protocol server, a remote memory service, a browser, or a configured tool. Available capabilities may improve proof, but their absence must not make the reasoning loop undefined.

## Source preservation

The frozen source packet lives outside the public skill tree. Its manifest records every discovered authored source file, byte count, line count, nonblank line count, hash, source version, and exclusion. No source file or clause may be silently dropped.

`evals/source-lineage.json` binds the public version to the frozen manifest. `evals/source-mapping.json` maps every nonblank source line to a public and evidence target. Every mapping must be approved, nonempty, and use an action other than `drop`.

The supplemental learning map records every material teaching cluster from the named source, whether the current procedure already covered it, whether the public skill strengthened it, or whether it was retained only as a claim. Promotional numbers, anecdotes, forecasts, and employment predictions never become operational facts without separate evidence.

## Public writing

Use plain language, one physical line per paragraph or list item, no forced symmetry, no praise filler, and no agent-product or model names. Keep examples complete enough to audit: user words, full visible reply, commands and exit status when any command ran, file effects, success test, and failure likelihood.

## Verification

The task graph has one entry point: `mise run ci`. It runs tests first, then structure, writing, code, and eval checks. Remote CI must call the same entry point.

Focused package tests must prove source-byte preservation, full line mapping, supplemental-learning classification, dependency freedom, canonical placement, and skill-local CI. Repository CI must pass after integration files are updated.

## Progressive disclosure decisions

- `PD-001`: `references/decision-checklist.md` owns the compact execution check. Load it for high-stakes work or when the main procedure cannot stay in working context. `SKILL.md` links it under Package resources.
- `PD-002`: `references/practice-loop.md` owns the optional thirty-day habit routine. Load it only when the user wants deliberate practice. `SKILL.md` links it under Practice loop.
- `PD-003`: `assets/strategy-packet-template.md` owns the reusable durable-output form. Load it only when a strategy packet is requested. `SKILL.md` links it under Package resources.
- `PD-004`: `examples/` owns calibration transcripts. Load one only when activation, safety, or output shape is uncertain. `SKILL.md` links the directory under Package resources.
- `PD-005`: `references/generation-contract.md` owns maintenance, provenance, and validation rules. Load it only when changing or publishing the skill. `SKILL.md` links it under Package resources.
