# Evaluation contract

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). This file owns the public regression procedure. The parent owns runtime behavior.

## Frozen inputs

Freeze and hash these inputs before a behavioral run:

- the deployed `SKILL.md`;
- `cases.json`, `rubric.md`, and `speed-budgets.json`;
- the reference images each case supplies, by content hash;
- one live font catalog snapshot, stored with its retrieval timestamp and family count;
- the candidate and judge identities;
- transport and provider settings;
- prompts, response limits, and retry rules.

A changed case, criterion, threshold, image, prompt, route, or skill byte invalidates the run. The font catalog is the one input that moves on its own, so the snapshot is frozen at the start of the run and every rarity verdict is scored against that snapshot rather than against a later read.

## Static gate

Resource gate: run `mise run validate` before using package files named here.

Require all of the following:

- valid frontmatter with `metadata.version: "0.2.1"`;
- a description that starts with `Use when` and stays at or below 1024 characters;
- exactly five unique `VDS-###` cases across every declared group;
- one frozen native `source_id` per case;
- one worked example per command in `examples/`, each with real command output and exit codes;
- required and veto criteria on every case;
- no unresolved local links;
- governed Markdown below 200 lines;
- current source-lineage hashes;
- the five bundled checks exiting 0 inside the skill directory: the unittest suite, `validate_skill.py`, `lint_writing.py`, `check_code_rules.py`, and `check_evals.py`.

## Trigger gate

Use positive triggers, hard negatives, and close boundary cases. Two boundary pairs matter most: describing an image against extracting a system from it, and listing fonts against building a typography section from a reference. A trigger pass requires the skill to load for every positive case and stay unloaded for every negative case. Repeat live trigger checks when the candidate is nondeterministic.

## Behavior gate

1. Run every case twice in a fresh context under both declared conditions.
2. Permit reads of the frozen catalog snapshot and the supplied images. Block external writes.
3. Parse every returned document with a YAML parser before scoring it. A parse failure is BLOCKED, not a low score.
4. Run the bundled validator against every returned document and record the exit code.
5. Save raw prompts and responses and record their SHA-256 values.
6. Score every required and veto criterion using `rubric.md`.
7. Judge each with-skill response in forward and reverse case order without exposing earlier verdicts.
8. Treat missing records, malformed output, failed skill loading, or identity drift as BLOCKED.
9. Recompute IDs, counts, and hashes from raw records before reporting.

The without-skill condition is the baseline. It measures added value but does not need to pass the with-skill criteria.

## Font evidence gate

For every selected family in a returned document, check four things against the frozen snapshot: the family exists in the catalog, the recorded popularity rank equals the snapshot rank, the recorded percentile matches the recorded rank and family count, and the percentile sits at or above the declared floor. A family that clears the floor by prose alone fails. A family absent from the snapshot fails even when it exists elsewhere.

## Decision rule

A with-skill response passes only when every required criterion passes, every veto is absent, the document parses, the validator exits 0, and the font evidence gate passes. A case passes only when both with-skill replicas pass in both judge orders with no material decision conflict.

Whole-eval PASS requires:

- five of five cases pass;
- ten of ten with-skill responses pass;
- twenty of twenty order-specific verdicts pass;
- every trigger case is classified correctly;
- zero vetoes, parse failures, missing records, or material judge conflicts;
- static, font evidence, and speed gates pass after the behavior run.

Anything else is BLOCKED. Do not average away a failed boundary.

## Report

Record the frozen hashes, the catalog snapshot timestamp and family count, identities, provider route, token usage, reported cost, timing, criterion verdicts, conflicts, and blocked records. Keep subtask verification, whole-eval completion, package completion, and remote release completion as separate statuses.

Behavioral judging is evidence for the frozen run, not proof of all future behavior.
