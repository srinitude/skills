# Validation

Run `mise run ci` from the skill root. It executes unit tests, sample token validation, artifact-boundary checks, package structure, writing, code, placeholder, and eval checks.

If the task runner is unavailable, run these direct commands in order and report every exit code:

| Order | Command                                                           | Proves                                                        |
| ----: | ----------------------------------------------------------------- | ------------------------------------------------------------- |
|     1 | `python3 -m unittest discover -s scripts/tests -p 'test_*.py'`    | Unit contracts pass.                                          |
|     2 | `python3 scripts/validate_dtcg.py evals/files/sample.tokens.json` | The sample token fixture passes the pinned DTCG checks.       |
|     3 | `python3 scripts/check_artifact_contract.py .`                    | Fixed visual precedents and removed generators remain absent. |
|     4 | `python3 scripts/validate_skill.py .`                             | Package structure and routes are valid.                       |
|     5 | `python3 scripts/lint_writing.py .`                               | Writing rules pass.                                           |
|     6 | `python3 scripts/check_code_rules.py .`                           | Code boundary rules pass.                                     |
|     7 | `python3 scripts/check_placeholders.py .`                         | Placeholder contracts pass.                                   |
|     8 | `python3 scripts/check_evals.py . --min-cases 4 --min-queries 8`  | Evaluation coverage meets its floor.                          |

Also parse every JSON asset and fixture, verify no removed visual generator or fixed proof template returned, and search the package for forbidden global-uniqueness claims.

Package checks prove structure, catalog coverage, validator behavior, and script boundaries. They do not prove that a visual artifact is well designed. Only recorded strong native vision review of the actual run can support that claim.
