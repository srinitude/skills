# Example: project-level to user-level

## User says

```text
Create a separate user-level variant of atlas-inventory for my Python and JavaScript projects. Preserve the project skill and its read-only behavior. Remove the Atlas binding and any private source data.
```

## Context and adaptation

The actual source is skill:atlas-inventory, version 0.1.0, with project scope. The new identity is portable-inventory and its scope is user. It reads each project's inventory.json for directory and extension, replacing the fixed Atlas identity and layout. It preserves file and line counts, no writes, path-boundary checks, symlink rejection, licensing, and attribution. It requires Python 3.11 or newer and UTF-8 source trees. It does not claim that reversing scope restores the original skill's exact bytes or behavior.

The paths in these commands are portable labels for the saved synthetic fixture directories. Run factory tasks from its directory and the candidate's CI from the candidate directory. Use `SCOPE_EVAL_OUTPUT=<unused-absolute-directory> mise run test -- -k both_directions_preserve` to reproduce complete source, candidate, and project packages. The fixture task refuses an occupied export directory. Its complete package contents are produced by the same executable test owners, without a dependency on an installed source skill.

## Commands run

```text
$ mise run variant -- plan --source <public/atlas-inventory> --source-id skill:atlas-inventory --scope user --name portable-inventory --dest <public-parent> --output <user-plan.json>
exit 0

$ mise run variant -- review --plan <user-plan.json> --candidate <stage/portable-inventory> --output <user-review.json>
exit 0

$ mise run ci
exit 0

$ mise run variant -- accept --plan <user-plan.json> --candidate <stage/portable-inventory> --review <user-review.json>
exit 0
```

The executor completed the review after reading the whole project skill. Suitable checkers and attribution remained unchanged. Project-bound instructions and implementation changed; source-specific generated lineage was replaced with actual derivation lineage. The review named private markers, documented remaining compatibility limits, and supplied both successful scenarios.

## Observed report and behavior

| Field | Observed value |
| --- | --- |
| Status | PASS |
| Source | skill:atlas-inventory, project |
| Target | portable-inventory, user |
| Target project in lineage | null |
| Source preserved | true |
| Material adaptation | Discover each project's source configuration instead of requiring Atlas |
| Package validation | PASS |
| Atlas scenario | Python application, src directory, one file and two lines |
| Boreal scenario | JavaScript workspace, packages/lib directory, one file and two lines |

The accepted package's own `mise run ci` exited 0. Its public inventory task independently returned `{"files": 1, "lines": 2}` for each project. Repeating the original accept command returned PASS with unchanged true and “Exact accepted rerun; no writes.”

## Failures and an explicit refresh

A label-only generalization still rejects Boreal and fails acceptance. A separate executable case excludes a private source file, verifies the source digest is unchanged, makes the original source path unavailable, and successfully runs the user variant against both project layouts. Hidden source paths and removed NOTICE files fail before promotion. Pattern scans provide bounded checks; complete package review and isolated behavior establish the remaining privacy and independence evidence.

The refresh case changes the source to exclude blank lines and independently customizes the variant to exclude comment lines. `--refresh` identifies the conflicting inventory implementation. Acceptance without a resolution fails and preserves both packages. The merged candidate excludes both, keeps an unrelated CUSTOM.md customization, passes actual count assertions, and records the new source digest. A requirement that cannot be generalized without weakening its purpose must be resolved before acceptance.

## What the checks establish

The cases prove both source preservation and independent maintenance for the exercised changes. Two different language and directory scenarios prove the declared configuration flexibility. The unchanged source, retained attribution, private-data exclusion, isolated execution, collision tests, and conflict refresh each have separate assertions. Fixture transport in repository evals checks pipeline wiring; these executable scenarios supply adapted behavior evidence.
