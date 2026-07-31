# Temporal non-contradiction

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before treating different effective dates as a conflict.

## What the user said

> The 2025 policy retained records for 90 days. The 2026 policy retains them for 30 days from January 1, 2026. Are these contradictory?

## The visible reply

> [2026-07-31 EDT] **Result: NOT_AN_ISSUE.**
>
> **Normalized reading:** The 90-day rule applies in 2025. The 30-day rule applies from January 1, 2026. Their time windows do not overlap, so the statements can both be true.
>
> **Remaining check:** Confirm that the 2026 policy supersedes the earlier rule for records created before its effective date. That transition case is unspecified, but it is a gap rather than a proved contradiction.
>
> **Decision: PARTIAL** because the supplied text does not define the transition case.

## Commands and files

Commands: None. Exit codes: None. Files created: None.

## A reply that fails

> The policies contradict because 90 is not 30.

This compares values before normalizing their effective dates and misses the transition gap.
