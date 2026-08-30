# Example: choose between two directions

Guess this example removes: what the skill withholds. The chosen column stays empty on purpose, and the reply stops before the recommendation.

## User says

```
we're deciding whether to put the cancel flow behind a save offer or leave it one click. which one?
```

## Executor replies

```
Posture: choose
Ledger: decision-ledger-cancel.md, 1 rows added, 0 marked inherited
Found: one open decision, save offer against one click, where one click buys a brand people return to and costs the saves you would have made, and the save offer buys recovered revenue and costs the asymmetry test
none
```

## Commands run

```
$ python3 scripts/slice.py --category "Persuasion, defaults and dark patterns" --lens ethics --limit 3
# 3 questions

**Is any step in this flow sludge: friction we would remove instantly if it sat on the signup path instead?**
- trades away: friction that protects vs. friction that profits
- risks: A refund request requiring three uploads while purchase requires none.
- Persuasion, defaults and dark patterns / Deliberate friction, confirmation and undo - Q11814
- source: Harvard Law School: Sludge Audits (Cass Sunstein) https://hls.harvard.edu/bibliography/sludge-audits/

**Is the delay on this screen honest work being shown, or an animation performing seriousness?**
- trades away: operational transparency vs. manufactured gravity
- risks: A verifying your details spinner that verifies nothing, discovered by a curious user.
- Persuasion, defaults and dark patterns / Deliberate friction, confirmation and undo - Q11815
- source: UX Collective: The trust-latency gap: why the future of UX is intentionally slower https://uxdesign.cc/the-trust-latency-gap-why-the-future-of-ux-is-intentionally-slower-3433c1787d5e

**Did the user explicitly agree to marketing notifications, or did they agree to notifications and get marketing?**
- trades away: one consent for all sends vs. separate marketing permission
- risks: Promotional content riding on permission granted for order updates.
- Persuasion, defaults and dark patterns / Engagement metrics, social pressure, harm and defensibility - Q11957
- source: Apple HIG: Managing notifications (sending marketing notifications) https://developer.apple.com/design/human-interface-guidelines/managing-notifications
exit 0

$ python3 scripts/ledger.py init --file decision-ledger-cancel.md --slug cancel
created decision-ledger-cancel.md
exit 0

$ python3 scripts/ledger.py add --file decision-ledger-cancel.md --slug cancel --decision "Save offer before cancel, or one click out" --trades "friction that protects vs. friction that profits" --risks "a refund path harder than the purchase path" --origin open --falsifier "the same friction judged unacceptable on signup"
appended to decision-ledger-cancel.md
exit 0

$ python3 scripts/check_reply.py --file draft.md
draft passed every rule
exit 0
```

## Files created

`decision-ledger-cancel.md`, in full:

```
# Decision ledger: cancel

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| Save offer before cancel, or one click out | - | friction that protects vs. friction that profits | a refund path harder than the purchase path | open | the same friction judged unacceptable on signup | - |
```

## Why the fourth line is none

The only row is open rather than inherited, and step 8 earns a question only from an inherited row. The sludge test from the slice is the sharpest thing in this run and it still does not go in the reply. It goes in the row, as the thing that would settle the fork, where the next run picks it up.
