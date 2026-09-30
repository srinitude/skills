# Dependency types, classes, and reading order

- Read this guide before mapping prerequisites. It governs reading within sections, across files, and through every linked child in the skill and every invocation output.
- Prerequisites: the source set, reader's task, applicable rules, and available tools. No other guide must be read first to understand this guide.

## Define a dependency before ordering it

- A dependency is a stated or supported relationship in which something needs another thing, fact, state, action, or constraint. Record what depends on what and why; resemblance or nearby placement is not enough.

### Separate reading from the subject being described

- A reading prerequisite is information the reader needs before a passage makes sense or can be used correctly. A package, service, approval, or physical resource may instead be an execution prerequisite. Explain that need before use without making all of its documentation a required read.
- Keep the topic tree, required reading graph, software graph, evidence graph, and work schedule distinct. A graph records items and their relationships. One topic can have several prerequisites without having several heading parents.
- Do not turn correlation, association, a citation, a containment link, or navigation into a prerequisite without evidence. A causal claim, a logical implication, and a required prior action are different relations.
- Read constraints before the decision they constrain. Reading about a dependency does not satisfy it, install a package, grant access, prove readiness, or authorize execution.

### Bound coverage honestly

- Screen every family and classification axis below against the full current input. Mark each relevant, not relevant with a reason, or unresolved. Follow each relevant item's own prerequisites until the known scope is covered.
- This is an extensible review catalog, not a claim to enumerate every dependency type that could ever exist. Domain rules can define new relations. Keep the user's broad coverage goal by searching for unlisted cases, rather than claiming a finite list is universal.
- Add an unlisted dependency with a plain definition, source evidence, direction, conditions, and effect on reading or work. If its meaning is unknown, retain it as unresolved and stop only the work that needs that answer.

## Screen dependency families

- These families are editorial review groups, not one universal standard. The same dependency may belong to several groups; avoid duplicate requirements when it does.

### Meaning, reasoning, and evidence

- D01 Language and reference: a word's meaning, pronoun referent, abbreviation, notation, unit, or translation needed to read a claim.
- D02 Concepts and learning: a definition, foundational idea, prior skill, or mental model needed for a later explanation.
- D03 Logical support: premises, assumptions, axioms, inference rules, necessary conditions, sufficient conditions, and proof obligations behind a conclusion.
- D04 Mathematical structure: domains, types, dimensions, equations, variable definitions, constraints, and boundary or initial conditions.
- D05 Evidence and provenance: observations, source data, attribution, derivation, quotations, revisions, and evidence needed to support a claim.
- D06 Causal and statistical relations: causes, mechanisms, mediators, confounders, conditional dependence, and sampling assumptions. Do not convert statistical dependence into causation or reading order by default.
- D07 Narrative and argument: an earlier event, reason, decision, question, or exception needed to understand what follows.
- D08 Authority and scope: applicable policies, precedence, jurisdiction, ownership, conditions, and narrow exceptions that govern a decision.

### Documents, data, and presentation

- D09 Context and reading: prerequisite passages, files, prior decisions, task state, and branch-specific instructions.
- D10 Document assembly: imports, includes, templates, shared text, transclusions, substitutions, and generated content.
- D11 References and identity: relative paths, base locations, anchors, identifiers, citations, footnotes, glossary targets, and versioned references.
- D12 Data flow: inputs, producers, consumers, transformations, schemas, encodings, units, and output contracts.
- D13 Data integrity: keys, foreign keys, uniqueness, functional or multivalued dependencies, validation rules, and cross-record constraints.
- D14 Data availability and history: snapshots, lineage, migration state, retention, freshness, source versions, and cache validity.
- D15 Presentation and accessibility: renderer, dialect, extension, theme, font, asset, language, alternative text, and export support needed to convey meaning.
- D16 Interaction and navigation: a prior choice, visible state, focus order, route, or user input needed for the next action.

### Software and infrastructure

