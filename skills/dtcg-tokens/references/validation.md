# Validation

Run `mise run ci` from the skill root. It executes unit tests, sample token validation, artifact-boundary checks, package structure, file-route audit, exploration validation, writing, code, placeholder, and eval checks.

If the task runner is unavailable, run these direct commands in order and report every exit code:

| Order | Command                                                           | Proves                                                            |
| ----: | ----------------------------------------------------------------- | ----------------------------------------------------------------- |
|     1 | `python3 -m unittest discover -s scripts/tests -p 'test_*.py'`    | Unit contracts pass.                                              |
|     2 | `python3 scripts/prepare_google_fonts.py --help`                  | The font-preparation interface documents its inputs.              |
|     3 | `python3 scripts/validate_dtcg.py evals/files/sample.tokens.json` | The sample token fixture passes the pinned DTCG checks.           |
|     4 | `python3 scripts/check_artifact_contract.py .`                    | Fixed visual precedents and removed generators remain absent.     |
|     5 | `python3 scripts/validate_skill.py .`                             | Package structure and routes are valid.                           |
|     6 | `python3 scripts/audit_file_triggers.py .`                        | Every current file has an activation or consumer route.           |
|     7 | `python3 scripts/validate_exploration.py .`                       | Frontier, corpus, transfer, experiment, and hash rules pass.      |
|     8 | `python3 scripts/lint_writing.py .`                               | Writing rules pass.                                               |
|     9 | `python3 scripts/check_code_rules.py .`                           | Code boundary rules pass.                                         |
|    10 | `python3 scripts/check_placeholders.py .`                         | Placeholder contracts pass.                                       |
|    11 | `python3 scripts/check_evals.py . --min-cases 4 --min-queries 8`  | Evaluation coverage meets its floor.                              |
|    12 | `skills-ref validate .`                                           | The current official Agent Skills reference validator accepts it. |

For each `generate` or `prove` run, also execute the current-catalog command in `references/google-font-selection.md` with at least three candidates and one selection. Save the returned catalog, manifest, and CSS. That network check is run-specific and does not belong in offline package CI.

For package maintenance, install `skills-ref` from the current official Agent Skills repository in an isolated environment before running row 12. If the official validator cannot run, record that external format proof as blocked. Do not treat `scripts/validate_skill.py` as a substitute for the official check.

Also parse every JSON asset and fixture, verify no removed visual generator or fixed proof template returned, and search the package for forbidden global-uniqueness claims.

Package checks prove structure, catalog coverage, validator behavior, and script boundaries. They do not prove that a visual artifact is well designed. Only recorded strong native vision review of the actual run can support that claim.
