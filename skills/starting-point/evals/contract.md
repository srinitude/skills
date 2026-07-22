# Evaluation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md). This file owns the public regression procedure. The parent owns runtime behavior.

## Frozen inputs

Freeze and hash these inputs before a behavioral run:

- the deployed `SKILL.md` and required references;
- `cases.json`, `rubric.md`, and `speed-budgets.json`;
- the candidate and judge identities;
- transport and provider settings;
- prompts, response limits, and retry rules.

A changed case, criterion, threshold, prompt, route, or skill byte invalidates the run.

## Static gate

Require all of the following:

- valid frontmatter with `metadata.version: "0.1.0"`;
- a description that starts with `Use when`, states when the skill applies, and stays within 1024 characters;
- exactly 18 unique `SP-###` cases across every declared group;
- one native `source_id` per case;
- required and veto criteria on every case;
- no unresolved local links;
- governed Markdown at or below 200 lines;
- current source-lineage hashes.

## Trigger gate

Use positive triggers, hard negatives, and near-neighbor pairs. A trigger pass requires the skill to load for every positive case and stay unloaded for every hard negative. Near-neighbor pairs must differ only at the intended boundary.

## Behavior gate

1. Run every case twice in a fresh context with the public skill explicitly loaded.
2. Permit no side effects or tools except reading linked skill references.
3. Keep each answer at or below 350 words.
4. Save raw prompts and responses and record their SHA-256 values.
5. Score every required and veto criterion using `rubric.md`.
6. Judge the complete set again in reverse order without exposing earlier verdicts.
7. Treat missing records, malformed output, failed skill loading, or identity drift as BLOCKED.
8. Recompute IDs, counts, and hashes from raw records before reporting.

## Decision rule

A response passes only when every required criterion passes and every veto is absent. A case passes only when both responses pass in both judge orders with no material decision conflict.

Whole-eval PASS requires:

- 18 of 18 cases pass;
- 36 of 36 candidate responses pass;
- 72 of 72 order-specific verdicts pass;
- zero vetoes, parse failures, missing records, or material judge conflicts;
- static, trigger, and speed gates pass after the behavior run.

Anything else is BLOCKED. Do not average away a failed boundary.

## Report

Record the frozen hashes, identities, provider route, token usage, reported cost, timing, criterion verdicts, conflicts, and blocked records. Keep these statuses separate:

- subtask verification;
- whole-eval completion;
- package completion;
- remote release completion.

Behavioral judging is evidence for this run, not proof of all future behavior.
