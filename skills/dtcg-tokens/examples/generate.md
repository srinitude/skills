# Generate command

**Guess removed:** Preliminary token validation does not imply that a proof artifact has passed visual review.

## User

> Generate DTCG tokens from the supplied visual references and brief. Use vision and prove the result is specific to them.

## Visible reply

I inventoried and hashed the sources, completed whole-frame, detail, and comparative visual passes, expanded the full possibility catalog, and narrowed each entry with a recorded reason. The preliminary DTCG file contains 44 tokens across all 13 standard types. Its required experimental partition contains two tokens from two different exploration strategies. Token structure passes. The evidence, run record, and run-specific HTML remain blocked until the strong-vision artifact review is recorded.

## Command and real output

```text
$ python3 scripts/validate_dtcg.py evals/files/sample.tokens.json
{
  "errors": [],
  "resolved_references": 9,
  "schema_sha256": "32e93b780e4e4bca778d0780cb797a560deedc470c608af16576223f7e42915f",
  "specification": "DTCG 2025.10",
  "token_count": 44,
  "types": {"border": 1, "color": 15, "cubicBezier": 2, "dimension": 9, "duration": 3, "fontFamily": 2, "fontWeight": 3, "gradient": 1, "number": 3, "shadow": 1, "strokeStyle": 1, "transition": 1, "typography": 2},
  "valid": true
}
exit 0
```

The preliminary token and evidence records are `evals/files/sample.tokens.json` and `evals/files/sample.evidence.json`. No HTML pass is claimed or bundled as a visual precedent.
