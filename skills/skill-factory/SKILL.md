---
name: skill-factory
description: "Use when a workflow or capability must become a new agent skill, when an existing skill must be updated or standardized without losing its purpose, when a user-level or project-level variant is needed, or when a skill needs validation, evaluation, scaffolding, scripts, tests, or a Mise task graph."
license: MIT
metadata:
  author: Kiren Srinivasan
  version: "0.5.1"
  scope: "user"
---
# Skill factory

- **Start here.** On every load, read this whole SKILL.md body first. Run `rule:read`, owned by [load tasks](tasks/context.toml). If its tool is not connected, use `mise run rule:read`. Bind exactly one `body` input: this skill’s real SKILL.md path, current hash and full text. Reject other paths, byte-only input and duplicate body roles before model work. Read the full `task-tools` body through its tool's inspect action; if tools are not connected, use `mise tasks info task-tools --json`. Follow its connection, task-call and model-handoff rules. Use the [Mise task graph](#mise-task-graph) and [Steps](#steps) to select work.
- **Read and retain context.** Run `mise run rule:context`, owned by [load tasks](tasks/context.toml), after the whole-body read. It owns source capture, meaning review, valid review reuse, missing-input recovery and integration duties. Read its full rules before work uses that context.

## Outcome

- **Run `mise run rule:outcome`.** Preserve the complete portable skill contract. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:scope-audience`.** Resolve scope, audience and allowed destinations. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:duties`.** Assign each action, judgment, check and acceptance owner. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:consumer`.** Validate the result for its real consumer. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:model-duty`.** Keep meaning, perception and creative judgment with the model. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:human-duty`.** Obtain real decisions and proof from their human owners. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:program-host`.** Verify actual program capabilities, interfaces and authority. Read the full [task rules](tasks/outcome.toml) when its trigger applies.
- **Run `mise run rule:acceptance-owner`.** Keep verification, real-use validation and acceptance distinct. Read the full [task rules](tasks/outcome.toml) when its trigger applies.

## Motivation

- **Run `mise run rule:purpose`.** Protect the reasons, allowed choices and intended result. Read the full [task rules](tasks/principles.toml) when its trigger applies.
- **Run `mise run rule:simplicity`.** Simplify only while preserving the complete contract. Read the full [task rules](tasks/principles.toml) when its trigger applies.
- **Run `mise run rule:methods`.** Choose methods from measured work and proof needs. Read the full [task rules](tasks/principles.toml) when its trigger applies.
- **Run `mise run rule:useful-output`.** Finish the producer work and test its real usefulness. Read the full [task rules](tasks/principles.toml) when its trigger applies.

## Evidence

- **Run `mise run rule:source-inputs`.** Bind current sources, scope and evidence. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-capture`.** Keep every source rule and its full context. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-identity`.** Keep exact meaning, source identity and rule force. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-applicability`.** State when a rule applies and what it must achieve. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-responsibility`.** Assign each duty to its real owner. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-dependencies`.** Bind needed state, inputs and their lifetimes. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-quality`.** Retain quality, resource and proof requirements. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-evidence`.** Bind each claim to its deciding proof. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-propagation`.** Trace body ownership, consumers and copied rules. Read its full [task rules](tasks/ledger.toml) when its trigger applies.
- **Run `mise run rule:ledger-relationships`.** Preserve each relationship and its exact meaning. Read its full [task rules](tasks/ledger.toml) when its trigger applies.

### Use the file graph for every change

![Complete file graph with SKILL.md as its hub](assets/file-map.svg)

- **Run `mise run rule:graph-map`.** Map every rule to its real file owners. Read its full [task rules](tasks/graph.toml) when its trigger applies.
- **Run `mise run rule:graph-paths`.** Keep every file on a true path to SKILL.md. Read its full [task rules](tasks/graph.toml) when its trigger applies.
- **Run `mise run rule:graph-coverage`.** Cover every file in a whole-directory update. Read its full [task rules](tasks/graph.toml) when its trigger applies.
- **Run `mise run rule:graph-order`.** Work outward while keeping real prerequisites. Read its full [task rules](tasks/graph.toml) when its trigger applies.
- **Run `mise run rule:graph-render`.** Render and inspect the complete file graph. Read its full [task rules](tasks/graph.toml) when its trigger applies.

