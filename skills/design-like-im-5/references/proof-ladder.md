# Proof ladder

Parent and backlink: [SKILL.md](../SKILL.md), Eval owner map.

Read this file before a skill eval. Use the rungs in their fixed order.

## One proof rule

- Each rung proves one bounded claim and names what it cannot prove.
- Do not carry a pass past its stated scope. Expand the test when its trigger fires.
- Use this fixed order: atomic, mutation, metamorphic, judgment pilot, combinatorial, representative, then whole skill.

## Packet shape

- Give each action one packet. Put the goal and current inputs first.
- Name every path, fixed rule, proof need, success rule, output shape, and stop.
- Include one passing example and one failed example. Missing packet fields block the action.
- Use tasks for counts, order, links, pairs, fields, and fixed comparisons. Keep product judgment in review records.

## Repeatability

- Run each pilot twice from clean context with the same fixture.
- Compare action order, context use, proof classes, vetoes, and status. Any clash makes the result stale.
- Allow wording to change, more valid options to appear, and a safe creative direction to change.
- Do not require copied prose or one fixed design answer.

## Small pilots

- Start with the five seeded scenes in [pilot-cases.json](../evals/pilot-cases.json).
- Give each one-fault scene eye, brain, and touch review.
- Require a current render for the overlap scene and a live trace for the motion scene.
- Require the named state and input proof for every other scene. Do not replace missing proof with a guess.

## Pair coverage

- The eight rows cover every value pair across six binary factors.
- This controls test count while checking all two-factor links. It does not cover every higher link.
- Escalate high-risk or failed links to three-way coverage or full scope.

## Representative work

- Use typical, edge, and adverse cases. Hold some cases back from edits.
- Expand when a held case adds a veto, state kind, or failure class.
- Use full scope for small products when it is practical.

## Source record

All sources below were checked on 2026-08-30.

- [Agent Skills evals](https://agentskills.io/skill-creation/evaluating-skills) support small real cases, fixed checks, and human review.
- [Agent Skills scripts](https://agentskills.io/skill-creation/using-scripts) support tested tools with no prompts and fixed output.
- [OpenAI evals](https://developers.openai.com/api/docs/guides/evaluation-best-practices) support scoped tests, usual cases, edge cases, and human checks.
- [OpenAI task guide](https://developers.openai.com/api/docs/guides/latest-model) supports short prompts, exact proof, fixed output, and clear stops.
- [Anthropic agent guide](https://www.anthropic.com/engineering/building-effective-agents) supports fixed chains, step gates, clear tools, and checked feedback.
- [Two-stage study](https://research.google/blog/small-models-big-results-achieving-superior-intent-extraction-through-decomposition/) supports small steps and outputs shaped like examples.
- [Task breakdown study](https://arxiv.org/abs/2205.10625) supports solving clear small tasks in order.
- [Context study](https://aclanthology.org/2024.tacl-1.9/) supports short packets and putting facts near their use.
- [Program-backed study](https://arxiv.org/abs/2211.10435) supports moving exact work into a check that can run.
- [Example format study](https://arxiv.org/abs/2202.12837) supports examples that fix input kind, labels, and output form.
- [NIST pair testing](https://www.nist.gov/programs-projects/combinatorial-testing) supports bounded pair checks with clear scope limits.
- [W3C atomic rules](https://www.w3.org/TR/act-rules-format-1.1/) support small rules with exact use, checks, and results.
- [W3C sample method](https://www.w3.org/TR/WCAG-EM/) supports scope, samples, full checks, and reports.
- [Metamorphic test paper](https://arxiv.org/abs/2007.07808) supports tests made from a known test when no full answer exists.
- [Mutation test study](https://research.google/pubs/mutation-testing-at-scale-experience-at-google/) supports seeded faults that prove a test can fail.
- [Playwright image checks](https://playwright.dev/docs/test-snapshots) support stable image baselines in one fixed place.

These sources guide the ladder. They do not prove this package passes.
