# Plan example

## Request

Plan an update for the account settings UI from a PRD and codebase. Do not change Figma or the repository.

## Command

```sh
mise run new-run -- --output /tmp/run.json --mode update --platform web --ui-scope account-settings --source prd=/workspace/prd.md --source codebase=/workspace/product
```

## Output

```json
{ "created": "/tmp/run.json", "run_id": "ds-update-account-settings", "status": "planned" }
```

The model then inspects the two sources, records conflicts and capability dispositions, inventories required screens, and leaves every mutation permission as `not_granted`.
