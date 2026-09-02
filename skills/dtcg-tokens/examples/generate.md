# Generate command

**Guess removed:** Preliminary token validation does not imply that a proof artifact has passed visual review.

## User

> Generate DTCG tokens from `evals/files/sample-brief.txt`. Prove the result is specific to that input. Use `mise run token-packet -- <args>` for this routed resource.

## Visible reply

The only source is text, so no visual-source inspection is claimed. I inventoried and hashed it, expanded the full possibility catalog, and narrowed each retained entry with a recorded reason. The committed fixture contains 45 tokens and 9 resolved references across all 13 standard types. Its required experimental partition contains three tokens from three different exploration strategies, including one hierarchy inversion. Its typography evidence records a same-date live catalog, three candidates outside the most popular 50%, two selected font token paths, licenses, and fixture-only asset hashes. Token structure passes. A completed run record and run-specific HTML remain blocked until a strong-vision reviewer authors the proof with real prepared WOFF2 bytes, visually compares the candidates, and inspects the final artifact.

## Command

| Command                                                     | Purpose                                                              |
| ----------------------------------------------------------- | -------------------------------------------------------------------- |
| `mise run token-validate -- evals/files/sample.tokens.json` | Validate the committed token fixture against the pinned DTCG checks. |

## Verified output

```json
{
  "errors": [],
  "resolved_references": 9,
  "schema_sha256": "9b501b5666f7515bd0051ff0aec3566b78a3cbe82b0280c90d03660c2e02246e",
  "specification": "DTCG 2025.10",
  "token_count": 45,
  "types": {
    "border": 1,
    "color": 15,
    "cubicBezier": 2,
    "dimension": 10,
    "duration": 3,
    "fontFamily": 2,
    "fontWeight": 3,
    "gradient": 1,
    "number": 3,
    "shadow": 1,
    "strokeStyle": 1,
    "transition": 1,
    "typography": 2
  },
  "valid": true
}
```

Exit code: `0`

The committed token and evidence fixtures are `evals/files/sample.tokens.json` and `evals/files/sample.evidence.json`. This checkpoint creates no new file. No HTML pass is claimed or bundled as a visual precedent. Use `mise run token-packet -- <args>` for this routed resource.
