# Evaluation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md). This file owns the public regression procedure. The parent owns runtime behavior.

## Frozen inputs

Freeze and hash these inputs before a behavioral run:

- the deployed `SKILL.md`;
- `cases.json`, `rubric.md`, and `speed-budgets.json`;
- the candidate and judge identities;
- transport and provider settings;
- prompts, response limits, and retry rules.

A changed case, criterion, threshold, prompt, route, or skill byte invalidates the run.

## Static gate

Require all of the following:

- valid Agent Skills frontmatter with `metadata.version: "0.1.0"`;
- a description that starts with `Use when` and stays at or below 1024 characters;
- exactly five unique `RFY-###` cases across every declared group;
- one frozen native `source_id` per case;
- required and veto criteria on every case;
- no unresolved local links;
- governed Markdown below 200 lines;
- current source-lineage hashes.

## Trigger gate

Use positive triggers, hard negatives, and close boundary cases. A trigger pass requires the skill to load for every positive case and stay unloaded for every negative case. Repeat live trigger checks when the candidate is nondeterministic.

## Behavior gate

1. Run every case twice in a fresh context under both declared conditions.
2. Permit only read-only capability discovery and named-source reads. Block external writes.
3. Keep each answer at or below 350 words.
4. Save raw prompts and responses and record their SHA-256 values.
5. Score every required and veto criterion using `rubric.md`.
6. Judge each with-skill response in forward and reverse case order without exposing earlier verdicts.
7. Treat missing records, malformed output, failed skill loading, or identity drift as BLOCKED.
8. Recompute IDs, counts, and hashes from raw records before reporting.

The without-skill condition is the baseline. It measures added value but does not need to pass the with-skill criteria.

## Decision rule

A with-skill response passes only when every required criterion passes and every veto is absent. A case passes only when both with-skill replicas pass in both judge orders with no material decision conflict.

Whole-eval PASS requires:

- five of five cases pass;
- ten of ten with-skill responses pass;
- twenty of twenty order-specific verdicts pass;
- every trigger case is classified correctly;
- zero vetoes, parse failures, missing records, or material judge conflicts;
- static and speed gates pass after the behavior run.

Anything else is BLOCKED. Do not average away a failed boundary.

## Report

Record the frozen hashes, identities, provider route, token usage, reported cost, timing, criterion verdicts, conflicts, and blocked records. Keep subtask verification, whole-eval completion, package completion, and remote release completion as separate statuses.

Behavioral judging is evidence for the frozen run, not proof of all future behavior.
