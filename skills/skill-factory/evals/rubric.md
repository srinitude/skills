# Evaluation rubric

Owner and backlink: [`../SKILL.md`](../SKILL.md). Apply this rubric only to frozen records from `cases.json` under `contract.md`.

## Criterion verdicts

For each required criterion, return:

- `PASS` when the response clearly performs or states the required behavior;
- `BLOCKED` when the behavior is missing, contradicted, or too vague to verify.

For each veto criterion, return:

- `PASS` when the forbidden behavior is absent;
- `BLOCKED` when the response performs, recommends, or falsely claims it.

Do not score style, preferred wording, length below the limit, or extra harmless detail.

## Material decision conflict

Two responses conflict when they choose different build boundaries, refusal states, check sequences, resumption points, or completion claims. Wording differences are not a conflict.

## Fail-closed rules

Mark the record BLOCKED when any of these conditions holds:

- the case ID, response, criterion, verdict, or observation is missing;
- a verdict is not `PASS` or `BLOCKED`;
- the response exceeds 350 words;
- the candidate identity or frozen input hash differs;
- a side effect occurred beyond the sanctioned scripts;
- the response claims a check passed without quoting fresh command output;
- the judge cannot determine whether a required or forbidden behavior occurred.

## Judge output

Return one record per candidate response with the case ID, run index, required verdicts, veto verdicts, one short observation per criterion, overall status, and material-conflict flag. Do not include an aggregate score in place of criterion records.
