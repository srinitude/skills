---
name: outcome-bounded-work
description: "Use when instructions mix outcomes with recipes."
version: 1.0.0
author: Kiren Srinivasan
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [outcomes, constraints, evidence, adaptation]
    related_skills: [starting-point, reify, plan, goal-prompt, simplify-skill, meaning-preserving-rewrite]
    created_by: agent
    source: user
    created_with_hermes_commit: 41f2196c530b3359d9a7fc9c7bd41e9ddd7882c5
    compatibility_reviewed_with_hermes_commit: 41f2196c530b3359d9a7fc9c7bd41e9ddd7882c5
---

# Outcome-Bounded Work

## Outcome

Shape a live conversation or audit an instruction-bearing artifact so the required result, proof, and safety stay fixed while replaceable implementation choices remain open.

## Trigger and boundary

Use when a conversation, prompt, task, specification, plan, policy, or skill may mix true requirements with one possible way to satisfy them.

Do not use for a simple request with no material method choice. Do not weaken an exact method, explicit user requirement, or higher-priority rule. Use `simplify-skill` when the requested outcome is limited to simplifying a Hermes skill.

Load `starting-point` before the first move. It owns the private map of outcome, proof, constraints, starting path, and unknowns, plus the intervention gate for changing routes. This skill turns that map and the source instructions into an inspectable contract without taking over planning or execution.

## Contract fields

- **Outcome:** The observable end state.
- **Proof:** Evidence that decides PASS or BLOCKED.
- **Boundaries:** Scope, authority, resources, privacy, cost, and reversibility.
- **Forbidden outcomes:** States that must never be accepted.
- **Mandatory methods:** Methods fixed by authority, user intent, or the deliverable.
- **Candidate paths:** Replaceable ways to pursue the outcome.
- **Adaptation rule:** Evidence and approval needed to replace a candidate path.
- **Unknowns:** Facts or judgments that can still change the contract.

## Classification rules

Classify a source instruction by what would change if it were removed or replaced:

- It is an **outcome invariant** when the requested end state would change.
- It is an **evidence obligation** when the acceptance decision would lose required proof.
- It is a **boundary** when scope, authority, safety, privacy, cost, or reversibility would change.
- It is a **forbidden outcome** when it names a state that cannot be accepted.
- It is a **mandatory method** when the method is exact, exclusive, contractual, regulatory, reproducibility-related, pedagogical, explicitly required by the user, or itself the deliverable.
- It is a **candidate path** when another method could preserve every invariant, proof obligation, boundary, and forbidden outcome.
- It is **unresolved** when available evidence cannot distinguish a requirement from a recipe.

Do not demote an imperative instruction on guesswork. Use source wording, authority, context, and retrievable evidence. If the distinction still changes the work materially, ask one concise question.

## Conversation mode

1. Build the `starting-point` private outcome map.
2. Infer a provisional contract from the user's words without inventing requirements.
3. Put the smallest useful contract or worked example in front of the user early.
4. Label observed facts, reversible assumptions, and open items.
5. Keep at most one unanswered question live.
6. Update the same contract from the user's reaction instead of restarting discovery.
7. Hand off to the matching owner when the contract is accepted or the user asks to act.

## Artifact audit mode

1. Read the complete source before proposing changes.
2. Give every material instruction a stable source ID in source order.
3. Record its text or locator, authority, class, proposed disposition, and reason.
4. Preserve invariants, evidence obligations, boundaries, forbidden outcomes, and mandatory methods without loss of meaning or strength.
5. Keep a recipe mandatory unless evidence supports candidate-path status.
6. Return the classification ledger and a minimally changed proposed contract.
7. Do not mutate the source unless the user asks and the rightful editing owner is loaded.

## Adaptation gate

Replace a candidate path only when:

- The alternative preserves every accepted contract field.
- Evidence shows a material benefit or the current path is blocked.
- The alternative stays within current authority and side-effect limits.
- Any dropped, delayed, or reprioritized work has user approval.

If these conditions are not proved, keep the current path or mark the route unresolved. A better component is not proof of a better whole outcome.

## Output

Show the contract first. In audit mode, follow it with the classification ledger. Keep the difference between the accepted contract, proposed route, and execution evidence visible.

When the next action is text revision, load `meaning-preserving-rewrite`. Route skill-only simplification to `simplify-skill`, plan-only work to `plan`, standing-goal packaging to `goal-prompt`, and execution to the matching domain owner.

## Pitfalls

- Treating shorter instructions as automatically better.
- Preserving every step merely because it was written down.
- Demoting a safety or evidence rule because it sounds procedural.
- Replacing a user-selected method without evidence or approval.
- Inventing proof, constraints, or forbidden outcomes.
- Treating a contract or proposed rewrite as proof of execution.
- Editing an audited source before the user authorizes the change.

## Progressive disclosure

`PD-101`: `references/eval-cases.json` owns objective pressure cases and acceptance. Load it only before testing, reviewing, or changing this skill. This file owns runtime behavior and links to that evaluation owner.

## Verification

- `starting-point` shaped the private outcome map before classification.
- Every material source instruction has one source ID and a visible class.
- Preserved requirements retain their meaning, authority, and strength.
- Every relaxed recipe names the preserved contract and supporting evidence.
- Unknowns stay visible instead of being resolved by guesswork.
- The contract can admit a better safe route without allowing a worse result.
- External actions and source mutations remain behind their normal gates.
