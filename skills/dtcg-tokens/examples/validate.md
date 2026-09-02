# Validate command

**Guess removed:** A readable JSON file is not assumed to be DTCG-conformant.

## User

> Validate evals/files/sample.tokens.json as DTCG 2025.10. Do not edit it. Use `mise run token-packet -- <args>` for this routed resource.

## Visible reply

The file passed the bundled DTCG 2025.10 structure, value, reference, type-agreement, and cycle checks. It contains 45 tokens and 9 resolved references. This does not prove visual quality or downstream tool support.

## Command

| Command                                                     | Purpose                                 |
| ----------------------------------------------------------- | --------------------------------------- |
| `mise run token-validate -- evals/files/sample.tokens.json` | Validate the sample without editing it. |

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

The command created no files.
