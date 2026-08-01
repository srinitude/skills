---
name: logic-audit
description: 'Use when finding contradictions or reasoning gaps.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.1'
---

# Logic audit

## Outcome

Find and repair material contradictions and missing links across claims, requirements, evidence, actions, and proof. Preserve authority and intent. Don't invent premises, erase real uncertainty, or weaken an exact requirement.

## Trigger and boundary

Use when a user asks to find, explain, reconcile, or repair logical inconsistencies, omissions, unsupported claims, conflicting requirements, incomplete cases, or gaps between an objective and its proof.

Use it for prose, policies, plans, specifications, research, decisions, and mixed source sets. For code failures, hand root-cause execution to `systematic-debugging` after this skill identifies the logical contract. For a formal theorem, use a proof assistant or solver when available and limit claims to what it verifies. Routine fact lookup alone doesn't trigger this skill.

A full audit is bounded by the named source set and outcome. Never claim that an open world has no possible gap.

## Required composition

Before auditing:

1. Load `always-current-datetime` and acquire its clock anchor.
2. Load `starting-point` and build its private outcome map.
3. Load `outcome-bounded-work` and classify fixed requirements, proof duties, boundaries, forbidden outcomes, mandatory methods, candidate routes, and unknowns.
4. Keep the same `as_of` anchor throughout the audit. Reacquire only after a new direct user turn or local midnight.

These skills remain the owners of date handling, the outcome map, and invariant-versus-recipe classification. This skill owns consistency and gap analysis.

## Evidence setup

1. Name the exact source set, authority order, versions, dates, and excluded material.
2. Read each source in full when accessible. If truncation remains, mark the omitted range and don't pass the whole source.
3. Give every material statement a stable source ID in source order.
4. Classify each statement as definition, fact, assumption, requirement, boundary, exception, evidence, inference, action, conclusion, or unknown.
5. Normalize terms, entities, references, quantifiers, modal verbs, units, time windows, versions, and scope before calling two statements inconsistent.

## Web evidence contract

Use every available source-relevant web capability with a clear purpose. Do not fire low-level actions that cannot change the finding.

1. Inventory current search, source extraction, rendered browser, social-source, academic, and domain-source capabilities. Inspect an unfamiliar capability's contract before use.
2. Keep a capability ledger with one row per distinct source-relevant capability. Mark each `USED`, `NOT_APPLICABLE` with a reason, or `UNAVAILABLE` with the observed failure. Every available relevant capability must be used.
3. Use the search capability for discovery and query variation. Search official or first-party domains first when a claim has an authoritative owner.
4. Use the source extraction capability on candidate locations before treating them as evidence. A search snippet is a lead, not proof.
5. Use the rendered browser capability for JavaScript-only, authenticated, interactive, layout-dependent, console, or network evidence. Follow the host's established computer-use owner.
6. Use the social-source capability for claims about social posts, profiles, or threads. Use source-specific academic, market, map, repository, or platform capabilities when their corpus can change the finding.
7. Use a terminal HTTP client only as a recorded fallback after the normal web capability fails or lacks the needed response surface. Never turn a fallback into evidence without inspecting the returned source.
8. Record URL or source ID, publisher, publication or update date when available, access date, relevant claim IDs, and source limits.

Prefer primary sources. Use independent corroboration when error cost, dispute, or source incentives make one source insufficient. Keep current facts separate from historical evidence.

## Audit procedure

