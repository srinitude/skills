# Generation contract

Every created, updated, standardized, imported or adapted skill follows this portable contract, including the factory. Read it through `mise run validate` before package changes. First read the full [SKILL.md body](../SKILL.md). It owns core behavior and the reusable ledger method. Apply all its first/later-load and review rules: capture all governing bytes, review every current rule and relationship, reuse only valid completed reviews, and block consumers with missing or stale coverage. Read initial resources in dependency order. Links and checks never replace reading, use or judgment.

## Layout

Use one directory named for the skill. Include SKILL.md, support, mise.toml and .github/workflows/ci.yml; check them through `mise run validate`. Keep references one support directory deep with public tasks and exact load triggers. Ship all authorized sources, ledger, records, checks, runtime and dependencies. Prove use without factory installation, private packets, host paths or shared state.

## Body, ledger and dependency ownership

Embed and apply [the body's complete ledger method](../SKILL.md#evidence) through `mise run ledger`. Reconcile every rule and relationship with the target domain and authorized sources. Each skill owns its source ledger and review history. Use that skill's source instructions and applicable portable factory rules. Do not use another task's ledger, quota, private records or approvals to meet this duty. Keep all record facets, source content, provenance, conditions, unknowns and proof. Prove independent loading, traversal, paging, guarded work, rejection and recovery in the real Mastra domain workflow. Missing, stale or ignored input blocks consumers. Capture is not judgment; absent relations do not prove independence.

Apply [the body's full dependency contract](../SKILL.md#evidence) through `mise run ledger` to every file, section, package, task, workflow, script and handoff. Preserve its distinct orders, dependency types, readiness, scope, audience, ownership, feedback and invalidation rules. All remain required in every output.

Through `mise run validate`, apply every remaining [body contract](../SKILL.md) in full, including research, human proof, modalities, tools, software, Mastra/companions, A/B/C, interfaces, consumer proof and efficiency. Outputs need independent domain inputs and proof. This grants no needless installs, services, secrets, hooks or data collection. Labels and schemas cannot prove outcomes.

## Frontmatter

Open with three dashes at byte 0; close the fence on its own line. Allow only these top-level fields: name, description, license, compatibility, metadata, allowed-tools.

- name: 1 to 64 characters matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`, equal to the directory name.
- description: quoted, 1 to 1024 characters, starts with "Use when", states applicability and user search keywords without summarizing the procedure.
- license: MIT unless the user directs otherwise.
- metadata: author `Kiren Srinivasan`, an independent quoted version, and one scope string (`user` or `project`) for every new or updated output. New skills start at `"0.1.0"`. Preserve other valid strings here. Scope sets intended availability, not location.

Parse frontmatter as YAML. Reject malformed syntax, duplicate keys, invalid field types, compatibility outside 1 to 500 characters, and non-string allowed-tools. Use the pinned cached environment behind `mise run validate`.

Before creating or changing a skill, load references/skill-scope-contract.md through `mise run validate`. It owns scope, legacy inspection, output acceptance, adaptation and placement. Copy both contracts to generated packages.

## Body and causal order

Bodies and their template stay below 200 lines and 100000 characters; other Markdown keeps its own limits. Reconcile all existing content and governing rules, conditions, exceptions, relationships and proof into one domain-complete body. Keep core behavior and initial context here. Use these seven H2 sections in order:

1. **Outcome:** name the observable result and its completion boundary.
2. **Motivation:** state why each material constraint protects the result and what bad outcome it prevents.
3. **Evidence:** identify live owners, proof, references, disconfirming evidence, and uncertainty.
4. **Mise task graph:** name the public task for each deterministic job, its dependencies, cache boundary, and failure branch.
5. **Steps:** put execution in dependency order with one action and one readback per step.
6. **Assets:** name each template, schema, fixture, policy, or other static input and the exact trigger for loading it.
7. **Evals:** define behavior, trigger, failure, recovery, timing, resource, and nonregression evidence.

Set a context budget without removing required full reads. Before and after every write, repeat write or removal, follow [the full read, review and change-history contract](../SKILL.md#evidence) through `mise run ledger`. All its scope, methods, fields, reuse conditions and gates bind outputs. Keep optional load triggers. Core changes update the body. A link does not replace these duties.

The command grammar starts with help and adds only needed domain commands. Scaffold diagnostics do not implement the result. Show the full plan before work. Use one default path per job. Number steps, each with one action and one observable result. Check each consequential step and name its failure branch. Stop and report missing required input; never guess. Log progress externally after each step. Back completion with fresh command output, never memory.

## Use-case specificity

Through `mise run use-case-policy`, map every [domain aspect and primitive](use-case-specificity.md) in full. Each material item needs its domain role, outcome, progress value, motivation, prevented failure and proof. Do not omit actors, states, authority, resources, quality, terms, exclusions or failure/recovery.

Load references/use-case-specificity.md and fill assets/use-case-contract.json through `mise run domain-research-policy` and `mise run use-case-policy`. Verify claim support, domain-name substitution, and domain-term removal. Generic or invented domain content fails.

Through `mise run primitive-lifecycle-policy`, map every aspect and primitive across the full lifecycle in assets/primitive-lifecycle.json, from discovery through retirement. Each phase needs a real domain task, objective progress, value, proof, applicability and prevented failure. Apply every lifecycle rule in [the use-case owner](use-case-specificity.md). Missing phases, generic profiles, missing owners and irrelevant mappings fail.

Each material program/model/human decision records outcome, motivation, fit, owner, inputs, effect, proof, falsifier and failure branch in assets/decision-records.json through `mise run decision-policy`. Structure proves a trace exists; direct review judges its truth.

## Simplicity and language

Preserve every accepted behavior with the smallest coherent structure. Keep one canonical rule owner, stable term, default route and material decision per branch. Remove demonstrated duplication, decorative sections, unnecessary indirection and equivalent options. Never hide essential domain complexity or weaken proof, safety, authority or behavior for size.

Load references/writing-rules.md through `mise run lint-writing`: result first, common words, active verbs, one idea per sentence/topic per paragraph, defined consistent terms and dependency-ordered steps. Lint proves only bounded checks. Same-meaning human review must confirm clarity, completeness and no unnecessary difficulty; model assessment cannot replace it.

## Deterministic and model-owned boundary

The body defines one effective owner per execution boundary: Mise for public entry/environment/outer prerequisites, Mastra for actual domain steps, scripts for mechanics, caller-controlled models for meaning/perception/creativity and humans for assigned evidence/decisions. Preserve scheduling, retries, cache, state, cleanup, outer guards and valid inner joins/feedback. Mechanical predicates do not prove meaning or sensory quality.

Copy the same tested, normalized whole-phrase domain-text matcher into generated packages through `mise run new`. Never fork this owner or treat matches as semantic or domain acceptance.

Apply [the body's capability and judgment contract](../SKILL.md#evidence) through `mise run agentic-request`. Keep every authorized modality, tool, skill, host runner and creative or human judgment needed for the outcome. Never disable, imitate or narrow them. Bind public calls, inputs, results, effects and recovery. Presence proves neither capability nor authority.

Implement [the body's full typed request contract](../SKILL.md#mise-task-graph) through `mise run agentic-request`. Keep every declared field, binding, transport, resource check, authority limit, error and judgment duty. Pass verified UTF-8 snapshots in `body.text`, `use_case.text`, `skills[].text` and `context[].text`. The caller owns runner and argument authority outside request data. Never infer relevance, actual use or adequacy from structural checks.

Decompose each job until its remaining correctness requires meaning, causal reasoning, novel creation, perception or human judgment. Record why code cannot supply that capability. Tested leaves own stable manifests, sources/queries, schemas, coverage, ordering, timestamps, digests, budgets, output envelopes, comparisons and rollback evidence.

Choose structures/algorithms from measured access, mutation, queries, order, interoperability and lifetime. Use streaming, lookup maps/sets, stable-key indexes, append-only history, digest invalidation, bounded independent concurrency and atomic accepted-state replacement where appropriate. Load references/resource-and-experiment-design.md through `mise run improvement-policy`; every trial measures or justifies non-use of every resource group in the improvement contract.

Do not cache mutable remote state, live judgment, an external side effect, or randomness without a captured seed. A cache declaration is an assertion that all inputs, tool versions, environment fields, and outputs are complete.

## Markdown layout

Keep every Markdown file at most 200 physical lines, including blanks and comments. Keep protected source bytes unchanged. Never use huge lines, dense cells or hidden prose to fit the cap.

Use `mise run markdown:accept` for every factory and output Markdown file, including templates and generated text. Follow [the body’s complete Markdown review loop](../SKILL.md#steps): inventory, mechanical checks, review request, whole-file review, section/block review, line review, review check, then acceptance. Mastra owns the steps and bound model handoffs. Keep every prerequisite, integrity and authority check, failure, evidence binding, invalidation and recovery rule. Early failures inform model review and still block acceptance.

Before choosing or changing a form, load [the full writing rules](writing-rules.md) through `mise run markdown:review-request`. Apply every feature-map, syntax, example, variant, non-use and renderer rule for CommonMark, GFM and target extensions. Apply the body's complete model-input and reply contract, including what, which, when, how, why and who for each feature. Preserve required human approval. Never infer support or force unneeded forms.

English prose must score at most grade 6.0 under the pinned extraction method and pass direct meaning review. Keep short-text limits, exact exclusions and failures. A score or reply shape does not prove clarity. Keep initial-use duties in SKILL.md. Prove these same gates on a real generated and updated skill; copied tasks and factory tests do not prove output behavior.

Every package-resource reference must name its owning `mise run <task>` in its prose block, fence or enclosing section. This covers all types and custom roots; register new roots through `mise run lint-writing`. Use descriptive owner links and public tasks, never private-script calls. Progressive disclosure cannot replace initial loading.

Through `mise run mise-primitives-policy`, classify every official Mise config, task, task-config and tool primitive in assets/mise-primitives.json. Use relevant primitives for domain progress, proof and useful creative composition. Justify each non-use for the target skill. Schema coverage binds one exact release; ceremony earns no acceptance.

## Examples

Through `mise run validate`, ship a full real run and likely failure in examples/ for each command. Include the guess removed, user words, reply, commands, observed outputs/exits and full created contents. Keep them aligned with SKILL.md. Update stale examples in the same commit as changed rules, paths, schemas or commands. Never invent output.

## Code

Through `mise run lint-code`, apply [all body code rules](../SKILL.md#assets): 200 physical lines per Markdown/code file, 30 per whole construct and file-wide block depth three. Count blanks and comments. Keep genuine configuration exempt. Ship real behavior, no work markers, mocks, stubs or placeholders. Prefer the standard library.

Every script supports --help with usage, exit codes, and an example. Scripts take input from flags or stdin, never from a prompt. Data goes to stdout, diagnostics to stderr. Exit 0 on success, 1 on a failed check, 2 on bad usage. Reruns are safe.

## Tests, tasks, CI

For a new skill, build test-first: mise.toml, CI and graph contract tests, failing behavior tests, implementation, docs, then evals. A whole-body rewrite must first reconcile source, ledger, infrastructure and body. Follow [the complete prerequisite and pending-validation branch](../examples/example-ledger-write.md#authorized-prerequisite-with-pending-body-validation) through `mise run ledger`. Keep SKILL.md-first design, outward implementation, actual authority, every guard and final acceptance. Reviews grant no authority. Run local and remote CI through `mise run ci`. Test public flags, exits, files and integration boundaries, not private details.

Every SKILL.md has one numbered dependency-ordered workflow in `## Steps`. Apply [the body's complete step contract](../SKILL.md#steps) through its named public Mise tasks. Before action, expose the full versioned plan with each step's reader/orchestrator, program, workflow, model, human and host owners, inputs, action, readback and failure/recovery. Use `Branch:`, `If:`, `For each:`, `Repeat:` and `Stop:` only for real choices, collections, retries and terminal states. Log progress and proof externally after each step. Return failures to the lowest owner and invalidate affected dependents. Replan explicitly for material changes. Do not add a competing workflow or decorative branch.

Use outer dependency edges, not nested tasks. Derive concurrency, caching and batching from actual domain/resource needs. Cache only deterministic tasks with complete declared inputs/outputs; exclude live, mutating, network, model-owned and human-judged work. Measure cold/warm aggregate paths and retain only faster behavior with no protected regression, preserving required order, evidence and capabilities.

Each task declares dependencies, empty only for a true root, and reaches CI or a public operation. Enforce [the full outer task-graph contract](../SKILL.md#mise-task-graph) through `mise run task-graph-policy`: exactly one reachable dependency path per public operation, with cycles, diamonds, disconnected or unknown tasks and redundant edges rejected. Mutating acceptance waits for all proof. Never nest `mise run` or cache live-web or model-judged output.

Keep Mise fixed during outcome work. Last, after outcome and acceptance, run `mise run mise-primitives-update` using [all catalog planning and reviews](../examples/example-ledger-write.md#plan-and-review-catalog-maintenance). Self-update without plugins; apply the reviewed catalog; reconcile dispositions and lineage. Rerun `mise run ci` and record version/catalog digest. Package ownership, network or compatibility failures stay `BLOCKED`; never override ownership.

Each task needs an assets/use-case-contract.json record for outcome, motivation, progress, proof and applicability. Run the selected path. Account for every other task with a source-supported request/domain reason and non-use proof. `mise run invocation-policy -- <receipt>` checks full accounting, including itself through execution. Bind fresh command output to each run claim. Accounting is not execution proof.

## Evals

Load evals/evals.json and evals/trigger-queries.json through `mise run evals`; registry authoring also loads its available references/eval-authoring.md through that route. Keep at least four realistic domain cases with prompts, expected output and verifiable assertions, plus positive/negative triggers and near misses. Registry outputs also emit manifest.json, cases.json, trigger-cases.json, contract.md, rubric.md, speed-budgets.json and source-lineage.json with real source sha256 hashes and `public_version` equal to the skill's version. Schema checks do not execute cases or establish outcome acceptance.

Only after required work passes, freeze a fresh baseline: evaluator, fixtures, applicable seed, environment, time, repetitions and resource measures. Change one named dimension at its smallest owner. Record keep/discard/crash outside the editable surface. Keep only material Pareto improvement with no protected regression. Otherwise restore accepted bytes and verify their digest. Worse, invalid and unknown results all require restoration.

## Updating, standardizing, and importing

Every operation that creates or changes a skill must satisfy references/skill-scope-contract.md through `mise run validate`; the factory uses its detailed variant workflow for adaptation.

Before change, freeze read-only owned-file inventory/digests, purpose, valid triggers, accepted behavior, task graph, examples and eval baseline, plus source outcome, proof, boundaries, forbidden outcomes and mandatory methods. Collisions, symlinks or unclassified host owners block writes. Preserve these unless the user changes them; standardization repairs shape/execution without replacing domain meaning.

Lineage and planning walk only owned regular files. Reject symlinks before reading or hashing them, and exclude runtime caches, dependency installations, generated bytecode, and tool state such as `.mise`, `node_modules`, `__pycache__`, and `.DS_Store`. These are execution products, not portable skill sources.

A source adapter is optional unless user-mandated. Classify current client markers separately from package formats; formats are not agents. Accept recognized subsets, but stop if no shape is recognized or any candidate remains unclassified. Translate reusable capabilities into SKILL.md, repository guidance into AGENTS.md, and hidden host ownership into `.agents/` through `mise run plan-standardize` only after path/semantic collision checks. Remove host-only fields, commands, paths, permissions and runtime assumptions from the destination. Preserve source bytes unless in-place migration is requested. Reject retained platform assumptions or lost source behavior.

## Reuse before building

Before writing anything new, use `mise run source-corpus` to find installed registry skills. Start with skills/starting-point/SKILL.md in the surrounding skills directory, from https://github.com/srinitude/skills. Defer to installed skills for jobs named by their descriptions.

## Prohibited content

Generated destinations do not name or require one agent product, harness, vendor, or model. Factory-only import evidence may identify a source host so the migration can remove its assumptions. Describe portable capabilities in the accepted destination: run in a terminal, read the file, search the tree. Nothing may assume host state beyond declared compatibility needs.
