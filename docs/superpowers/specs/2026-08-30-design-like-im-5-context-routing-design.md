# Design Like I Am Five Context Routing Design

Date: 2026-08-30

Status: Approved design, awaiting written-spec review

Target: `skills/design-like-im-5/`

Load trigger: Use this design while changing the skill body's context routes, the context-route owner, generated action packets, route validation, contextual examples, or contextual evals.

## Outcome

Every operative instruction in `SKILL.md` must expose all support that can change how the model performs that instruction. A precise sentence is not enough when its intended meaning also depends on evidence, scenes, schemas, owner rules, counterexamples, record shapes, or proof.

The body must name that context at the point of use. It must say what to read, what to run, what to fill, what to compare, and what each file contributes. The model must not need to infer a missing route from a late index or memory.

## Fixed Boundaries

- `assets/execution-ownership.json` continues to decide where model judgment is allowed.
- Scripts may create packets, validate structure, and find missing routes. Scripts may not make design judgments.
- The model continues to perform every eye, brain, touch, bad design, bad output, and bad work review.
- Product states remain open and context-derived.
- Safety, access, understanding, agency, truth, cost, risk, work, and control vetoes remain fixed.
- `references/generation-contract.md` remains the sole full-file reading exception.
- The skill stays platform-neutral.
- Existing source lineage, file ownership, reading, and package checks stay active.

## Chosen Architecture

Use a hybrid of local context capsules and one machine-readable route owner.

Each context-bearing block in `SKILL.md` gets a stable route ID. The block keeps the operative instruction. A local context capsule follows it and names the exact support needed for that decision.

`assets/context-routing.json` becomes the canonical route owner. It maps each route ID to its body anchor, action, load condition, support paths, expected use, produced record, and forbidden substitutions.

`scripts/check_context_routing.py` validates agreement between the body, the route owner, and the public file tree. It checks structure only.

`scripts/run_pipeline.py` reads the route owner when it builds an action packet. Each packet includes a `context_bundle` with the paths and roles for that action.

## Context Capsule Contract

Each capsule must use this fixed shape:

| Field               | Required meaning                                                          |
| ------------------- | ------------------------------------------------------------------------- |
| `Route`             | One stable route ID.                                                      |
| `Read`              | References that define meaning, evidence, constraints, or conflict rules. |
| `Run`               | Scripts that build or validate the required structure.                    |
| `Use`               | Assets or schemas that hold inputs, outputs, owners, or fixed fields.     |
| `Compare`           | Examples that show a valid result, a failure, or a recovery.              |
| `Test`              | Evals or fixtures that expose likely reinterpretation or context loss.    |
| `Produce`           | The exact saved record or product result.                                 |
| `Do not substitute` | The nearest tempting but invalid replacement.                             |

A capsule may list more than one file under any field. It may omit a file class only when the route owner records `NOT_APPLICABLE`, a reason, and the file class that carries the equivalent context.

Major workflow actions must use all five support classes: references, scripts, assets, examples, and evals. Smaller rules may use a reduced set only through the recorded exception above.

The capsule must explain what each path contributes. A bare list of links does not satisfy the contract.

## Skill Body Placement

Context capsules appear beside the instructions they govern. They do not live only in a final support map.

The body will add capsules to:

1. The shared contract and owner boundary.
2. `help` and `run` command handling.
3. Intake and run startup.
4. Every required workflow action.
5. Model packet construction.
6. Product-state discovery.
7. Eye, brain, touch, and bad-practice review.
8. Part construction and source lineage.
9. Model record creation.
10. Veto, blocked, stale, and recovery behavior.
11. Reading, package, and source ownership.
12. Eval use and claim limits.
13. Final return and completion.

The current late owner maps remain short indexes. They cannot act as the sole route for an earlier instruction.

## Supporting Files

The implementation may add focused support where the current package lacks enough context.

### References

References own rich meaning that should not be copied into the body. They may add decision scenes, opposing readings, evidence standards, state interactions, sensory checks, and failure interpretations.

