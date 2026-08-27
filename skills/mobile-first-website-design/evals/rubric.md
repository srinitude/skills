# Evaluation rubric

Backlink: [SKILL.md](../SKILL.md). Use with [the evaluation contract](contract.md).

## PASS

The response selects the correct release state, names the failing invariant when blocked, preserves exact prompt and packet hashes, traverses breakpoints from smallest to largest, and never advances style before the style-free wireframe gate.

## FAIL

Fail any case that weakens a threshold, skips unavailable-route fallback, accepts style leakage, uses a mismatched prompt hash, changes native evidence, reports a broader PASS than the fixture proves, or retries a human or billing gate as transient.

## Speed

Fixture timing must stay within `speed-budgets.json`. Timing failure is `BLOCKED` and cannot be offset by a behavior score.
