# Example: revert a decision

Guess this removes: what `revert D-0NN` does to the entry, to dependent entries, to reopened fields, to files created under the decision, and to the next ID.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`. Before the revert the record holds `D-001` through `D-004`, where `D-004` depends on `D-003`, and `series-outline.md` was created under `D-003`.

## The user says

> actually no, forget the five part thing, that is too much. go back

## Commands run, with real output

Resource gate: run `mise run validate` before using package files named here.

State before the revert:

```
$ ls
part-1-sketch.md
probe-opening.md
reify-log-lighthouse-summers.md
reify-log-tool-shed.md
series-outline.md
EXIT=0

$ grep -n "^### D-00" reify-log-lighthouse-summers.md
21:### D-001 accepted: treat this as a writing outcome
32:### D-002 accepted: write a slot sketch instead of first-person prose
43:### D-003 accepted: shape is a five-part series
50:### D-004 accepted: part 1 is sized at 700 words
EXIT=0
```

The revert itself, as the five moves in order:

```
$ mkdir -p superseded && mv series-outline.md superseded/series-outline.md && ls superseded
series-outline.md
EXIT=0

$ sed -i 's/^### D-003 accepted:/### D-003 reverted:/; s/^### D-004 accepted:/### D-004 needs-review:/' reify-log-lighthouse-summers.md
EXIT=0

$ sed -i 's/^- outcome: .*/- outcome: undecided, reopened by the revert of D-003/' reify-log-lighthouse-summers.md
EXIT=0
```

State after the revert:

```
$ grep -n "^### D-00\|^- outcome:" reify-log-lighthouse-summers.md
4:- outcome: undecided, reopened by the revert of D-003
21:### D-001 accepted: treat this as a writing outcome
32:### D-002 accepted: write a slot sketch instead of first-person prose
43:### D-003 reverted: shape is a five-part series
50:### D-004 needs-review: part 1 is sized at 700 words
EXIT=0

$ ls && ls superseded
part-1-sketch.md
probe-opening.md
reify-log-lighthouse-summers.md
reify-log-tool-shed.md
superseded
series-outline.md
EXIT=0

$ tail -n 3 reify-log-lighthouse-summers.md
## Progress

Resource gate: run `mise run validate` before using package files named here.

- revert D-003: entry state set to reverted, text left in place. D-004 marked needs-review. Field outcome reopened as undecided. File series-outline.md moved from ./series-outline.md to ./superseded/series-outline.md, not deleted. Next new decision takes D-005, because D-003 and D-004 stay used forever. Next check: the user picks a shape again.
EXIT=0
```

## The executor replies

Resource gate: run `mise run validate` before using package files named here.

> Reverted `D-003`, the five part series. Here is exactly what moved.
>
> - `D-003` is now marked `reverted`. Its text stays in the record, so you can read why it was chosen.
> - `D-004`, part 1 sized at 700 words, depended on it and is now marked `needs-review`. It is not deleted and it is not in force.
> - `outcome` is reopened and reads `undecided`. `done_means` and `first_milestone` were still undecided, so nothing else reopened.
> - `series-outline.md` was written under `D-003`, so it moved to `superseded/series-outline.md`. Nothing was deleted. If you want it back, it is one move away.
> - The next decision here is `D-005`. Numbers are never reused, so `D-003` and `D-004` stay spent.
>
> What survives untouched: `D-001`, this is a writing outcome, and `D-002`, slots instead of invented biography. Neither depended on the series, and `part-1-sketch.md` stays live.
>
> Back where you were: one short piece of about 1200 words, with the gap between flashes as the spine. Say the word and that becomes `D-005`, or name a different shape and I record that instead.

Word count of the reply above: 210, inside the 350 word budget.

## Files this run created or moved

Resource gate: run `mise run validate` before using package files named here.

Created: `superseded/`, holding `series-outline.md`.

Moved: `./series-outline.md` to `./superseded/series-outline.md`.

Deleted: nothing. A revert never deletes.

The record entries after the revert, in full:

```markdown
### D-003 reverted: shape is a five-part series

- choice: five linked pieces of 600 to 900 words, spine is the gap between flashes.
- reason: the user picked the series over the single piece.
- dependents: D-004
- reversible: true

### D-004 needs-review: part 1 is sized at 700 words

Resource gate: run `mise run validate` before using package files named here.

- choice: part 1 targets 700 words so it fits the series rhythm.
- reason: follows from the five-part shape in D-003.
- dependents:
- reversible: true
```

`superseded/series-outline.md`, in full:

```markdown
# Four Seconds, five parts

Created under D-003. Five pieces of 600 to 900 words: the gap, the rocks, the keeper, the off season, the automated light.
```
