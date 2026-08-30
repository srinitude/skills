# Example: the ledger earns no question

Removes the guess: what the fourth line of the reply says when nothing in the ledger has earned a question. The answer is the word none, and step 10 fails a reply that asks one anyway.

This is a run on an accessibility statement programme brought under the European rules now being enforced.

## Steps 6 and 7, the rows

```
$ python3 scripts/ledger.py init --file decision-ledger-eaa.md --slug eaa
created decision-ledger-eaa.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-eaa.md --decision "What the accessibility statement claims" --chosen "only what a person meets on the screen today" --trades "a statement that reads well vs. one that survives a visit" --risks "a published claim contradicted by the first page a user opens" --origin deliberate
appended to decision-ledger-eaa.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-eaa.md --decision "Who signs the evidence" --chosen "the team that ships the surface, not the audit vendor" --trades "an external name on the page vs. accountability where changes happen" --risks "a signature nobody can act on when the surface changes" --origin deliberate
appended to decision-ledger-eaa.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-eaa.md --decision "How often the evidence is retaken" --chosen "every release that touches a declared surface" --trades "a cheap annual sweep vs. evidence that tracks the product" --risks "a statement that was true on the day it was written and never since" --origin deliberate
appended to decision-ledger-eaa.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-eaa.md --decision "Where the statement gets its wording from" --chosen "" --trades "a template that is quick vs. wording that describes this product" --risks "a page of boilerplate that tells a user nothing about what they will meet" --origin deliberate
appended to decision-ledger-eaa.md
exit 0
```

## Step 8, the interruption check

```
$ python3 scripts/speak.py --file decision-ledger-eaa.md --rank
no inherited rows, so nothing earns a question
exit 0
```

Four rows, every one of them deliberate. A programme designed on purpose has nothing inherited in it, which is the good case and also the quiet one.

## The draft that broke the rule

The first draft asked the sharpest question from the slice anyway, which is exactly the move the rule exists to stop.

```
The statement has to match what a person meets on the screen today: which success criterion passes here on a technicality that a disabled user would still call broken?
```

```
$ python3 scripts/check_reply.py --file draft.md
the ledger holds no inherited row, so this reply has not earned its question
exit 1
```

## The reply that passed

```
Posture: shape
Ledger: decision-ledger-eaa.md, 4 rows added, 0 marked inherited
Found: four decisions, all made on purpose, which is what an evidence programme looks like when it is designed rather than inherited, and one of them is still open: where the accessibility statement gets its wording from.
none
```

```
$ python3 scripts/check_reply.py --file reply.md
draft passed every rule
exit 0
```

## Files created

`decision-ledger-eaa.md`, in full:

```
# Decision ledger: eaa

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| What the accessibility statement claims | only what a person meets on the screen today | a statement that reads well vs. one that survives a visit | a published claim contradicted by the first page a user opens | deliberate | - | - |
| Who signs the evidence | the team that ships the surface, not the audit vendor | an external name on the page vs. accountability where changes happen | a signature nobody can act on when the surface changes | deliberate | - | - |
| How often the evidence is retaken | every release that touches a declared surface | a cheap annual sweep vs. evidence that tracks the product | a statement that was true on the day it was written and never since | deliberate | - | - |
| Where the statement gets its wording from | - | a template that is quick vs. wording that describes this product | a page of boilerplate that tells a user nothing about what they will meet | deliberate | - | - |
```

The question is not lost. It goes in the ledger as the open row it belongs to, where the next run picks it up.
