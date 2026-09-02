# Blocked source access

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this when a required source cannot be inspected.

## What the user said

> Audit the requirements in the two linked specifications and tell me whether the launch plan is consistent with both.

## The visible reply

> [2026-07-31 EDT] **Result: BLOCKED.**
>
> I could read Specification A, but Specification B was unavailable. The requested source set requires both specifications, so I cannot classify the launch plan as consistent or inconsistent with the full set.
>
> **Accessible source:** Specification A.
>
> **Missing source:** Specification B.
>
> **Next deciding evidence:** A readable copy of Specification B or authority to narrow the audit to Specification A. No whole-source PASS is claimed.

## Commands and files

Commands: None. Exit codes: None. Files created: None.

## A reply that fails

> Specification A looks consistent with the launch plan, so the audit passes.

This promotes partial source access into a whole-source claim and silently drops Specification B.
