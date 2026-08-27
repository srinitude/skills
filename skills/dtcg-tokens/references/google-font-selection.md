# Live Google Font selection

Use this procedure in Steps 10, 11, 13, 14, 17, 18, and 23. It turns the current Google Fonts catalog into an uncommon, source-fitting typography decision while keeping the proof artifact offline.

## Fixed rarity rule

`assets/google-font-policy.json` is the canonical machine policy. Fetch the live first-party catalog during every `generate` or `prove` run. A remembered list, cached recommendation, prior run, or hard-coded family list cannot establish current rarity.

Rank 1 is the most popular family. Let `N` be the number of families in the fetched catalog and let `cutoff = floor(N * 0.5)`. A family is eligible only when its live `popularity_rank` is greater than `cutoff`, so every eligible family is outside the most popular 50% of that exact catalog capture.

If the catalog cannot be fetched, its schema changed, the response lacks a server date, or the run crosses local midnight before final readback, set `E_FONT_CURRENT`. Reacquire the run clock and rerun font selection after midnight. Never substitute a previously uncommon family without a fresh rank check.

## Selection sequence

1. Start with the full live catalog and record the fresh local run date, exact response bytes, server date, family count, and SHA-256. The response must be no more than 600 seconds from the current clock.
2. Narrow by the source's scripts, languages, required glyphs, categories, stroke structure, classifications, available styles, and axes. Keep at least three structurally different eligible candidates. Do not use popularity alone as design judgment.
3. Run `scripts/prepare_google_fonts.py` with every candidate and each selected CSS2 family specification. The script rejects candidates inside the popular half, closed or brand families, missing source-script support, missing licenses, invalid WOFF2 bytes, and non-standalone CSS.
4. Render all candidates with source-specific language, long and short strings, numerals, punctuation, mixed case, smallest claimed text, largest claimed display text, and every selected weight or style. The vision executor inspects whole-frame, detail, and comparative specimens for voice, hierarchy, legibility, spacing, collisions, fallback, script fit, source fit, and a credible alternative.
5. Select at least one passing family. Put every selected family in source-supported `fontFamily` tokens, every affected composite `typography` token, and the standalone proof. Additional source-mandated families may coexist, but they do not satisfy this gate.
6. Copy the script's inlined `@font-face` blocks into the authored proof candidate. Keep the exact WOFF2 data URLs, asset hashes, license identifiers, license text, and source URLs. Do not add a stylesheet link, `@import`, fetch, relative font path, or runtime request.
7. Fill the script manifest's token paths and visual-review fields, then copy the final record into `evidence.google_fonts`. Set the selection review to `pass` only after the final HTML renders the selected bytes and the final visual comparison passes.

## Command

| Input                                               | Command                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Three or more candidates and one or more selections | `python3 scripts/prepare_google_fonts.py --run-date YYYY-MM-DD --candidate "Rare Family A" --candidate "Rare Family B" --candidate "Rare Family C" --select-spec "Rare Family A:wght@400;700" --required-subset latin --output-catalog <name>.google-fonts.catalog.json --output-manifest <name>.google-fonts.json --output-css <name>.google-fonts.css` |

The catalog capture, manifest, and CSS are run records, not extra final deliverables. The final HTML remains one file because its font CSS contains data URLs.

## PASS

PASS only when the live capture and evidence agree, every candidate rank is greater than the current cutoff, at least three candidates were visually compared, every selected family passes source and script fit, selected paths exist in token JSON, each recorded WOFF2 SHA-256 matches an embedded data URL, every license is recorded, the proof uses the selected families, and the final pixels show no fallback or typography defect.

## BLOCKED

Return `E_FONT_CURRENT` for a missing or stale live catalog, `E_FONT_RARITY` for an ineligible or too-small candidate set, `E_FONT_ASSET` for a missing font, license, hash, or offline embedding, and `E_REVIEW` for a visual failure. Fix the earliest failed record and rerun its dependents. Do not lower the 50% threshold, choose a common fallback, or mark a pending visual decision as passed.

## Sources

- The live catalog endpoint is `https://fonts.google.com/metadata/fonts`.
- The popularity ordering and WOFF2 capability are documented at `https://developers.google.com/fonts/docs/developer_api`.
- CSS2 family specifications are documented at `https://developers.google.com/fonts/docs/css2`.
- Font files, metadata, and per-family licenses come from `https://github.com/google/fonts`.
