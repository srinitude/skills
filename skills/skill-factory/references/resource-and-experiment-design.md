# Resource and experiment design

Read this file before selecting a data structure, file format, cache policy, task graph, benchmark, or optional skill-improvement trial. Aim for less time to a fully proved skill result. Never speed up a command by weakening correctness.

## Research basis

The [Agent Skills specification](https://agentskills.io/specification) assigns always-loaded instructions to SKILL.md and loads scripts, references, and assets only as needed. Its [authoring guidance](https://agentskills.io/skill-creation/best-practices) recommends concise steps, purpose-based guidance for flexible work, precise instructions for fragile work, and tested scripts for repeated mechanics. Its [evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) calls for fresh contexts, assertion evidence, timing review, human review, and reruns after changes.

The [AGENTS.md open format](https://agents.md/) gives repository guidance one predictable owner and supports nested files for local scope. The [Mise task configuration](https://mise.jdx.dev/tasks/task-configuration.html) supports dependency edges, parallel eligible tasks, source and output freshness, and content-based caching. Mise warns through its contract that cache correctness depends on declaring complete inputs.

[Blueprint First, Model Second](https://arxiv.org/abs/2508.02721) reports gains from separating coded workflow control from bounded language-model work. [DSPy](https://arxiv.org/abs/2310.03714) frames language-model systems as declarative graphs optimized against a validation metric. [OSWorld](https://arxiv.org/abs/2404.07972) uses real initial state plus execution-based final-state evaluation for computer tasks. These support deterministic orchestration and real outcome checks, while semantic and sensory acceptance remain judgment work.

Karpathy's [autoresearch](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117) supplies the experiment mechanics: establish the actual baseline, freeze the evaluator, keep the time budget fixed, record each candidate outside the editable surface, diagnose crashes within a bound, keep measured gains, and reset rejected work exactly. General skills add multi-dimensional protection because one scalar score can hide regressions.

The [TOML specification](https://toml.io/en/v1.0.0), [JSON RFC 8259](https://www.rfc-editor.org/rfc/rfc8259), [YAML 1.2.2 specification](https://yaml.org/spec/1.2.2/), [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core), [SQLite use guidance](https://www.sqlite.org/whentouse.html), [SQLite query planner](https://www.sqlite.org/queryplanner.html), [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html), [Git object model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects.html), and [Bazel remote caching](https://bazel.build/remote/caching) inform the storage, indexing, and invalidation rules below.

## Access pattern decides the structure

| Access pattern | Default structure | Reason and rejection signal |
| --- | --- | --- |
| Small bounded record with named fields | Object or map | Direct lookup; reject when ordering or duplicate keys carry meaning. |
| Repeated membership tests | Set | Near-constant membership; reject when counts or order matter. |
| Stable key lookup over many records | Index or keyed map | Avoid repeated scans; reject when writes dominate and index maintenance costs more. |
| One-pass large input | Iterator or streaming parser | Bounded memory; reject when the full set is required for sorting or cross-record decisions. |
| Ordered append-only evidence | JSONL or TSV ledger | Cheap append and streaming replay; reject when transactional multi-record updates are required. |
| Query-heavy local state | SQLite with measured indexes | Durable indexed queries; reject for high concurrent writes or network-shared ownership. |
| Large analytical column scans | Arrow or Parquet | Column locality and batch operations; reject for frequent point mutation. |
| Reusable immutable artifacts | Content-addressed map | Exact invalidation and deduplication; reject when inputs or tool identity cannot be captured. |

Batch independent reads and writes. Bound queues, worker counts, retry counts, and output sizes. Prefer atomic write then rename for one accepted owner. Keep one writer per mutable artifact. Profile before adding a specialized structure; complexity that does not reduce the measured bottleneck is a regression.

## Format follows ownership

| Format | Use | Do not use as |
| --- | --- | --- |
| Markdown | Always-loaded instructions, explanation, and progressive links | Machine state or an exact query index. |
| TOML | Human-authored tasks, tools, and project configuration | Large event streams or deeply variable records. |
| JSON | Bounded machine contracts, snapshots, manifests, and interchange | An ordered object model or append-heavy log. |
| JSONL or TSV | Append-only trials, events, and stream processing | A transactional graph with cross-row updates. |
| YAML | External systems that own YAML or concise nested human input | Ambiguous unquoted scalars or logic that needs a script. |
| SQLite | Large local mutable state with indexed queries and one main writer | Remote shared service or high writer concurrency. |
| Arrow or Parquet | Large typed analytical batches and column scans | Human editing or frequent row mutation. |
| CBOR | Compact binary exchange with an explicit deterministic encoding | Default human-authored configuration. |

Schema validation proves shape. It does not prove truth, meaning, ordering intent, safe authority, or domain quality. Keep those checks at the model-owned or human-owned boundary.

## Resource disposition

Measure the resources that can decide a candidate, and state why the rest do not apply. Never collect a metric that cannot change retention.

| Resource | Candidate measures |
| --- | --- |
| Time | Wall, critical path, queue, startup, cold and warm runs. |
| CPU | User time, system time, utilization, instruction-heavy hot paths. |
| Memory | Peak resident bytes, allocations, faults, swap, retained buffers. |
| Storage | Read and write bytes, operations, temporary data, artifact size. |
| Network | Requests, bytes, latency, rate limits, retries, remote cache traffic. |
| Cache | Hits, misses, invalidations, key computation, cold and warm deltas. |
| Context | Input and output tokens, resource loads, repeated instructions, prompt-cache hits. |
| Process | Starts, tool calls, retries, timeouts, setup and teardown. |
| Concurrency | Eligible and actual parallel work, contention, queue delay, one-writer waits. |
| Accelerator | Device time, memory, utilization, energy where available. |
| Cost | Compute, API, storage, and transfer cost. |
| Human attention | Review time, interruptions, approval rounds, correction rounds. |

## Context budget

Set a context budget from the current domain operation, its risk, and the proof it needs. Keep the always-loaded skill body as the smallest domain-complete causal path. Load one support owner only when a current branch needs it, verify its digest or current receipt, and reuse it until its canonical owner changes or its prior load is uncertain. Prefer a stable index or manifest over repeated tree scans, and prefer a digest plus focused readback over reloading unchanged large content.

Token efficiency is non-lossy. A shorter prompt or fewer loads fail if they remove domain motivation, constraints, interfaces, counterevidence, failure and recovery branches, proof duties, model-owned tools, or the context needed for creative and thoughtful judgment. Measure input and output tokens, support loads, repeated instructions, prompt-cache hits, and correction rounds only when those measures can change a retention decision.

## Mise graph and cache policy

Each deterministic job has one Mise task. Express true prerequisites with dependency edges, not repeated shell calls. Let independent read-only checks run together under a measured job bound. Serialize shared writers and stateful external actions. Put fast failure checks early only when later work depends on them; otherwise parallel scheduling reduces the critical path. Use the target domain's dependency and resource profile to set concurrency, caching, and batching; a copied preset without measured value is ceremony.

Web and model capabilities may gather or judge evidence outside the task runner, but Mise owns their deterministic envelope. Validate research questions, source receipts, dimension coverage, timestamps, result shape, and saved disposition through the owning task. Never cache that live research gate or mistake a valid receipt for proof that its claim is true.

Send long prompts and extensible agentic requests through standard input or digest-bound files instead of command arguments, environment values, or generated shell. Bind the request to its completed use-case contract and exact promised outcome. Give the prompt, every referenced skill, and every primitive a target-domain role, outcome contribution, relevance reason, and expected proof. Bind each referenced skill or immutable input to a content digest. Keep the runner executable and argument array outside the request so input data cannot grant process authority. The task graph can then dispatch model-owned work without depending on one agent product. Term and shape checks are only early rejection gates; model or human judgment must still reject irrelevant items and weak results.

Declare sources, outputs, arguments, environment, tool versions, platform, and dependency artifacts in a cache key. Use content digests for large stable inputs. Do not cache a task that reads time, mutable network state, ambient user state, uncaptured randomness, or model-owned or human-owned judgment. Treat a cache hit as reused computation, never fresh external proof. Mise reduces mechanical delay and exposes reproducible faults so the model can spend its context and time on meaning, creativity, perception, and exceptions that code cannot decide.

Measure each script as its own workload before tuning the whole graph. A script can become faster while delaying the critical path through startup, serialization, extra artifacts, or cache churn. Retain an optimization only when the end-to-end graph remains correct and no protected resource dimension regresses.

## Improvement dimension catalog

At initial loading, read the entire [dimension catalog and evaluation basis](improvement-dimensions.md) through `mise run improvement-policy` before the experiment contract below. That owner retains every dimension, its measurement requirements and the numbered source notes. The body requires this full load for the factory and every generated or updated skill.

## Experiment contract

Fresh baseline and human review remain mandatory under their original conditions. The opportunity checkpoint is required; the trial remains conditional on an actual opportunity, authority and adequate proof budget. Use `mise run improvement-policy` for policy shape, the existing real domain workflow for the experiment, and `mise run ledger` for reviewed file effects. A passing policy checker has neither executed an experiment nor restored a version.

1. **Load and check prior adoption.** On each invocation read the current body, ledger, improvement contract, complete applicable dimension catalog and any unresolved prior trial. Before relying on changed behavior, run the frozen regression probe. At the final checkpoint compare the actual invocation outcome too. A previous pass does not exempt the next invocation.
2. **Select an actual opportunity.** Review failures, delays, repetitive work, unmet user needs and measured bottlenecks. Choose one hypothesis with a named intended dimension and predicted mechanism. Record no-op, blocked, or a bounded trial. Do not fabricate an experiment merely to populate a log or delay required repairs.
3. **Freeze the evidence boundary.** Retain the complete last accepted skill, owned path/mode inventory, dependencies, source/body identities and evaluator outside the candidate's editable surface. Capture already-existing unrelated modifications separately. Freeze task cases, relevant seeds, task-graph and effective evaluator digests, conditions, thresholds, minimum meaningful gain, repetition/stopping rules, time and resource budgets and applicability before seeing candidate results.
4. **Test the restoration prerequisite.** In disposable state prove that the retained baseline can actually be restored and its real consumer works. Cover changed files, newly created paths, retired paths, executable modes and independent edits. If restoration is not available, do not adopt the trial.
5. **Make one attributable change.** Use the smallest responsible owner and existing per-file ledger reads/reviews. A single hypothesis may require several dependent files. Preserve creative alternatives. Do not also tune the evaluator, change resource ceilings, drop difficult cases, or relax safeguards.
6. **Run matched comparisons.** Use the same public task and real domain workflow. Separate cold and warm conditions; interleave baseline and candidate when appropriate. Include failures, timeouts, repairs, reading, installation, maintenance and verification costs. Use median plus spread for noisy timing and retain raw results; one lucky run cannot establish a gain. Freeze or record unavoidable external changes and classify incomparable results as unresolved.
7. **Confirm all protected dimensions.** Run cheap decisive failures first, then the remaining required checks. Use held-out confirmation and authentic human or sensory evidence where required. Retain a candidate only when its intended improvement is material and every applicable protected outcome meets its unchanged requirement with adequate evidence. No weighted score can cancel a regression. Reject, crash, timeout or unknown results require restoring the last accepted version, verifying its digest and rerunning the narrow proof before dependent use.
8. **Adopt provisionally and verify use.** Record `keep` with a separate pending next-invocation confirmation; keep/discard/crash remain trial outcomes, not acceptance of the whole skill. Bind the candidate to its baseline, exact change set, evaluator, observations and actual consumers. After the next invocation confirms the protected dimensions, record confirmation. If it reveals a regression attributable to the change, restore immediately at the affected boundary. Unknown causality does not justify continued reliance on an unproved candidate.
9. **Finish maintenance and delivery.** Run required final maintenance and all invalidated checks under the actual resulting runtime, preserving the source-defined final task order. Publish only within existing authorization. Keep later invocations capable of reopening a confirmed trial when new evidence contradicts it.


## Restoration and process improvement

The rollback target is the complete pre-trial accepted skill snapshot, not an arbitrary prior commit or only its SKILL.md. Preserve sources, other skills, independent variants, working-tree changes, external state and shared history. A rollback is itself a reviewed skill update and requires the same full reads, body integration checks and per-file changelog.

Stop the affected consumer and any cooperating writer. Compare baseline, candidate and current bytes and modes. If current equals the candidate, restore the owned change set in dependency-safe order with the existing reviewed writer and promotion mechanism. If current contains later edits, compute the three-way difference and retain independent changes; an overlapping conflict requires resolution before replacement. Verify the restored subject and its dependent outputs. Do not label a conflict-preserving merge byte-identical to the old snapshot.

For an already committed isolated trial, Git revert can record a new inverse commit while preserving history. Git restore instead replaces selected working-tree/index contents and can remove tracked paths absent from its source. Neither is a substitute for scope review, current-byte checks, source protection or runtime validation. Never run a repository-wide hard reset, blind folder copy, clean command, force push, or bulk deletion as this process. Sources 15 and 16 are in [the catalog source notes](improvement-dimensions.md#source-notes), loaded through `mise run improvement-policy`.

Preserve the rejected candidate and measurements outside the editable skill. Restore newly created and retired paths only through an owner that supports their reviewed lifecycle; do not invent deletion support in a replacement-only writer. If a supported safe removal/promotion route is unavailable, block that restoration effect and retain both states for recovery. A crash during multiple writes does not magically become an atomic transaction: use the existing package backup/promotion guarantees and report their actual isolation limits.

Restore compatible dependencies and configuration when they were part of the trial. Expired credentials, live services or irreversible external effects cannot be restored by Git; use their authorized recovery owner. Invalidate affected plans, caches, evidence and approvals. Run the failure reproduction, restored consumer, affected regressions and required integrated checks. Record the observed state and exact restoration receipt, then resume eligible work. A published Git revert remains a new commit. Publish it only within the caller's authority. Merge only with the required approval.


Apply the same method to the factory's experiment selection, prompts, scripts, task graph, sampling and review workflow. Evaluate a process change on held-out skill creation/update workloads, including deterministic, creative and exploratory tasks and both scope/audience types. Measure accepted improvements per total wall time, tokens, money and human effort, plus false keeps, false discards, recurrence and rollback success. Count failed experiments and all added review work.

Keep the evaluator for that comparison outside the process candidate. Changing the process and its success test together prevents attribution. A proposed better evaluator is a separate experiment, calibrated on known good/bad cases and independent judgments; do not promote it using only its own higher score. This separates useful self-improvement from self-awarded success.

Use staged evaluation to save resources: reject a broken candidate with a cheap decisive check before an expensive run, but never promote it before every mandatory check. Reuse unchanged valid evidence only where the contract permits, and preserve required fresh reads. Prioritize hypotheses from observed bottlenecks; investigate near misses only when new evidence supplies a distinct mechanism. Stop repeated failed approaches at the existing bound and change course.

The main counterargument is overhead: protecting more dimensions can make a small skill slower to improve. The response is explicit applicability, shared evidence, narrow capable tests and one existing record owner, not removing protected outcomes. Another limit is that strict improvement in one dimension with no loss anywhere may not exist. In that case keep the baseline and report the tradeoff. This process creates opportunities for improvement; it cannot guarantee an improvement on every invocation.
