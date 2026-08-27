# Generate command

**Guess removed:** Preliminary token validation does not imply that a proof artifact has passed visual review.

## User

> Generate DTCG tokens from `evals/files/sample-brief.txt`. Prove the result is specific to that input.

## Visible reply

The only source is text, so no visual-source inspection is claimed. I inventoried and hashed it, expanded the full possibility catalog, and narrowed each retained entry with a recorded reason. The committed fixture contains 44 tokens and 9 resolved references across all 13 standard types. Its required experimental partition contains two tokens from two different exploration strategies. Token structure passes. A completed run record and run-specific HTML remain blocked until a strong-vision reviewer authors and inspects the actual proof artifact.

## Command

| Command                                                           | Purpose                                                              |
| ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| `python3 scripts/validate_dtcg.py evals/files/sample.tokens.json` | Validate the committed token fixture against the pinned DTCG checks. |

## Verified output

```json
{
  "errors": [],
  "resolved_references": 9,
  "schema_sha256": "9b501b5666f7515bd0051ff0aec3566b78a3cbe82b0280c90d03660c2e02246e",
  "specification": "DTCG 2025.10",
  "token_count": 44,
  "types": {
    "border": 1,
    "color": 15,
    "cubicBezier": 2,
    "dimension": 9,
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

The committed token and evidence fixtures are `evals/files/sample.tokens.json` and `evals/files/sample.evidence.json`. This checkpoint creates no new file. No HTML pass is claimed or bundled as a visual precedent.
