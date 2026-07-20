# OpenRouter sweeps

Use the sweep runner to execute immutable request packets against one exact OpenRouter provider route at a time. It reserves the worst-case request cost before sending, records first-party cost, and resumes from verified checkpoints.

## Safety contract

- `dry-run` requires no API key and makes no network call.
- Each request names one model, one provider route slug, and its expected provider label.
- Provider fallbacks are disabled.
- `max_input_tokens` must cover the UTF-8 byte length of the request messages.
- Known pricing sets route-level `max_price` values and includes `request_usd` in reservations.
- Unknown-price requests never execute.
- `pilot` and `full` require a user approval artifact.
- The approval binds the manifest SHA-256, total cap, and unknown-price cap.
- The spend ledger reserves before each request and reconciles reported cost afterward.
- The runner opts into route metadata and checks the selected provider label.
- A missing provider label, missing cost, invalid response, or cap mismatch blocks the run.

The JSON contracts are [`sweep-manifest.schema.json`](../schemas/sweep-manifest.schema.json), [`sweep-approval.schema.json`](../schemas/sweep-approval.schema.json), and [`sweep-checkpoint.schema.json`](../schemas/sweep-checkpoint.schema.json).

## Run a dry check

Create the request manifest outside the repository. Keep generated output under `.artifacts/`.

```sh
npm run skills -- sweep --phase dry-run \
  --manifest .artifacts/openrouter/manifest.json \
  --cap "$APPROVED_CAP_USD" \
  --unknown-price-cap "$APPROVED_UNKNOWN_PRICE_CAP_USD" \
  --out .artifacts/openrouter/run
```

Read `.artifacts/openrouter/run/plan.json`. Confirm the request count, manifest hash, known-price reservation, and unknown-price reservation before asking for spend approval.

## Record approval

After the user states both caps, write an approval artifact matching [`sweep-approval.schema.json`](../schemas/sweep-approval.schema.json). Set `manifest_sha256` to the value in `plan.json`. Set `approved_by` to `user` only for approval stated by the user.

Never infer approval from a numeric CLI flag. Never store the API key in the manifest, approval, report, checkpoint, or spend ledger.

## Run the pilot

Provide `OPENROUTER_API_KEY` through the process environment. The pilot executes only the first request in the manifest.

```sh
npm run skills -- sweep --phase pilot \
  --manifest .artifacts/openrouter/manifest.json \
  --approval .artifacts/openrouter/approval.json \
  --cap "$APPROVED_CAP_USD" \
  --unknown-price-cap "$APPROVED_UNKNOWN_PRICE_CAP_USD" \
  --out .artifacts/openrouter/run
```

Inspect `report.json`, `spend-ledger.json`, `checkpoints/`, and `raw/` before continuing.

## Run or resume the full set

Use the same manifest, approval, caps, and output directory.

```sh
npm run skills -- sweep --phase full \
  --manifest .artifacts/openrouter/manifest.json \
  --approval .artifacts/openrouter/approval.json \
  --cap "$APPROVED_CAP_USD" \
  --unknown-price-cap "$APPROVED_UNKNOWN_PRICE_CAP_USD" \
  --out .artifacts/openrouter/run
```

A matching completed checkpoint is reconciled and skipped. A changed request, manifest, cap, or approval blocks instead of sending.

## Version boundaries

GitHub releases, package versions, schema identifiers, integration versions, and each skill's `metadata.version` are separate version axes. A skill must not depend on another skill's version.
