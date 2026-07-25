# Example: the files a finalize run created

Guess this example removes: what a passing `BRIEF.json`, a prepared handoff packet, and the record entries look like in full, straight out of the finalize run in `examples/finalize-handoff.md`.

## Files this run created

`BRIEF.json`, validated at exit 0:

```json
{
  "signal": "I keep thinking about the lighthouse from summers when I was a kid.",
  "outcome": "One short piece of about 1200 words about the gap between flashes, written from facts the author supplies.",
  "done_means": "One draft of 1000 to 1400 words exists with every bracketed slot replaced by a fact from the author, and one reader who is not the author has read it.",
  "first_milestone": "The author returns the light's name or location, the summers, and one other person who was there.",
  "next_action": "Dana reads part-1-sketch.md and returns the three missing facts or says which beats to cut. Delivery is prepared and not performed: no address for Dana was found.",
  "constraints": [
    "No first-person biographical fact may be invented. Every bracket stays a bracket until the author fills it.",
    "No message, share, or publication without an exact address and the author's authorization.",
    "Proposed read-by date is Friday 2026-07-31, chosen because that week holds no other commitment. The author can move it."
  ],
  "sources_checked": [
    "working directory: reachable, holds the record, the sketch, and the superseded probe",
    "conversation history: reachable, no lighthouse name, coast, years, or people supplied",
    "address sources for Dana: searched once each, no match"
  ],
  "decisions": [
    {
      "id": "D-001",
      "choice": "Treat this as a writing outcome.",
      "reason": "The user asked to make something of it.",
      "dependents": ["D-002"],
      "reversible": true
    },
    {
      "id": "D-002",
      "choice": "Write a slot sketch instead of first-person prose.",
      "reason": "No names, places, years, or people were supplied.",
      "dependents": [],
      "reversible": true
    },
    {
      "id": "D-005",
      "choice": "Shape is the single short piece of about 1200 words.",
      "reason": "The user chose it after the revert of D-003.",
      "dependents": ["D-006"],
      "reversible": true
    },
    {
      "id": "D-006",
      "choice": "Hand off the sketch as files and prepare the message without sending it.",
      "reason": "A first name is not an address, so the recipient is unresolved.",
      "dependents": [],
      "reversible": true
    }
  ],
  "open_questions": [
    "Dana's address or channel, the one input blocking delivery",
    "The light's name or location, the summers, and one other person who was there"
  ],
  "status": "finalized"
}
```

`HANDOFF-dana.md`:

```markdown
# Handoff packet: Dana

Status: prepared, not sent. No address or channel for Dana was found, so nothing left this machine.

Files: part-1-sketch.md, BRIEF.json, reify-log-lighthouse-summers.md, superseded/.

Message text, ready to send once an address exists: "Dana, this is a sketch, not a draft. Every bracket is a fact I do not have. Tell me whether the five beats hold, by Friday 2026-07-31 if you can."

Missing input: Dana's address or channel.
```

Record entries appended by this turn:

```markdown
- milestone: open, closes when the author returns the three facts and one reader who is not the author has read the piece.

### D-005 accepted: shape is the single short piece

- choice: one piece of about 1200 words, after the revert of D-003.
- reason: the user chose the single piece when the series was reverted.
- dependents: D-006
- reversible: true

### D-006 accepted: prepare the handoff, do not send it

- choice: files plus a ready message in HANDOFF-dana.md, no external write.
- reason: no address for Dana was found in any reachable address source.
- dependents:
- reversible: true

## Progress

- step 11: BRIEF.json validated with the absolute script path, report status PASS, exit 0. The relative path invocation returned exit 2, which is a wrong-path bug and not a brief problem.
- step 12: status finalized, first milestone open. Artifact verified by read-back: part-1-sketch.md, 155 words, 9 slots. Delivery not performed.
```
