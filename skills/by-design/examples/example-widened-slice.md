# Example: the failure this skill causes most, a silently widened slice

Guess this example removes: the case where the tool returns a confident answer to a question nobody asked, and how to catch it.

## What goes wrong

`mise run slice` widens the pin when a three coordinate slice falls under its floor of 12. It has to. Of the 1400 category, stage, and artifact type cells in the corpus, 786 hold fewer than 12 questions and some hold none.

The widened result looks the same as a precise one. Same format, same confidence, same shape. The only difference is one line on stderr, and an executor that reads stdout alone will report colour questions as concept stage artifact questions and never know.

## The run

```
$ mise run slice --category "Color, theming and dark mode" --stage concept --applies-to artifact --lens ethics --limit 3
widened: dropped lens, applies-to
# 3 questions
Widened by dropping: lens, applies-to.

**Are theme and mode separate axes here, or tangled into one flat list of colour files?**
- trades away: one dimension of variation vs. two orthogonal ones
- risks: Six brands times three modes becoming eighteen hand-maintained files that drift apart.
- Color, theming and dark mode / Multi-brand and white-label theming contracts - Q03853
- source: dbanks design: Dark Mode with Style Dictionary https://dbanks.design/blog/dark-mode-with-style-dictionary/

**Which tokens must a new tenant supply, and which must they never be permitted to touch?**
- trades away: customization surface vs. safety floor
- risks: A tenant overriding focus-ring color and quietly removing keyboard accessibility.
- Color, theming and dark mode / Multi-brand and white-label theming contracts - Q03854
- source: Workday Canvas: Color Tokens https://canvas.workday.com/guidelines/color/color-tokens

**What does primary mean in your system: the brand's color, or the color of the most important action?**
- trades away: brand ownership of a word vs. functional ownership
- risks: Brand and product each using primary for different things, producing two competing accents.
- Color, theming and dark mode / Semantic color tokens and state colors - Q03920
- source: Material Design 3: Color roles https://m3.material.io/styles/color/roles
exit 0
```

The ethics lens is gone. The artifact pin is gone. What came back is multi tenant theming, which is a real answer to a different question.

## What the executor must do

Say it. One clause is enough: "no ethics lens material exists for colour at concept stage, so this is the wider colour slice." Then either accept the wider slice or re pin.

## The fix that is not a fix

Do not raise `--floor` to force a narrow slice. A floor of 3 returns three questions and a false sense that the shelf was full. The floor exists so the slice is worth reading. The report exists so the widening is visible. Removing either one hides the problem rather than solving it.
