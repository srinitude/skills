# Mastra workflow boundary

Load this owner before implementing, running or changing a domain workflow. Return to [the skill body](../SKILL.md) for scope, audience, task accounting and acceptance. Use `mise run workflow -- --help` for the current standardization interface.

The shared [native workflow contract](generation-contract.md#tests-tasks-ci) owns the mandatory factory and output behavior through `mise run validate`. This reference describes the current factory implementation and its tested limits. Other public leaf routes retain their own effect guards.

## Runtime and operation

The package manifest and lock own SDK and compiler versions. Mise owns executable versions. Install through `mise run runtime-install`, with dependency lifecycle scripts disabled. Use `mise run typecheck-native` and `mise run test-native`. Prove portable packages with their own dependencies.

New packages receive the pinned runtime and their own public install, syntax, type-check and native-test path. The shared runtime copier preserves an existing compatible manifest, lock and compiler options. It rejects partial files, incompatible baseline declarations, another package manager, or a mismatched lock root before producing a standardized candidate. Reconcile those differences explicitly under the target's existing ownership; the copier does not merge dependency graphs or establish compatibility by itself. Run the target's actual clean installation, compiler and behavioral checks afterward. The copied engine probes establish their named mechanics and never substitute for the target's required domain workflow or human evidence.

The selected core is 1.64.0 with LibSQL 1.22.3. Source review uses [the release tag](https://github.com/mastra-ai/mastra/tree/%40mastra/core%401.64.0), revision `c19a93b0956f957581931786645d0597efec41eb). The observations below apply to the default engine and this adapter. Other engines, dynamic definitions and workers require their own review and executable proof.

The current route runs the code-defined `skill-factory-standardization-v1`:

1. `freeze-source` reads the actual source inventory, profile and factory identity.
2. `prepare-candidate` runs the existing standardization implementation, creates a separate unaccepted package and verifies that the original stayed unchanged.
3. `review-candidate` suspends with that candidate and a concrete review question. The process exits with code 3 and domain status `pending`.
4. `promote-candidate` revalidates frozen inputs and evidence, invokes the existing guarded replacement and compares the delivered and candidate inventories.

Start requires explicit source, profile, candidate, scope, audience, private state directory and run ID. Resume uses the same run and inputs plus the four external bindings in [evidence acceptance](evidence-acceptance.md). Keep bindings outside the candidate and untrusted request data. Success covers only the host-bound claims checked by the actual consumer.

The host supplies reviewed evidence. The continuation value is a control signal, not authenticated human approval or a quality judgment. Retain required human participation and its provenance. This route does not replace host identity, communication or permission enforcement.

Before claiming the pause, read-only preflight checks the candidate and evidence through `standardize-target --check-candidate --candidate <path>`. Invalid evidence leaves that pause available for valid recovery. Actual promotion repeats the guard inside its destination lock. An earlier check cannot authorize a later effect.

An explicit rejection is terminal and preserves the original. Reject duplicate starts, completed-run replay and changed saved inputs. A changed implementation, original, profile or candidate blocks continuation. Reconcile affected evidence and run compatibility explicitly; never silently repin a pause.

## Observed engine limits

These native tests execute the installed SDK:

| Behavior | Observation and required treatment |
| --- | --- |
| Branches | All true branches execute. False predicates and predicate errors may yield an empty successful result. Use a validated decision for exclusive routing and failing steps for required gates. |
| Callbacks | Finish/error callback exceptions can be caught and logged. They cannot own the only acceptance gate. |
| Output schema | An invalid final value can accompany engine success. Explicitly parse and validate domain results before downstream effects and completion. |
| Initial schemas | Tested invalid input, state and request-context values reject before the step. Retain actual runtime validation. |
| State update | An invalid update fails against the step schema before the later effect. |
| Committed suspension | A local LibSQL snapshot survived a killed process after suspension completed; a new process resumed it. |
| Concurrent resume | Two local processes contended for one suspension; only one produced the effect. Completed-run replay rejected. |
| Invalid resume and rejection | Neither caused the protected test effect. Synthetic responses are not human evidence. |

Atomic resume requires storage support for concurrent updates and persistence of running state. Unsupported storage or persistence policies can warn and continue without atomic claims. This LibSQL adapter uses a write transaction and an expected-status comparison. Do not infer the guarantee for other stores, engines, initial starts or arbitrary external effects.

These probes do not prove machine power-loss recovery, distributed exactly-once effects, crashes inside promotion, human authentication, full domain acceptance or every workflow feature. Test each promised guarantee at its actual consumer. Retries and time travel may repeat external work. Use a proved transaction, idempotency, deduplication or compensation when the contract requires it.

## Privacy and ownership

Keep only required local references and version bindings in workflow state. Secrets must stay out of input, state, prompts, results, snapshots, logs and portable artifacts. Resolve authorized fnox references at the actual consumer. A trace-field filter does not protect every secret value or snapshot.

The CLI requires a private state directory separate from both packages. It disables telemetry before SDK initialization and configures no exporter. Verify actual host export, retention and identity behavior for each added integration. Installation grants no transmission or signing permission.

Mise owns public prerequisites and executable versions. Mastra owns domain step order and persisted run state. Existing scripts own inventories, standardization and guarded replacement. The host owns human identity and runner authority. Keep one retry, schedule, cleanup and protected-effect owner. This CLI does not run a background scheduler or represent a sleeping process as durable scheduling.
