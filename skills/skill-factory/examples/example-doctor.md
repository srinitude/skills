# Example: doctor readiness and blocking

Guess this example removes: whether work continues when Mise is missing and which receipt proves readiness.

## User says

```
before I ask for anything big: is this environment ready for building skills?
```

## Executor replies

```
Ready. The required interpreter, Mise runner, factory commands, templates, and references are present.

$ mise run doctor
{
  "ready": true,
  "mode": "mise",
  "checks": [
    {"name": "python", "required": true, "ok": true},
    {"name": "mise", "required": true, "ok": true},
    {"name": "scripts", "required": true, "ok": true},
    {"name": "templates", "required": true, "ok": true},
    {"name": "references", "required": true, "ok": true}
  ]
}
exit 0
```

## Commands run

```
$ mise run doctor
{"ready": true, "mode": "mise", "checks": [{"name": "python", "required": true, "ok": true}, {"name": "mise", "required": true, "ok": true}, {"name": "git", "required": false, "ok": true}, {"name": "scripts", "required": true, "ok": true}, {"name": "templates", "required": true, "ok": true}, {"name": "references", "required": true, "ok": true}]}
exit 0
```

## Files created

None.

## What the run proves

The doctor task proves only environment readiness. If Mise or another required owner is absent, it exits 1 with `ready` false and the build stops. There is no direct-command fallback because every deterministic action must stay behind its owning Mise task.
