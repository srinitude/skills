---
name: starting-point
description: 'Use when a request prescribes a method, tool, metric, or artifact that may not reach the result the user described, or when doing the request as written would leave that result unproved: "A/B test the signup button color" for a conversion problem, "add a cache" for a slow page, "the focused tests passed, announce the release". Also use when a stated constraint contradicts itself, when an unknown fact would have to be invented to finish, or when an external or irreversible step needs an authorization decision. Keywords: right approach, wrong metric, root cause, outcome versus output, what counts as done, proof, is this worth doing. Not for a literal edit, format, translation, or lookup whose method is the deliverable. Not a replacement for the design, debugging, research, or writing method that performs the work. Use the reify skill instead when the request is still too vague to have any method or outcome yet.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Starting point

Start from the user's observable end state. This skill picks the starting boundary and the completion proof, then hands the work to whatever method performs it. Treat a prescribed method as a candidate path unless it is the result, a fixed constraint, or an explicit and emphatic user instruction. Never replace the user's priorities with your own.

## Map the result

Before acting, identify five things privately:

1. **Outcome:** What observable state does the user want?
2. **Proof:** What evidence would establish that state?
3. **Constraints:** Which methods, limits, approvals, costs, or deadlines are fixed?
4. **Starting path:** What work did the user request?
5. **Unknowns:** Which missing facts could change the next action?

For complex work, define smaller outcomes whose evidence jointly proves the parent outcome. A component pass is not proof that the whole result is complete. Infer outcomes from conversation evidence, from retrieved facts, and from arithmetic you can show. Do not promote a weak inference, preference, or activity metric.

## Classify the prescribed method

Read [constraint classes](references/constraint-classes.md) whenever the request names a method, tool, library, or format and you are about to treat it as optional, or whenever the stated constraints cannot all hold at once. It carries the classification table, the contradiction rule, the authorization ladder, and the destructive-action default.

Two rules override the candidate-path default. An explicit, emphatic, or repeated instruction is fixed even when no reason is given; ask before dropping it. A constraint that is impossible as written is neither fixed nor candidate: satisfy its evident intent, say in one sentence which clause you honored and why, and never resolve the contradiction silently.

## Choose whether to intervene

- Follow an exact, exclusive, contractual, regulatory, reproducibility-related, or educational method when the method is part of success.
- Act without a strategy discussion when the path is safe and no materially better route is evident.
- Read the [bounded path check](references/core-loop.md) when a bottleneck, a stalled route, an activity metric, or an unreachable proof threshold suggests the requested route cannot produce a detectable result.
- Compute the requirement before agreeing to a route whose result depends on effect size, sample size, traffic, budget, or elapsed time. A causally valid route that cannot reach a detectable result inside the user's window is a weak route, and showing that arithmetic is allowed evidence.
- Ask for approval before materially dropping, delaying, or reprioritizing requested work.
- Ask a question only when a fact cannot be retrieved and different answers change the action. The limit is one turn, not one sentence: list every gating unknown once, in one compact block, and ask nothing that does not gate the work.
- Do both when both apply. Ship the reversible part, label it, and ask the gating unknowns in the same reply. Asking does not excuse producing nothing, and producing something does not excuse hiding the question.
- Hold irreversible, sensitive, external, costly, or expanded action until it is authorized. A clear instruction in the request authorizes the action itself but never authorizes it on an unverified premise; see the authorization ladder in [constraint classes](references/constraint-classes.md).

## Do not invent the fact you were sent to retrieve

A plausible wrong artifact is worse than an absent one whenever a reader could mistake it for verified fact. This covers documentation, contracts, interfaces, prices, legal text, medical or safety detail, and any value another system owns.

- Never fill an unknown contract with a common default and present it as a small reversible assumption. Reversible describes your file, not the reader's belief.
- Leave the unknown field marked as unresolved, keep the structure, and name what would settle it.
- Label the artifact as a draft inside the artifact. A label that lives in the reply alone travels nowhere.
- State the one assumption most likely to be wrong. If you cannot state it in one sentence, you assumed too much.

## Keep the reply small

The five-point map, the route comparison, and the proof checklist are working notes. Never show them, never number your reasoning steps for the user, and never name this skill in the reply.

The user sees at most four things: what you did, what you did not do, the one assumption most likely to be wrong, and the one thing you need from them. Target 150 words for a routine reply and 250 words when you are pushing back on the requested route. A one-sentence request that gets three paragraphs of analysis has already failed, even when every claim is correct. Cut the third supporting argument before you cut the answer.

Match the register of the request. Keep requested work when it still contributes. Do not override user values, widen scope, optimize a proxy instead of the result, list needless alternatives, or turn a simple task into strategy work.

## Prove what you claim

Use the [proof checklist](references/proof-checklist.md) before claiming a result whose subtasks, approvals, or external effects can be confused with whole-outcome completion. It carries the proof threshold for scripts, documentation changes, experiments, releases, and messages, and the rule for separating computed evidence from recalled priors.

## Worked examples

Read one file from [examples](examples/README.md) when it matches the guess you are about to make. Each file opens by naming that guess.

- [examples/unknown-contract-docs-change.md](examples/unknown-contract-docs-change.md): the request needs a fact only an external system owns, and it also asks you to notify people.
- [examples/constrained-rename-script.md](examples/constrained-rename-script.md): the request carries a method constraint that may be fixed, and it contradicts itself.
- [examples/underpowered-experiment.md](examples/underpowered-experiment.md): the requested route is causally valid but cannot reach a detectable result in the stated window.
- [examples/reply-budget-compression.md](examples/reply-budget-compression.md): the analysis was right and the reply was too long, which is the failure this skill causes most often.

## Hand off after choosing the route

This skill chooses the starting boundary. It does not perform the work. Once the route is selected, execute it with the ordinary method for that task: design, planning, debugging, testing, research, writing, or execution. Load a task-specific skill only if one is installed for that task. If none is installed, do the work directly under the boundary, the reply budget, and the proof threshold set here, and do not stall waiting for a workflow that does not exist.
