# Runtime worker orchestration

Read this file in Step 01 when the runtime supports independent workers. It owns the dependency graph, task packets, one-writer rule, handoffs, conflicts, and sequential fallback in `assets/subagent-task-contract.json`.

## Decide eligibility

Delegate when at least two ready tasks are independent, bounded, and have disjoint write ownership. Research shards, modality slices, comparison-corpus shards, experiment candidates, and read-only checks are common candidates. Do not split tightly coupled writing or let two workers write one file.

## Send the packet

Give each worker the exact objective, input paths and hashes, dependencies, source boundary, allowed and forbidden actions, tools, output schema, evidence, completion rule, budget, and status. Do not include a favored reviewer conclusion.

## Require evidence

Each result records claims, primary sources, located evidence, counterevidence, uncertainty, conflicts, output paths, output hashes, and `PASS` or `BLOCKED`. At least one independent task seeks counterevidence. A visual worker must first pass `assets/vision-probe-manifest.json`.

## Integrate

The lead removes duplicate work, preserves disagreements, rereads primary sources, checks hashes, resolves conflicts, and verifies current bytes. A worker verdict is not final proof.

## Fall back

If workers are unavailable, run the same roles sequentially with the same packet and result records. Return `E_DELEGATION` for skipped eligible delegation, `E_HANDOFF` for stale or missing hashes or schemas, and `E_CONFLICT` for unresolved disagreement.
