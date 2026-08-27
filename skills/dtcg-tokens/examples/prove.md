# Prove command

**Guess removed:** The assembler cannot invent a proof design or issue its own visual verdict.

## User

> Prove evals/files/sample.tokens.json with evals/files/sample.evidence.json and make the report standalone.

## Visible reply

The token and evidence records are valid preflight inputs, but no strong-vision-authored HTML candidate was supplied. Proof remains blocked. The next required action is artifact authorship from the current sources and tokens, using the selected prepared WOFF2 bytes and their licenses, followed by assembly, candidate comparison, wide and narrow visual review, fallback inspection, repair, final assembly, and final readback.

## Command

| Command                                                                                                                                                                                                                    | Purpose                                                                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `python3 scripts/assemble_artifact.py --candidate does-not-exist.html --tokens evals/files/sample.tokens.json --evidence evals/files/sample.evidence.json --output .artifacts/sample-proof.html --run-id sample-preflight` | Confirm that proof assembly blocks when the required run-specific candidate is absent. |

## Verified output

```text
error: candidate, tokens, and evidence must exist
```

Exit code: `2`

No file was created. This failure is intentional because a reusable proof shell would violate the run-specific artifact contract.
