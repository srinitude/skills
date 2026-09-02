# Example: watch, the default posture

Guess this example removes: what the skill does when nobody invoked it, which is the case that decides whether it is usable at all.

## User says

```
ok so for the settings page I'm going to use the same 12 column grid we used on the dashboard, and 32px row height like the orders table
```

## Executor replies

```
Posture: watch
Ledger: decision-ledger-settings.md, 2 rows added, 2 marked inherited
Found: the grid column count and the row height, both carried over from other pages rather than chosen for this one
Is 12 columns derived from the settings content, or from the dashboard it came from?
```

## Commands run

```
$ mise run ledger show --file decision-ledger-settings.md
no ledger at decision-ledger-settings.md
exit 1

$ mise run ledger init --file decision-ledger-settings.md --slug settings
created decision-ledger-settings.md
exit 0

$ mise run ledger add --file decision-ledger-settings.md --decision "Grid column count on settings" --chosen "12 columns, carried from the dashboard" --origin inherited
appended to decision-ledger-settings.md
exit 0

$ mise run ledger add --file decision-ledger-settings.md --decision "Row height on settings rows" --chosen "32px, carried from the orders table" --origin inherited
appended to decision-ledger-settings.md
exit 0

$ mise run ledger count --file decision-ledger-settings.md --decision "Grid column count"
1
exit 0

$ mise run speak --file decision-ledger-settings.md --decision "Grid column count on settings" --origin inherited --live yes
ask: inherited, live, and recorded once including this one
exit 0

$ mise run speak --file decision-ledger-settings.md --decision "Row height on settings rows" --origin inherited --live yes
ask: inherited, live, and recorded once including this one
exit 0
```

Both returned ask, and the reply carries one question, because the budget counts one interruption per turn no matter how many rows earned one.

```
$ mise run check-reply --file draft.md
draft passed every rule
exit 0
```

## Files created

`decision-ledger-settings.md`:

```
# Decision ledger: settings

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| Grid column count on settings | 12 columns, carried from the dashboard | - | - | inherited | - | - |
| Row height on settings rows | 32px, carried from the orders table | - | - | inherited | - | - |
```

## Why one question and not two

Resource gate: run `mise run validate` before using package files named here.

Both rows are inherited, so both passed the second test in references/interruption.md. The budget is one interruption per decision, and two decisions arrived in one turn. The grid carries the larger consequence, so it got the question and the row height got a row.
