# Example: audit a brief for constraints that are really choices

Guess this example removes: the highest yield single pass this skill has, and the one that reads as rude if the reply is not careful.

## User says

```
here's the design brief for the new onboarding, anything look off? [attaches a brief listing five hard rules]
```

## Executor replies

```
Posture: audit
Ledger: decision-ledger-onboarding.md, 5 rows added, 3 marked inherited
Found: two real constraints, card fields and legal review, and three choices written in the grammar of a rule, the three screen maximum, the account before the workspace, and brand purple on every primary action.
none
```

## Commands run

```
$ python3 scripts/ledger.py init --file decision-ledger-onboarding.md --slug onboarding
created decision-ledger-onboarding.md
exit 0

$ python3 scripts/slice.py --category "Onboarding, activation and first run" --limit 2 --format json
{
 "count": 2,
 "widened": [],
 "questions": [
  {
   "id": "Q11006",
   "question": "Are you shipping this to learn something specific, or to stop working on it?",
   "category": "Onboarding, activation and first run",
   "subcategory": "Contextual teaching and tone",
   "secondary_tags": [],
   "applies_to": [
    "system",
    "flow"
   ],
   "stage": "pre-ship",
   "tension": "launch as an experiment vs. launch as an escape",
   "failure_it_catches": "A release with no learning goal, so nothing is measured and nothing is concluded.",
   "provenance": "sourced",
   "source_publisher": "Intercom",
   "source_title": "Shipping is the beginning of a process",
   "source_url": "https://www.intercom.com/blog/shipping-is-the-beginning/",
   "seniority": "senior",
   "confidence": 0.9,
   "source_name": "Intercom: Shipping is the beginning of a process"
  },
  {
   "id": "Q11227",
   "question": "Name the aha moment for this product in one sentence, then point to the pixel that delivers it?",
   "category": "Onboarding, activation and first run",
   "subcategory": "Time-to-value and the aha moment",
   "secondary_tags": [],
   "applies_to": [
    "flow",
    "screen"
   ],
   "stage": "concept",
   "tension": "abstract value talk vs. a specific interface moment",
   "failure_it_catches": "A team that agrees on the aha moment in the abstract and has never located it in the UI.",
   "provenance": "sourced",
   "source_publisher": "Lenny's Newsletter",
   "source_title": "What is a good activation rate",
   "source_url": "https://www.lennysnewsletter.com/p/what-is-a-good-activation-rate",
   "seniority": "director",
   "confidence": 0.9,
   "source_name": "Lenny's Newsletter: What is a good activation rate"
  }
 ]
}
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-onboarding.md --decision "Card fields follow the network rules" --chosen "the fields the networks require" --trades "a shorter form vs. a payment that clears" --risks "a form that cannot take a payment" --origin deliberate
appended to decision-ledger-onboarding.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-onboarding.md --decision "Legal review before launch" --chosen "required, signed by counsel" --trades "a faster launch vs. a claim nobody can defend" --risks "shipping a page counsel has not read" --origin deliberate
appended to decision-ledger-onboarding.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-onboarding.md --decision "Onboarding fits in three screens" --chosen "three, stated as a hard rule" --trades "a short flow vs. the fields the product actually needs" --risks "a number carried from the last product, enforced as a law here" --origin inherited --falsifier "completion rate of a four screen variant"
appended to decision-ledger-onboarding.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-onboarding.md --decision "Account required before the workspace is visible" --chosen "required, stated as a hard rule" --trades "qualified signups vs. time to first value" --risks "a wall in front of the thing that would have sold the product" --origin inherited --falsifier "activation rate of a cohort shown the workspace first"
appended to decision-ledger-onboarding.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-onboarding.md --decision "Brand purple on every primary action" --chosen "purple, stated as a hard rule" --trades "a consistent brand vs. a primary action that reads as primary" --risks "a call to action that loses to the surface it sits on" --origin inherited --falsifier "contrast measured against the panel it sits on"
appended to decision-ledger-onboarding.md
exit 0

$ python3 scripts/speak.py --file decision-ledger-onboarding.md --decision "Account required before the workspace is visible" --origin inherited --live no
hold: the decision is not being made right now
exit 0
```

The brief is being read rather than written, so nothing is live and the reply asks nothing.

```
$ python3 scripts/check_reply.py --file draft.md
draft passed every rule
exit 0
```

## Files created

`decision-ledger-onboarding.md`, in full:

```
# Decision ledger: onboarding

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| Card fields follow the network rules | the fields the networks require | a shorter form vs. a payment that clears | a form that cannot take a payment | deliberate | - | - |
| Legal review before launch | required, signed by counsel | a faster launch vs. a claim nobody can defend | shipping a page counsel has not read | deliberate | - | - |
| Onboarding fits in three screens | three, stated as a hard rule | a short flow vs. the fields the product actually needs | a number carried from the last product, enforced as a law here | inherited | completion rate of a four screen variant | - |
| Account required before the workspace is visible | required, stated as a hard rule | qualified signups vs. time to first value | a wall in front of the thing that would have sold the product | inherited | activation rate of a cohort shown the workspace first | - |
| Brand purple on every primary action | purple, stated as a hard rule | a consistent brand vs. a primary action that reads as primary | a call to action that loses to the surface it sits on | inherited | contrast measured against the panel it sits on | - |
```

## Tone, which decides whether this lands

Say what the rule is, say what it traces to, and stop. Do not say the brief is wrong. The finding is that a choice was recorded in the grammar of a constraint, and the person who wrote it usually knows that already once it is named.
