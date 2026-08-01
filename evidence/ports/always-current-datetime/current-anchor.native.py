#!/usr/bin/env python3
"""Print a fresh, profile-aware local time anchor as JSON."""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def configured_timezone():
    """Return the configured timezone and its source."""
    value = os.environ.get("HERMES_TIMEZONE", "").strip()
    if value:
        return value, "environment"
    try:
        result = subprocess.run(
            ["hermes", "config", "get", "timezone"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("could not read Hermes timezone configuration") from exc
    if result.returncode == 0:
        value = result.stdout.strip()
        return (value, "hermes-config") if value else (None, "system-local")
    if "Config key not set: timezone" in result.stderr:
        return None, "system-local"
    raise RuntimeError("Hermes timezone configuration lookup failed")


def current_time(timezone_name):
    """Read the current time in the requested zone."""
    if timezone_name:
        return datetime.now(ZoneInfo(timezone_name))
    return datetime.now().astimezone()


def utc_offset(now):
    """Format the active UTC offset with a colon."""
    compact = now.strftime("%z")
    if len(compact) != 5:
        raise ValueError("clock did not provide a numeric UTC offset")
    return f"{compact[:3]}:{compact[3:]}"


def main():
    """Acquire and emit one complete clock anchor."""
    try:
        timezone_name, source = configured_timezone()
        now = current_time(timezone_name)
        today = now.date()
        payload = {
            "captured_at": now.isoformat(timespec="seconds"),
            "date": today.isoformat(),
            "time": now.strftime("%H:%M:%S"),
            "weekday": WEEKDAYS[now.weekday()],
            "timezone": timezone_name or "system-local",
            "zone_abbreviation": now.tzname() or "local",
            "utc_offset": utc_offset(now),
            "source": source,
            "yesterday": (today - timedelta(days=1)).isoformat(),
            "tomorrow": (today + timedelta(days=1)).isoformat(),
        }
    except Exception as exc:
        print(f"current_anchor_error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
