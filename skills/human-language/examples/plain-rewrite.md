# Example: a plain rewrite

- This example answers one question: when you strip inflated words from a sentence, what stays and what goes?
- It follows validation case `HL-001`, "Plain rewrite". Native use runs no commands, so this run has none.

## The request

- User: "Use human-language. Rewrite this: “We are harnessing a powerful methodology to facilitate the frictionless completion of your onboarding journey.”"

## The run

### Find the real action

- The sentence says one thing: we will help you finish onboarding.
- “Harnessing a powerful methodology”, “facilitate”, “frictionless”, and “journey” add no fact. The source names no method, speed, or benefit, so the rewrite must not add one.

### Check before sending

- Meaning: the promise to help finish onboarding is kept.
- Exact data: the source has no numbers, names, or dates to keep.
- Invented facts: none. The rewrite claims no speed, ease, or result the source did not state.

## The reply

- “We'll help you finish setting up your account.”
