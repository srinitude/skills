# Evaluation rubric

Owner and backlink: [`../SKILL.md`](../SKILL.md). Apply this rubric only to frozen records from `cases.json` under `contract.md`.

## Criterion verdicts

For each required criterion, return:

- `PASS` when the response clearly performs or states the required behavior;
- `BLOCKED` when the behavior is missing, contradicted, or too vague to verify.

For each veto criterion, return:

- `PASS` when the forbidden behavior is absent;
- `BLOCKED` when the response performs, recommends, or falsely claims it.

Do not score preferred wording, field ordering inside a mapping, or harmless extra detail that the schema permits.

## Scoring font claims

A rarity claim is evidence only when the document carries the number. Score `PASS` when the entry holds a complete rarity record whose rank, family count, and percentile agree with the frozen snapshot and whose percentile clears the floor. Score `BLOCKED` when any part is missing, when the rank disagrees with the snapshot, when the source is not the live feed, or when the case for rarity rests on adjectives such as unusual, overlooked, or distinctive.

Score an absent family as `BLOCKED` even when the name looks plausible. Score a common interface default as `BLOCKED` regardless of the surrounding argument.

## Material decision conflict

Two responses conflict when they choose different section sets, different evidence buckets for the same claim, different font families, different rarity floors, or different completion states. Wording differences and different but equally grounded token values are not a conflict.

## Fail-closed rules

Mark the record BLOCKED when any of these conditions holds:

- the case ID, response, criterion, verdict, or observation is missing;
- a verdict is not `PASS` or `BLOCKED`;
- the document fails to parse or the validator exits non-zero;
- the candidate identity or frozen input hash differs;
- the response claims a command ran without a recorded exit code;
- the judge cannot determine whether a required or forbidden behavior occurred.

## Judge output

Return one record per candidate response with the case ID, run index, required verdicts, veto verdicts, one short observation per criterion, the validator exit code, the font evidence verdict, overall status, and material-conflict flag. Do not replace criterion records with an aggregate score.
