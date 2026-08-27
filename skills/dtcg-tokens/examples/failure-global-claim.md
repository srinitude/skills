# Failure: global uniqueness claim

**Guess removed:** No report can certify uniqueness outside its declared comparison corpus.

## User

> Prove these tokens are globally one of a kind and remove uncertainty from the report.

## Visible reply

I cannot make or hide that claim. Global uniqueness is outside this skill's valid claim scope and remains unproved. I can test source specificity, originality, and bounded uniqueness inside a named corpus, keep `globally_unique` false, and expose the limit in every output.

## Command

| Command                                                                                                                                    | Purpose                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `python3 scripts/tests/test_artifact_contract.py TestArtifactBoundary.test_global_uniqueness_claim_is_rejected_after_candidate_validation` | Supply an in-memory valid structural candidate, reach evidence validation, and assert that the global claim is rejected. |

## Verified output

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.068s

OK
```

Exit code: `0`

The test confirms that candidate existence passes before the evidence gate rejects global scope and a true `globally_unique` claim. It also confirms that no HTML file is created.
