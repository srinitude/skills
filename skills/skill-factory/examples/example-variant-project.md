# Example: user-level to project-level

## User says

```text
Create a separate project-level variant of my user-level file-inventory skill for Atlas. Preserve the original. Atlas counts Python files under src and must never write project files.
```

## Context and adaptation

The source is skill:demo-skill, version 0.1.0, with user scope. Atlas declares repo:atlas in its explicit inventory configuration. Its AGENTS.md requires configured source counts without writes. The variant has a distinct name, atlas-inventory, and project scope. Its implementation rejects another project identity or a changed src and .py configuration. Its instructions, reference, example, configuration inputs, and acceptance cases preserve the read-only count capability. MIT and NOTICE remain byte-exact.

The paths in these commands are portable labels for the saved synthetic fixture directories. Run factory tasks from its directory and the candidate's CI from the candidate directory. Use `SCOPE_EVAL_OUTPUT=<unused-absolute-directory> mise run test -- -k both_directions_preserve` to reproduce complete source, candidate, and project packages. The fixture task refuses an occupied export directory. Its complete package contents are produced by the same executable test owners, without a dependency on an installed source skill.

## Commands run

```text
$ mise run variant -- plan --source <source/demo-skill> --source-id skill:demo-skill --scope project --name atlas-inventory --dest <public-parent> --project <atlas> --project-id repo:atlas --output <project-plan.json>
exit 0

$ mise run variant -- review --plan <project-plan.json> --candidate <stage/atlas-inventory> --output <project-review.json>
exit 0

$ mise run ci
exit 0

$ mise run variant -- accept --plan <project-plan.json> --candidate <stage/atlas-inventory> --review <project-review.json>
exit 0
```

Between review and accept, the executor read every source and project file, completed the draft's dispositions and six project-fact categories, and bound the behavior expectation to Atlas. An empty review was also tried: acceptance failed with source_preserved true and promoted false. It produced no destination.

## Observed report

| Field | Observed value |
| --- | --- |
| Status | PASS |
| Source | skill:demo-skill, user |
| Target | atlas-inventory, project |
| Target project in lineage | repo:atlas |
| Source preserved | true |
| Material adaptation | Fixed project identity, Python src layout, and matching applicability and checks |
| Package validation | PASS |
| Atlas behavior | PASS, one file and two lines |

The accepted package's own `mise run ci` also exited 0. Running its inventory task against Boreal exited 1 with `wrong project`. The recorded lineage contains the actual source digest, both scopes, target identity, adaptations, requirements, compatibility, and refresh baselines.

## Failure and maintenance boundaries

Missing target-project context blocks planning. Missing or stale project review, lost attribution, and an occupied destination block acceptance. Updating demo-skill does not update atlas-inventory. Refresh only on request, using `--refresh`, the recorded source identity, and the same destination; compare baselines and resolve every conflicting customization before writing.

## What the checks establish

The package gates prove structural and scope contracts. The positive and negative executions prove the declared project restriction and count behavior for the fixture. Direct review connects that restriction to Atlas's authoritative instructions. These are synthetic acceptance scenarios and model review, not human usability testing or a claim about every future project.
