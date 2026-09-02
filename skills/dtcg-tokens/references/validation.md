# Validation

Run `mise run ci` from the skill root. Mise uses dependency edges to run eligible read-only jobs together and covers every check below.

| Task                            | Proves                                                                     |
| ------------------------------- | -------------------------------------------------------------------------- |
| `mise run test`                 | Unit and package contracts pass.                                           |
| `mise run validate-dtcg`        | The sample token fixture passes the pinned DTCG checks.                    |
| `mise run artifact-contract`    | Fixed visual precedents and removed generators remain absent.              |
| `mise run validate`             | Package structure and routes are valid.                                    |
| `mise run audit-files`          | Every current file has an activation or consumer route.                    |
| `mise run validate-exploration` | Frontier, corpus, transfer, experiment, and hash rules pass.               |
| `mise run lint-writing`         | Writing rules pass.                                                        |
| `mise run lint-code`            | Code boundary rules pass.                                                  |
| `mise run lint-placeholders`    | Placeholder contracts pass.                                                |
| `mise run evals`                | Evaluation coverage meets its floor.                                       |
| `mise run improvement-policy`   | The optional trial cannot trade a protected dimension for its target gain. |
| `mise run lineage`              | The release version, inventory, and source hashes match current bytes.     |

If Mise is unavailable, return `BLOCKED`. Do not bypass its graph with direct script commands.

For each `generate` or `prove` run, also execute the current-catalog command in `references/google-font-selection.md` with at least three candidates and one selection. Save the returned catalog, manifest, and CSS. That network check is run-specific and does not belong in offline package CI. Use `mise run token-packet -- <args>` for this routed resource.

For package maintenance, run the current official Agent Skills reference validator through an owning Mise task in the consuming repository. If the official validator cannot run, record that external format proof as blocked. Do not treat the local structure task as a substitute for the official check.

Also parse every JSON asset and fixture, verify no removed visual generator or fixed proof template returned, and search the package for forbidden global-uniqueness claims.

Package checks prove structure, catalog coverage, validator behavior, and script boundaries. They do not prove that a visual artifact is well designed. Only recorded strong native vision review of the actual run can support that claim.
