# Generation contract

Every generated skill follows this recursive contract, including a skill that builds skills. The factory is not exempt.

## Layout

A skill is one directory whose name equals the frontmatter name. It holds SKILL.md, support directories, mise.toml, and .github/workflows/ci.yml. The body routes support files through `mise run validate`, keeps implementation private behind Mise tasks, and keeps referenced paths at most one support directory deep.

## Frontmatter

The file opens with three dashes at byte 0 and the fence closes on its own line. Allowed top-level fields, and no others: name, description, license, compatibility, metadata, allowed-tools.

- name: 1 to 64 characters matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`, equal to the directory name.
- description: quoted, 1 to 1024 characters, says what the skill does and when it applies, contains "Use when", and carries the keywords a user would type.
- license: MIT unless the user directs otherwise.
- metadata: author, a quoted version string, and exactly one scope string, `user` or `project`, for every new or updated output. The scope contract owns intended-availability semantics and preserves other metadata within this extension point.

Parse frontmatter as YAML. Reject malformed syntax, duplicate keys, invalid field types, compatibility outside 1 to 500 characters, and non-string allowed-tools. Use the pinned cached environment behind `mise run validate`.

Load references/skill-scope-contract.md through `mise run validate` before creating or changing a skill. It owns scope resolution, legacy inspection versus output acceptance, adaptation, and placement boundaries. Copy it with this generation contract so generated packages retain those requirements.

## Body and causal order

Keep the body under 200 lines and the file under 100000 characters. The always-loaded body carries the smallest causal chain that lets an executor act correctly. Use this order:

1. **Outcome:** name the observable result and its completion boundary.
2. **Motivation:** state why each material constraint protects the result and what bad outcome it prevents.
3. **Evidence:** identify live owners, proof, references, disconfirming evidence, and uncertainty.
4. **Mise task graph:** name the public task for each deterministic job, its dependencies, cache boundary, and failure branch.
5. **Steps:** put execution in dependency order with one action and one readback per step.
6. **Assets:** name each template, schema, fixture, policy, or other static input and the exact trigger for loading it.
7. **Evals:** define behavior, trigger, failure, recovery, timing, resource, and nonregression evidence.

Set a context budget. Keep the body domain-complete, load only the branch's canonical owner, verify its digest, reuse current receipts, and reread after change or uncertainty. Token efficiency cannot remove domain motive, constraints, interfaces, failure branches, proof, model-owned capability, or needed context.

The command grammar starts with help and adds only the commands the skill needs. Write for the least capable executor:

- Numbered steps, one action and one observable result per step.
- The full plan visible upfront, never improvised midway.
- A mechanical check after each consequential step, with an explicit branch for failure.
- A stop-and-report branch wherever required information can be missing. Guessing is the failure mode, stopping is the contract.
- One default path per job, no menus of equal options.
- Progress written to an external log file after each step.
- Completion claims backed by fresh command output, never memory.

## Use-case specificity

Before defining or changing domain aspects or primitives, load references/use-case-specificity.md through `mise run domain-research-policy`. Its domain maps, required matrix use, research preservation, lifecycle and decision records, Mise dispositions and semantic attacks bind every new or updated package.

## Simplicity and language

Simplicity is a protected behavior. Every created, updated, standardized, or imported skill must preserve every accepted behavior while using the smallest coherent structure that makes the causal path easy to reason about. Keep one canonical owner per rule, one stable term per concept, one default path per job, and one material decision per branch. Remove duplicate rules, decorative sections, needless indirection, and options that produce the same result. Do not hide essential domain complexity or weaken proof, safety, authority, or behavior to make a package shorter.

Use plain and direct language. Put the result first. Use common words, active verbs, one idea per sentence, one topic per paragraph, and execution order for steps. Define a term once and use it consistently. Mechanical lint proves only its stated checks. Same-meaning human review must also confirm that the instructions are clear, complete, and no harder to follow than the domain requires.

## Deterministic and model-owned boundary

Mise owns every deterministic command. Put schemas, parsing, validation, file generation, state transitions, task ordering, receipts, metrics, comparisons, and reproducible rollback checks in tested scripts behind one owning Mise task. The model-owned boundary contains semantic interpretation, causal reasoning, domain judgment, creative generation, and direct human-sense review. A schema pass cannot prove meaning, usefulness, or visual quality.

Use one shared normalized whole-phrase matcher for deterministic domain-specificity checks. Every semantic gate must call that owner so a short token or a substring inside an unrelated word cannot satisfy a domain contract. A generated package receives the same matcher through `mise run new`.

Mise is an orchestration boundary, not a capability ceiling. Use every available, authorized capability required by the domain, including direct vision, current web research, browser or computer interaction, tool calls, multimodal inspection, semantic reasoning, synthesis, creativity, and human-sense judgment. Mise may prepare the input, route work, preserve evidence, and validate reproducible claims, but it must never replace direct judgment with a proxy. A generated skill fails if its deterministic envelope disables, imitates, or narrows a capability that the outcome needs, even when its machine gates pass.

Every generated skill supports one typed, platform-neutral agentic request path through `mise run agentic-request`. Pass long prompts by a digest-bound file or standard input, never a shell argument or environment variable. Bind each request to the completed use-case contract, its digest, and its exact promised outcome. Require the operation and prompt to use the target skill's domain terms. Give the prompt, every digest-bound SKILL.md dependency, and every open-ended primitive record a domain role, outcome contribution, relevance reason, and expected proof. The invoking caller supplies the runner executable and argument array outside the request, so untrusted request data cannot grant process authority. Dispatch through standard input without shell interpolation. Validate structure, terms, files, digests, runner exit, and output. A model or human still decides whether each item is truly relevant, correctly used, and sufficient for the promised outcome.

Assume an apparently nondeterministic job can be decomposed further. Mise owns its stable input manifest, source and query register, schema, coverage, dependency order, timestamps, digests, budgets, output envelope, comparison record, and rollback receipt. Repeat the split until only the part whose correctness depends on interpreting meaning, forming a causal conclusion, creating a novel candidate, direct perception, or human-sense judgment remains model-owned. Record why code cannot supply that remaining capability.

Choose data structures and algorithms after measuring the access, mutation, query, ordering, interoperability, and lifetime pattern. Prefer streaming for one-pass large inputs, maps or sets for repeated lookup, indexes for stable query keys, append-only records for experiment history, content digests for invalidation, bounded concurrency for independent work, and atomic replacement for accepted state. Load references/resource-and-experiment-design.md through `mise run improvement-policy` for the decision tables. For each trial, measure or justify as not applicable every resource group named by the machine-readable improvement contract.

Do not cache mutable remote state, live judgment, an external side effect, or randomness without a captured seed. A cache declaration is an assertion that all inputs, tool versions, environment fields, and outputs are complete.

## Markdown layout

Load references/writing-rules.md through `mise run lint-writing` before Markdown authoring. Its line layout, exclusions, file-reference routing and full-tree checks bind every factory and output file.

## Examples

Every skill ships examples/ through `mise run validate`, with at least one worked example per command in its grammar and one more for the failure the skill is most likely to cause. An example is a complete run, not a fragment: the user's words, the executor's visible reply, every command with its real output and exit code, and every file the run created with its full contents. Each example names the guess it removes at the top and stays consistent with SKILL.md, so a rule change that outdates an example changes the example in the same commit.

## Code

Load references/code-rules.md through `mise run lint-code` before implementation. Its file, function and nesting caps, script interfaces, standard-library preference and test-first order bind every code file and output.

## Tests, tasks, CI

Build in the fixed test-first order at references/code-rules.md through `mise run lint-code`. Local runs and remote CI use one command, `mise run ci`.

Every generated SKILL.md contains one numbered `Ordered workflow` before its detailed branches. Each step names `Mise:` work, `Model:` work, or both. Use `Branch:`, `If:`, `For each:`, `Repeat:`, and `Stop:` where the domain has a real decision, collection, retry, or terminal state. Each failure returns to the lowest owning step and invalidates its dependents. Do not add a loop or branch that cannot change action, evidence, recovery, or acceptance.

Every accepted factory, generated skill, updated skill and scope variant must execute its promised domain operation through a real Mastra workflow behind a public Mise task, for both human and agent audiences. Bind the actual inputs, declared resources, step outputs, required decisions, protected effects and final domain result. Preserve working script leaves and use the smallest necessary TypeScript integration. An installed SDK, unused workflow, schema wrapper, copied engine probe or successful synthetic example cannot satisfy this requirement.

Mise owns executable versions, the prepared environment and public prerequisites. Mastra owns the domain step graph and declared run state. Scripts own their actual transformations and effect guards; the host owns runner authority and authentic human identity. Pass the caller-selected runner and its argument array outside untrusted request data. Invoke leaves directly inside the prepared workflow environment. Do not create recursive Mise calls or competing retry, scheduling, cache and state owners.

Keep exact compatible native executable versions, package-manager identity, dependency manifests and lockfiles under their current owners. Run clean installation without unapproved lifecycle scripts, native syntax and type checks, real engine probes, and the target's domain tests through the public task graph. Verify generated packages with their own dependencies. Preserve compatible custom runtime configuration; reconcile incompatible or partial inputs explicitly. Enforce required results at the consuming step, since output schema declarations and lifecycle callbacks do not reliably reject bad domain results in the selected engine. Persisted pauses, human decisions, replay, concurrency and failure recovery need their own actual boundary tests and stated limits before acceptance.

Use dependency edges rather than repeated nested task calls when Mise can schedule independent work safely. Derive the job bound, cache keys, and task batching from the target domain's real dependency and resource profile instead of copying a generic preset. Cache only deterministic tasks with complete declared sources and outputs. Keep target-specific live, mutating, network, model-owned, and human-judged tasks outside the cache. Measure cold and warm aggregate paths, and retain an optimization only when speed improves without a protected regression. The task graph must optimize elapsed time without weakening required ordering, evidence, or model capability.

Every task declares a dependency list, including an empty list for a true root. Every task must lead to CI, a named public operation, or a required dependency of one of those entry points. From any public operation, each dependency has exactly one reachable path. Cycles, diamonds, disconnected tasks, unknown edges, and redundant transitive edges fail. A mutating acceptance task waits for every prerequisite proof. Do not invoke `mise run` inside a task or cache a task whose output depends on live web state or model judgment.

Keep the active Mise version fixed during meaningful domain work. After the skill outcome and all acceptance tasks conclude, run `mise run mise-primitives-update` as the final maintenance chain. Its predependency self-updates Mise without plugins, its body refreshes the exact release schema catalog, and its postdependency forces target-skill reconciliation plus lineage refresh when the skill owns lineage. Rerun `mise run ci` under the resulting binary and record its version and catalog digest. Treat a package-manager instruction, network failure, or compatibility regression as `BLOCKED`; never force past package ownership.

Every task has a domain-specific record in assets/use-case-contract.json with outcome, motivation, progress value, proof, and applicability. Each invocation runs its selected operation path and records every remaining task as inapplicable only when the current request and skill nature supply a domain-specific reason and proof. `mise run invocation-policy -- <receipt>` validates the complete disposition; its own execution accounts for the validator task. Accounting alone leaves evidence acceptance pending. Before accepting a result, load references/evidence-acceptance.md through that same `mise run invocation-policy` route and supply its host-bound context and receipt digests. Consume actual supporting contents, current source and subject bindings, every required claim, independently frozen predicates, and responsible judgments. A valid record cannot prove that a semantic review or human contribution happened.

## Evals

Load evals/evals.json, evals/trigger-queries.json, and the registry contract at references/eval-authoring.md through `mise run evals`. Keep at least four realistic cases with prompts, expected output, and verifiable assertions, plus positive and negative trigger queries with near misses. A registry skill also emits manifest.json, cases.json, trigger-cases.json, contract.md, rubric.md, speed-budgets.json, and source-lineage.json with real sha256 source hashes.

Import the complete supplied case and trigger collections without a sample cap. Preserve stable IDs, conditions, required assertions, expected results, and additional source fields. Missing expected results or assertions remain missing; mechanical preparation cannot invent them. The minimum case count is a lower bound for acceptance, never a reason to truncate a larger source or fill an empty collection with generic cases. Run `mise run evals` to reject incomplete seeds before acceptance.

An optional improvement trial begins only after required work passes. Freeze a fresh baseline, frozen evaluator, fixtures, seed when applicable, environment, time budget, repetitions, and resource measures before viewing the candidate result. Change one named dimension at the smallest owner. Record keep, discard, or crash outside the editable surface. Accept only Pareto improvement: the named dimension improves materially and no protected dimension regresses. On a worse, invalid, or unknown result, restore the last accepted version and verify its digest.

## Updating, standardizing, and importing

Every operation that creates or changes a skill must satisfy references/skill-scope-contract.md through `mise run validate`; the factory uses its detailed variant workflow for adaptation.

Before changing an existing skill, freeze a read-only file inventory, content digests, current purpose, valid triggers, accepted behavior, task graph, examples, and eval baseline. Also freeze the source outcome, proof, boundaries, forbidden outcomes, and mandatory methods. A collision, symlink, or unclassified host owner blocks the plan before any write. Preserve those owners unless the user explicitly changes them. Standardization repairs package shape and execution contracts; it does not replace domain meaning.

Preserve authored use-case fields, nested conditions, stable IDs, dependency references, matrix selections, unresolved decisions, and extension fields while filling missing structural defaults. Existing lifecycle, decision, invocation-template, and Mise disposition records stay intact. Make intended record changes through the existing profile-bound text rewrites; keep unrelated entries. Resolve audience changes through the audience owner and supply fresh research records only after their actual review. Preserved records can remain incomplete or stale: preservation does not establish current applicability, evidence validity, checker parity, or acceptance. Reconcile those requirements through their own checks before use.

Lineage and planning walk only owned regular files. Reject symlinks before reading or hashing them, and exclude runtime caches, dependency installations, generated bytecode, and tool state such as `.mise`, `node_modules`, `__pycache__`, and `.DS_Store`. These are execution products, not portable skill sources.

For a platform-specific source, a source adapter is a candidate path unless the user makes it mandatory. Classify current client markers and package formats separately, since a package format is not a coding agent. Accept a recognized subset, but stop when no source shape is recognized or a candidate shape remains unclassified. Translate reusable capability instructions into SKILL.md and repository guidance into AGENTS.md. Translate a hidden host-specific ownership directory into `.agents/` through `mise run plan-standardize` only after detecting path and semantic collisions. Remove host-only fields, commands, path assumptions, permissions, and runtime behavior from the destination. The source stays unchanged unless the user explicitly requests in-place migration. Reject a destination that retains platform-specific assumptions or loses source behavior.

## Reuse before building

Check for installed registry skills through `mise run source-corpus` before writing anything new, starting with starting-point from https://github.com/srinitude/skills. Look for skills/starting-point/SKILL.md through that task in the surrounding skills directory. Defer to an installed skill for the jobs its description names.

## Prohibited content

Generated destinations do not name or require one agent product, harness, vendor, or model. Factory-only import evidence may identify a source host so the migration can remove its assumptions. Describe portable capabilities in the accepted destination: run in a terminal, read the file, search the tree. Nothing may assume host state beyond declared compatibility needs.
