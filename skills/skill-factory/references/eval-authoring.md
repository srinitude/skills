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

## How do I run them?

`mise run evals` validates both files: schema, unique ids, listed input files, both trigger labels present.

To measure behavior, run each case twice in fresh contexts, once with the skill installed and once without, and grade every assertion with evidence. For triggering, run each query about three times and use a 0.5 trigger rate threshold. When tuning a description, keep a train and a validation split, change the description only from train failures, and stop after about five rounds or when gains stall.
