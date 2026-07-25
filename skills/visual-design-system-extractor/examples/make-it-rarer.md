# Example: make it rarer

Guess removed: that raising the rarity floor always returns something usable. It returns fewer candidates, and the ones it drops are usually dropped for legibility, not for rarity.

## The user says

> make it rarer

## The reply

I raised the floor to percentile 96 and reran the ranking. One family survives, Ramsina at percentile 98.1, and its fit falls to 0.9 because it ships a single weight, so weight_score is 0.5. The three rarer families the floor admitted were all dropped for legibility. Rarer than 96 is available, usable and rarer than 96 is not, so this is the honest ceiling for this brief.

## Command run

```
$ python3 scripts/rare_google_fonts.py discover --skeleton Serif --need-weight 400 --need-weight 700 --min-rarity-percentile 96 --limit 3 --show-rejected
{
  "candidates": [
    {
      "category": "Serif",
      "family": "Ramsina",
      "fit": {
        "common_default": false,
        "family": "Ramsina",
        "fit_band": 0.9,
        "fit_score": 0.9,
        "legibility_floor": 0.7,
        "legibility_score": 0.7,
        "passes": true,
        "reject_reason": "",
        "role": "text",
        "script_score": 1.0,
        "skeleton_score": 1.0,
        "style_score": 1.0,
        "weight_score": 0.5,
        "width_score": 1.0
      },
      "rarity": {
        "date_added": "2026-02-12",
        "popularity_rank": 2073,
        "rank_ceiling": 2113,
        "rarity_percentile": 98.1,
        "retrieved_at": "2026-07-25",
        "source": "https://fonts.google.com/metadata/fonts",
        "total_families": 1942,
        "trending_rank": 275,
        "variable": false
      }
    }
  ],
  "ranked_by": "fit_band descending, then rarity_percentile, then rank",
  "rejected": [
    {
      "family": "Jacquarda Bastarda 9 Charted",
      "rarity_percentile": 96.1,
      "reason": "legibility 0.4 is below the text floor 0.7"
    },
    {
      "family": "Yarndings 12",
      "rarity_percentile": 97.3,
      "reason": "legibility 0.4 is below the text floor 0.7"
    },
    {
      "family": "Yarndings 12 Charted",
      "rarity_percentile": 97.2,
      "reason": "legibility 0.4 is below the text floor 0.7"
    }
  ],
  "retrieved_at": "2026-07-25",
  "source": "https://fonts.google.com/metadata/fonts",
  "total_families": 1942
}
exit=0
```

## What to report back

Ramsina holds display, where a single weight is survivable, and Epunda Slab keeps text, where 300 to 900 carries the hierarchy. Yarndings 12 is rarer by 0.8 of a percentile than nothing usable at all: it is a dingbat set, and a rarity number cannot make it read.

## Files created

None. The run only ranks.