### Review and change through the ledger

- **Run `mise run rule:ledger-traverse`.** Read the right context and preserve traversal limits. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:body-ownership`.** Keep core work and load routes rooted in SKILL.md. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:change-review`.** Review full inputs and affected meaning around each change. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:change-history`.** Keep a useful record of every file change. Read its full [task rules](tasks/progress.toml) when its trigger applies.
- **Run `mise run rule:native-effects`.** Use the native file tool within its reviewed boundary. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:staged-changes`.** Protect current content during staged promotion. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:deterministic-checks`.** Prove only the exact predicates code can decide. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:isolation`.** State and test the real limits of replay and isolation. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:prerequisites`.** Find prerequisites from real outcomes and consumers. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:runtime-scheduling`.** Bind discovered work and protect shared state. Read its full [task rules](tasks/review.toml) when its trigger applies.
- **Run `mise run rule:factory-repair`.** Fix factory faults before resuming affected skill work. Read its full [task rules](tasks/review.toml) when its trigger applies.

### Preserve judgment and human evidence

- **Run `mise run rule:judgment-scope`.** Keep exploration, production and acceptance distinct. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:creative-scope`.** Preserve allowed creative choices and media. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:meaning-decisions`.** Resolve material facts and competing readings. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:human-matrix`.** Load and use the required human-work matrix. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:human-inventory`.** Keep the full applicable study and work inventory. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:human-context`.** Study the actual task, people and medium. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:selection-meaning`.** Preserve selection order, members and limits. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:research-design`.** Use research to inform real design choices. Read its full [task rules](tasks/judgment.toml) when its trigger applies.
- **Run `mise run rule:human-proof`.** Match each human claim to the right proof. Read its full [task rules](tasks/judgment.toml) when its trigger applies.

## Mise task graph

- **Run `mise run rule:work-owners`.** Assign tools, workflows, code and judgment to their owners. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:rule-coverage`.** Give each work unit a full task, tool and workflow. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:commands`.** Choose the supported command and its reviewed path. Read the full [task rules](tasks/operations.toml) before its work.
- **Run `mise run rule:typed-dispatch`.** Pass full bound inputs to the authorized runner. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:resource-binding`.** Bind initial resources to their actual consumers. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:resource-duties`.** Name and test every resource handoff. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:runtime-interfaces`.** Verify the real interface before composing a runtime. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:runtime-versions`.** Freeze compatible environments and exact versions. Run `setup-runtime` to reuse a checked install or retain and rebuild it. Stop its users before a rebuild; keep failed checks and recovery copies. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:task-dependencies`.** Review and declare every real task dependency. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:native-task-fields`.** Check native wait, post-task and inheritance behavior. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:mise-features`.** Review each released Mise feature and its domain use. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:companion-authority`.** Check companion need, versions and authority. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:usage`.** Keep one native argument owner. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:packslip`.** Verify distribution and provenance boundaries. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:fnox`.** Pass scoped secrets only to ready consumers. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:pitchfork`.** Own persistent processes and their cleanup. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:hk`.** Reuse checks within the verified hook boundary. Read the full [task rules](tasks/companions.toml) before its work.
- **Run `mise run rule:mastra-capability`.** Run the real skill capability in Mastra. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:mastra-recovery`.** Test actual workflow state and failure behavior. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:human-handoff`.** Bind real human input before protected effects. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:human-review`.** Use the full human review protocol and its limits. Read the full [task rules](tasks/runtime.toml) before its work.
- **Run `mise run rule:workflow-granularity`.** Compare real workflow structures before choosing one. Read the full [task rules](tasks/runtime.toml) before its work.

## Steps

- **Run `mise run rule:loop-contract`.** Use the seven stages without replaying finished effects. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:reconciled`.** Bind the current request, sources and rights. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:selected`.** Start design at SKILL.md. Build broad working paths, then fix owned gaps in dependency order. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:ready`.** Bind the exact allowed change and deciding checks. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:implemented`.** Carry out the reviewed change and retain its effects. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:validated`.** Check actual behavior and invalidate affected proof. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:finalized`.** Review the whole changed file and its known consumers. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:advance`.** Record results, remaining work and verified delivery. Read the full [task rules](tasks/execution.toml) before its work.
- **Run `mise run rule:markdown-order`.** Review whole files before blocks and lines. Read the full [task rules](tasks/writing.toml) before its work.
- **Run `mise run rule:markdown-payload`.** Read the full bound review result. Read the full [task rules](tasks/writing.toml) before its work.
- **Run `mise run rule:markdown-choices`.** Explain and prove each Markdown form choice. Read the full [task rules](tasks/writing.toml) before its work.
- **Run `mise run rule:markdown-reply`.** Validate the review and its exact prior stage. Read the full [task rules](tasks/writing.toml) before its work.
- **Run `mise run rule:markdown-recovery`.** Prove failed and resumed review paths. Read the full [task rules](tasks/writing.toml) before its work.
- **Run `mise run rule:markdown-authority`.** Keep workflow and human authority separate. Read the full [task rules](tasks/writing.toml) before its work.

