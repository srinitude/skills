# Example: fonts

Guess removed: that the rarest available family is the right family. Fit and legibility decide first, and rarity only breaks a tie between candidates that already fit.

## The user says

> find me fonts for this poster, a serif headline with a quieter serif for the body

## The reply

I mapped the visible type evidence into `assets/font-brief.json`, pinned the closest readable display and text matches, ran the live catalog set command, and checked the pair. Wittgenstein takes display, Parastoo takes text, and all seven pairing dimensions pass.

## Command run

```text
$ python3 scripts/rare_google_fonts.py set \
    --brief assets/font-brief.json \
    --output examples/work/set.json
exit=0
$ python3 -c "import json;d=json.load(open('examples/work/set.json'));print([(c['family'],c['rarity_percentile']) for c in d['chosen']]);print(d['vetoes']);print(d['pairing']['passes'])"
[('Wittgenstein', 70.2), ('Parastoo', 81.5)]
[]
True
exit=0
```

The role filters make the visual decision reproducible. Both selected families clear the percentile 70 floor on the explicit popularity-sorted feed route, and the decision record stores the fit and pairing result.

## Verification

```text
$ python3 scripts/rare_google_fonts.py verify \
    --family Wittgenstein --family Parastoo
{
  "checked": 2,
  "failed": 0,
  "verdicts": [
    {
      "family": "Wittgenstein",
      "rarity": {
        "popularity_rank": 1483,
        "rank_ceiling": 2113,
        "rarity_percentile": 70.2,
        "retrieved_at": "2026-08-12",
        "source": "https://fonts.google.com/metadata/fonts?sort=popularity"
      },
      "status": "PASS"
    },
    {
      "family": "Parastoo",
      "rarity": {
        "popularity_rank": 1723,
        "rank_ceiling": 2113,
        "rarity_percentile": 81.5,
        "retrieved_at": "2026-08-12",
        "source": "https://fonts.google.com/metadata/fonts?sort=popularity"
      },
      "status": "PASS"
    }
  ]
}
exit=0
```

## Files created

| File                   | Contents                                                                                             |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| examples/work/set.json | The current font decision record: chosen set, fit results, veto list, pairing result, and retrieval. |