- D17 Package roles: production, development, test, peer/host compatibility, optional, and bundled dependencies. Preserve the owning ecosystem's meanings; names do not transfer unchanged to every package manager.
- D18 Resolution and supply: registries, repositories, local paths, artifacts, manifests, lockfiles, checksums, signatures, provenance, and dependency substitutions.
- D19 Versions and compatibility: version ranges, API/ABI contracts, peer constraints, platform markers, feature flags, mutually incompatible versions, and fallback choices.
- D20 Build and generation: source files, build targets, compilers, generators, link inputs, generated files, toolchains, and incremental rebuild inputs.
- D21 Loading and binding: modules, imports, shared libraries, plugins, symbols, dependency injection, and compile-time or runtime binding.
- D22 Execution environment: operating systems, architecture, runtime, system libraries, configuration, environment variables, locale, and timezone.
- D23 Service and network: API contracts, endpoints, DNS, certificates, network paths, remote services, message formats, and connectivity.
- D24 Infrastructure and deployment: resource creation, provider behavior, readiness, health, storage, topology, deployment stages, and teardown requirements.

### Work, people, resources, and change

- D25 Workflow and state: preconditions, postconditions, handoffs, branches, lifecycle states, transactions, and stage gates.
- D26 Time and scheduling: deadlines, start/finish relations, delays, time windows, expiration, event order, and time-indexed state.
- D27 Concurrency and synchronization: locks, barriers, shared mutable state, ordering constraints, races, leases, and ownership transfer.
- D28 Capacity and availability: memory, compute, storage, bandwidth, quotas, rate limits, energy, and other scarce resources.
- D29 Physical and spatial needs: materials, parts, tools, location, access routes, environmental conditions, calibration, and physical tolerances.
- D30 People and organizations: assigned roles, decisions, availability, expertise, handoffs, suppliers, and external commitments.
- D31 Access and trust: identity, authentication, authorization, consent, trust roots, secrets, and allowed information flows.
- D32 Legal and commercial conditions: licenses, contractual duties, purchasing, funding, cost ceilings, and applicable compliance requirements.
- D33 Risk and recovery: backups, rollback paths, containment, failover, restart state, recovery points, and safe retry conditions.
- D34 Testing and acceptance: environments, fixtures, test data, expected results, oracles, reviews, and evidence required before acceptance.
- D35 Change impact: upstream changes, downstream invalidation, migration order, backward compatibility, and revalidation needs.
- D36 Feedback and recurrence: iteration, recursion, mutual dependence, and feedback loops in the source domain. Preserve them as subject matter; do not force a circular required reading path.

## Classify each relevant relationship

- These axes describe a relationship from different angles. They are not competing choices in one flat list, and their values depend on the source domain.

### Record its form and conditions

- Direction and reach: prerequisite to dependent; direct or through other dependencies; one-to-one, one-to-many, many-to-one, or many-to-many.
- Discovery: declared or inferred; explicit or implicit; visible or hidden; known or unresolved. Keep the evidence for an inferred edge.
- Force: required, preferred, optional, or forbidden. A preference must not become a hard prerequisite without authority.
- Activation: unconditional, conditional, feature-specific, platform-specific, version-specific, task-specific, or time-specific.
- Logic: all-of requirements, any-of alternatives, exclusive choices, minimum counts, and exclusions. Do not turn alternatives into a requirement to load or satisfy them all.
- Relation: informational, logical, causal, structural, data-carrying, compatibility, resource, authority, or temporal. More than one may apply.
- Phase: design, authoring, install, build, test, deploy, startup, runtime, maintenance, teardown, or recovery.
- Time: static or changing; eager or deferred; event-triggered; fresh or stale; temporary or persistent; sequence-only or invalidation-causing.
- Boundary: internal or external; local or remote; trusted or untrusted; controlled by this owner or another owner.
- Shape: acyclic, cyclic, recursive, shared, converging, or branching. Distinguish the source graph from the reading graph.
- State: available, missing, incompatible, failed, stale, satisfied, pending, or uncertain. Specify what evidence changes the state.
- Impact: what becomes unclear, invalid, unavailable, or unsafe if the dependency fails, and which work can still proceed.

