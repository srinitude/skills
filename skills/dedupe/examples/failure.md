# Example: unsupported adapter

## User says

```text
Use the database adapter to dedupe [1, 1].
```

## Request

Resource gate: run `mise run validate` before using package files named here.

The command reads `examples/invalid-request.json`.

```json
{
  "adapter": "database",
  "mode": "exact",
  "items": [1, 1]
}
```

## Command

```text
$ mise run dedupe inspect --request examples/invalid-request.json
error: unsupported adapter: database
exit 1
```

## Reply

Inspection stopped because `database` is not an adapter. No report or mutation was produced. Use `record` with an explicit bounded array, schema, and identity fields, or provide another supported adapter.
