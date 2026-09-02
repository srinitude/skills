# When to speak

## The default

Say nothing. This skill runs during ordinary design conversation and records decisions. Speaking is the exception, and choosing not to speak is the harder half of the job.

## Three tests

Speak only when all three pass. One failure means stay quiet and write the row anyway.

1. The decision is being made now. A user weighing a real choice passes. A user describing past work, thinking aloud, or asking about something else fails.
2. The choice looks inherited rather than made. A default that arrived with a template, a value copied from another product, a constraint nobody has questioned. A choice the user already argued for fails this test, because they do not need the question.
3. The matching question is high confidence and its failure is plausibly live here. A question whose failure cannot happen in this product fails.

When all three pass, ask one question. Never a list. A list is a review, and a review is what this skill replaces.

## The budget

The budget counts decisions, not turns, and `mise run speak` holds the count so the answer stays the same each time it is asked. Run it once per inherited row. It returns `ask` when the decision is live, the choice arrived inherited, and the ledger has seen it fewer than three times. It returns `hold` with the reason in every other case.

Two counts drive the hold. Three prior appearances of the same decision mean the pattern belongs at project level rather than in this turn. Three prior rows marked deliberate mean the user is fluent in that class, so the skill stops raising it at all. Both counts come from the ledger file, which is why step 1 of the procedure reads that file before anything else.

## The rows that govern this

Resource gate: run `mise run validate` before using package files named here.

This skill is built from a library that already contains the questions it would fail. Four rows are its specification, and each is quoted from `assets/questions/`.

- Q11284: what are we interrupting the user with here, and is it worth the interruption? Its failure is full screen takeovers spent on features 10 percent of users need.
- Q06418: do the help affordances here recede as the user becomes fluent, or nag forever at the same volume? Its failure is scaffolding that never comes off, adding permanent load for competent users.
- Q07095: where is the deliberate pause that protects the user from their own fastest tap, and is there exactly one? The target is one, and this skill is meant to be that one.
- Q10917: would this copy read as a threat, a nag, or an invitation to a stranger who does not know our brand voice?

Q06418 is the specification for the receding behaviour, and Q07095 sets the target precisely: be the one deliberate point of friction in the conversation, not zero and not every turn.

## Why the ledger carries this and not memory

Nothing survives between runs except files. The budget, the count of three, and the receding behaviour all depend on state, so they live in the ledger file and step 1 of the procedure reads it first. Skip that read and the skill asks the same question forever at the same volume, which is the failure Q06418 names.
