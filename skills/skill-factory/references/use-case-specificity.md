# Use-case specificity

Read this file before creating, updating, standardizing, or importing a skill, and for relevant human-outcome research during invocation. Return to the [SKILL.md body](../SKILL.md) through `mise run domain-research-policy` for governing ownership, dependencies and acceptance. The target is a reusable skill for one coherent task class, not prose that could survive a domain-name swap.

## Research basis

The [Agent Skills authoring guidance](https://agentskills.io/skill-creation/best-practices) says effective skills start from real expertise, project artifacts, real failures, corrections, and execution traces. It warns that generic model knowledge produces vague procedure and that excess detail can waste context. The [Agent Skills specification](https://agentskills.io/specification) keeps domain references and scripts loadable on demand so the always-loaded body can stay focused.

The [SKOS Recommendation](https://www.w3.org/TR/skos-reference/) separates concepts from preferred, alternate, hidden, broader, narrower, and related labels. The [PROV-O Recommendation](https://www.w3.org/TR/prov-o/) relates entities, activities, agents, derivation, attribution, and time. The [SHACL Recommendation](https://www.w3.org/TR/shacl/) separates machine-checkable shapes from the data being judged. The [NASA Systems Engineering Handbook](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) links stakeholder expectations, rationale, authority, verification, validation, state, function, and time. These sources support the domain map and trace rules below. None proves a target skill's private facts.

## Domain map

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

## Meaning and decision method

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Resolve vague meaning through the use-case and decision owners: establish outcome/context, competing readings and material facts; identify fixed, bounded and open choices; trace actors, objects, interfaces and state; assign capable checks and residual judgment; test falsifiers, failure and recovery; bind the decision and invalidate dependents.
- Use relevant requirement, design, causal, formal or experimental methods for their actual contribution.
- Test domain-name substitution and removal of domain terms.
- Finite cases do not prove universal uniqueness or deterministic judgment.
- For decision and creative dependencies, use [NASA decision analysis](https://www.nasa.gov/reference/6-8-decision-analysis/) for context, criteria, alternatives and uncertainty, [Double Diamond](https://www.designcouncil.org.uk/resources/the-double-diamond/) for exploration/testing/iteration, and [Stanford adaptable methods](https://dschool.stanford.edu/tools/design-thinking-bootleg) for revisiting framing, making and testing.
- Adapt relevant methods to actual uncertainty; none imposes a universal workflow or makes judgment deterministic.
- Ground applicable methods in [NASA requirements guidance](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/), [SEI quality scenarios](https://sei.cmu.edu/documents/5465/2013_018_101_60984.pdf), [Goal/Question/Metric](https://www.cs.umd.edu/users/basili/qip/tsld025.htm), [NIST statistical evaluation guidance](https://www.nist.gov/news-events/news/2026/02/new-report-expanding-ai-evaluation-toolbox-statistical-models) and [CheckList behavioral testing](https://aclanthology.org/2020.acl-main.442/).
- Bind adopted rules to supporting sources and label adaptations as inference; import no entire process or certification claim.
- Review definitions at creation and material changes; reuse valid definitions during ordinary invocations.
- Define units, ranges, tolerances, timing and workload where meaningful, using source requirements or measured baselines rather than invented numbers.
- Select relevant goal/questions/measures, glossaries/taxonomies, quality scenarios, task/lifecycle/state models, decision tables, invariants, interfaces/data flow/trust boundaries, failure/recovery/impact analysis, boundary/property/state-transition/metamorphic tests, conflicting evidence, causal comparisons and anchored design alternatives.
- Metamorphic checks compare expected behavior across changed inputs.
- Where generated inputs or action sequences help, consider supported [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) for [Python](https://docs.python.org/3/) or a verified language equivalent.
- Reuse existing dependencies; add no framework merely to fill this catalog.

## Research gate

Use every relevant available web research capability. Start with current first-party owners, standards, source repositories, schemas, API references, issue history, real failure reports, and execution evidence. Add independent research or practitioner evidence where it can confirm, bound, or challenge an owning claim. Local project sources remain authoritative for private project facts.

Register a question for every domain dimension before drafting. Retain at least four distinct current web sources across at least two hosts and two source classes. Record source URL, class, checked timestamp with timezone, supported claim, covered dimensions, limitation, and disposition in `assets/use-case-contract.json` through `mise run domain-research-policy`. A check timestamp older than 31 days is stale, and a future timestamp fails. Search for counterevidence to the strongest retained claim and record how it changed or bounded the package.

Run `mise run domain-research-policy` before accepting any domain map. The task proves receipt shape, diversity, current access time, and coverage. It cannot prove that a source supports the recorded claim. Read each source and make that judgment directly. If current web evidence is unavailable or external access is prohibited, mark affected domain claims `BLOCKED`; do not fill them from plausible memory.

## Study and work inventories

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Start with complete applicable [OECD research fields](https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/frascati-manual-2015_g1g57dcb/9789264239012-en.pdf), [ILO occupations](https://isco.ilo.org/en/isco-08/), [UN everyday activities](https://unstats.un.org/unsd/demographic-social/time-use/icatus-2016/), [O*NET concepts](https://www.onetcenter.org/content.html), [versioned O*NET data](https://www.onetcenter.org/database.html) and [NIST human-centered AI uses](https://www.nist.gov/publications/ai-use-taxonomy-human-centered-approach).
- Preserve overlap, unmapped/other categories, interdisciplinary and emerging work.
- No taxonomy proves all human mechanisms or future work; occupational populations do not predict individuals.
- Paid occupations do not cover all work; current-resolving identifiers are not immutable snapshots.

## Domain discovery and human outcomes

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Through `mise run domain-research-policy`, use the [domain guidance](use-case-specificity.md) to discover relevant sensory, physiological, cognitive, learning, emotional, social, ergonomic, accessibility, linguistic, cultural, economic, organizational, artistic, ethical, historical and physical/material fields.
- Consider research, teaching, communication, creation, planning, coordination, engineering, making, repair, care, service, culinary, civic, domestic and recreational work.
- These guide discovery, not compulsory activation.
- Establish actual people, task, medium, setting, needs, expertise, language, culture and time horizon without inferring preferences from demographics or collecting needless sensitive data.
- Distinguish producer capability from recipient perception, comprehension, decision, task success, learning, comfort, aesthetics, emotion, trust, originality and longer-term effects.

## Selection and relationship representation

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Represent arbitrary finite unordered selections, ordered sequences, repetition, grouping and higher-order interactions across study concepts, work, people/context, outcomes, choices, constraints, evidence and judgments without materializing cross-products.
- Preserve every member's addressability, source version, selector, conditions and execution bounds.
- Keep exact, alias, broader/narrower, related and approximate mappings distinct using [SKOS](https://www.w3.org/TR/skos-reference/); no RDF service is required.
- Reproduce parsing, resolution, filtering, serialization and enumeration with explicit comparators, locale and versions.
- Canonicalize only semantically unordered structures.
- Use standard combinatorial iterators and lazy records; avoid model calls per cell.
- Measure input-pool memory as well as output size.
- Representation does not establish usefulness, truth, permission or tested coverage.

## Research-informed design choices

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Use selections to make actual design choices.
- Map the brief and challenge its first categories.
- Ask the exact property-to-human-outcome question, label proposed mechanisms as hypotheses, inspect relevant standards/reviews/original studies and counterevidence, and connect each finding to a choice and transfer rationale.
- Retain dates, population, setting, task, medium, comparisons, measures, effects, uncertainty and access limits.
- Distinguish standards, causation, association, theory, practice and inference.
- Assign capable checks and model/human duties; inspect and revise the actual artifact.
- Refresh material gaps and changed selections without loading every global cell into every context.
- Freshness is not relevance; separately supported choices do not prove their combined effect.

## Human-evidence judgment

Use `mise run domain-research-policy` and the actual domain workflow for this required method.

- Keep mechanical checks, research, model assessment, authentic human evidence and physical observations separate.
- Predeclare suitable comparisons, participants, order, sample, measures and uncertainty when human proof is required; invent no universal sample size.
- Calibrate evaluators against known good/bad and held-out or independent cases.
- Model judges need relevant held-out or authentic human comparisons before claims to predict human evaluation.
- Test presentation order, verbosity, shared model biases and changed context; agreement among model calls is not independent human confirmation.
- Investigate disagreement, sensitivity, novelty and diversity separately.
- Permission, preferences, craft review, subjective comparison and observed performance answer different questions.
- Research supports bounded transfer, not guaranteed appreciation or measured improvement here.
- Ease may differ from learning; productive practice may serve the outcome.
- One story experiment cannot establish general creative uplift.
- More agents, reviewers or checkpoints do not prove better collaboration.
- Missing required evidence remains pending.
- Optional unavailable studies permit only narrower truthful claims.
- Through `mise run domain-research-policy`, read the [human evidence examples](#human-evidence-examples) for their relevant methods, populations, transfer limits and links before using their claims.
- Where feasible for the question, use matched, blinded or counterbalanced comparisons; record unavoidable order/exposure effects and sample, selection and subgroup limits without profiling people.

## Human evidence examples

Use these source examples through `mise run domain-research-policy` when evaluating relevant human outcomes. Read the actual sources and preserve their scope, uncertainty and transfer limits; these examples do not prove this skill produces the reported effect.

- [NASA's human-performance guidance](https://www.nasa.gov/reference/5-0-human-performance-and-error-vol-2/) connects visual, auditory, sensorimotor, and cognitive capabilities to task performance, workload, legibility, and recovery. Its spaceflight-specific thresholds require domain justification before reuse. The useful pattern is capability plus task plus conditions plus outcome.
- [W3C's explanation of contrast requirements](https://www.w3.org/WAI/WCAG22/Understanding/contrast-enhanced.html) gives a concrete connection between visual capability and a measurable display property. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [W3C's evaluation-tool guidance](https://www.w3.org/WAI/test-evaluate/tools/selecting/) also show why automated checks cover only part of accessibility. Inspect actual states, content, interactions, and required human evidence.
- [NIDCD's account of flavor perception](https://www.nidcd.nih.gov/health/taste-disorders) connects taste, smell, temperature, texture, and chemical sensation. For a culinary or material skill, inspect the relevant physical inputs and available measurements; a model viewing a photograph has not smelled, tasted, touched, or physically tested the result.
- [Deslauriers and colleagues' classroom experiment](https://www.pnas.org/doi/10.1073/pnas.1821936116) found a difference between actual learning and perceived learning in its introductory physics setting. Measure the intended learning outcome; do not remove useful practice or challenge merely because an artifact feels easier.
- [Liang and colleagues' 2026 neuroaesthetics study](https://www.nature.com/articles/s41467-026-73153-6) relates shared evaluations of traditional Chinese paintings to separable neural patterns and art expertise, within its sample and stimuli. [Poldrack's analysis of reverse inference](https://brainmapping.org/NITP/PNA/Readings/Poldrack2006.pdf) explains why brain-region activation alone does not prove a particular mental experience. Neither source supplies a universal formula for beauty, a neurochemical quality score, or evidence about an unseen person's response.
- [Doshi and Hauser's creative-writing experiment](https://www.science.org/doi/10.1126/sciadv.adn5290) found improved individual story ratings alongside greater similarity among AI-assisted stories. Preserve useful novelty and diversity as well as local quality. Do not generalize a short-story experiment to every creative profession.
- [Vaccaro and colleagues' human-AI meta-analysis](https://www.nature.com/articles/s41562-024-02024-1) found that combining humans and AI did not reliably outperform the higher-performing component, with variation by task. Assign roles and test the collaboration; more reviewers, models, or checkpoints do not automatically improve the result.
- [Ashokkumar and colleagues' 2026 experiment-prediction study](https://www.nature.com/articles/s41586-026-10742-x) provides evidence that models can forecast treatment effects in the studied social-science experiments, while reporting effect-size overestimation and weaker results in another archive. [Wang and colleagues' identity-representation study](https://www.nature.com/articles/s42256-025-00986-z) documents limits in simulated populations. Model-based forecasting may guide investigation when calibrated for its setting; synthetic respondents never become actual human participants.

These are examples of a method to test. Research grants no diagnosis, biological intervention, behavioral manipulation, surveillance or new data-collection authority. Follow the actual task permissions and safeguards.

## Human input and review

Choose the human method from the unresolved question and the evidence needed. Bring a human in when mandatory, and also when a targeted interaction is the best authorized way to resolve a material uncertainty or improve the outcome. Do not wait until every possible source has been searched. Use existing answers and approvals while they remain applicable; do not ask people to redo available mechanical work.

Before a relevant human interaction, read the entire [human-input protocol](eval-authoring.md#human-input-and-review) through `mise run domain-research-policy` and the actual domain workflow. Apply every gate and proof limit there.
