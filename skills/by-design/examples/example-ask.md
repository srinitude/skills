# Example: ask for the full slice

Guess this example removes: what happens when the user wants the questions rather than the judgment, and how the quiet default is dropped on request.

## User says

```
just give me the accessibility questions for a form, don't hold back
```

## Commands run

```
$ mise run slice --category "Forms and input" --lens accessibility --limit 15
# 15 questions

**Is the primary button disabled until everything is valid, and how does a stuck user learn why?**
- trades away: preventing invalid submits vs. giving feedback at all
- risks: A greyed-out button that gives no reason, no focus, and no path forward.
- Forms and input / Labels, hints and input format masking - Q06219
- source: Adam Silver: The problem with disabled buttons https://adamsilver.io/blog/the-problem-with-disabled-buttons-and-what-to-do-instead/

**Does this name field accept an apostrophe, a diacritic, a hyphen, and a single-word name?**
- trades away: validation strictness vs. the actual range of human names
- risks: Rejecting O'Neill, Ståhl, or a mononym as invalid input.
- Forms and input / Identity and locale-sensitive fields - Q06206
- source: GOV.UK Design System: Names pattern https://design-system.service.gov.uk/patterns/names/

**How many separate inputs does this one value occupy, and what does splitting it actually buy you?**
- trades away: chunked legibility vs. interaction cost
- risks: Four boxes for one code, none of which can be pasted into or labelled meaningfully.
- Forms and input / Labels, hints and input format masking - Q06222
- source: Adam Silver: Multiple inputs versus one input https://adamsilver.io/blog/form-design-multiple-inputs-versus-one-input/

**Is maxlength quietly truncating what people type without telling them anything happened?**
- trades away: error prevention vs. silent data loss
- risks: A user who looks at the keyboard, not the screen, saving a truncated account number.
- Forms and input / Labels, hints and input format masking - Q06223
- source: Adam Silver: Don't use the maxlength attribute https://adamsilver.io/blog/dont-use-the-maxlength-attribute-to-stop-users-from-exceeding-the-limit/

**Can a password manager complete this login, or does a script block it from filling?**
- trades away: perceived security control vs. accessible authentication
- risks: Locking out users who cannot transcribe a long password by hand.
- Forms and input / Validation timing and inline error recovery - Q06311
- source: W3C: Understanding SC 3.3.8 Accessible Authentication (Minimum) https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html

**Does a password manager recognise these fields, or has a custom component hidden them from it?**
- trades away: bespoke component styling vs. browser and manager heuristics
- risks: A beautifully custom login that no password manager can fill.
- Forms and input / Autofill, inference and smart defaults - Q06114
- source: web.dev: Sign-in form best practices https://web.dev/articles/sign-in-form-best-practices

**Is paste disabled on this password field, and which specific threat does that stop?**
- trades away: perceived security theatre vs. actual usability harm
- risks: Blocking password managers and forcing weaker, memorable passwords.
- Forms and input / Autofill, inference and smart defaults - Q06115
- source: W3C: Understanding SC 3.3.8 Accessible Authentication (Minimum) https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html

**Which value are you asking a user to type twice within the same process?**
- trades away: per-step independence vs. carrying answers forward
- risks: Redundant entry that penalises anyone slow to type or reliant on memory aids.
- Forms and input / Autofill, inference and smart defaults - Q06116
- source: W3C: Understanding SC 3.3.7 Redundant Entry https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html

**Can a keyboard user even reach the disabled button to discover that it exists?**
- trades away: visual state signalling vs. focusability
- risks: A non-focusable button that keyboard users never find, leaving no visible way to proceed.
- Forms and input / Labels, hints and input format masking - Q06225
- source: Adam Silver: The problem with disabled buttons https://adamsilver.io/blog/the-problem-with-disabled-buttons-and-what-to-do-instead/

**Does focus jump automatically between these boxes, and what happens when someone mistypes a digit?**
- trades away: perceived speed vs. recoverable mistakes
- risks: Auto-advance that moves focus early and strands the user hunting for the box to fix.
- Forms and input / Labels, hints and input format masking - Q06226
- source: Adam Silver: Multiple inputs versus one input https://adamsilver.io/blog/form-design-multiple-inputs-versus-one-input/

**After a failed submit, does keyboard focus move to the error summary, or stay where it was?**
- trades away: not stealing focus vs. announcing failure at all
- risks: A screen reader user who never learns the submission failed.
- Forms and input / Validation timing and inline error recovery - Q06318
- source: GOV.UK Design System: Error summary component https://design-system.service.gov.uk/components/error-summary/

**Can a user click an item in the error summary and land directly on the field it names?**
- trades away: a summary as decoration vs. a summary as navigation
- risks: An error list that reports problems without helping anyone reach them.
- Forms and input / Validation timing and inline error recovery - Q06319
- source: GOV.UK Design System: Error summary component https://design-system.service.gov.uk/components/error-summary/

**Does a screen reader announce this error, or does it appear silently below the input?**
- trades away: visual proximity vs. programmatic association
- risks: An error that exists visually and not at all for assistive technology.
- Forms and input / Validation timing and inline error recovery - Q06320
- source: Home Office: Error messages guidance https://design.homeoffice.gov.uk/accessibility/interactivity/error-messages

**Does logging in here require remembering, transcribing or solving anything, and which of those did you assume was unavoidable?**
- trades away: security ritual vs cognitive burden
- risks: An authentication flow that is a memory test wearing a security costume.
- Forms and input / Validation timing and inline error recovery - Q06321
- source: W3C Understanding SC 3.3.8 Accessible Authentication (Minimum) https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html

**How long does this undo toast stay on screen, and is that enough time for someone who reads slowly and aims slowly?**
- trades away: unobtrusive toast timing vs realistic reaction time
- risks: A four-second undo window that expires before a switch user reaches it.
- Forms and input / Validation timing and inline error recovery - Q06323
- source: W3C Understanding SC 2.2.1 Timing Adjustable https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html
exit 0
```

Nothing was printed on stderr, so every coordinate held and the slice is the one that was asked for.

```
$ mise run slice --category "Forms and input" --lens accessibility --limit 500 --format json | python3 -c "import json,sys; print(json.load(sys.stdin)['count'])"
74
exit 0
```

The second run answers a question the first cannot: how much material sits behind the slice, which decides whether fifteen is a sample or the whole shelf. It is a sample of 74.

```
$ mise run check-reply --file draft.md --full-slice
draft passed every rule
exit 0
```

## Executor replies

The reply is the three template lines followed by the fifteen questions above, unanswered.

```
Posture: ask
Ledger: untouched, 0 rows added, 0 marked inherited
Found: fifteen questions on forms and input under the accessibility lens, no widening, out of 74 that exist on that shelf
[the fifteen questions above follow, unanswered]
```

## Files created

None. Ask returns questions and writes no ledger rows, because nothing was decided.

## When to use ask instead of judge

Ask is the escape hatch. Use it when the user says give me, list, or what should I be asking. Use judge when they hand over work and want an answer. Handing over a screenshot and saying what should I be asking is ask, because the words beat the attachment.
