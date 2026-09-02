# Artifact audit

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this when a policy or specification may mix a fixed approval rule with a replaceable tool.

Guess it removes: whether a two-person production approval rule is merely procedural because the rollout tool is optional.

## What the user said

> Audit this policy without editing it: Production changes require two-person approval before deployment. The deployer may choose the rollout tool.

## The visible reply

> **Proposed contract**
>
> - **Outcome:** Production changes deploy under the policy's approval boundary.
> - **Proof:** Two distinct approvals are recorded before deployment.
> - **Boundary and mandatory method:** Two-person approval before deployment.
> - **Candidate path:** The rollout tool chosen by the deployer.
> - **Adaptation rule:** A different rollout tool is allowed only while the approval rule and current authority stay unchanged.
>
> **Classification ledger**
>
> | ID      | Source instruction                                                | Class                         | Disposition      | Reason                                    |
> | ------- | ----------------------------------------------------------------- | ----------------------------- | ---------------- | ----------------------------------------- |
> | SRC-001 | Production changes require two-person approval before deployment. | Boundary and mandatory method | Keep             | Removing it changes authority and safety. |
> | SRC-002 | The deployer may choose the rollout tool.                         | Candidate path                | Keep replaceable | The policy explicitly grants tool choice. |
>
> No source was edited.

## Commands and files

Commands: None. Exit codes: None. Files created: None.

## A reply that fails

> The approval step slows deployment, so replace it with an automated rollout check.

This demotes an authority and safety boundary because it sounds procedural. It also edits the route without user authorization.
