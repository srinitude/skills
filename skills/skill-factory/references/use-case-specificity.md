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

The canonical `audience.primary` field in assets/use-case-contract.json is `human` or `agent`; check it through `mise run use-case-policy`. It identifies the main consumer of the promised result, independently of the executor and `metadata.scope`. Either audience can have either scope. Honor explicit choices and preserve valid existing designations. Resolve missing or conflicting meaning from the actual purpose and authoritative context before an affected write; ask one concise question only when it remains unresolved. Do not hide a material human audience behind an agent label.

Derive the early SKILL.md audience label and reading/action/evidence key from that field. Put the key in the Outcome/Evidence structure before operational steps. Distinguish the primary consumer, actual executor and workflow owner, mechanical evidence, model assessment, authentic human evidence, mandatory gates, and open creative choices. Use explicit labels; the designation grants neither runtime permission nor instruction authority. Identify secondary consumers and each distinct output's real audience where this changes obligations in the existing domain and ownership records.

Use `mise run new -- --audience <human-or-agent>` with the other creation arguments. For an authorized update, `mise run standardize-target` preserves the current audience unless an explicit `--audience` choice changes it. A label change only declares the new target: acceptance still requires adapted inputs, instructions, interfaces, presentation, evaluation, and required human participation. Check actual output suitability and downstream use. Untouched legacy inspection can use `mise run use-case-policy -- --inspect-legacy`; accepting new or updated output cannot omit the designation. Invalid types, values, duplicate keys, contradictory body labels, and a key following execution steps fail.

Map these dimensions for the target skill. Add a domain-owned dimension when it changes behavior or proof.

| Dimension | Required question |
| --- | --- |
| Actors | Who requests, acts, decides, reviews, owns, receives, or is affected? |
| Objects | Which concepts, artifacts, data, facts, and identifiers exist? |
| Actions | Which operations produce the result and which side effects can occur? |
| States | Which valid, invalid, partial, blocked, accepted, and recovery states exist? |
| Invariants | Which truths must hold before, during, and after the work? |
| Variants | Which differences are valid, and which are defects or separate task classes? |
| Interfaces | Which APIs, formats, tools, services, files, and handoffs meet the skill? |
| Authorities | Who may read, write, approve, transmit, publish, delete, or spend? |
| Failures | Which wrong outputs, omissions, conflicts, and false success claims matter? |
| Recoveries | Which rollback, retry, repair, escalation, and resume paths are real? |
| Evidence | Which direct observations, tests, receipts, and judgments prove the result? |
| Time | Which order, duration, deadline, freshness, recurrence, and expiry rules apply? |
| Resources | Which compute, context, cost, capacity, and attention limits change decisions? |
| Quality | Which use-case measures separate acceptable work from failure? |
| Terminology | Which preferred, alternate, overloaded, deprecated, and rejected terms matter? |
| Exclusions | Which adjacent requests must the skill refuse, preserve, or hand off? |

## Aspect and primitive map

Treat the domain dimensions above as the aspect layer. Map the skill body, references, assets, scripts, tests, Mise tasks, examples, evals, policies, schemas, and records as the primitive layer. Every material aspect and primitive states its domain role, protected outcome, concrete progress value, motivation, prevented failure, and proof. A shared validator may retain shared implementation, but its value in the target package must still be specific. Never copy a factory seed, generic resource policy, example, eval, rationale, or task and call standard shape domain work.

Map every Mise task separately in the use-case contract. Its record must explain the domain result it advances, why it exists, the concrete progress it creates, the proof it returns, and when the skill's nature makes it applicable. Domain terms must be normalized, unique phrases and must match whole words, never convenient substrings. Run `mise run use-case-policy` and `mise run task-graph-policy`. Then perform two semantic attacks. Replace the skill name with an unrelated domain; if the package still reads plausibly, it is generic. Remove its domain terms; if the remaining instructions still claim full use-case completion, the domain behavior is missing. Repair the lowest owner and rerun both Mise policies.

## Deterministic split