## Assets

- **Run `mise run rule:package-shape`.** Keep valid package metadata and required files. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:physical-limits`.** Keep readable files within physical size and depth limits. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:plain-writing`.** Write clear sixth-grade prose and verify its meaning. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:resource-links`.** Give each resource a clear route and checked link. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:code-contract`.** Keep scripts correct at real runtime boundaries. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:ponytail-duties`.** Apply all six code simplicity duties within scope. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:code-simplicity`.** Use the smallest sound code and measured tradeoffs. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:domain-records`.** Keep domain, lifecycle and decision records at their owners. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:examples`.** Reuse existing owners and keep complete actual examples. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:source-adaptation`.** Preserve source and accepted behavior during adaptation. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:variants`.** Adapt independent variants with their own proof. Read the full [task rules](tasks/package.toml) before its work.
- **Run `mise run rule:output-propagation`.** Carry the whole contract into independent outputs. Read the full [task rules](tasks/package.toml) before its work.

## Evals

- **Run `mise run rule:eval-design`.** Freeze the eval rules before building or testing. Read its full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:eval-cases`.** Run real domain cases and trigger checks. Pass [local cases](evals/evals.json) and [trigger queries](evals/trigger-queries.json) to their owning tasks. Read the full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:eval-recovery`.** Prove rejection, required non-effects and safe recovery. Read its full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:eval-coverage`.** Cover required operations alone and together. Read its full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:eval-antipatterns`.** Find real failures and test sound alternatives. Read its full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:improvement-trial`.** Load the full trial contract; keep gains only without protected loss. Read its full [task rules](tasks/improvement.toml) when its trigger applies.
- **Run `mise run rule:improvement-confirm`.** Check an adopted trial on the next invocation; restore regressions. Read its full [task rules](tasks/improvement.toml) when its trigger applies.
- **Run `mise run rule:implementation-progress`.** Build useful paths before polish. Keep each gap's repair owner and check. Apply this method to creation, updates and each skill's own work. Read its full [task rules](tasks/progress.toml) when its trigger applies.
- **Run `mise run rule:change-history`.** Bind each change, its proof, open gap and next action. Read its full [task rules](tasks/progress.toml) when its trigger applies.
- **Run `mise run rule:eval-resources`.** Measure complete paths with matched inputs and honest limits. Read its full [task rules](tasks/evaluation.toml) when its trigger applies.
- **Run `mise run rule:acceptance`.** Check the whole factory, whole output skill and whole domain result at their own finish. Require all applicable proof. Read its full [task rules](tasks/progress.toml) when its trigger applies.
- **Run `mise run rule:delivery-report`.** Give the full decision trail and distinguish work from acceptance. Read its full [task rules](tasks/progress.toml) when its trigger applies.

[use-case]: assets/use-case-contract.json
[variants]: references/scope-variants.md
[file-review]: examples/example-ledger-write.md
[mise]: https://mise.jdx.dev/
[mastra]: https://mastra.ai/docs/workflows/overview
[usage]: https://usage.jdx.dev/
[hk]: https://hk.jdx.dev/
[packslip]: https://packslip.dev/
[pitchfork]: https://pitchfork.jdx.dev/
[body]: SKILL.md
[python]: https://docs.python.org/3/
