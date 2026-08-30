# Research protocol

Read this file before discovery, schema inspection, source research, or runtime probing. Research answers one question: what can this exact callable do now, what evidence can it return, and what safety facts govern its use?

## Source order

1. Inspect the live callable entry in the actual target environment.
2. Inspect current owner-controlled source, schema, types, handlers, tests, reference material, and release history applicable to the origin.
3. Inspect only the protocol or format that governs this origin.
4. Inspect reproduced failures or owner-controlled issue records that affect lifecycle decisions.
5. Use secondary material only to find primary evidence or challenge a conclusion.

## Source ledger

For each source record URL or local locator, owner, retrieval date, version or commit, exact supported claim, evidence kind, status, and any discrepancy. Mark a claim normative, runtime evidence, comparative evidence, or inference. An inference names its evidence and a test that could disprove it.

## Runtime probes

Probe only when the call is authorized, confined, reversible, free or approved, and decisive. Prefer a read-only call, dry run, isolated temporary state, or recorded contract test. For a state change, capture the exact input and returned handle, then use an independent readback. Do not inspect a destructive, paid, publishing, messaging, purchasing, deployment, credential, or account-changing operation merely to learn its contract.

## Capability-use matrix

Record capability class, concrete tool or fallback, acceptance criterion, distinct evidence, planned input, side effects, destination, artifact, and status. Use `used`, `available but not relevant`, `unavailable`, or `blocked`. A class is irrelevant when it duplicates stronger evidence, cannot affect acceptance, adds unauthorized effects, discloses data, or changes presentation without meaning.

## Enforcement evidence

Source-visible hooks, callbacks, guardrails, middleware, policy layers, progress, cancellation, tasks, and approval controls are origin-specific comparative concepts. They do not prove that another host or tool supplies the same mechanism. Keep a requested stronger control as an explicit gap until the actual environment proves it.