Assume an apparently nondeterministic job can be decomposed further. Move its stable shell into Mise: input manifest, query register, source receipt, schema, coverage matrix, task order, dependency check, timestamp, digest, budget, output envelope, decision record, and rollback receipt. Repeat until only source interpretation, causal reasoning, creative choice, direct perception, or human-sense judgment remains. Record why that core needs model capability that code cannot supply.

## Required human-study and human-work matrix

The matrix is required in this factory and every new or updated skill, for both audiences and both scopes. Its presence, explicit resource access, required use, independent operation and acceptance evidence are separate obligations. Each invocation uses its relevant selection in domain research, use-case framing, decisions and evaluation. A machine-facing result still retains this contract; justify non-use of a particular human evaluation from the actual outcome. Do not replace the full declared inventories with a fixed shortlist or call unresolved relationships inapplicable.

Start with the actual brief, artifact, activity, people, purpose, medium, setting, access needs, abilities, expertise, language, cultural context and time horizon. Separate producer capability from recipient need. Select the relevant outcomes: perception, understanding, learning, accomplishment, recovery, comfort, emotion, trust, originality or preference. Do not average unlike outcomes into a taste score, infer individual preferences from demographics, or collect sensitive attributes to fill a model.

Load assets/human-catalogs.json through `mise run human-matrix` for the exact source versions, URLs, digests, hierarchy counts, scope, attribution and reuse limits. OECD research fields, ISCO occupations, ICATUS everyday and unpaid activities, O*NET abilities and work context, and NIST AI contributions are complementary inventories. None certifies every mechanism, activity or future field. Retain absent definitions, unmapped items, overlaps and named extensions. Source-defined other categories do not establish knowledge of their unspecified members. Preserve captured labels and distinguish a missing definition from an inferred one.

Load references/human-matrix-format.md through `mise run human-matrix` before constructing or consuming a matrix. That reference owns resource inputs, schema fields, symbolic selection, canonical identity and enumeration budgets; this file owns required use and human evidence.

## From evidence to human outcomes

Use the matrix to frame an exact question about which property or choice could affect which outcome, for whom and under what conditions. Search neighboring and missing fields, relevant activities and counterevidence to challenge the first mapping. Extend disciplinary and activity discovery for the task. Include a field only when applicable evidence or a labeled hypothesis bears on a concrete outcome or choice. Preserve several valid creative directions.

Read relevant standards, reviews and original studies with their methods and limits. Record publication and revision dates, population, setting, task, medium, comparison, measures, effect and uncertainty when available, and access limits. Separate normative requirements, causal findings, associations, theories, domain practice and model inference. Translate each retained finding into a specific choice, constraint, input, test or review criterion; record the transfer reason, interactions and tradeoffs in existing domain and decision records. Individually supported choices do not establish a supported combined effect.

Assign each condition to an actual mechanical predicate, model assessment, human observation or authorized decision. Artifact measurements establish their named property under captured conditions. Research can support an expectation; model or expert review establishes that evaluator's assessment. None alone establishes the actual recipient's response or universal taste. Preserve conflicting findings, unsupported transfer and unavailable physical or sensory capabilities. A photograph cannot establish smell, taste, touch or physical performance. Synthetic respondents remain simulations.

Create, directly inspect and revise the actual artifact. Evaluate the intended outcome separately from perceived ease, popularity, fluency or satisfaction. Use domain criteria, defect examples, comparisons and multiple acceptable outcomes. For material human claims, distinguish craft review, preference and observed performance; use relevant participants and matched, blinded or counterbalanced comparisons when feasible, recording selection, exposure, order and sample limits. Calibrate claims that model judges predict human assessment against held-out or actual human evidence; inspect order, verbosity and shared-bias sensitivity. Agreement between model calls is not independent human confirmation.

Use the existing Mastra human-input and host-authority contract when an actual response, observation, expertise or permission is required, or a targeted authorized interaction best resolves material uncertainty. Prepare the concrete artifact and question before asking. Preserve authentic provenance, explicit decisions, current input binding, expiry and recovery. Continue eligible work while required input is pending. Do not fabricate participants, physical measurements, permissions, numerical confidence or demonstrated improvement. A missing required human or physical evaluation blocks only its dependent claim or action and remains incomplete.
