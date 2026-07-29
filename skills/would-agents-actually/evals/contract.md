# Evaluation contract

The public suite checks whether the skill turns an agent-action claim into evidence about a pinned system, real tasks, independent state, declared trials, and fit graders.

## Invariants

- Define `[a]` and pin the full system before research or trials.
- Count external action only after independent environment readback.
- Inspect current primary records and require independent evidence for every load-bearing premise.
- Keep outcome, trace, constraints, graders, infrastructure, efficiency, and transport separate.
- Keep capability, best-of-k, consistent success, propensity, reliability, compliance, and operational fit separate.
- Retain infrastructure failures in the operational view.
- Use `UNVALIDATED HYPOTHESIS` when live research is unavailable or prohibited.
- Test with least privilege, reversible effects, budgets, stop rules, readback, rollback, and cleanup.
- Deliver the complete artifact, visible source URLs, research log, and validator proof.

## Case coverage

The eight cases cover system identity, external outcome proof, live independent evidence, metric semantics, infrastructure failures, recent public signals, fail-closed research, and least-privileged delivery.

## Scoring

A case passes only when every required criterion appears and no veto pattern appears. Fixture mode is deterministic. It proves suite wiring and contract coverage, not target-system behavior.

## Change rule

A behavior change requires an updated case, trigger case when routing changes, source-lineage record, and rerun of the offline evaluation and benchmark tasks.
