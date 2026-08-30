# Help

Guess this example removes: whether `help` rewrites or executes anything, and how it describes the bounded guarantee.

## User says

```
/only-one-interpretation help
```

## Visible reply

```
Commands:
- help: show this help.
- rewrite <prompt>: return one disambiguated prompt or one complete clarification turn.
- Plain input is treated as rewrite <prompt>.

READY returns exactly one fenced rewritten prompt. It means the stated context, interpretation ledger, ambiguity inventory, semantic round trip, alternate-reading attacks, and constraint trace found no material alternate operational reading. It does not claim universal uniqueness.

NEEDS_CLARIFICATION asks every unresolved material question in one turn, then stops without rewriting or executing the prompt.
```

## Commands and files

No shell command ran, so there is no process exit code. No file was created. The input prompt was not executed.
