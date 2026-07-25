# Example: maintain

Guess removed: that a rule can be added to the schema and the references without a test that fails first.

## The user says

> add a rule that every selected font records its fit and legibility score

## The reply

Test first. I added the fit tests to scripts/tests/test_font_rules.py, watched them fail against the old fixture and the old messages, then changed font_rules.py, the schema skeleton, and the fixture until the suite went green. Four tests failed on the way through, which is the point of the order.

## Commands run

The red run, after the new rule landed in the checker and before the fixtures and messages caught up:

```
$ PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with 'PyYAML>=6,<7' python -m unittest discover -s scripts/tests -p 'test_*.py'
FAIL: test_a_complete_candidate_passes (test_font_rules.AcceptanceTests.test_a_complete_candidate_passes)
FAIL: test_observed_families_carry_no_rarity_duty (test_font_rules.AcceptanceTests.test_observed_families_carry_no_rarity_duty)
FAIL: test_a_common_default_is_rejected (test_font_rules.RejectionTests.test_a_common_default_is_rejected)
FAIL: test_a_common_family_is_rejected (test_validate_extraction.RejectionTests.test_a_common_family_is_rejected)
Ran 140 tests in 3.826s
FAILED (failures=4)
exit=1
```

The green run, after the candidate fixtures carried a fit block and the common face message changed to name the stated reason:

```
$ PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with 'PyYAML>=6,<7' python -m unittest discover -s scripts/tests -p 'test_*.py'
Ran 144 tests in 3.992s
OK
exit=0
```

The four new tests are the ones that pinned the rule: a missing fit record is rejected, a fit score under the bar is rejected, a legibility score under the role floor is rejected, and an overexposed default passes only when common_face_reason states the evidence.

Then the other four checks:

```
$ python3 scripts/check_code_rules.py .
checked 32 files, 0 problems
exit=0
```

## Files created or changed

| File                             | Change                                                                    |
| -------------------------------- | ------------------------------------------------------------------------- |
| scripts/tests/test_font_rules.py | Four new rejection tests and a fit block in the shared candidate fixture. |
| scripts/font_rules.py            | check_fit and check_bar, plus the common face exception path.             |
| assets/schema-skeleton.yaml      | fit keys under every selected family and the meta.viability block.        |
| assets/minimal-extraction.yaml   | Real fit blocks, live rarity blocks, and a recorded viability judgment.   |

Every rule change touches the checker, a test, the schema reference, and the examples in the same commit. An example that contradicts SKILL.md is a defect, not documentation.