## Build and enforce the reading order

- Use the catalog to discover real prerequisites, then produce an order justified by those relationships. Do not use alphabetical order, file depth, heading rank, or link position as a substitute.

### Follow prerequisites just in time

1. Identify the reader's current task and branch, then list the passages, facts, and requirements needed for that branch.
2. Record each edge as prerequisite to dependent, with stable source and destination locations, type, conditions, reason, version when relevant, and deciding evidence. Record execution gates separately from required reads.
3. Follow the prerequisites of each prerequisite. Verify needed sources exist and can be read. Resolve conditions and alternatives before treating their edges as active.
4. Order active required reads so every prerequisite comes before its dependent. This is a topological order. Independent items may have several valid orders; choose a clear one without inventing dependencies.
5. Detect required-reading cycles and show the exact path. Repair the content owner, extract shared foundations, or use an explicit overview before detailed treatment. Preserve real feedback in the subject. Never hide a cycle by deleting a true prerequisite or renaming a required link as navigation.
6. Place the reading route at the owning heading and point of need. Introduce shared context before its first active consumer, read only needed detail, and reuse complete current text under the existing reread rules.
7. Recheck order within lists, tables, quotations, includes, files, and assembled output. Keep essential warnings and conditions before the governed action and preserve any exact protected sequence.
8. After a change, identify affected dependents, invalidate only stale proof, and rerun affected checks plus the final whole-set review. Block missing, cyclic, or incompatible prerequisites on the affected path; keep unrelated valid work available.

### Test the reading contract

- Test a term used before its definition, a conclusion before its needed premise, an implicit prerequisite absent from the link list, a shared prerequisite, a transitive chain, a conditional branch, any-of alternatives, an optional package, a version conflict, an unavailable source, and a required-reading cycle.
- Test a legitimate feedback loop explained through an acyclic reading path, a software dependency that needs no extra reader documentation, and independent sections with more than one valid order.
- Check the semantic edges against source evidence before checking the graph. A cycle-free but incomplete or invented graph does not establish correct reading order.
- Treat the source graph, ordering proof, rendered reading check, and human comprehension evidence as separate results. A passed graph check cannot prove understanding.

## Research basis and limits

- Sources below were accessed on 17 September 2026. Update dates are stated separately where verified; a retrieval or copyright date is not a publication date. The cross-domain catalog is an editorial synthesis for this project.

### First-party sources

- [Python graphlib](https://docs.python.org/3/library/graphlib.html): prerequisite ordering and cycle handling; Python 3.14.7 page updated 17 September 2026. This supports graph mechanics, not semantic edge discovery.
- [npm package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/): package roles, optional and peer dependencies, and version constraints; version 11.19.1 documentation, update date not established. Other ecosystems may differ.
- [Bazel dependencies](https://bazel.build/concepts/dependencies): actual versus declared dependencies and direct versus transitive requirements; update date not established.
- [Terraform depends_on](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on): hidden behavior dependencies beyond visible data references; update date not established.
- [W3C PROV-O](https://www.w3.org/TR/prov-o/): entities, activities, agents, derivation, and provenance; Recommendation dated 30 April 2013. It is a provenance vocabulary, not an exhaustive dependency taxonomy.
- [OpenAPI references](https://learn.openapis.org/referencing/overview.html): reference identity, external documents, and version-specific behavior; update date not established.
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html): cross-record and cross-table integrity; PostgreSQL 18 documentation, page update date not established.
- [W3C meaningful sequence](https://www.w3.org/WAI/WCAG22/Understanding/meaningful-sequence.html): preserve reading order where order affects meaning; multiple correct orders can exist. Updated 16 September 2025.
- The [skill entry](../SKILL.md) is a navigation-only return route, not a required read from this file.
