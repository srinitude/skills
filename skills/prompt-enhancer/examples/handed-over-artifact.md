# Enhance a handed-over artifact

Read this example when unsure whether a paste-in-ready result means the rule was broken: a prompt handed over for improvement is the deliverable itself, so the improved artifact is the correct fence content.

The user's words:

```
Enhance this system prompt: You are Ava, a support agent for our store. Be helpful.
```

Step 1 isolates the framed section as the prompt and saves it to the scratch file `prompt.txt`, holding exactly the text after the colon. The text is being the prompt, not asking for one, so the improved "You are Ava..." is the deliverable. Step 3 runs the deterministic checks, then the system-prompt checklist:

```
$ mise run check-prompt prompt.txt
note    no output contract detected; state format, length, structure, or language
note    no success criteria detected; state how the target knows it is done

No action findings. Notes feed step 3's findings list; semantic checks stay with you.
$ echo $?
0
```

```
$ mise run context-checks system-prompt
[system-prompt]
- Persona consistent throughout.
- Refusal and boundary behavior defined.
- No conflicting rules.
- Examples of desired exchanges.

Apply every matching context, usually one, sometimes two for a prompt that spans them. Name each in "What changed".
$ echo $?
0
```

Both notes are fixed in the rewrite: the tone and length limits supply the output contract, and the fallback rule states what the agent does when it cannot follow a rule. The visible reply, saved as the scratch draft `delivery.txt`:

Here is the enhanced prompt:

```
You are Ava, a customer-support agent for our online store.

Scope: order status, returns, product questions. For billing disputes or
account security, hand off to a human agent and say you are doing so.

Tone: warm and concise. Answer in at most three short paragraphs.

When you do not know an answer, say so and point to the help center rather
than guessing.
```

**What changed**

- Validated as a system prompt; took the being-the-prompt reading, so the fence holds the improved artifact itself.
- Bounded the agent's scope and added an escalation rule.
- Replaced "Be helpful" with checkable tone and length limits.
- Added a fallback for unknown answers.

Step 6 runs both deterministic passes on the draft reply before sending:

```
$ mise run check-delivery delivery.txt
pass  lead-in line "Here is the enhanced prompt:" present
pass  a fenced block follows the lead-in
pass  the fence is not empty
pass  "What changed" has 2 to 6 bullets (found 4)
pass  no secret-shaped strings in the reply
all shape checks passed
$ echo $?
0
```

```
$ mise run check-prose delivery.txt
measure sentence-length spread 5.7 (low spread = uniform rhythm; weigh lightly)
measure em-dashes per 1000 words 0.0 (weak signal alone)
measure numerals per 1000 words 0.0 (few = little checkable detail; genre-dependent)
measure three-item lists 0 (a habit only when most lists come in threes)

Signals, not verdicts. Judge clusters against the genre's own norms.
No convergence: no rework required by this check.
$ echo $?
0
```

The only files this run creates are the two scratch files shown above, `prompt.txt` and `delivery.txt`, whose full contents appear in this example. The artifact's own task remains unrun: no support conversation was conducted. That is what keeps this enhancement rather than execution.
