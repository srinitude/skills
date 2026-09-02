# Use-case specificity

Read this file before creating, updating, standardizing, or importing a skill. The target is a reusable skill for one coherent task class, not prose that could survive a domain-name swap.

## Research basis

The [Agent Skills authoring guidance](https://agentskills.io/skill-creation/best-practices) says effective skills start from real expertise, project artifacts, real failures, corrections, and execution traces. It warns that generic model knowledge produces vague procedure and that excess detail can waste context. The [Agent Skills specification](https://agentskills.io/specification) keeps domain references and scripts loadable on demand so the always-loaded body can stay focused.

The [SKOS Recommendation](https://www.w3.org/TR/skos-reference/) separates concepts from preferred, alternate, hidden, broader, narrower, and related labels. The [PROV-O Recommendation](https://www.w3.org/TR/prov-o/) relates entities, activities, agents, derivation, attribution, and time. The [SHACL Recommendation](https://www.w3.org/TR/shacl/) separates machine-checkable shapes from the data being judged. The [NASA Systems Engineering Handbook](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) links stakeholder expectations, rationale, authority, verification, validation, state, function, and time. These sources support the domain map and trace rules below. None proves a target skill's private facts.

## Research gate

Use every relevant available web research capability. Start with current first-party owners, standards, source repositories, schemas, API references, issue history, real failure reports, and execution evidence. Add independent research or practitioner evidence where it can confirm, bound, or challenge an owning claim. Local project sources remain authoritative for private project facts.

Register a question for every domain dimension before drafting. Retain at least four distinct current web sources across at least two hosts and two source classes. Record source URL, class, checked timestamp with timezone, supported claim, covered dimensions, limitation, and disposition in `assets/use-case-contract.json` through `mise run domain-research-policy`. A check timestamp older than 31 days is stale, and a future timestamp fails. Search for counterevidence to the strongest retained claim and record how it changed or bounded the package.

Run `mise run domain-research-policy` before accepting any domain map. The task proves receipt shape, diversity, current access time, and coverage. It cannot prove that a source supports the recorded claim. Read each source and make that judgment directly. If current web evidence is unavailable or external access is prohibited, mark affected domain claims `BLOCKED`; do not fill them from plausible memory.

## Domain map

Map these dimensions for the target skill. Add a domain-owned dimension when it changes behavior or proof.

| Dimension   | Required question                                                               |
| ----------- | ------------------------------------------------------------------------------- |
| Actors      | Who requests, acts, decides, reviews, owns, receives, or is affected?           |
| Objects     | Which concepts, artifacts, data, facts, and identifiers exist?                  |
| Actions     | Which operations produce the result and which side effects can occur?           |
| States      | Which valid, invalid, partial, blocked, accepted, and recovery states exist?    |
| Invariants  | Which truths must hold before, during, and after the work?                      |
| Variants    | Which differences are valid, and which are defects or separate task classes?    |
| Interfaces  | Which APIs, formats, tools, services, files, and handoffs meet the skill?       |
| Authorities | Who may read, write, approve, transmit, publish, delete, or spend?              |
| Failures    | Which wrong outputs, omissions, conflicts, and false success claims matter?     |
| Recoveries  | Which rollback, retry, repair, escalation, and resume paths are real?           |
| Evidence    | Which direct observations, tests, receipts, and judgments prove the result?     |
| Time        | Which order, duration, deadline, freshness, recurrence, and expiry rules apply? |
| Resources   | Which compute, context, cost, capacity, and attention limits change decisions?  |
| Quality     | Which use-case measures separate acceptable work from failure?                  |
| Terminology | Which preferred, alternate, overloaded, deprecated, and rejected terms matter?  |
| Exclusions  | Which adjacent requests must the skill refuse, preserve, or hand off?           |

## Aspect and primitive map

Treat the domain dimensions above as the aspect layer. Map the skill body, references, assets, scripts, tests, Mise tasks, examples, evals, policies, schemas, and records as the primitive layer. Every material aspect and primitive states its domain role, protected outcome, concrete progress value, motivation, prevented failure, and proof. A shared validator may retain shared implementation, but its value in the target package must still be specific. Never copy a factory seed, generic resource policy, example, eval, rationale, or task and call standard shape domain work.

Map every Mise task separately in the use-case contract. Its record must explain the domain result it advances, why it exists, the concrete progress it creates, the proof it returns, and when the skill's nature makes it applicable. Domain terms must be normalized, unique phrases and must match whole words, never convenient substrings. Run `mise run use-case-policy` and `mise run task-graph-policy`. Then perform two semantic attacks. Replace the skill name with an unrelated domain; if the package still reads plausibly, it is generic. Remove its domain terms; if the remaining instructions still claim full use-case completion, the domain behavior is missing. Repair the lowest owner and rerun both Mise policies.

## Deterministic split

Assume an apparently nondeterministic job can be decomposed further. Move its stable shell into Mise: input manifest, query register, source receipt, schema, coverage matrix, task order, dependency check, timestamp, digest, budget, output envelope, decision record, and rollback receipt. Repeat until only source interpretation, causal reasoning, creative choice, direct perception, or human-sense judgment remains. Record why that core needs model capability that code cannot supply.
