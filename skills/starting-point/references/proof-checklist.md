# Proof checklist

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this reference before claiming a result when component evidence, approvals, or external effects can be mistaken for whole completion.

## Before execution

- Name the observable parent outcome.
- Name each sub-outcome that must hold.
- Separate fixed constraints from candidate methods.
- Identify approvals for sensitive, irreversible, external, costly, or expanded action.
- State what evidence would disprove the chosen route.

## Before a completion claim

- Verify every claimed file, command, test, setting, or external state with fresh evidence.
- State subtask verification separately from whole-outcome completion.
- Do not use a component test to claim an untested parent result.
- Do not treat output volume, activity, or a proxy metric as outcome proof.
- Keep unapproved action pending even when analysis suggests it would help.
- Record blocked checks and the smallest next action that could resolve them.

## Proof thresholds by task type

| Task                    | Proof                                                                                            | Not proof                                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Script or tool          | Executed against representative inputs with the output and exit code shown.                      | The code reads correctly, or it ran on inputs the user will never have. |
| Documentation change    | The change exists in the target system and matches behavior verified against the running system. | A local draft, which proves only that a draft exists.                   |
| Experiment              | A pre-registered stopping rule was reached and the primary metric was read once.                 | The test is live, or an early peek looks good.                          |
| Bug fix                 | The failure was reproduced before the change and does not reproduce after it.                    | The symptom was absent on one rerun.                                    |
| Message or notification | Send confirmation from the sending system.                                                       | A prepared draft, or an intent to send.                                 |
| Release                 | Every gate the owner requires, run on the shipped artifact.                                      | A passing component suite.                                              |

When you cannot reach the threshold, say which one you reached, name the gap in one sentence, and give the smallest next action that would close it. An unreached outcome reported plainly is a good result. A reached-sounding sentence over component evidence is not.

## Wording rule

Say exactly what the evidence proves. A focused test proves the focused scope. A local package check does not prove remote installation. A prepared message does not prove delivery. A passing component does not prove the whole release.