1. Build a dependency map from each conclusion or required outcome back to its premises, actions, owners, and evidence.
2. Run every applicable consistency class in `references/check-catalog.md` against each statement, pair, dependency chain, and authority layer.
3. Run every applicable gap class in that catalog against every required outcome, branch, interface, state transition, and proof claim.
4. Search for counterexamples and boundary cases before confirming a universal or exhaustive claim.
5. Verify externally checkable premises through the web evidence contract. Don't use source agreement as a substitute for valid inference.
6. Create one finding for each independent issue. Don't split one root issue into inflated duplicates.
7. Adjudicate each candidate as `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `NOT_AN_ISSUE`, or `BLOCKED`.
8. Rank impact as `critical`, `high`, `medium`, or `low` based on the accepted outcome, not on wording intensity.
9. Repair the smallest coherent unit. Prefer clarification, scope correction, explicit premise, missing case, evidence replacement, or requirement reconciliation over a broad rewrite.
10. Rebuild the dependency map and rerun the audit on the repaired artifact.

## Finding ledger

Each finding must include:

- ID and source locator or statement IDs.
- Type and affected outcome or proof duty.
- Candidate conflict or missing link.
- Normalized reading and competing readings.
- Status, impact, and confidence.
- Evidence used, including web capability rows.
- Minimal repair and any side effects.
- Resolution state and remaining uncertainty.

A difference is not a contradiction until both statements have the same relevant entity, time, scope, meaning, authority context, and modality. Missing evidence is not proof that a claim is false.

## Repair rules

- Higher-priority instructions and explicit user requirements win.
- Preserve the strongest jointly satisfiable contract. Don't silently choose one side of an authority conflict.
- When a method is mandatory, use it. Label any alternative as an optional comparison and never substitute it silently.
- State new assumptions as assumptions and request approval when they change material action.
- Keep unresolved alternatives visible when evidence cannot choose among them.
- Separate source correction from implementation. Use the rightful editor and normal side-effect gates.
- When rewriting, load `meaning-preserving-rewrite` and preserve every accepted requirement and proof duty.

## Proof threshold

Return `PASS` only when all of these are true:

- The full bounded source set was read or every inaccessible range is excluded from the claim.
- No unresolved critical or high-impact contradiction remains.
- Every required outcome has a complete chain of premises, owner, action or inference, and deciding evidence.
- Every material external premise has current source evidence or is marked unresolved.
- The web capability ledger accounts for every available source-relevant capability.
- The repaired artifact survives the same checks plus at least one counterexample or negative case.
- Component checks are not presented as whole-outcome proof.

Use `PARTIAL` when useful findings are proved but the threshold is incomplete. Use `BLOCKED` when missing authority, source access, or evidence prevents a safe repair.

## Output

Lead with the result and `as_of` date. Then provide the bounded source set, finding ledger, repaired artifact or exact patch, unresolved items, web capability ledger, and final `PASS`, `PARTIAL`, or `BLOCKED` decision. Cite source IDs and URLs close to the claims they support.

## Common failures

- Treating different dates, scopes, definitions, or modalities as contradictions.
- Converting ambiguity into a hidden assumption.
- Fact-checking premises while ignoring an invalid inference.
- Listing gaps without tracing their effect on the outcome.
- Using search snippets, source counts, or model agreement as proof.
- Calling a repaired paragraph proof that execution works.
- Claiming completeness outside the bounded source set.

## Package resources

Use `assets/finding-ledger-template.md` when the user requests a durable ledger. Copy it outside the installed skill before filling it. Read `examples/direct-contradiction.md`, `examples/temporal-non-contradiction.md`, or `examples/blocked-source-access.md` for complete visible runs. Package maintainers use `references/generation-contract.md`, `scripts/`, `scripts/tests/`, and `evals/`, then run `mise run ci`; ordinary audits do not load those paths.

## Progressive disclosure

`PD-101`: `references/check-catalog.md` owns the detailed inconsistency and gap taxonomy. Load it before a full audit or when a candidate doesn't fit the core classes. This file owns the trigger, procedure, and backlink.

`PD-102`: `references/eval-cases.json` owns objective pressure cases and acceptance. Load it before testing, reviewing, or changing this skill. This file owns runtime behavior and links back to that evaluation owner.

`PD-201`: `references/generation-contract.md` owns portable package structure, source lineage, examples, and evaluation proof. Package maintainers load it before changing those surfaces. This file owns the public procedure and backlink.
