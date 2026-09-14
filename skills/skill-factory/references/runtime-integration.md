# Runtime integration contract

Before choosing, setting up or changing runtimes, tool interfaces, companions or domain workflows, read this whole contract via `mise run agentic-request` resource inputs. [SKILL.md](../SKILL.md#mise-task-graph) keeps core owners, gates and outcomes. This file owns mandatory methods and release checks where applicable.

## Tool discovery and selection

- Check readiness, public interfaces, domain fit and explicit choices before choosing the default, real alternatives and failure route.
- Honor known preferences. Inferred choices stay provisional and grant no authority.
- Integration binds clients, accounts, projects and callable tools, and resolves preferences.
- Names, installs and model claims cannot prove availability.
- Use available authorized vision, audio, web research, browser/computer, tools and multimodal creation directly when required. Physical smell, taste, touch and measurements need real authorized people or instruments.
- Use supported protocols to find relevant tasks, managed tools, project commands, skills, host tools, apps, connectors, MCP servers, CLIs, browsers and services. Handle pages and partial or changed inventories.
- Disclose inventory limits.
- Check existence, supported operations, readiness and authority separately. Check exact identity, schema/version, effects, target and context.
- Descriptions and effect labels grant no authority.
- Use authorized preferences and relevant context. Do not collect unrelated history, credentials or account data.
- Installation alone weakly indicates preference.
- After mandatory choices, filter capability, privacy, permission, compatibility, fidelity and proof, then prefer the supported user preference and fastest adequate route.
- Record provisional choices and sources without invented confidence scores. Make correction easy.
- Retain valid bindings using a stable tie rule, and recheck changed versions, readiness, configuration, permission, targets and preferences before dependent actions.
- Inference grants no install, account-connection, extra-access, saved-profile or transmission authority.
- Use a verified allowed alternative only if fixed requirements survive; validate its actual result.

## Language and interface method

- For every tool, package, language, snippet and integration used: define its domain result and proof; inspect published artifacts, installed types/schema, APIs, config and transitive behavior; compose the smallest supported real interfaces; test effects, failures, recovery and joins; propagate independent support.
- For each material operation, distinguish what the dependency supplies, what this skill must implement or configure, and what remains model- or human-owned.
- Use existing use-case, primitive, decision, integration and lineage records, not a new catalog or a record for each trivial call.
- Record input/output shapes, units, encoding, nulls, defaults, check timing, errors, state lifetime, concurrency, retries, cancellation and cleanup.
- Use current first-party sources and runtime probes. Keep public contracts, examples, internals and unreleased changes distinct.
- For every language or dialect, including embedded and declarative code, find its actual runtime/compiler, platform and native package constraints.
- Match official language/library and release guidance, plus maintained first-party formatters, analyzers and tests, to the target version. Separate supported use from proposals, previews, deprecated advice and popularity.
- Apply the full ladder after tracing the outcome and every caller; preserve error, encoding, numeric, concurrency, lifetime, security and platform semantics.
- Manage executable versions through Mise and native package locks through public tasks; a missing supported route blocks dependent acceptance, not a hidden system fallback.
- Encode objective checks in native tools or tested scripts, pass chosen language rules as resources and retain explicit semantic reviewers.
- Keep sources, versions, applicability, choices and proof in existing lineage. Refresh guidance after tool, language, target, dependency or rule changes. Reuse unchanged knowledge; test declared toolchains; propagate accepted rules/checkers.
- For unfamiliar languages, avoid JavaScript/Python assumptions, unused tools and repeated broad research.
- Distinguish tag, package, CLI, binding and service identities. Trace consumed artifacts. If source is missing, use official contracts and authorized probes; state limits.

## Mise release and feature review

- Cache only deterministic work with complete input, tool/version, environment and output bindings, including captured randomness when relevant.
- Separate task freshness from artifact caching and bypass both for mandated fresh evidence.
- Never present cached live judgment, mutable remote state or side effects as fresh proof.
- Preserve selected-release locking, isolation, MCP and skill-sync limits; locks are not arbitrary transactions, MCP declarations are not approval and symlinks are not independent variants.
- Classify every schema-derived [Mise](https://mise.jdx.dev/) primitive through `mise run mise-primitives-policy` and [its catalog/dispositions](../assets/mise-primitives.json), proving useful domain use or source-supported non-use, including a useful creative composition.
- At implementation start, verify the latest stable Mise release, excluding drafts/prereleases, then freeze its version and commit and reconcile exact runtime/CI pins and min_version.
- The source research baseline is [v2026.9.3](https://github.com/jdx/mise/releases/tag/v2026.9.3), [commit 5e6a800da6f878ec56b7ffa70a76a6c595c632b5](https://github.com/jdx/mise/commit/5e6a800da6f878ec56b7ffa70a76a6c595c632b5).
- Check every selected command, flag, setting, default, platform and dependency claim against that release documentation, schema, source/tests and installed help; resolve drift without assuming unreleased behavior.
- Review every official command and feature. Record each outcome, use/trigger/exclusion, owner, source and proof.
- Cover toolchains/locks/platforms, configuration/secrets, task interfaces, scheduling/lifecycle, includes/templates/workspaces/invalidation, caches, diagnostics/documentation, CI/shell/IDE/bootstrap, packages/dotfiles/repos/services/remotes, OCI/MCP/plugins and tool-provided skills.
- For each chosen experimental feature, check need, authority, activation, tests, limits and supported fallback. Keep native package managers and locks.
- Inspect run references separately because `mise tasks deps` excludes them.
- Fresh checks can use `mise run --force --task-cache off TASK`; cached logs remain historical, and checksums/cache audits prove neither determinism nor producer trust.
- Tool locks omit some package/system dependencies; strict locking is not offline mode and has backend limits.
- Trust, safe mode, child sandboxing and host approval differ; even configuration evaluation and remote discovery may have effects.
- Redaction is neither encryption nor a complete secret filter.
- Verify host limits, including Windows filesystem/network restrictions.
- In the source baseline, experimental MCP run_task uses MISE_YES=1 without interactive stdin and install_tool is unimplemented; host controls must retain approvals.
- Skill sync links installed tools, does not create independent variants and does not enforce metadata.scope.

## Companion selection and authority

- Review current official features, interfaces and sources for all five companions. Prove compatible versions and actual native boundaries.
- Use each only for its source-defined role.
- Each companion follows Mise’s latest-stable release, frozen commit, full feature-map and release-specific proof rules.
- Freeze a compatible set managed through Mise, retaining native package locks, and rerun affected integration checks after changes.
- Record each output’s roles and justified non-use. No secrets means no lookup; no persistent process means no daemon.
- Bound total concurrency. Translate statuses without hiding errors. Run shared checks once per required input state.
- Preserve explicit authority for hooks, vendor MCP, machine setup, provisioning, signing/publication and skill sync.

## Usage

- One native argument owner drives parsing, help, examples, completion and interface documentation.
- Prove export, spec lint/diff and downstream forwarding of spaces, Unicode, empty/repeated values, quoting, shell characters and environment.
- Reject stale projections before effects.
- Inspect exporter loss reports, warnings and metadata changes affecting authority or effects.
- Planned exporters and preview frameworks are not stable support; no universal language framework is assumed.
- Test variadic values, the end-of-options marker, shell differences and environment collisions.
- Spec diff does not prove implementation equivalence; domain validation stays with its code owner.

## Packslip

- Use supported manifests, signatures, artifact/platform/resource identity and consumer policy where distribution requires them.
- Verify signer/key policy, bytes, project/version, expiry, withdrawal/rollback and separately claimed provenance.
- Native backends may supply installation; decoding is not verification.
- Never invent artifacts or signing authority.
- Prefer the native Mise backend when the release publishes supported manifests; it does not require the Packslip CLI.
- Add that CLI only for actual creation or independent verification.
- Enforce trusted issuer, host requirements, release age and sequence as well as consumer policy; CLI verification alone is insufficient.
- Bind Usage specs and vendor skill resources to the release and review downloaded instructions before activation.
- Preserve scope, version, lineage, license and bytes; an instruction-only skill needs no invented binary.
- Signatures prove origin and bytes, not quality or authority.

## fnox

- Prefer the maintained scoped-subprocess CLI through [Mise](https://mise.jdx.dev/).
- Bind provider/profile, identity, required names, scope, lease freshness and consumer readiness.
- Reject missing, expired or overbroad credentials despite skips or ambient alternatives.
- Keep secrets, keys, caches, proxy and lease material outside traces/packages.
- Keep sync, activation, authentication and isolation limits distinct.
- Resolve non-sensitive references at the authorized consumer; keep values out of prompts, arguments, lineage, eval evidence and ordinary caches.
- Use fnox exec for scoped subprocesses; the incomplete experimental mise-env-fnox plugin is not the default.
- Missing required values must fail despite the native warn default; test missing leases, provider failure, expiry and cleanup.
- Choose file delivery, leases or proxy only when suited to the consumer.
- The proxy requires cooperating clients and supports bounded HTTPS/header behavior; it is not an OS sandbox.

## Pitchfork

- Use only for genuinely persistent required processes.
- Bind project/worktree, executable, directory, ports, dependencies, environment, lifetime and platform.
- All required readiness predicates must pass even if native probes accept first success.
- Reuse matching healthy instances; bound retries and terminate/clean up only owned children.
- Activation needs purpose and authority.
- Keep finite transformations in Mise.
- Resolve the pinned environment for both daemon and probes because the supervisor may outlive its launch shell.
- A PID, open port or delay cannot prove app readiness.
- Specify health checks and interruption recovery; verify owned child termination and preservation of existing services.
- Boot startup, schedules, shell auto-start, proxies, dashboards and exposed listeners each need an actual use case and authority.

## hk

- Reuse actual checks with exact roots and selection, pinned [Pkl](https://pkl-lang.org/main/current/) imports and the built-in evaluator unless a needed feature requires another declared one.
- Prove read-only checks with an empty diff; authorized fixes preserve staged, unstaged, untracked and unrelated work.
- Test per-directory fallback/cache behavior.
- Incremental checks, tool installation and locks have separate limits.
- Force the intended mode after reading effective configuration: hk check may fix or stage files.
- Check labels and safe-mode effect labels are not isolation.
- Declare write sets and dependencies. File locks cannot cover undeclared writes or other processes.
- Test partial-stage restoration and conflicts.
- Per-directory Mise resolution can warn and fall back; inspect that behavior and configuration-cache invalidation.
- Hooks and host snippets remain explicit integration actions.

## Mastra capability and package selection

- [Mastra](https://mastra.ai/docs/workflows/overview) must execute the actual skill capability with a managed runtime, native lock and minimal necessary [TypeScript](https://www.typescriptlang.org/docs/) adapter, preserving existing script languages and caller-controlled runners.
- Map supported input/output/state/resume schemas, steps, sequence/parallel/branch composition, loops, suspend/resume, storage/snapshots/replay, observation, dynamic definitions, scheduling and engines.
- Optional non-use never waives the domain workflow.
- A one-node proxy is insufficient. A caller runner needs no extra provider/Agent setup.
- Review every public workflow feature/API for the chosen stable compatible packages: applicability, operation, exact version/engine needs, source, actual behavior and proof.
- Use public exports, docs, source/tests and probes to distinguish stable, beta, experimental, deprecated and engine-specific features. Install packages or a CLI only for needed roles.
- The source baseline [core 1.64.0](https://github.com/mastra-ai/mastra/releases/tag/@mastra/core@1.64.0) requires [Node](https://nodejs.org/en/about/previous-releases) >=22.13.0; verify the consumed package and select an exact supported runtime, peers, schemas, storage, engine, platform, license and upgrade path.
- Include registration/commit, identities, reuse/cloning/inspection/nesting, request context, mapping, foreach/concurrency, sleep/until, agent/tool/processor steps, structured results/scorers, starts/streaming/events/cancellation/retries/bail/callbacks/state, persistence/pruning/suspension/restart/time travel, dynamic serialization/registries, scheduling/history/reconciliation/workers/deployment and observation/filtering/retention.
- Require triggers for optional features. Availability cannot add unrelated voice, retrieval, memory, cloud or multi-agent systems.
- Explain each workflow entry, purpose, inputs, outputs, context, step owners, completion gates and failure states.
- Keep full multimodal/tool context through the caller runner. Resolve any loss before acceptance.
- Extend language discovery, size/type/build checks, tests, templates and copied checkers for added languages.

### Code, model and human work

Name each primitive’s work owner and proof. Code owns code work. Models own model work. Humans own human work. Keep these roles in created and updated skills.

| Native feature | Use and ownership check |
| --- | --- |
| Steps, schemas and `.then()` | Code checks data and runs ordered work. Valid data can still hold a bad judgment. |
| Mapping, state, context | Code passes exact inputs/results. Keep all needed model context, images and tools. |
| `.parallel()` and `.foreach()` | Bound independent work. Join every required result with its owner and evidence. |
| `.branch()` | Route a rule or bound model or human choice. Reject no match; use disjoint choices for one route. Test the engine: multiple true routes may run. |
| `.dowhile()` and `.dountil()` | Bound review and repair. Both run once before testing; check authority first. Missing proof never passes at the limit. |
| `suspend()` and resume schemas | Return the request before effects. The named model or human responds; resume the exact run and step with fresh checked input. |
| Human input and `bail()` | Verify the person, viewed inputs, current scope and choice. Keep denial, revision and missing input distinct. Denial may return workflow `success`; never accept it. |
| Nested runs, labels, `forEachIndex` | Bind replies to exact pending items within their approval scope. |
| Sleep, schedules, async starts | Use an authorized, tested host. Time and queued work cannot supply human input. |
| Snapshots, restart, time travel | Keep state/proof. Check identity, authority and safe effects before replay; replay cannot undo effects. |
| Retries, cancel, callbacks, streams | Bound retries; stop owned work. Gate in steps. Logged errors or stream closure cannot decide acceptance. |
| Dynamic definitions, registries | The model designs needed flows. Code checks schemas, references and faithful storage. Review beta limits. |
| Agent, tool, processor and scorer adapters | Check fit; keep adapters optional and the caller’s model and tools. Use skill-owned evals, never Mastra scorers or required Mastra Agents. |

Check choices against [human input](https://mastra.ai/docs/workflows/human-in-the-loop) and the installed API. Core 1.65.0 removed `waitForEvent`; use suspend/resume. Replies and actor labels alone cannot prove human identity or approval. Record host limits; keep missing human work pending.

## Mastra state and failure behavior

- Test the engine: all-true branches, explicit exclusive choices, bad input/output/resume, changed definitions and missing steps.
- False predicates and swallowed completion-callback errors cannot hide failed requirements.
- Suspend/bail must return before protected effects.
- Store or replay work under supported policy with fresh operation, input, identity and real approval bindings. Storage proves neither crash safety nor exactly-once effects.
- Dynamic beta definitions require faithful serialization and trusted registry resolution.
- Schedules need the actual host, storage, transport and endpoint controls.
- Optional engines are not interchangeable or all production-ready.
- Keep secrets outside persistable state; verify actual filtering, exporter, retention, trace and snapshot limits.
- Record the tested engine, configuration, semantics, unsupported cases and recovery.
- Queued runs, timers, stored requests, transport receipts and process-local sleep prove neither durable work nor human input.
- Test multiple/no-match/error branches and keep mandatory failures in failing steps.
- Distinguish success, failure, tripwire, suspended, waiting, pending, paused, canceled, skipped and bailed states.
- Validate state/request context, transformations and configuration too; invalid foreach concurrency may fall back to one.
- Prefer separate parallel outputs and explicit merges to unproved shared state.
- Bound loops, retries, total concurrency, time, tokens and effects.
- Test storage/persistence guarantees because unsupported atomic resume can warn and proceed.
- Replay does not undo effects: test permitted idempotency, deduplication, transactions or compensation and recheck current credentials, authority, target and resource/source identity.
- Bind workflow/run/step and skill/graph/schema/tool/source/resource versions; explicitly migrate or block incompatible saved runs without changing suspended meaning or variant customizations.
- Test dynamic round trips, lost options, missing registries/dependencies, collisions and graph drift; prefer code-defined workflows when faithful serialization is unavailable.
- Schedules may choose the evented engine and need additional storage; worker separation is beta in the source baseline.
- Inngest and Temporal have different requirements, and Temporal is not production-ready at that baseline.
- Trace filtering matches fields, may miss values/snapshots, and custom field lists can replace defaults; verify actual protection and retention.
- An exporter grants no transmission authority.
