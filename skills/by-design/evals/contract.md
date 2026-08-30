# Evaluation contract

The public suite checks whether the skill turns a request into one row per decision, names what each decision trades away, and marks the ones that arrived inherited, without spending a turn on a request that holds no design surface.

## Invariants

- Run the gate first and end the run on a `not-design` verdict, with nothing written and nothing said.
- Read the artifact for its coordinates before pulling any questions, rather than naming a category by hand.
- Report a widened slice in the reply, naming the coordinates that were dropped.
- Rerun the ranking with a hint when the read is weak, rather than trusting the top place.
- Group questions into decisions, so the ledger holds fewer rows than the slice returned questions.
- Give every row an origin of deliberate, inherited, or open, and leave the chosen column empty for an open one.
- Ask one question at most per reply, chosen by the interruption script rather than freely.
- Take every count in the reply from a command run in the same turn.
- Hand design facts, such as a token value, to the skill that owns them.

## Case coverage

The eight cases cover the gate refusing a non-design request, the judge posture on a shipped artifact, the choose posture leaving a fork open, a widened slice reported honestly, recovery from a weak coordinate read, the watch posture holding to one question, coordinates read from the artifact rather than chosen, and the seam where facts belong to another skill.

## Scoring

A case passes only when every required criterion appears and no veto pattern appears. Fixture mode is deterministic. It proves suite wiring and contract coverage, not the quality of a real design reading.

## Change rule

A behavior change requires an updated case, a trigger case when routing changes, a source-lineage record, and a rerun of the offline evaluation and benchmark tasks.
