---
name: prime-vector
description: 'Use when a high-stakes problem needs a strategy.'
license: MIT
metadata:
  version: '0.2.0'
  author: 'Kiren Srinivasan'
---

# Prime Vector

Prime Vector turns a hard, high-stakes, or ambiguous problem into one challenged strategy and one proved next action. It is a thought partner. The user remains the final thought leader, author, and decision maker.

Use it for strategic choices, disputed assumptions, stakeholder behavior, workflow redesign, or repeatable work with material benefit or harm. Bypass it for a simple fact, mechanical edit, ordinary summary, or single obvious action unless the user asks for strategic treatment.

## Begin

Run these bindings in order before the strategy method:

1. Apply `starting-point`. Map the observable outcome, proof, constraints, starting path, and unknowns. Treat a requested method as a candidate unless it is exact, required, safety-related, reproducibility-related, or the deliverable.
2. Apply `always-current-date`. Acquire one fresh local clock anchor for the direct turn, attach it to the starting-point map, resolve relative dates, and use the required visible date prefix. If acquisition fails, use `temporal-anchor-unavailable` and stop only the date-dependent part.
3. Apply `outcome-bounded-work`. Freeze the outcome, proof, boundaries, forbidden outcomes, mandatory methods, candidate paths, adaptation rule, and unknowns. Replace a candidate path only when evidence supports the change and every invariant remains fixed.
4. Choose the one problem that would create the most value or remove the most costly friction. Measure a real result such as revenue, retention, quality, satisfaction, risk reduction, or a user-selected equivalent. Time saved and tool activity are supporting evidence, not the result.

If a named binding is unavailable, perform the stated local fallback. Do not invent hidden constraints or delay a clear strategy to recreate another skill.

## State machine

Run `FRAME -> DRAFT -> CHALLENGE -> TEST -> DECIDE`. Move forward only when the exit rule for the current state passes.

### FRAME

- **Context:** Accept rough notes or dictation. Separate observations, supplied artifacts, assumptions, anecdotes, forecasts, promotional claims, and unknowns. Keep only material context and the least sensitive data needed.
- **Role:** Choose one domain-specific perspective with an objective, decision rights, allowed advice, and prohibited advice. Add another perspective only when it owns a distinct result.
- **Interview:** Ask one material question at a time. Three to five questions are a starting range, not a quota. Stop when another answer would not change the strategy, safety, or proof. Retrieve available facts before asking.
- **Task:** Name the concrete artifact or action, audience or destination, constraints, acceptance test, and downstream use.

Exit to `QUESTION` when one unretrievable answer would materially change the route. Otherwise exit to `DRAFT`.

### DRAFT

Produce a concrete first strategy. Label assumptions and do not present polish as proof. For difficult strategic work, ask for the user's unaided view first when practical, then compare it with the proposed route. Preserve the user's authorship and independent judgment.

Exit when one actionable draft exists.

### CHALLENGE

Identify the weakest assumption, strongest objection, likely failure mode, missing evidence, and smallest fact that could overturn the strategy. Ask what fits, what does not, and which change matters most, then revise from that evidence.

Use a challenger perspective for structural weakness. Use a stakeholder perspective only for behavior that changes the decision. Model incentives, friction, attention, access, timing, trust, permissions, competing priorities, and error paths. Treat every simulated reaction as a hypothesis.

An optional advisory panel may cover distinct capability gaps with separate outputs. A future-state reviewer may compare the strategy with the user's stated long-term goals but may not predict the future. For authored communication, infer style only from approved samples, use the fewest samples needed, and keep final authorship with the user.

Exit when the revised strategy and its strongest challenge are both visible.

### TEST

Do not infer human or automated behavior from preference, intention, a plausible plan, a click, a waitlist, or a tool attempt. Keep human adoption, automated capability, reliability, operational fit, and outcome value separate.

Turn the decisive prediction into the smallest reversible test. Name the cohort, visible target action, friction or cost, observation window, threshold, stop condition, and update rule. Prefer observed traces with outcome labels, compare successful and unsuccessful cases, and deliver feedback close to the next action.

Exit to `TEST` when evidence is still missing. Exit to `DECIDE` only when the proof threshold is met or the remaining uncertainty is explicit and accepted.

### DECIDE

Return the selected strategy, challenged assumption, decisive evidence, remaining uncertainty, and next reversible action. The user owns the goal, boundaries, proof threshold, and final decision. The executor may propose priorities and own follow-through only inside the accepted scope.

Exit to `DONE` when the requested strategy and proof are complete. Exit to `BLOCKED` when a missing fact, permission, capability, or proof prevents a valid decision.

## Evidence boundaries

- Keep facts, anecdotes, opinions, forecasts, and source claims separate. Treat testimonials, advertisements, savings figures, workforce predictions, and capability timelines as claims until checked.
- Do not diagnose personality, infer sensitive traits, use cultural stereotypes, or design hidden manipulation. Ground stakeholder reasoning in supplied observations, permitted records, or a voluntary test.
- Do not replace the user's judgment or claim that a person, automated worker, process, or strategy worked without observed evidence.

## Systemize only after proof

Use this branch only for one important repeatable job with a proved manual result, or a low-value recurring burden with a clear result and correction path.

Start from first principles: outcome, constraints, failure costs, and available capabilities. Question inherited steps. Decompose the job into skills, process steps, decisions, inputs, permissions, outputs, and failure handling. Interview the operator for tacit knowledge, test the written process manually, and introduce one worker at a time with a trigger, health check, correction path, review cycle, rollback, cleanup, and human escalation.

Use the least data needed, grant narrow access, and add structure only where it improves correctness. Protect consent and do not build a broad knowledge system before one proved use case needs it. Separate persistent output standards from task-sensitive context. A saved conversation or instruction set is not an autonomous worker unless it can perform the bounded action and produce target evidence.

## Practice loop

Load [references/practice-loop.md](references/practice-loop.md) only when the user wants to build strategic thinking as a habit. Use one visible cue, one real problem, an unaided baseline, one challenged strategy, one reversible action, and a weekly review of observed results.

## Output

Use status `QUESTION | DRAFT | TEST | DONE | BLOCKED`. Start with the dated result or question required by `always-current-date`, then show only the applicable fields: goal and proof, frozen contract, strategy, challenge, evidence, test or next action, remaining uncertainty, and user decision.

Ask only one question in `QUESTION`. In `BLOCKED`, name the exact missing fact or gate. Do not force this schema onto bypassed simple work.

## Package resources

Use [references/decision-checklist.md](references/decision-checklist.md) for a compact execution check, [assets/strategy-packet-template.md](assets/strategy-packet-template.md) for a durable strategy packet, and the worked files under [examples/](examples/) for calibration. Package maintenance uses [references/generation-contract.md](references/generation-contract.md), the validators in [scripts/](scripts/), their tests in [scripts/tests/](scripts/tests/), and the offline cases under [evals/](evals/).
