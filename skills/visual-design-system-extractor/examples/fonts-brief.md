# Example: fonts

Guess removed: that the rarest available family is the right family. Fit and legibility decide first, and rarity only breaks a tie between candidates that already fit.

## The user says

> find me fonts for this poster, a serif headline with a quieter serif for the body

## The reply

I filled the brief in assets/font-brief.json from the visible evidence, ranked the catalog by fit, dropped every candidate under the role legibility floor, then broke the remaining tie by rarity. Ramsina takes display, Epunda Slab takes text, and the set passes the pairing check. The rejections are listed so the tradeoff is visible.

## Commands run

```
$ python3 scripts/rare_google_fonts.py discover --skeleton Serif --need-weight 400 --need-weight 700 --limit 2 --show-rejected
{
  "candidates": [
    {
      "category": "Serif",
      "family": "Namdhinggo",
      "fit": {
        "common_default": false,
        "family": "Namdhinggo",
        "fit_band": 1.0,
        "fit_score": 1.0,
        "legibility_floor": 0.7,
        "legibility_score": 0.8,
        "passes": true,
        "reject_reason": "",
        "role": "text",
        "script_score": 1.0,
        "skeleton_score": 1.0,
        "style_score": 1.0,
        "weight_score": 1.0,
        "width_score": 1.0
      },
      "rarity": {
        "date_added": "2024-02-14",
        "popularity_rank": 1872,
        "rank_ceiling": 2113,
        "rarity_percentile": 88.6,
        "retrieved_at": "2026-07-25",
        "source": "https://fonts.google.com/metadata/fonts",
        "total_families": 1942,
        "trending_rank": 357,
        "variable": false
      }
    },
    {
      "category": "Serif",
      "family": "Epunda Slab",
      "fit": {
        "common_default": false,
        "family": "Epunda Slab",
        "fit_band": 1.0,
        "fit_score": 1.0,
        "legibility_floor": 0.7,
        "legibility_score": 1.0,
        "passes": true,
        "reject_reason": "",
        "role": "text",
        "script_score": 1.0,
        "skeleton_score": 1.0,
        "style_score": 1.0,
        "weight_score": 1.0,
        "width_score": 1.0
      },
      "rarity": {
        "date_added": "2025-08-25",
        "popularity_rank": 1867,
        "rank_ceiling": 2113,
        "rarity_percentile": 88.4,
        "retrieved_at": "2026-07-25",
        "source": "https://fonts.google.com/metadata/fonts",
        "total_families": 1942,
        "trending_rank": 2000,
        "variable": true
      }
    }
  ],
  "ranked_by": "fit_band descending, then rarity_percentile, then rank",
  "rejected": [
    {
      "family": "Kalnia Glaze",
      "rarity_percentile": 84.1,
      "reason": "legibility 0.5 is below the text floor 0.7"
    },
    {
      "family": "Elsie Swash Caps",
      "rarity_percentile": 72.9,
      "reason": "legibility 0.5 is below the text floor 0.7"
    }
  ],
  "retrieved_at": "2026-07-25",
  "source": "https://fonts.google.com/metadata/fonts",
  "total_families": 1942
}
exit=0
```

Kalnia Glaze and Elsie Swash Caps are rarer than nothing here and still lose: a decorative serif cannot hold a reading measure, and no rarity number buys past the 0.7 text floor.

Both survivors sit in the same 1.0 fit band, so rarity breaks the tie and Namdhinggo, at percentile 88.6 against 88.4, leads. Slot filling then runs as a set, which is where the ranking and the final choice diverge.

```
$ python3 scripts/rare_google_fonts.py verify --family Ramsina --family "Epunda Slab"
{
  "checked": 2,
  "failed": 0,
  ...
}
exit=0
```

The full verify payload for both families is in examples/work/log1.txt with the discover runs.

## Files created

| File                   | Contents                                                                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| examples/work/log1.txt | The captured stdout of the field lookup, both discover runs, and the verify run, each with its exit code. |
| examples/work/set.json | The decision record written by the set command.                                                           |

## Why the winner beat the runner up

Namdhinggo ranks first for the text slot on fit 1.0 and percentile 88.6. It does not ship in the final set, because the set level pairing check vetoed it against the display face. That case is worked in examples/pairing-veto.md.
