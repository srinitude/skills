# Direct contradiction

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this for a same-scope contradiction with an authorized minimal repair.

## What the user said

> Audit and minimally repair these rules. Rule 1: Every production deployment requires two reviewers. Rule 2: A production deployment may proceed with one reviewer. Rule 2 was intended to cover rehearsal deployments only.

## The visible reply

> [2026-07-31 EDT] **Result: CONFIRMED high-impact contradiction.**
>
> **Bounded source set:** Rule 1, Rule 2, and your statement that Rule 2 was intended for rehearsals.
>
> **Finding LA-F001**
>
> - **Normalized reading:** Both written rules currently govern production deployments, at the same time and authority level. Rule 1 requires two reviewers. Rule 2 permits one.
> - **Evidence:** The two supplied rules and your stated intent.
> - **Repair:** Replace Rule 2 with: `A rehearsal deployment may proceed with one reviewer.`
> - **Confidence:** High.
>
> **Negative case:** A rehearsal deployment with one reviewer now satisfies Rule 2 and does not weaken Rule 1. A production deployment with one reviewer still fails Rule 1.
>
> **Decision: PASS** for this bounded source set after the stated repair.

## Commands and files

Commands: None. Exit codes: None. Files created: None.

## A reply that fails

> Rule 2 is newer, so it overrides Rule 1.

This invents a date and authority rule, then weakens the two-reviewer requirement without using the user's stated rehearsal scope.
