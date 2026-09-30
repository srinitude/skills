# Example: checking the package

- This example answers one question: which commands prove this package is sound before a change ships?

## The request

- User: "Check the human-language package before I change it."

## The run

- The executor ran three quick checks from the skill folder. `mise run ci` runs these and the rest of the package gate.

### Package structure

- Command: `mise run -q validate`
- Output, exit code 0:

```text
PASS human-language: 0 problems
```

### Eval files

- Command: `mise run -q evals`
- Output, exit code 0:

```text
eval checks: 0 problems
```

### Writing lint

- Command: `mise run -q lint-writing`
- Output, exit code 0:

```text
checked 13 files, 0 problems
```

## The reply

- "The package passes its structure, eval, and writing checks. Run `mise run ci` for the full gate before you ship a change."
