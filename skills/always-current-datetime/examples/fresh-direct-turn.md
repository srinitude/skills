# Resource-only direct turn

This run removes the assumption that a loaded skill has a local directory. The process runner executes the Python block from SKILL.md directly; it reads no supporting files. Package validation uses `mise run validate`.

## Input

```text
Continue with the task.
```

## Process input

Use the installed Python 3 interpreter with `-c`, the following code, and `--timezone America/New_York`.

```python
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

parser = argparse.ArgumentParser(description="Emit one fresh local-time anchor.")
parser.add_argument("--timezone", help="IANA zone; overrides PROFILE_TIMEZONE")
args = parser.parse_args()
try:
    zone = (args.timezone or os.environ.get("PROFILE_TIMEZONE", "")).strip()
    source = "argument" if args.timezone else "profile-environment"
    now = datetime.now(ZoneInfo(zone)) if zone else datetime.now().astimezone()
    if not zone:
        zone = getattr(now.tzinfo, "key", None) or str(now.tzinfo) or "system-local"
        source = "system-local"
    seconds = int(now.utcoffset().total_seconds())
    hours, remainder = divmod(abs(seconds), 3600)
    offset = f"{'+' if seconds >= 0 else '-'}{hours:02d}:{remainder // 60:02d}"
    today = now.date()
    result = dict(captured_at=now.isoformat(timespec="seconds"), date=today.isoformat(),
                  time=now.strftime("%H:%M:%S"), weekday=now.strftime("%A"),
                  timezone=zone, zone_abbreviation=now.tzname() or "local",
                  utc_offset=offset, source=source,
                  yesterday=(today - timedelta(days=1)).isoformat(),
                  tomorrow=(today + timedelta(days=1)).isoformat())
except Exception as error:
    print(f"current_anchor_error: {type(error).__name__}: {error}", file=sys.stderr)
    sys.exit(2)
print(json.dumps(result, sort_keys=True))
```

## Real output

```json
{
  "captured_at": "2026-10-20T20:30:06-04:00",
  "date": "2026-10-20",
  "source": "argument",
  "time": "20:30:06",
  "timezone": "America/New_York",
  "tomorrow": "2026-10-21",
  "utc_offset": "-04:00",
  "weekday": "Tuesday",
  "yesterday": "2026-10-19",
  "zone_abbreviation": "EDT"
}
```

Exit code: `0`. Created files: none.

## Visible response

```text
[2026-10-20 20:30:06 EDT] Continuing with the task.
```

This verifies clock execution and prefix formatting. The unit tests independently exercise this block from an empty directory and cover invalid zones, configuration precedence, fractional offsets, and the full output schema.
