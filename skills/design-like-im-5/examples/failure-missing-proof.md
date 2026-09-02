# Missing proof example

Guess removed: A missing proof bar must stop the run without files.

## Request

> Start this run now. I have not set the proof bar.

## Command

```sh
mise run run-start --intake evals/files/missing-proof.json --run-dir run
```

## Real output

```text
blocked: missing proof_threshold
```

The command exits with code `1`. It creates `0` files.

## Visible reply

The run is blocked. Add a clear proof bar to the intake.
