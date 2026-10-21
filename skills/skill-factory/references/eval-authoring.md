# Eval authoring

Evals prove a skill helps. Load each skill's files under evals/ through `mise run evals`.

Return to the [SKILL.md evaluation contract](../SKILL.md#evals). Before defining, changing or running evaluation, read this entire owner through `mise run evals` and the actual case runner. All applicable source cases, conditions and proof remain mandatory; schema validation is only one prerequisite.

## Freeze the evaluation boundary

- Freeze source requirements, expected outcomes, allowed variation, falsifiers, fixtures, evaluators, failure/recovery and comparison boundaries before implementation.
- Specify expected checker decisions independently of the implementation.
- Every substantive parent and applicable component remains required even if a checklist omits it.
- Use isolated real packages and authorized test credentials; preserve unrelated state.
- Exercise actual public paths and final consumers with available authorized models, including less capable models where available, repeated fresh contexts and matched with/without-skill baselines.
- Record real identities and sample limits privately.
- Distinguish one pass, retry-selected success and all-observed reliability.
- Declare model capability needs and retain tool/model versions, failures, variation, repetitions, uncertainty and trial-independence limits.
- Measure within each case and across cases; best-of-many success is not reliability.
- Use held-out cases and domain calibration where available; avoid sole self-report grading.
- Stable scoring code does not make model judgment deterministic.
- Add statistical infrastructure only when the evidence question needs it.

## Behavior cases

The shape:

    {
      "skill_name": "csv-cleaner",
      "evals": [
        {
          "id": 1,
          "prompt": "clean up sales_2025.csv, some emails are missing",
          "expected_output": "A cleaned file plus a count of rows fixed.",
          "assertions": ["The reply states how many emails were missing."],
          "files": ["sales_2025.csv"]
        }
      ]
    }

At least four cases. Prompts read like real requests: file paths, column names, casual phrasing, an occasional typo. Cover at least one edge, such as malformed input or a request the skill must refuse. Load input files under evals/files/ through `mise run evals` and list them per case.

Assertions are verifiable statements. "The output file is valid JSON" and "the report holds at least 3 recommendations" work; "the output is good" does not. Grade against quoted evidence, and mark a section header with no substance as a fail. Leave taste and style to human review instead of assertions.

## Trigger queries

A list of entries shaped {"query": "...", "should_trigger": true}. The checker enforces a floor of 4 with both labels present, and the shipping bar is about 20, half positive and half negative. Treat the floor as the schema minimum, never as the target. The strongest negatives are near misses: queries that share keywords with the skill yet need something different. Realism helps, so include paths, personal context, and abbreviations.

## What does the srinitude registry add?

A skill destined for the srinitude/skills registry loads the registry artifact set under evals/ through `mise run evals`: manifest.json names run inputs, cases.json holds graded behavior cases, trigger-cases.json holds trigger prompts, contract.md freezes regression, rubric.md guides the judge, speed-budgets.json caps timing, and source-lineage.json records real source hashes and the public version.

## Rejection and recovery

- Test omitted source clauses/conditions, weakened outputs, stale identical copies, wrong bindings, changed reviewed bytes, false non-use, bypassed prerequisites, ignored resources, swallowed failures, stale caches, failing outputs hidden by factory passes, forged/wrong-target/duplicate/expired/replayed human input, changed thresholds and simulated evidence.
- Inspect actual non-effects, preserved state and process status, then restore legitimate prerequisites and observe successful recovery.
- Keep atomicity/isolation and host-perimeter limits explicit.
- Exercise missing links, undefined labels, wrong anchors, renamed files, root-relative versus file-relative paths, external redirects/failures, private paths, wrong versions and reachable but irrelevant sources through the actual reference consumers.
- Validate native task schemas with `mise tasks validate --json`, assessing material warnings despite a zero exit.
- For adopted caches test misses, hits, invalidation, missing outputs, failed-run reruns and fresh uncached evidence.
- Include actual crash after effect but before checkpoint, restart/storage failure/concurrent resume and preserved unrelated state.
- Read-only conventions cannot substitute for non-effect observation.

## Required case coverage

Use `mise run evals` and the actual case runner for all cases in this section.

- Exercise all source families together and separately: scope/audience and legacy/changed acceptance; domain meaning/tool choice; ownership/handoffs; prerequisite readiness, selected intermediates, creativity and invalidation; actual source/resource use; matrix integrity, exact counts/round trips, order/repetition/grouping/higher-order context and resource bounds; research transfer and human claims; companion composition/failure; [Mastra](https://mastra.ai/docs/workflows/overview) schemas/status/branching/suspension/replay/privacy/dynamic/schedule behavior; human gates; A/B/C; unfamiliar languages and wrong APIs/versions/configurations; variants/customization; recipient usefulness and WorkSlop.
- Report interaction strength, omitted combinations and sampling.
- Pairwise tests cannot replace required higher-order or exhaustive proof.
- Include complete deterministic, variable/creative and exploration-led worked traces.
- Include a visual artifact using perception/cognition, a learning/explanatory artifact separating understanding from apparent ease, and a creative audio, narrative, physical or multisensory artifact with several valid outcomes.
- One case combines multiple study fields and activities; one depends on order or repeated practice.
- Include unfamiliar work, contradictory findings, missing physical capability and an irrelevant proposed field.
- These cases do not limit the supported domain.
- For larger finite spaces, justify interaction and sequence coverage using [NIST combinatorial coverage](https://www.nist.gov/publications/combinatorial-coverage-measurement) and [event-sequence methods](https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/event-sequence-testing).
- Include changed-meaning and meaning-preserving inputs at word, phrase, sentence, paragraph and mixed-document levels; validate test labels and grader decisions on valid, broken and borderline outputs.
- Exercise instructions embedded in untrusted examples/tool results and passed mechanics with failed domain outcomes.
- Every required source test remains independently required; the initial ledger retains their complete conditions and the public case runner must bind each to actual evidence.
- Test independent creation/update and invocation of deterministic, creative and applicable service/credential skills, with both scope variants and full Mastra capability; a scaffold or signed package cannot satisfy that end-to-end proof.

## Anti-pattern evaluation

- Review wrong goals/audiences, speculative abstraction, incomplete simplicity, ceremonial tools, lost determinism/creativity, competing ownership, hidden context, stale/leaked state, masked failures, misleading speed, proxy proof, false human evidence, broken maintenance and difficult language.
- For each applicable pattern record trigger, temptation, violated rule, observable failure, smallest compliant alternative, owner, detection and positive/negative examples.
- Distinguish violations from review signals; preserve justified abstractions, caches, parallelism, documentation, human review and mandatory methods.
- Observe actual agent choices and usable results.
- Extend this inventory from real domain failures and adversarial cases; it is a coverage floor, not every possible defect.
- Use [specification-gaming examples](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/), [ML system technical-debt research](https://papers.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf) and [behavior-focused testing guidance](https://abseil.io/resources/swe-book/html/ch12.html) as candidate failure mechanisms, reconciled with repository methods rather than automatic evidence of a local defect.
- Give each pattern a stable ID and context, apply compliant defaults/interfaces/templates/evals, and keep prohibited examples clearly labeled outside executable production paths.
- Test legitimate counterexamples and actual agent choices across affected operations; measure false positives, missed violations and limits.
- Repair the smallest confirmed owner and propagate, retaining one catalog owner instead of copying an encyclopedia into every body.

## Outcome and resource measurement

- Measure accepted end-to-end factory invocation, creation/update, output invocation and maintenance separately, including cold/warm discovery, full reads, transport, work, waits, retries, recovery, verification and recipient effort.
- Record time, tokens, compute/memory/storage/network, processes/concurrency, accelerators, money and attention or justified non-use.
- Investigate variance and evaluator disagreement; microbenchmarks do not prove whole-result savings.
- Freeze fresh baselines and repeat matched cold/warm runs with the same inputs, environments, runners and acceptance criteria.
- Report phase/total elapsed time, human effort and actual input/output tokens separately, with available cached/reasoning counters; label estimates and missing counters.
- Include recipient clarification, repair, coordination and successful use.
- Separate external waits; never double-count concurrent work or label necessary review and creative iteration waste.
- Record task selection, incomplete trials, model changes and concurrency bias.
- Use existing Mise measurement, resource, experiment and speed-budget mechanisms; derive budgets from evidence.
- Test small, typical and larger supported workloads, resource/token growth and generation cost versus later savings.
- Optimize the measured critical path without protected regressions; report tradeoffs and keep the verified baseline when no further gain is proved.

## Human input and review

Before a relevant human interaction, load this protocol through `mise run domain-research-policy` and the actual domain workflow. Return to the [SKILL.md human-input owner](../SKILL.md#mise-task-graph) for the core gate.

Apply this protocol in the factory and every generated or updated skill whenever the test or task benefits materially from actual human input. Research coverage, a model's ability, and a populated study/work catalog cannot supply a person's unexpressed preference, lived experience, real task behavior, authority, or physical observation.

Choose the human method through the [research owner](use-case-specificity.md#human-input-and-review) before this protocol.

| Question or test | Suitable contribution | Evidence boundary |
| --- | --- | --- |
| Missing intent, preference, or creative direction | A concise question or comparison for the person who owns that choice. | Establishes that person's stated choice, not a population preference. |
| Usability, accessibility, comprehension, or learning | Relevant people attempt realistic tasks with the actual artifact or an identified prototype. | Observe behavior and errors; satisfaction alone does not prove performance or learning. |
| Craft, interpretation, or domain suitability | A suitably qualified reviewer inspects the artifact using domain criteria and examples. | Establishes the review and its reasons, not every recipient's reaction. |
| Subjective experience or comparative appeal | Participants from the declared audience compare or experience candidates under a stated protocol. | Preserve variation and disagreement; the sample and context bound the conclusion. |
| Physical or sensory performance | An authorized person or instrument performs the measurement or observation the model cannot. | Record actual conditions and calibration; a simulation remains a simulation. |
| Permission for a consequential action | The authorized decision-maker reviews the concrete action and its effects. | Permission is not quality evidence, and quality feedback is not permission. |

Adapt [W3C's guidance on involving actual users](https://www.w3.org/WAI/test-evaluate/involving-users/) and [GOV.UK's task-based usability-testing guidance](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing) to the relevant domain. Select realistic, non-leading tasks, participants selected for the stated question and intended population, accessible review materials, and the smallest study that answers the question. Match any sample-size or statistical claim to the required sensitivity and available evidence. Do not copy a universal participant count or mistake one person's approval for broad validation. Human input itself can be incomplete or biased; preserve required domain and mechanical checks.

Use [Mastra's human-input workflow guidance](https://github.com/mastra-ai/mastra/blob/c19a93b0956f957581931786645d0597efec41eb/docs/src/content/en/docs/workflows/human-in-the-loop.mdx), [suspend/resume implementation guidance](https://github.com/mastra-ai/mastra/blob/c19a93b0956f957581931786645d0597efec41eb/docs/src/content/en/docs/workflows/suspend-and-resume.mdx), and [snapshot documentation](https://github.com/mastra-ai/mastra/blob/c19a93b0956f957581931786645d0597efec41eb/docs/src/content/en/docs/workflows/snapshots.mdx), verified against the chosen stable release. Map their supported features to the following behavior:

1. **Prepare the decision.** Complete the authorized research, artifact preparation, and mechanical checks that make the request concrete. Show the exact artifact, relevant alternatives, question, criteria, remaining uncertainty, and effect of each decision in plain language. Ask missing prerequisites before their dependent work; request final approval only after its reviewable preparation. Keep implementation identifiers out of the person's flow unless they help the decision.
2. **Define the pause.** Use the existing contract to identify clarification, creative feedback, expert review, participant observation, approval, rejection, or revision. Bind it to the workflow/run, exact step or nested path, iteration where applicable, artifact and input revision, decision owner, and the data required to continue. Use `suspendSchema` and `resumeSchema` plus the actual runtime and domain validators. Treat human-facing labels separately from machine identifiers.
3. **Suspend before the dependent action.** Return from the step after `suspend()`. At the inspected [step-handler source](https://github.com/mastra-ai/mastra/blob/c19a93b0956f957581931786645d0597efec41eb/packages/core/src/workflows/handlers/step.ts), suspension records state and resolves; it does not by itself prevent the remaining JavaScript from executing. Return from rejection paths using `bail()` as well. A resumed step runs again, so keep preparation outside the gate where possible and make any repeated operation safe. Select workflow-level versus tool-level approval according to where the first protected effect occurs, as described in [Mastra's approval-placement guidance](https://mastra.ai/blog/hitl-where-to-put-approval-in-agents-and-workflows). A pause after that effect is too late.
4. **Expose the request through the supported host.** Use the existing authorized UI, input tool, app, or interface and its verified integration binding. Mastra owns workflow state; the host owns identity, communication, and permission enforcement. Do not assume a stored `approver` string authenticates a person. Do not install an approval platform, contact participants, record sessions, or transmit private artifacts without the necessary authorization.
5. **Wait without pretending to finish.** Preserve the review context in the declared storage, with access controls and minimal sensitive content. Use references to versioned artifacts instead of copying large or private material into every snapshot. Choose storage and host lifetime that actually survive the required wait. Keep eligible independent work moving where the selected engine supports it. Avoid model polling, duplicate requests, or a sleeping process represented as durable scheduling. Silence, elapsed time, a notification, and a selected default are never an answer or approval.
6. **Validate and route the response.** Check its provenance, expected reviewer where required, schema, actual meaning, run/step/iteration target, artifact revision, and current authority. Use explicit accept, reject, revise, clarify, and still-pending outcomes as applicable. An explicit rejection must not enter a repeated approval loop. Separate human response data from instructions that could expand scope or bypass safeguards.
7. **Resume the right work.** Resume the existing run and correct suspended path with validated data. Handle repeated human interactions, nested workflows, and concurrent item reviews using the release's supported identifiers, labels, and iteration handling. Serialize conflicting updates. Reject duplicates, stale replies, replayed decisions, wrong targets, and unauthorized responses; verify the selected storage/engine's actual concurrency guarantees.
8. **Reconcile changes and finish the test.** A revision changes only its authorized owners and invalidates affected artifacts, evidence, dependent work, and approvals. Preserve intentional customizations and unaffected work. Recheck changed inputs, resources, permissions, and required gates before the protected effect. A rejected or bailed run is not an accepted domain outcome even if an engine reports a normal completion status. Record the final artifact, actual human contribution, resulting adaptation, validation, and remaining limits.

Handle cancellation, unavailable reviewers, conflicting feedback, expiry, process restart, storage failure, and a deadline reached without an answer. Give each a truthful state and an authorized recovery route. Block only what depends on required missing input. If a proposed optional study cannot run, retain the narrower supported claim and disclose the gap; do not silently waive required acceptance evidence or manufacture a favorable response.

Use existing experiment and decision records to compare the literature/model-only baseline with the human-informed revision when claiming that the intervention improved the skill. Preserve the original test conditions or explain the change. Check for new regressions and recipient burden. Incorporate useful feedback into the current artifact and, when skill maintenance is authorized, its smallest owning rule or eval. One invocation's feedback must not silently rewrite the installed skill, its source, other variants, user preferences, or durable memory.

## How do I run them?

`mise run evals` validates both files: schema, unique ids, listed input files, both trigger labels present.

To measure behavior, run each case twice in fresh contexts, once with the skill installed and once without, and grade every assertion with evidence. For triggering, run each query about three times and use a 0.5 trigger rate threshold. When tuning a description, keep a train and a validation split, change the description only from train failures, and stop after about five rounds or when gains stall.
