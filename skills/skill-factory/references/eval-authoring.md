# Eval authoring

Evals prove a skill helps. Each skill carries two files under evals/.

## evals/evals.json

The shape:

    {
      "skill_name": "csv-cleaner",
      "evals": [
        {
          "id": 1,
          "prompt": "clean up sales_2025.csv, some emails are missing",
          "expected_output": "A cleaned file plus a count of rows fixed.",
          "assertions": ["The reply states how many emails were missing."],
          "files": ["evals/files/sales_2025.csv"]
        }
      ]
    }

At least four cases. Prompts read like real requests: file paths, column names, casual phrasing, an occasional typo. Cover at least one edge, such as malformed input or a request the skill must refuse. Input files live under evals/files/ and are listed per case.

Assertions are verifiable statements. "The output file is valid JSON" and "the report holds at least 3 recommendations" work; "the output is good" does not. Grade against quoted evidence, and mark a section header with no substance as a fail. Leave taste and style to human review instead of assertions.

## evals/trigger-queries.json

A list of entries shaped {"query": "...", "should_trigger": true}. Aim for about 20, half positive and half negative. The strongest negatives are near misses: queries that share keywords with the skill yet need something different. Realism helps, so include paths, personal context, and abbreviations.

## What does the srinitude registry add?

A skill destined for the srinitude/skills registry keeps both files above and also ships the registry eval artifact set under evals/: manifest.json names the run inputs, cases.json holds graded behavior cases with required and veto criteria, trigger-cases.json holds positive, hard negative, and near neighbor prompts, contract.md freezes the regression procedure, rubric.md guides the judge, and speed-budgets.json caps fixture and live timing. The seventh file, source-lineage.json, records a sha256 hash for every source file plus a public_version equal to the skill's metadata.version, so the registry validator can prove which bytes produced the release. Regenerate the hashes whenever a hashed file changes; a stale or invented hash fails registry validation.

## How do I run them?

`mise run evals` validates both files: schema, unique ids, listed input files, both trigger labels present.

To measure behavior, run each case twice in fresh contexts, once with the skill installed and once without, and grade every assertion with evidence. For triggering, run each query about three times and use a 0.5 trigger rate threshold. When tuning a description, keep a train and a validation split, change the description only from train failures, and stop after about five rounds or when gains stall.
