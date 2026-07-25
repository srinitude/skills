# Example: help

Guess removed: that the skill can answer any request about the design system without naming its own command grammar first.

## The user says

> what can you do

## The reply

I read one or more reference images and write a design system document that validates against the schema in references/extraction-schema.yaml, then prove it renders. Six commands:

| Command  | Words that trigger it                                      | What it returns                                                                          |
| -------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| help     | what can you do, help                                      | This table plus the schema version.                                                      |
| extract  | extract, pull the system out of this, tokenize this design | A design system file, the validator report, and a rendered preview judged by eye.        |
| fonts    | find fonts, what typeface is this, make it rarer           | A brief, the ranked candidates with fit scores, the chosen set, and the pairing verdict. |
| preview  | render this, screenshot it, does it actually work          | The generated page, the screenshot path, and a verdict per criterion.                    |
| validate | validate, check this file                                  | The validator report and the fix for each error.                                         |
| maintain | add a rule, change the schema                              | The changed files, the new tests, and the five checks run green.                         |

Every command answers with the same three parts: what I did, the files I touched, and the checks I ran with their exit codes. extract and fonts add the fit, pairing, and viability records.

## Command run

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py field meta.rarity_floor
meta.rarity_floor: Record the rarity percentile floor the run enforced, `70.0` unless the user set another
  value. The validator reads this number and raises its own floor to match, so a recorded floor is a binding
  claim rather than a note. It never lowers the floor the contract or the `--min-rarity-percentile` flag
  sets.
exit=0
```

## Files created

None. help writes nothing.
