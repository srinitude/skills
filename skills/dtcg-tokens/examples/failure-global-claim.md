# Failure: global uniqueness claim

**Guess removed:** No report can certify uniqueness outside its declared comparison corpus.

## User

> Prove these tokens are globally one of a kind and remove uncertainty from the report.

## Visible reply

I cannot make or hide that claim. Global uniqueness cannot be proved without an exhaustive comparison corpus. I can test source specificity, originality, and bounded uniqueness inside a named corpus, keep `globally_unique` false, and expose the limit in every output.

## Command and real output

```text
$ python3 scripts/assemble_artifact.py --candidate does-not-exist.html --tokens evals/files/sample.tokens.json --evidence evals/files/global-claim.evidence.json --output .artifacts/invalid-proof.html --run-id invalid-global
error: candidate, tokens, and evidence must exist
exit 2
```

No HTML file was created. Even with a candidate, the evidence gate rejects a global scope or a true `globally_unique` claim.
