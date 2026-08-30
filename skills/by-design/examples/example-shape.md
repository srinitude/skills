# Example: shape work that does not exist yet

Guess this example removes: what a ledger looks like before anything has been decided, and why empty cells are the deliverable rather than a gap.

## User says

```
we're adding a bulk export to the reports page next sprint. nothing designed yet
```

## Commands run

```
$ python3 scripts/ledger.py init --file decision-ledger-export.md --slug export
created decision-ledger-export.md
exit 0

$ python3 scripts/slice.py --category "Empty, loading, error and edge states" --stage concept --match "export" --limit 6
widened: dropped stage
# 6 questions
Widened by dropping: stage.

**Where does this long job live if the tab closes: a jobs panel, an email, or nowhere?**
- trades away: ephemeral in-page status vs. a persistent home for work in flight
- risks: Users re-running a heavy export because they cannot tell whether the first one finished.
- Empty, loading, error and edge states / Optimistic UI, in-flight work, queue visibility and retry - Q05576
- source: UX Handbook: Design Background Jobs and Long Tasks https://ux.tfmstyle.com/guide/design-background-jobs-and-long-tasks

**What does this page do the moment a subscription lapses: lock, go read-only, or vanish?**
- trades away: commercial pressure to lock vs. the user's right to their own data
- risks: A lapsed customer unable to export the records they created and paid for.
- Empty, loading, error and edge states / Permission, quota and lockout states - Q05734

**Is this full-page spinner covering a task the user could have watched happen in one corner?**
- trades away: blocking to protect data integrity vs. leaving the rest of the product usable
- risks: An export locking the whole app when a corner progress chip would have sufficed.
- Empty, loading, error and edge states / Optimistic UI, in-flight work, queue visibility and retry - Q05598
- source: Pencil & Paper: Loading Feedback https://www.pencilandpaper.io/articles/ux-pattern-analysis-loading-feedback---new-examples

**Would starting this heavy export on a metered connection or a low battery warn the user first?**
- trades away: frictionless start vs. spending someone else's data and power
- risks: A 900MB sync silently consuming a traveller's roaming allowance.
- Empty, loading, error and edge states / Optimistic UI, in-flight work, queue visibility and retry - Q05603
- source: UX Handbook: Design Background Jobs and Long Tasks https://ux.tfmstyle.com/guide/design-background-jobs-and-long-tasks

**Does a failed export leave a partial file, and does the interface say which rows made it?**
- trades away: all-or-nothing simplicity vs. salvaging partial results
- risks: A user unknowingly circulating a truncated CSV that stops at row 4,000.
- Empty, loading, error and edge states / States nobody designed and API assumptions - Q06045
- source: UX Handbook: Design Background Jobs and Long Tasks https://ux.tfmstyle.com/guide/design-background-jobs-and-long-tasks

**Does this table render its first ten rows immediately, or wait for the full result set to count itself?**
- trades away: complete pagination vs. early rows
- risks: A 40,000-row export view that shows nothing for four seconds while the total is computed.
- Empty, loading, error and edge states / Progressive rendering, the instant window, peaks and endings - Q05794
exit 0
```

The stage pin dropped, and the run says so rather than presenting the wider slice as a concept-stage answer. The match held, which is the pin worth holding: the word export came from the request, and every question that came back is about an export rather than about states in general.

```
$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "Export scope: current filter, full set, or saved view" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "Where a running export lives if the tab closes" --trades "ephemeral in-page status vs. a persistent home for work in flight" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "What a partial export delivers when a job times out" --trades "shipping something vs. shipping a file the user will trust wrongly" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "Whether the export blocks the product while it runs" --trades "blocking to protect integrity vs. leaving the rest usable" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "Whether a heavy export warns before it spends someone's data" --trades "a frictionless start vs. spending someone else's allowance" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-export.md --decision "Who may export, and what happens when a subscription lapses" --trades "commercial pressure to lock vs. the user's right to their own records" --origin open
appended to decision-ledger-export.md
exit 0

$ python3 scripts/ledger.py count --file decision-ledger-export.md --decision "Export scope"
1
exit 0

$ python3 scripts/check_reply.py --file draft.md
draft passed every rule
exit 0
```

## Executor replies

```
Posture: shape
Ledger: decision-ledger-export.md, 6 rows added, 0 marked inherited
Found: six open decisions, covering export scope, where a running job lives, partial results, whether the product blocks, warning before a heavy transfer, and who may export at all.
none
```

The fourth line is the word none, and that is the whole line. No row is inherited, so nothing earns a question.

## Files created

`decision-ledger-export.md`, in full, with every chosen cell a dash on purpose:

```
# Decision ledger: export

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| Export scope: current filter, full set, or saved view | - | - | - | open | - | - |
| Where a running export lives if the tab closes | - | ephemeral in-page status vs. a persistent home for work in flight | - | open | - | - |
| What a partial export delivers when a job times out | - | shipping something vs. shipping a file the user will trust wrongly | - | open | - | - |
| Whether the export blocks the product while it runs | - | blocking to protect integrity vs. leaving the rest usable | - | open | - | - |
| Whether a heavy export warns before it spends someone's data | - | a frictionless start vs. spending someone else's allowance | - | open | - | - |
| Who may export, and what happens when a subscription lapses | - | commercial pressure to lock vs. the user's right to their own records | - | open | - | - |
```

## Why this is not a brief

A brief records what was decided. This records what has not been, which is the more useful half at this moment. When the sprint ends, the same file holds the answers and every row still shows whether the answer was chosen or inherited.
