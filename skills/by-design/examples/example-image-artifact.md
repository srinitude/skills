# Example: the artifact is a picture

Removes the guess: what to run when the work arrives as a screenshot rather than as words. The coordinates come from words, so the state visible in the picture has to be written down before step 3 can use it.

This is a real run on a seat selection modal from a corporate travel tool.

## What the picture shows

A two column modal titled Select seats, a legend, a passenger card reading auto assigned, a virtual tour tile, an economy grid of rows one to seven, a footer reading total seat cost dollar zero, and a quiet Done beside a loud Next flight.

Every seat in the visible cabin carries the unavailable mark.

## Step 3, written as two lines first

```
What this is: a seat picker inside a flight booking flow.
What state it is in: empty, because nothing on it can be chosen.
```

The first attempt described the picture without that second line and landed on layout, because a grid, a legend and a tile are what the description said.

```
$ python3 scripts/locate.py --file brief.txt --top 3
  2.98   3 terms  Empty, loading, error and edge states  [unavailable, flight, tile]
  2.76   3 terms  Layout, grid, hierarchy and density  [grid, tile, legend]
  1.86   2 terms  Spatial, ambient and built space  [virtual, tile]
weak read: the top two places are too close to separate, so name the artifact type with --hint and run this again
exit 0
```

The warning is doing its job. Naming the state fixes it.

```
$ python3 scripts/locate.py --file brief.txt --hint "empty error states" --top 2
 32.98   4 terms  Empty, loading, error and edge states  [hint, unavailable, flight, tile]
  2.76   3 terms  Layout, grid, hierarchy and density  [grid, tile, legend]
exit 0
```

## What the slice asked that the eye had not

```
$ python3 scripts/slice.py --category "Empty, loading, error and edge states" --stage refinement --match "empty" --limit 1
# 1 questions

**Is the no-results message typographically loud enough that someone scanning past the header will actually register it?**
- trades away: restrained visual tone vs. cutting through a strong scanning habit
- risks: Users scanning past a small grey 'no matches found' line and mistaking ads for results.
- Empty, loading, error and edge states / User-emptied and filtered-to-empty - Q06070
- source: NN/g: 3 Guidelines for Search Engine "No Results" Pages https://www.nngroup.com/articles/search-no-results-serp/
exit 0
```

That is the question the screenshot deserved and the eye had not put into words: the message is missing entirely, so there was nothing to be loud.

## The reply

```
Posture: judge
Ledger: decision-ledger-seatmap.md, 5 rows added, 3 marked inherited
Found: five decisions, and the load-bearing one was never made: a cabin with nothing left is being rendered as a working picker, so the screen makes the traveller read a grid of identical marks to learn something one sentence could tell them.
Every seat here is gone, and the screen still says Select seats: what should this modal say instead, and which button should be the loud one when the answer is nothing is available?
```

Five rows, three inherited, one question. The row that mattered was the one nobody had made: a cabin with nothing left is being drawn as a working picker.
