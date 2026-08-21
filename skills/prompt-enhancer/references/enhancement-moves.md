# Enhancement moves

Apply these at workflow step 4 where a step 3 finding calls for them. Work out every change before writing the final text.

- Lead with the task. Follow with context, constraints, and output contract.
- Replace each ambiguity with the most likely specific reading, and flag the substitution so the user can correct it.
- Add success criteria and an output format where they were missing.
- When the output has three or more named parts, add one example of the output format: a shaped stub, never a worked instance of the task.
- Name edge cases the target should handle. For each rule the prompt gives its target, state what the target should do when the rule cannot be followed. A rule with no fallback fails at its first unanticipated case.
- Where the prompt says "don't do X" with nothing in X's place, restate it as the behavior that replaces X.
- Steer the prompt toward substance its author actually has, never toward performing it. Asking for inserted errors, costume informality, or invented personal stories makes the output worse.
