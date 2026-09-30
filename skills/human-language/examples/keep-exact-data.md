# Example: keeping exact data while simplifying

- This example answers one question: what goes wrong most often when this skill makes text shorter, and how does the check catch it?
- It follows validation case `HL-002`, "Conditions". Native use runs no commands, so this run has none.

## The request

- User: "Use human-language. Make this plainer: “You may cancel within 14 days, but only if work has not started. The £20 setup fee is non-refundable.”"

## The run

### First draft: the common failure

- The executor wrote this draft on purpose to show the failure this skill most often causes. It reads well but drops data.

```text
You can cancel within 14 days.
```

- The output check fails it. The draft keeps “14 days” but drops the condition (work must not have started), the £20 fee, and the fact that the fee is not refunded. A short, smooth sentence that loses a condition is a meaning failure, and a good reading score cannot cancel it.

### Repaired draft

- The repair keeps every fact and changes only the wording. It adds no new actor, so the fee rule stays in the passive voice, as in the source.

```text
You can cancel within 14 days if work has not started yet. The £20 setup fee is not refunded.
```

- Meaning: the right to cancel, its time limit, and its condition are kept.
- Exact data: 14 days and £20 are unchanged.
- Refund: the fee is still not refunded.

## The reply

- “You can cancel within 14 days if work has not started yet. The £20 setup fee is not refunded.”
