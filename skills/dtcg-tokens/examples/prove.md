# Prove command

**Guess removed:** The assembler cannot invent a proof design or issue its own visual verdict.

## User

> Prove evals/files/sample.tokens.json with evals/files/sample.evidence.json and make the report standalone.

## Visible reply

The token and evidence records are valid preflight inputs, but no strong-vision-authored HTML candidate was supplied. Proof remains blocked. The next required action is artifact authorship from the current sources and tokens, followed by assembly, wide and narrow visual review, repair, final assembly, and final readback.

## Command and real output

```text
$ python3 scripts/assemble_artifact.py --candidate does-not-exist.html --tokens evals/files/sample.tokens.json --evidence evals/files/sample.evidence.json --output .artifacts/sample-proof.html --run-id sample-preflight
error: candidate, tokens, and evidence must exist
exit 2
```

No file was created. This failure is intentional because a reusable proof shell would violate the run-specific artifact contract.
