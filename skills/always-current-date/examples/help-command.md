# Help command

## Intent

Inspect the runtime contract without skipping the direct-turn clock.

## Input

```text
help
```

## Command

Run with the skill directory as the process working directory.

```bash
python3 scripts/current_anchor.py --timezone UTC
```

## Real output

```json
{
  "captured_at": "2026-07-30T21:16:35+00:00",
  "date": "2026-07-30",
  "source": "argument",
  "time": "21:16:35",
  "timezone": "UTC",
  "tomorrow": "2026-07-31",
  "utc_offset": "+00:00",
  "weekday": "Thursday",
  "yesterday": "2026-07-29",
  "zone_abbreviation": "UTC"
}
```

Exit code: `0`.

## User-facing response

```text
TODAY: Thursday, July 30, 2026 | UTC | UTC+00:00
[2026-07-30 UTC] This skill runs before every direct user reply. It loads starting-point, acquires one fresh clock anchor, resolves temporal language before date-sensitive tools, and stores the dated prefix in the actual response. Timezone order is --timezone, PROFILE_TIMEZONE, then system-local. A missing or invalid anchor blocks date-dependent work with temporal-anchor-unavailable.
```

Created files: none.

Verification: the help turn made one clock call, parsed every required field, and used both visible prefixes because it was the first reply for the local date.
