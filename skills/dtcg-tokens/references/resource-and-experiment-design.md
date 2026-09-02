# Resource and experiment design

Read this file before selecting a data structure, file format, cache policy, task graph, benchmark, or optional skill-improvement trial. The goal is shorter elapsed time to a fully proved result, not a faster command that weakens correctness.

## Research basis

The [Agent Skills specification](https://agentskills.io/specification) assigns always-loaded instructions to SKILL.md and loads scripts, references, and assets only as needed. Its [authoring guidance](https://agentskills.io/skill-creation/best-practices) recommends concise steps, purpose-based guidance for flexible work, precise instructions for fragile work, and tested scripts for repeated mechanics. Its [evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) calls for fresh contexts, assertion evidence, timing review, human review, and reruns after changes.

The [AGENTS.md open format](https://agents.md/) gives repository guidance one predictable owner and supports nested files for local scope. The [Mise task configuration](https://mise.jdx.dev/tasks/task-configuration.html) supports dependency edges, parallel eligible tasks, source and output freshness, and content-based caching. Mise warns through its contract that cache correctness depends on declaring complete inputs.

[Blueprint First, Model Second](https://arxiv.org/abs/2508.02721) reports gains from separating coded workflow control from bounded language-model work. [DSPy](https://arxiv.org/abs/2310.03714) frames language-model systems as declarative graphs optimized against a validation metric. [OSWorld](https://arxiv.org/abs/2404.07972) uses real initial state plus execution-based final-state evaluation for computer tasks. These support deterministic orchestration and real outcome checks, while semantic and sensory acceptance remain judgment work.

Karpathy's [autoresearch](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117) supplies the experiment mechanics: establish the actual baseline, freeze the evaluator, keep the time budget fixed, record each candidate outside the editable surface, diagnose crashes within a bound, keep measured gains, and reset rejected work exactly. General skills add multi-dimensional protection because one scalar score can hide regressions.

The [TOML specification](https://toml.io/en/v1.0.0), [JSON RFC 8259](https://www.rfc-editor.org/rfc/rfc8259), [YAML 1.2.2 specification](https://yaml.org/spec/1.2.2/), [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core), [SQLite use guidance](https://www.sqlite.org/whentouse.html), [SQLite query planner](https://www.sqlite.org/queryplanner.html), [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html), [Git object model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects.html), and [Bazel remote caching](https://bazel.build/remote/caching) inform the storage, indexing, and invalidation rules below.

## Access pattern decides the structure

| Access pattern                         | Default structure            | Reason and rejection signal                                                                     |
| -------------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------- |
| Small bounded record with named fields | Object or map                | Direct lookup; reject when ordering or duplicate keys carry meaning.                            |
| Repeated membership tests              | Set                          | Near-constant membership; reject when counts or order matter.                                   |
| Stable key lookup over many records    | Index or keyed map           | Avoid repeated scans; reject when writes dominate and index maintenance costs more.             |
| One-pass large input                   | Iterator or streaming parser | Bounded memory; reject when the full set is required for sorting or cross-record decisions.     |
| Ordered append-only evidence           | JSONL or TSV ledger          | Cheap append and streaming replay; reject when transactional multi-record updates are required. |
| Query-heavy local state                | SQLite with measured indexes | Durable indexed queries; reject for high concurrent writes or network-shared ownership.         |
| Large analytical column scans          | Arrow or Parquet             | Column locality and batch operations; reject for frequent point mutation.                       |
| Reusable immutable artifacts           | Content-addressed map        | Exact invalidation and deduplication; reject when inputs or tool identity cannot be captured.   |

Batch independent reads and writes. Bound queues, worker counts, retry counts, and output sizes. Prefer atomic write then rename for one accepted owner. Keep one writer per mutable artifact. Profile before adding a specialized structure; complexity that does not reduce the measured bottleneck is a regression.

## Format follows ownership

| Format           | Use                                                                | Do not use as                                            |
| ---------------- | ------------------------------------------------------------------ | -------------------------------------------------------- |
| Markdown         | Always-loaded instructions, explanation, and progressive links     | Machine state or an exact query index.                   |
| TOML             | Human-authored tasks, tools, and project configuration             | Large event streams or deeply variable records.          |
| JSON             | Bounded machine contracts, snapshots, manifests, and interchange   | An ordered object model or append-heavy log.             |
| JSONL or TSV     | Append-only trials, events, and stream processing                  | A transactional graph with cross-row updates.            |
| YAML             | External systems that own YAML or concise nested human input       | Ambiguous unquoted scalars or logic that needs a script. |
| SQLite           | Large local mutable state with indexed queries and one main writer | Remote shared service or high writer concurrency.        |
| Arrow or Parquet | Large typed analytical batches and column scans                    | Human editing or frequent row mutation.                  |
| CBOR             | Compact binary exchange with an explicit deterministic encoding    | Default human-authored configuration.                    |

Schema validation proves shape. It does not prove truth, meaning, ordering intent, safe authority, or domain quality. Keep those checks at the model-owned or human-owned boundary.

## Resource disposition

Measure the resources that can decide a candidate, and state why the rest do not apply. Never collect a metric that cannot change retention.

| Resource        | Candidate measures                                                                 |
| --------------- | ---------------------------------------------------------------------------------- |
| Time            | Wall, critical path, queue, startup, cold and warm runs.                           |
| CPU             | User time, system time, utilization, instruction-heavy hot paths.                  |
| Memory          | Peak resident bytes, allocations, faults, swap, retained buffers.                  |
| Storage         | Read and write bytes, operations, temporary data, artifact size.                   |
| Network         | Requests, bytes, latency, rate limits, retries, remote cache traffic.              |
| Cache           | Hits, misses, invalidations, key computation, cold and warm deltas.                |
| Context         | Input and output tokens, resource loads, repeated instructions, prompt-cache hits. |
| Process         | Starts, tool calls, retries, timeouts, setup and teardown.                         |
| Concurrency     | Eligible and actual parallel work, contention, queue delay, one-writer waits.      |
| Accelerator     | Device time, memory, utilization, energy where available.                          |
| Cost            | Compute, API, storage, and transfer cost.                                          |
| Human attention | Review time, interruptions, approval rounds, correction rounds.                    |

## Mise graph and cache policy

Each deterministic job has one Mise task. Express true prerequisites with dependency edges, not repeated shell calls. Let independent read-only checks run together. Serialize shared writers and stateful external actions. Put fast failure checks early only when later work depends on them; otherwise parallel scheduling reduces the critical path.

Declare sources, outputs, arguments, environment, tool versions, platform, and dependency artifacts in a cache key. Use content digests for large stable inputs. Do not cache a task that reads time, mutable network state, ambient user state, uncaptured randomness, or a live design judgment. Treat a cache hit as reused computation, never fresh external proof.

Measure each script as its own workload before tuning the whole graph. A script can become faster while delaying the critical path through startup, serialization, extra artifacts, or cache churn. Retain an optimization only when the end-to-end graph remains correct and no protected resource dimension regresses.

## Experiment contract

1. Fresh baseline: run the current accepted owner now. Never rely on a remembered score.
2. Freeze the evaluator, inputs, seed where applicable, environment, time budget, repetitions, and resource dispositions before viewing the candidate.
3. Name one improvement dimension and its smallest editable owner. Large architectural trials are valid when small changes cannot affect the outcome.
4. Run baseline and candidate through the same owning Mise task. Randomize order or repeat interleaved runs when thermal, cache, or service noise can bias timing.
5. Record content digests, task graph digest, environment, raw measurements, summaries, keep or discard or crash status, and reasons outside the editable owner.
6. Keep only a material improvement with no protected regression. Use median plus spread for noisy timing, not one lucky run.
7. Restore the last accepted version after reject, crash, timeout, or unknown result, then verify its digest and rerun the narrow proof.
8. Finish with semantic or human review whenever the outcome includes meaning, taste, safety, usefulness, or sensory quality.

The optional loop changes one dimension per trial so evidence stays attributable. It stops at the skill's completion condition, a fixed budget, or no material gain. It never weakens safety, authority, domain proof, or the user's required result for speed.
