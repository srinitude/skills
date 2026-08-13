# Example: make it rarer

Guess removed: that raising the rarity floor always returns something usable. It can return no candidates, and that empty result is the correct boundary when every rarer face fails a hard fit rule.

## The user says

> make it rarer

## The reply

I raised the floor to percentile 96 and reran the current fit-first ranking. No usable serif text family survives. The command rejected the charted and dingbat faces for legibility and the guide face for missing the required script subset, so I kept the existing pair instead of claiming an unusable replacement.

## Command run

```text
$ python3 scripts/rare_google_fonts.py discover \
    --skeleton Serif \
    --need-weight 400 \
    --need-weight 700 \
    --min-rarity-percentile 96 \
    --limit 3 \
    --show-rejected
{
  "candidates": [],
  "ranked_by": "fit_band descending, then rarity_percentile, then rank",
  "rejected": [
    {
      "family": "Jacquarda Bastarda 9 Charted",
      "rarity_percentile": 97.1,
      "reason": "legibility 0.4 is below the text floor 0.7"
    },
    {
      "family": "Yarndings 12",
      "rarity_percentile": 97.8,
      "reason": "legibility 0.4 is below the text floor 0.7"
    },
    {
      "family": "Playwrite RO Guides",
      "rarity_percentile": 100.0,
      "reason": "missing a required script subset"
    }
  ],
  "retrieved_at": "2026-08-12",
  "source": "https://fonts.google.com/metadata/fonts?sort=popularity",
  "total_families": 1942
}
exit=0
```

## What to report back

No replacement clears the stated floor and the text-role fit gates. Keep Wittgenstein and Parastoo, or relax one requirement explicitly and rerun. Do not turn a rarity number into permission to use charted glyphs, dingbats, or a family that misses the requested script.

## Files created

None. The run only ranks.
