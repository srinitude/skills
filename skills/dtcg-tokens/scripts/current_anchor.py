#!/usr/bin/env python3
"""Capture one local clock anchor.

Exit codes:
  0  anchor written as JSON
  2  invalid timezone or usage

Example:
  python3 scripts/current_anchor.py --timezone UTC
"""
import argparse
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parser():
    value = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    value.add_argument("--timezone", help="IANA timezone; system local time is the default")
    return value


def capture(timezone=None):
    zone = ZoneInfo(timezone) if timezone else datetime.now().astimezone().tzinfo
    now = datetime.now(zone)
    return {"captured_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "weekday": now.strftime("%A"), "timezone": timezone or now.tzname(), "utc_offset": now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:], "source": "explicit-timezone" if timezone else "system-local"}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        print(json.dumps(capture(args.timezone), sort_keys=True))
    except ZoneInfoNotFoundError as error:
        print(f"error: unknown timezone {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