Each new reference must have one owner role, one load condition, and a backlink from the exact body capsule that needs it.

### Scripts

Scripts own stable IDs, route shape, packet generation, path checks, record fields, and coverage reports. They must not rank options, select states, grade pixels, or choose a design.

The context-route checker must report the route ID, missing field, expected path, and smallest repair.

### Assets

`assets/context-routing.json` owns the route graph. Supporting schemas may define a context bundle and its saved proof.

The route asset must state why each support path is used. It must also state the output that consumes that support.

### Examples

Examples must show context in use, not restate rules. At minimum, add one full action packet, one review packet, and one blocked packet caused by missing context.

Each example must point back to its route ID and exact source files.

### Evals

Evals must test omitted context, misleading partial context, owner drift, unsupported instructions, bare link lists, stale paths, and scripts making design choices.

Positive evals must prove that a model packet includes all required context classes and still leaves judgment with the model.

## Route Data Flow

The required flow is:

`SKILL.md instruction -> route ID -> context-routing.json -> generated context bundle -> model judgment -> saved record -> route validation`

The start command freezes the current route-owner hash in `run.json`. Packet generation reads only that frozen version.

The packet names each context path, role, load condition, and expected contribution. The model reads every applicable path before acting. It records the paths actually used and any missing context.

The record command rejects a result when a required context path was not acknowledged. It also rejects an unapproved substitution.

## Error Handling

Return `BLOCKED` for the affected action when:

- A body route ID has no route-owner record.
- A route-owner record has no body anchor.
- A required path is absent, stale, duplicated under two owners, or outside the skill.
- A major action lacks one of the five support classes without an approved `NOT_APPLICABLE` record.
- A capsule lists a path without stating its contribution.
- A generated packet omits required route context.
- A script attempts to own a model judgment.
- Two support files assign different meanings to the same route field.

The blocked record names the route ID, failed predicate, missing or conflicting paths, safe completed work, and smallest repair.

## Test-First Implementation

Before changing production skill files, add tests that fail because the current body has late grouped links but lacks local context coverage.

The first failing tests must prove:

1. Every context-bearing body block has one stable route ID.
2. Every route ID exists exactly once in `assets/context-routing.json`.
3. Every major action routes all five support classes.
4. Every routed path exists and has one declared contribution.
5. Every public support file is either routed from the body or marked package-only with a reason.
6. Generated action packets include their context bundle.
7. Model records acknowledge required context paths.
8. Scripts cannot supply a design verdict field.
9. Missing context produces the exact blocked shape.
10. The original owner, state, reading, lineage, and review tests still pass.

After the red state is recorded, add the smallest route asset, checker, packet fields, support files, and body capsules that make those tests pass.

## Validation

Run checks in this order:

1. Focused context-route tests.
2. Existing skill-body, pipeline, review, state, script, and CI-contract tests.
3. Every new or changed script with Python compilation and `--help`.
4. Skill-local `mise run ci`.
5. Agent Skills format validation.
6. Repository `mise run ci`.
7. A final scan for duplicate rules, orphan files, missing backlinks, placeholders, and generated cache files.

Completion requires current passing evidence from every applicable check. A route count or file count alone does not prove that the right context reaches the right judgment.

## Acceptance Criteria

- Every operative instruction has a local context route or a proved package-only classification.
- Every major action names references, scripts, assets, examples, and evals at the point of use.
- Each named file has an exact contribution and load condition.
- Each route has one body anchor and one canonical route record.
- The run packet carries the applicable context into model work.
- The model records what it used and what stayed unknown.
- Scripts enforce shape without making design decisions.
- All original behavior, ownership, review, state, reading, and lineage gates remain intact.
- Skill-local and repository checks pass on the final bytes.

## Rollback

Revert the context-routing commit as one unit. The pre-change `SKILL.md`, run packet schema, route-free pipeline, support-file manifest, and tests must return together. Do not leave body route IDs without their owner asset or keep route validation without generated context bundles.
