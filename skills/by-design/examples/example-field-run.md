# Example: the whole procedure against one brief

Guess this example removes: what every step looks like in one run, and how many questions collapse into how few decisions.

## The artifact

Resource gate: run `mise run validate` before using package files named here.

`evals/files/brief-05-packaging.txt`, a sun cream for runners packaged to look as though it has melted. It ships with this skill, so every command below runs from a clean checkout and prints what is pasted here.

## User says

```
here is the sun cream packaging brief, we lock the artwork this week, what have we not decided
```

## Commands run

```
$ mise run gate --text "$(cat evals/files/brief-05-packaging.txt)"
design: matched strong:brand, weak:copy, weak:label
exit 0

$ mise run ledger show --file decision-ledger-suncream.md
no ledger at decision-ledger-suncream.md
exit 1

$ mise run ledger init --file decision-ledger-suncream.md --slug suncream
created decision-ledger-suncream.md
exit 0

$ mise run locate --file evals/files/brief-05-packaging.txt --top 2
 15.47   8 terms  Physical product, packaging and print  [retail, recycl, silhouette, label, regulatory, bottle]
  3.59   3 terms  Icons, illustration and photography  [thumbnail, marketplace, packag]
exit 0

$ mise run slice --category "Physical product, packaging and print" --match "claim" --limit 3
# 3 questions

**How does the low-carbon toggle change what gets downloaded, not merely what gets displayed?**
- trades away: a visible gesture of restraint vs. bytes actually saved
- risks: A toggle that greys out images already sitting in the cache.
- Physical product, packaging and print / Regulatory panels and sustainability claims - Q12406
- source: CSS { In Real Life }: Greenwashing and the COP28 website https://css-irl.info/greenwashing-and-the-cop28-website/

**Which claim on our sustainability page could survive an audit of the page it is printed on?**
- trades away: the message vs. the medium carrying it
- risks: A twelve-megabyte page about reducing digital emissions.
- Physical product, packaging and print / Regulatory panels and sustainability claims - Q12407
- source: CSS { In Real Life }: Greenwashing and the COP28 website https://css-irl.info/greenwashing-and-the-cop28-website/

**Which environmental word on this pack could a regulator ask you to substantiate tomorrow?**
- trades away: warm generic language vs. provable specificity
- risks: The words eco-friendly and climate-friendly printed into a plate you cannot cheaply change.
- Physical product, packaging and print / Regulatory panels and sustainability claims - Q12408
- source: Dentons: When one word can cost you 10 percent of your turnover https://www.dentons.com/en/insights/articles/2026/may/5/when-one-word-can-cost-you-10-percent-of-your-turnover-the-new-rules-on-environmental-marketing
exit 0

$ mise run ledger add --file decision-ledger-suncream.md --decision "The bottle silhouette is distorted on purpose" --chosen "melted shape, kept at every size" --trades "a memorable shelf presence vs. a unit that reads as damaged" --risks "returns from buyers who think the bottle failed in transit" --origin deliberate --falsifier "return rate against the undistorted line"
appended to decision-ledger-suncream.md
exit 0

$ mise run ledger add --file decision-ledger-suncream.md --decision "The joke has to survive at thumbnail size" --chosen "distortion tuned for the marketplace listing first" --trades "shelf drama vs. legibility at 100 pixels" --risks "a silhouette that reads as a rendering error in the grid" --origin deliberate
appended to decision-ledger-suncream.md
exit 0

$ mise run ledger add --file decision-ledger-suncream.md --decision "Which environmental words go on the pack" --chosen "" --trades "warm generic language vs. provable specificity" --risks "a word printed into a plate that a regulator can ask you to substantiate" --origin inherited --source "Q12408 https://www.dentons.com/en/insights/articles/2026/may/5/when-one-word-can-cost-you-10-percent-of-your-turnover-the-new-rules-on-environmental-marketing"
appended to decision-ledger-suncream.md
exit 0

$ mise run ledger add --file decision-ledger-suncream.md --decision "Mono material is stated as a target rather than a constraint" --chosen "" --trades "a recyclability claim vs. the finishes the distortion wants" --risks "a target quietly dropped late, with the claim left on the label" --origin inherited
appended to decision-ledger-suncream.md
exit 0

$ mise run ledger add --file decision-ledger-suncream.md --decision "How the regulatory panel sits on a distorted surface" --chosen "" --trades "the melted idea vs. a legally required block of small type" --risks "SPF rating and warnings bent into the part of the bottle nobody photographs" --origin inherited
appended to decision-ledger-suncream.md
exit 0

$ mise run speak --file decision-ledger-suncream.md --rank
1. Mono material is stated as a target rather than a constraint (3 columns unknown)
2. How the regulatory panel sits on a distorted surface (3 columns unknown)
3. Which environmental words go on the pack (2 columns unknown)
exit 0

$ mise run speak --file decision-ledger-suncream.md --decision "How the regulatory panel sits on a distorted surface" --origin inherited --live yes
ask: inherited, live, and recorded once including this one
exit 0

$ mise run check-reply --file draft.md
draft passed every rule
exit 0
```

## Executor replies

```
Posture: judge
Ledger: decision-ledger-suncream.md, 5 rows added, 3 marked inherited
Found: the distortion and its thumbnail budget were both chosen; the environmental wording, the mono material target and the place the regulatory panel lands were not.
The melted silhouette has to carry SPF rating, warnings, ingredients and directions: where on a deliberately distorted surface does that block of small type sit?
```

## Files created

`decision-ledger-suncream.md`, in full:

```
# Decision ledger: suncream

One row per decision. A row marked inherited is a choice nobody made on purpose.

| The decision | What was chosen | What it trades away | What it risks | Deliberate or inherited | What would change it | Source |
|---|---|---|---|---|---|---|
| The bottle silhouette is distorted on purpose | melted shape, kept at every size | a memorable shelf presence vs. a unit that reads as damaged | returns from buyers who think the bottle failed in transit | deliberate | return rate against the undistorted line | - |
| The joke has to survive at thumbnail size | distortion tuned for the marketplace listing first | shelf drama vs. legibility at 100 pixels | a silhouette that reads as a rendering error in the grid | deliberate | - | - |
| Which environmental words go on the pack | - | warm generic language vs. provable specificity | a word printed into a plate that a regulator can ask you to substantiate | inherited | - | Q12408 https://www.dentons.com/en/insights/articles/2026/may/5/when-one-word-can-cost-you-10-percent-of-your-turnover-the-new-rules-on-environmental-marketing |
| Mono material is stated as a target rather than a constraint | - | a recyclability claim vs. the finishes the distortion wants | a target quietly dropped late, with the claim left on the label | inherited | - | - |
| How the regulatory panel sits on a distorted surface | - | the melted idea vs. a legally required block of small type | SPF rating and warnings bent into the part of the bottle nobody photographs | inherited | - | - |
```

## What the run proved about the steps

Step 3 exists so the shelf comes from the artifact. The brief never says packaging in the first line, and the ranking still put physical product first at 15.47 on eight terms, four times the score of the second place.

Step 4 takes `--match` for the same reason. The category alone returns what is common in that category. The word claim, taken from the brief's own regulatory language, returned three questions about substantiating an environmental word, and the third of them wrote a ledger row on its own.

Step 5 is where the count drops. Three questions and a reading of the brief produced five decisions, and only two of them were made on purpose.

Step 8 ranks because three rows came back inherited and the reply carries one question. The first two rank equally at three unknown columns, and the tie went to the row the artwork lock actually forces this week.
