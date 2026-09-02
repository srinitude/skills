# Conversation candidate path

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this when a live request names an outcome, a safety boundary, and a proposed implementation.

Guess it removes: whether three screens and a REST endpoint are requirements or candidate paths.

## What the user said

> I need first-time account setup completed in under two minutes, with no personal data in logs. Start with three screens and a REST endpoint. Help me make it concrete.

## The visible reply

> **Contract**
>
> - **Outcome:** A first-time user completes account setup in under two minutes.
> - **Proof:** A timed run of the complete setup flow finishes in under two minutes.
> - **Boundary:** Logs contain no personal data.
> - **Candidate path:** Three screens backed by a REST endpoint.
> - **Adaptation rule:** Replace that path only if the alternative keeps the time limit and logging boundary, and evidence shows a material benefit or the current path is blocked.
> - **Unknown:** Which target user and environment should supply the timed run?
>
> I can turn this into the first inspectable flow once that proof context is fixed. Which target user and environment should the timed run represent?

## Commands and files

Commands: None. Exit codes: None. Files created: None.

## A reply that fails

> I will build three React screens and a REST endpoint, then time them.

This executes a candidate implementation before the contract is accepted, silently adds a framework, and leaves the privacy boundary without proof.
