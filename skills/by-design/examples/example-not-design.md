# Example: the request is not design work

Guess this example removes: what happens on the majority of turns, and how much a non-design request costs.

## User says

```
fix the failing test in auth.py, it broke after the merge
```

## Executor replies

```
[nothing from this skill]
```

## Commands run

```
$ python3 scripts/gate.py --text "fix the failing test in auth.py, it broke after the merge"
not-design: another craft named, matched exclusions:failing test
exit 0
```

One command, one line, and the run ends at step 0. No ledger is read, no question file is opened, and nothing is added to the reply.

## Files created

None.

## Why the gate names the terms it matched

Matching the request against a fixed vocabulary gives the same verdict every time, and printing the matched terms lets the verdict be checked rather than trusted. A borderline case makes this concrete:

```
$ python3 scripts/gate.py --text "design a database schema for users and orders"
not-design: another craft named, matched exclusions:database schema
exit 0
```

The word design appears and the request still stops, because naming another craft outranks a bare verb. Only a strong design surface overrides a named craft, and the opposite case passes on a surface alone:

```
$ python3 scripts/gate.py --text "here's a screenshot, what do you think"
design: matched weak:screenshot
exit 0
```

## The bias, stated

The gate continues by default and stops only when another craft is named and no design surface appears. Continuing costs one ledger row and no question. Stopping costs a decision nobody recorded. The cheaper mistake is the one worth making, so the gate leans toward continuing.
