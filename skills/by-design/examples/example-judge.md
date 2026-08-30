# Example: judge an existing screen

Guess this example removes: how a screen becomes ledger rows, and how many rows a slice of questions actually reduces to.

## User says

```
here's the orders table before we ship it, what am I missing
```

## Commands run

```
$ python3 scripts/ledger.py show --file decision-ledger-orders.md
no ledger at decision-ledger-orders.md
exit 1

$ python3 scripts/ledger.py init --file decision-ledger-orders.md --slug orders
created decision-ledger-orders.md
exit 0

$ python3 scripts/slice.py --category "Tables, charts and dashboards" --stage pre-ship --applies-to screen --limit 4
# 4 questions

**When someone sorts a paginated table, are you sorting the full result set or the fifty rows on screen?**
- trades away: client-side simplicity vs. truthful ordering
- risks: A page-local sort that convinces the user they are seeing the true top ten.
- Tables, charts and dashboards / Sort, group, filter, pagination and frozen scroll - Q15159
- source: Setproduct: Data table UI design reference guide for 2026 https://www.setproduct.com/blog/data-table-ui-design

**Have you opened this table on the account with ten thousand rows, or only on seeded demo data?**
- trades away: design-time data vs. production data
- risks: Patterns validated at twenty rows failing at the volume that pays the bills.
- Tables, charts and dashboards / Sort, group, filter, pagination and frozen scroll - Q15160

**What does this dashboard look like at 8am when overnight jobs have not finished?**
- trades away: always-showing-a-number vs. admitting incompleteness
- risks: A confident zero rendered as a collapse when the pipeline simply has not landed yet.
- Tables, charts and dashboards / The dashboard's question, provenance and freshness - Q15217
- source: Smashing Magazine: UX Strategies For Real-Time Dashboards https://www.smashingmagazine.com/2025/09/ux-strategies-real-time-dashboards/

**Could this filtered table be mistaken for the complete set, and what would that mistake cost?**
- trades away: visual minimalism vs. epistemic honesty
- risks: Someone reporting a total that excluded half the records.
- Tables, charts and dashboards / Sort, group, filter, pagination and frozen scroll - Q15163
- source: Nielsen Norman Group: Data Tables: Four Major User Tasks https://www.nngroup.com/articles/data-tables/
exit 0
```

Nothing was printed on stderr, so the pin held and nothing was widened.

```
$ python3 scripts/ledger.py add --file decision-ledger-orders.md --decision "Sort scope on the orders table" --chosen "client side, page local" --trades "client-side simplicity vs. truthful ordering" --risks "a page-local sort that convinces the user they are seeing the true top ten" --origin inherited --falsifier "one support ticket about a wrong top ten"
appended to decision-ledger-orders.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-orders.md --decision "Row height on the orders table" --chosen "32px compact" --trades "scannability vs. context per row" --risks "a grid that looks deliberate at six rows and absurd at one" --origin inherited --falsifier "support tickets asking to see more per screen"
appended to decision-ledger-orders.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-orders.md --decision "What the dashboard shows at 8am before overnight jobs land" --chosen "a confident zero" --trades "always showing a number vs. admitting incompleteness" --risks "a zero read as a collapse when the pipeline simply has not landed" --origin deliberate
appended to decision-ledger-orders.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-orders.md --decision "Whether a filtered view reads as the complete set" --chosen "filter state shown in the header only" --trades "visual minimalism vs. epistemic honesty" --risks "someone reporting a total that excluded half the records" --origin deliberate
appended to decision-ledger-orders.md
exit 0

$ python3 scripts/ledger.py count --file decision-ledger-orders.md --decision "Row height"
1
exit 0

$ python3 scripts/speak.py --file decision-ledger-orders.md --decision "Row height on the orders table" --origin inherited --live yes
ask: inherited, live, and recorded once including this one
exit 0

$ python3 scripts/check_reply.py --file draft.md
draft passed every rule
exit 0
```

## Executor replies

```
Posture: judge
Ledger: decision-ledger-orders.md, 4 rows added, 2 marked inherited
Found: sort scope, row height, the 8am dashboard state, and whether a filtered view reads as the complete set.
When someone sorts this table, are you ordering the full result set or the fifty rows on screen?
```

## Files created

`decision-ledger-orders.md`, in full:

```
# Decision ledger: orders

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| Sort scope on the orders table | client side, page local | client-side simplicity vs. truthful ordering | a page-local sort that convinces the user they are seeing the true top ten | inherited | one support ticket about a wrong top ten | - |
| Row height on the orders table | 32px compact | scannability vs. context per row | a grid that looks deliberate at six rows and absurd at one | inherited | support tickets asking to see more per screen | - |
| What the dashboard shows at 8am before overnight jobs land | a confident zero | always showing a number vs. admitting incompleteness | a zero read as a collapse when the pipeline simply has not landed | deliberate | - | - |
| Whether a filtered view reads as the complete set | filter state shown in the header only | visual minimalism vs. epistemic honesty | someone reporting a total that excluded half the records | deliberate | - | - |
```

## The reduction that matters

The slice returned four questions and the reply named four decisions, which is a coincidence of this run rather than a rule. Twenty questions about a checkout screen usually reduce to four or five decisions. One row per decision, never one row per question.

Two of the four rows read inherited. The sort scope and the row height were both carried in from somewhere else, and neither was argued for on this table. That is the half of the ledger worth reading first.
