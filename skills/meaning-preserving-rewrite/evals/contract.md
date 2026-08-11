# Evaluation contract

Evaluate the six public cases in `cases.json` under `with_skill` and `without_skill` conditions with two repetitions.

A case passes only when every required marker is present in meaning and every veto is absent. Trigger tests must include positive, rejection, and near-neighbor prompts. Fixture timing proves runner behavior only. Live behavior needs separately labeled model evidence.

Return `BLOCKED` for source drift, missing authority, inaccessible required evidence, or a required dependency with no portable equivalent.
