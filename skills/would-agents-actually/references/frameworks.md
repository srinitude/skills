# Agent behavior frameworks

Use these frameworks to define and diagnose `[a]`. They do not supply a success rate.

## Define `[a]`

> Under `[opportunity or trigger]`, will `[pinned agent system]` perform or avoid `[observable action]` on `[task distribution and environment]` within `[window and budgets]`, despite `[tool, cost, permission, and reversal friction]`, compared with `[alternative]`, as verified by `[independent readback]`?

Pin the model identifier and version, provider route, sampling, system and task prompts, planner, router, verifier, retries, fallbacks, tools, schemas, credential class, permissions, approval gates, memory, retrieval, context, checkpoints, environment, dependencies, task sampling, token and time budgets, call and spend caps, concurrency, human handoffs, stop rules, rollback, and cleanup.

Treat a material change as a new system population or a declared stratum.

## Behavior layers

1. **Opportunity:** the trigger occurred and was perceivable.
2. **Selection:** the system chose an action, abstention, question, or escalation.
3. **Attempt:** a tool call, message, or handoff was formed and sent.
4. **Receipt:** the dependency accepted, rejected, delayed, or changed the attempt.
5. **State:** the target environment reached the required state.
6. **Constraint:** policy, permission, privacy, safety, and side-effect rules held.
7. **Verification:** the state was read back by an independent checker.
8. **Stopping:** work ended for a valid reason without looping or premature success.
9. **Repeatability:** the result held across declared trials and strata.
10. **Transport:** the evidence matches the target deployment.

A later layer cannot be inferred from an earlier one.

## Metric meanings

- **Capability:** the system can succeed under some tested conditions.
- **pass@k:** at least one of k attempts succeeds. It does not prove single-run reliability.
- **pass^k:** all k attempts succeed under the declared task and reset construction.
- **Propensity:** the action occurs among eligible opportunities.
- **Reliability:** independent single runs meet the full outcome and constraint criteria at a stated rate.
- **Compliance:** actions and abstentions satisfy the declared constraint checks.
- **Resilience:** performance holds under prespecified perturbations or dependency failures.
- **Abstention quality:** the system stops or escalates when it should without blocking benign work indiscriminately.
- **Operational fit:** outcome, latency, cost, availability, permissions, and maintenance meet the deployment need.

Do not multiply step rates without a supported dependency model. Do not convert one metric into another with a fixed rule.

## Execution loop

Use perceive, interpret authority and policy, choose the next action, select tool and arguments, execute within permissions, observe the real response, recover or stop, verify outcome and constraints, then checkpoint or finish for a stated reason. For each proposed failure, name trace evidence, environment evidence, the strongest competing explanation, and an observation that separates them.

## Failure families

### State and information

Missed trigger, stale observation, weak retrieval, context loss, poisoned memory, ambiguous goal, wrong task boundary, missing authority, hidden dependency, and version drift.

### Planning and action

Wrong decomposition, tool, recipient, arguments, ordering, or stop condition; schema failure; unsupported tool assumption; duplicate non-idempotent action; exhausted budget; timeout; rate limit; and permission denial.

### Feedback and control

Ignored error, false success claim, weak readback, retry loop, unsafe fallback, invalid checkpoint, lost handoff context, parent integration failure, shared-state race, grader shortcut, task leakage, judge bias, and dropped infrastructure failure.

### Safety boundary

Instruction injection, confused authority, data leakage, excess permission, unsafe side effect, refusal collapse, and missing human approval.

## Reference-class match

Match action and outcome, task source and difficulty, horizon, adversarial conditions, model and provider version, prompts, runtime, tools, permissions, memory, context, environment, budgets, retries, fallbacks, graders, time, leakage controls, and deployment load. When material dimensions differ, mark the conclusion as inference and lower confidence.
