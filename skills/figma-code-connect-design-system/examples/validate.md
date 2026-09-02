# Validate example

## Request

Validate the current run ledger and external targets without changing them.

## Command

```sh
mise run validate-run -- /tmp/run.json
```

## Output

```text
run validation: 0 problems
```

The model still re-reads repository files, Figma nodes, mappings, and rendered pixels because the script proves ledger structure only.
