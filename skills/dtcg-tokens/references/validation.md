# Validation

Run `mise run ci` from the skill root. It executes unit tests, sample token validation, artifact-boundary checks, package structure, writing, code, placeholder, and eval checks.

If the task runner is unavailable, run these direct commands in order and report every exit code:

```sh
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
python3 scripts/validate_dtcg.py evals/files/sample.tokens.json
python3 scripts/check_artifact_contract.py .
python3 scripts/validate_skill.py .
python3 scripts/lint_writing.py .
python3 scripts/check_code_rules.py .
python3 scripts/check_placeholders.py .
python3 scripts/check_evals.py . --min-cases 4 --min-queries 8
```

Also parse every JSON asset and fixture, verify no removed visual generator or fixed proof template returned, and search the package for forbidden global-uniqueness claims.

Package checks prove structure, catalog coverage, validator behavior, and script boundaries. They do not prove that a visual artifact is well designed. Only recorded strong native vision review of the actual run can support that claim.
