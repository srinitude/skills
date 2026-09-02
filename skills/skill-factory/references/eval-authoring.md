# Eval authoring

Evals prove a skill helps. Load each skill's files under evals/ through `mise run evals`.

## Behavior cases

The shape:

    {
      "skill_name": "csv-cleaner",
      "evals": [
        {
          "id": 1,
          "prompt": "clean up sales_2025.csv, some emails are missing",
          "expected_output": "A cleaned file plus a count of rows fixed.",
          "assertions": ["The reply states how many emails were missing."],
          "files": ["sales_2025.csv"]
        }
      ]
    }

At least four cases. Prompts read like real requests: file paths, column names, casual phrasing, an occasional typo. Cover at least one edge, such as malformed input or a request the skill must refuse. Load input files under evals/files/ through `mise run evals` and list them per case.

Assertions are verifiable statements. "The output file is valid JSON" and "the report holds at least 3 recommendations" work; "the output is good" does not. Grade against quoted evidence, and mark a section header with no substance as a fail. Leave taste and style to human review instead of assertions.

## Trigger queries

A list of entries shaped {"query": "...", "should_trigger": true}. The checker enforces a floor of 4 with both labels present, and the shipping bar is about 20, half positive and half negative. Treat the floor as the schema minimum, never as the target. The strongest negatives are near misses: queries that share keywords with the skill yet need something different. Realism helps, so include paths, personal context, and abbreviations.

## What does the srinitude registry add?

A skill destined for the srinitude/skills registry loads the registry artifact set under evals/ through `mise run evals`: manifest.json names run inputs, cases.json holds graded behavior cases, trigger-cases.json holds trigger prompts, contract.md freezes regression, rubric.md guides the judge, speed-budgets.json caps timing, and source-lineage.json records real source hashes and the public version.

## How do I run them?

`mise run evals` validates both files: schema, unique ids, listed input files, both trigger labels present.

To measure behavior, run each case twice in fresh contexts, once with the skill installed and once without, and grade every assertion with evidence. For triggering, run each query about three times and use a 0.5 trigger rate threshold. When tuning a description, keep a train and a validation split, change the description only from train failures, and stop after about five rounds or when gains stall.
