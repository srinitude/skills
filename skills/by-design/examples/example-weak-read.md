# Example: the ranking warns, so the artifact type comes from you

Removes the guess: what to do when step 3 names a shelf that reads wrong. The answer is not to pick a category by hand and carry on, it is to run step 3 again with `--hint`.

This is a real run on a consent banner rework, where the two leading shelves are both defensible and the ranking cannot separate them.

## What arrived

```
Consent banner rework for a European audience under the rules now enforced. Accepting and rejecting must take the same number of clicks, so reject all moves onto the first layer beside accept all, with neither larger, more coloured nor better placed than the other. Labels become accept all, reject all and manage preferences, and vague words like continue and proceed are dropped. Rejection behind manage preferences, extra clicks to refuse, visual weight favouring acceptance, and a reject button that does not actually stop the tracking are all named as failures. The banner sits over the first screen a visitor ever sees of the product.
```

## Step 0, gate

```
$ python3 scripts/gate.py --text "$(cat brief.txt)"
design: matched strong:screen, weak:audience, weak:banner, weak:button, weak:label
exit 0
```

## Step 3, locate, first attempt

```
$ python3 scripts/locate.py --file brief.txt --top 3
  2.47   2 terms  Privacy, consent and compliance  [consent, acceptance]
  2.41   2 terms  Persuasion, defaults and dark patterns  [consent banner, continue]
  2.00   1 terms  Layout, grid, hierarchy and density  [visual weight]
weak read: the top two places are too close to separate, so name the artifact type with --hint and run this again
exit 0
```

Compliance came first at 2.47 and dark patterns second at 2.41, six hundredths apart on two terms each. The warning is the point: an order this close is a coin flip wearing a ranking, and the two shelves ask different questions. Compliance asks whether the banner meets the rule. Dark patterns asks whether the equal-weight buttons are the whole of the choice. The brief names visual weight and a reject button that does not stop the tracking, so the second shelf is the one holding this work.

## Step 3 again, with the artifact type named

```
$ python3 scripts/locate.py --file brief.txt --hint "consent banner dark patterns" --top 3
 22.41   3 terms  Persuasion, defaults and dark patterns  [hint, consent banner, continue]
 12.47   3 terms  Privacy, consent and compliance  [hint, consent, acceptance]
 10.00   1 terms  Color, theming and dark mode  [hint]
exit 0
```

No warning this time, because the artifact type came from the person holding the work rather than from a six hundredths gap.

## Step 4, the slice, and what it caught

```
$ python3 scripts/slice.py --category "Persuasion, defaults and dark patterns" --stage concept --match "consent" --limit 3
# 3 questions

**Have we designed the third option (advertising without tracking) or only the two that suit our current stack?**
- trades away: binary framing that maximises consent vs. the option most users say they want
- risks: A forced choice presented as exhaustive when a third, more popular option was never built.
- Persuasion, defaults and dark patterns / Consent quality, attention capture and re-engagement vs harassment - Q11603
- source: noyb: Pay or Okay study https://noyb.eu/en/pay-or-okay-study-users-prefer-tracking-free-third-option

**If the user pays to avoid tracking, what exactly do they get that the free tier does not, and is that difference a service or a right?**
- trades away: subscription revenue vs. charging for the exercise of a right
- risks: A consent-or-pay wall that prices a legal entitlement rather than a product.
- Persuasion, defaults and dark patterns / Consent quality, attention capture and re-engagement vs harassment - Q11608
- source: noyb: Pay or Okay study https://noyb.eu/en/pay-or-okay-study-users-prefer-tracking-free-third-option

**Was this consent informed, or merely obtained, and which of the two does the screen actually optimise for?**
- trades away: a completed consent rate vs. a user who understood
- risks: Treating the click as the goal, so the design improves the number while degrading the understanding.
- Persuasion, defaults and dark patterns / Consent quality, attention capture and re-engagement vs harassment - Q11610
- source: EDPB Guidelines 03/2022 on deceptive design patterns https://www.edpb.europa.eu/documents/guideline/guidelines-032022-on-deceptive-design-patterns-in-social-media-platform_en
exit 0
```

The first question is the one the compliance shelf would never have asked. The brief treats accept and reject as the whole of the choice, and the library asks who decided that.

## Steps 6 to 8, the ledger and the one question

```
$ python3 scripts/ledger.py init --file decision-ledger-consent.md --slug consent
created decision-ledger-consent.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-consent.md --decision "Rejecting costs the same as accepting" --chosen "reject all on the first layer beside accept all" --trades "consent rate vs. a refusal that is actually reachable" --risks "a reject path nobody finds, which is the pattern the rules name" --origin deliberate
appended to decision-ledger-consent.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-consent.md --decision "Which words the two buttons carry" --chosen "accept all and reject all, with continue and proceed dropped" --trades "a familiar softener vs. a label that says what the click does" --risks "a vague verb read as agreement by a visitor who meant to refuse" --origin deliberate
appended to decision-ledger-consent.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-consent.md --decision "Whether a third option exists beside accept and reject" --chosen "" --trades "a binary that suits the current stack vs. the option most people say they want" --risks "a forced choice presented as exhaustive when a third option was never built" --origin inherited --source "Q11603 https://noyb.eu/en/pay-or-okay-study-users-prefer-tracking-free-third-option"
appended to decision-ledger-consent.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-consent.md --decision "That the banner is the first screen anyone sees" --chosen "" --trades "compliance placed where it is unavoidable vs. a first impression spent on a dialog" --risks "an entire first encounter that is a legal interstitial" --origin inherited
appended to decision-ledger-consent.md
exit 0

$ python3 scripts/ledger.py show --file decision-ledger-consent.md
| Rejecting costs the same as accepting | reject all on the first layer beside accept all | consent rate vs. a refusal that is actually reachable | a reject path nobody finds, which is the pattern the rules name | deliberate | - | - |
| Which words the two buttons carry | accept all and reject all, with continue and proceed dropped | a familiar softener vs. a label that says what the click does | a vague verb read as agreement by a visitor who meant to refuse | deliberate | - | - |
| Whether a third option exists beside accept and reject | - | a binary that suits the current stack vs. the option most people say they want | a forced choice presented as exhaustive when a third option was never built | inherited | - | Q11603 https://noyb.eu/en/pay-or-okay-study-users-prefer-tracking-free-third-option |
| That the banner is the first screen anyone sees | - | compliance placed where it is unavoidable vs. a first impression spent on a dialog | an entire first encounter that is a legal interstitial | inherited | - | - |
exit 0

$ python3 scripts/speak.py --file decision-ledger-consent.md --rank
1. That the banner is the first screen anyone sees (3 columns unknown)
2. Whether a third option exists beside accept and reject (2 columns unknown)
exit 0

$ python3 scripts/speak.py --file decision-ledger-consent.md --decision "That the banner is the first screen anyone sees" --origin inherited --live yes
ask: inherited, live, and recorded once including this one
exit 0
```

## The reply

```
$ python3 scripts/check_reply.py --file draft.md
draft passed every rule
exit 0
```

The draft that passed:

```
Posture: audit
Ledger: decision-ledger-consent.md, 4 rows added, 2 marked inherited
Found: four decisions, two of them stated as rules in the brief and two that nobody made, including the choice to spend a visitor's first screen on a legal dialog.
The brief treats accept and reject as the whole of the choice: has anyone tested whether a third option belongs on this banner?
```

The rank put the first-screen row above the third-option row, and the question in the reply is about the second. That is allowed and it is a judgement: the rank orders by how little is known, and the row worth asking about was the one the person could still change this week.
