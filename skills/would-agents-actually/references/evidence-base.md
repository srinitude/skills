# Evidence base

This ledger supports the method. It does not provide a target system's base rate. Recheck every load-bearing claim and magnitude at the live primary source before use.

## Claim rules

- A load-bearing claim needs two independent teams, task sets, or datasets.
- A result stays bound to its model version, runtime, tools, tasks, graders, budget, and date.
- Two papers using one benchmark or run set do not become independent by citing each other.
- External state is stronger than a completion claim.
- Outcome, process, constraints, infrastructure, and efficiency answer different questions.

## The evaluated unit is the full system

Cost-aware agent evaluation research shows that downstream runtime choices and costs can change comparisons. Pin the model, prompts, runtime, tools, permissions, state, environment, budgets, and versions. No source supplies a universal gain from adding orchestration.

- [Cost-aware agent evaluation paper](https://arxiv.org/abs/2407.01502)
- [Agent evaluation survey](https://arxiv.org/abs/2308.03688)

## External state and process evidence

State-based tool interaction studies grade environment state and policy constraints, while web and desktop studies use execution-based outcomes. These sources support independent state readback and separate process checks, but each environment covers only its declared tasks and access rules.

- [State-based tool interaction study](https://arxiv.org/abs/2406.12045)
- [Execution-based web task study](https://arxiv.org/abs/2307.13854)
- [Open-ended computer task study](https://arxiv.org/abs/2404.07972)

## Reliability needs repeated trials

Repeated-interaction research distinguishes average success from consistent success across trials. Report tasks, trials, eligible denominator, reset rules, uncertainty, and failure concentration. No source defines one correct trial count or threshold for every action.

- [Repeated tool interaction study](https://arxiv.org/abs/2406.12045)
- [Sequential decision evaluation study](https://arxiv.org/abs/2406.12045)

These two labels point to one dataset and count once. A second independent task set is still required for a load-bearing reliability premise.

## Capability, reliability, and security differ

Utility and defined unsafe-action outcomes should be measured separately under a stated threat model. A capability score, one success, or best-of-k result cannot establish single-run reliability or overall security.

- [Dynamic tool-environment security study](https://arxiv.org/abs/2406.13352)
- [Risk-management profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

## Transport must be argued

Research on agent evaluation identifies cost omission, runtime coupling, shortcuts, overfitting, and reproducibility risks. Long-task studies also limit findings to their curated task distributions. Audit task, horizon, runtime, tools, graders, budgets, cost, leakage, environment, and release date before transport.

- [Cost-aware evaluation paper](https://arxiv.org/abs/2407.01502)
- [Task-horizon study](https://arxiv.org/abs/2503.14499)
- [Evaluation survey](https://arxiv.org/abs/2308.03688)

## Required capabilities must match `[a]`

Evidence must exercise the modalities, tools, permissions, and environment required by the target action. Generic language-task scores do not establish tool or environment behavior.

- [General assistant task study](https://arxiv.org/abs/2311.12983)
- [Computer environment task study](https://arxiv.org/abs/2404.07972)

## Complexity, retries, and extra workers are interventions

Compare a more complex runtime with a simpler baseline on outcome, constraints, cost, latency, and failure. Retries, fallbacks, and extra workers alter both capability and budget. Current prices and system behavior age quickly.

- [Cost-aware agent evaluation paper](https://arxiv.org/abs/2407.01502)
- [Multi-agent scaling study](https://arxiv.org/abs/2402.05120)

## Foundation limit

These sources define method and known evaluation problems. They do not prove that a target system will perform `[a]`. Every verdict still needs live inspection, a pinned system, matched tasks, visible failures, fit graders, and independent readback.
