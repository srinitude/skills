---
name: would-agents-actually
description: 'Use when a claim depends on an agent taking a real action.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Would Agents Actually?

Produce an evidence-backed verdict about whether a pinned agent system will perform or avoid a defined action under declared tasks, tools, policies, budgets, and trials. Separate what the system says, what the trace records, and what the environment proves.

## Command grammar

- `/would-agents-actually help`: show the contract, verdict labels, and required system pin without researching.
- `/would-agents-actually verdict <agent-action question>`: research the claim, run or inspect the required action evidence, issue the supported verdict, and validate the artifact.

## Procedure

1. Define the action as `[a]`. Name the opportunity or trigger, pinned system, observable action or abstention, task distribution, environment, window, budgets, real friction, comparator, and independent readback. Ask one question only when an unknown changes the evidence plan. Otherwise state the assumption.
2. Pin the model identifier and version, provider route, prompts, runtime, planner, router, verifier, retries, fallbacks, tools, schemas, permissions, approval gates, memory, context, checkpoints, environment, dependencies, task sampling, and budgets. A material change creates a new system stratum.
3. Write support, contradiction, and insufficient-evidence conditions before research or trials. Keep target outcomes, target traces, matched analogs, component checks, mechanism evidence, and inference separate. When current reports or fast-changing runtime behavior matters, load [recent-public-signal.md](references/recent-public-signal.md).
4. Verify every load-bearing source at its primary record. Complete the source and trace cards in [verdict-protocol.md](references/verdict-protocol.md). Require two independent teams, task sets, or datasets for every premise needed by the verdict or confidence. Shared tasks, runs, graders, and restatements count once.
5. Count an external action only after independent environment readback. A plan, final claim, tool-call attempt, accepted request, or long trace is not outcome proof. Keep model-caused and infrastructure-caused diagnostics separate while retaining both in the operational verdict.
6. Define the reference class before reading results. Match action, tasks, horizon, tools, permissions, state, runtime, model version, environment, graders, budgets, failures, threat conditions, and time. Do not transport a score by model name alone.
7. Load [frameworks.md](references/frameworks.md) after evidence collection to diagnose opportunity, selection, attempt, receipt, state, constraints, verification, stopping, repeatability, and transport. Keep capability, propensity, reliability, compliance, resilience, abstention, and operational fit separate.
8. Choose `LIKELY`, `UNLIKELY`, `UNCERTAIN`, or `INSUFFICIENT EVIDENCE` under [verdict-protocol.md](references/verdict-protocol.md). If live research is unavailable or forbidden, use `UNVALIDATED HYPOTHESIS`. Never invent a run, trace, tool call, state change, grader result, rate, cost, quote, source, or URL.
9. Design the smallest production-like test with the least authority. Prespecify representative tasks, holdout, trials, denominator, comparator, graders, budgets, permissions, faults, stop rules, readback, rollback, cleanup, and the decision changed. Use approved or synthetic data and fake or reversible side effects.
10. Render the result with [output-template.md](references/output-template.md), save it outside the installed skill, then run `python3 scripts/validate_verdict.py --input <verdict.md>`. Exit 0 proves the artifact has the required shape. Exit 1 means it is incomplete. Exit 2 means the command or input path is wrong.
11. Append queries, sources, system pins, task identity, excluded runs, failures, readback, assumptions, and validation output to an external research log after each consequential step. Stop and report the missing item when a load-bearing source, permission, readback, or safety control cannot be verified.

## Load conditions

- Load [evidence-base.md](references/evidence-base.md) when benchmark, trial, grader, or transport evidence may inform the analysis, then recheck every primary source before use.
- Load [verdict-template.md](assets/verdict-template.md) when creating a verdict. Copy it outside `assets/`; do not edit the installed template.
- Load [help.md](examples/help.md) for the help command, [verdict-insufficient-evidence.md](examples/verdict-insufficient-evidence.md) for a researched verdict, and [failure-unvalidated.md](examples/failure-unvalidated.md) when the system pin or live research is missing.
- Run [validate_verdict.py](scripts/validate_verdict.py) after writing the artifact. Read [test_validate_verdict.py](scripts/tests/test_validate_verdict.py) only when changing the validator contract.
- Read [contract.md](evals/contract.md) before changing behavior, trigger boundaries, or evaluation cases.
- Load [generation-contract.md](references/generation-contract.md) only when maintaining or repackaging this skill.

## Gotchas

- A successful component check does not prove the full action.
- `pass@k`, `pass^k`, single-run success, action propensity, and deployment reliability answer different questions.
- An outcome grader, trace grader, constraint grader, and infrastructure grader cannot replace one another.
- Do not remove setup, dependency, transport, timeout, permission, or rate-limit failures from an operational denominator without reporting both views.
- Never add credentials, payment power, destructive access, or broad permissions merely to make a test realistic.
- In a sensitive domain, judge the defined action only. Do not infer overall safety, efficacy, legality, entitlement, authorization, compliance, or permission to act.

## Completion criteria

- `[a]` pins the system, action, opportunity, tasks, window, costs, comparator, and readback.
- Every load-bearing premise passes the independence gate.
- Outcome, trace, constraints, grader validity, infrastructure, cost, and transport remain separate.
- Trials, eligible denominator, dropped runs, uncertainty, and task concentration are visible.
- Confidence is capped by the weakest premise, grader, independence check, and transport bridge.
- The next test uses least privilege, budgets, stop rules, readback, rollback, and cleanup.
- Every load-bearing source has a visible URL.
- The validator prints `"status": "PASS"` and exits 0.
