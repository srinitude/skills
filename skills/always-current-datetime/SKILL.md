---
name: always-current-datetime
description: 'Use when replying. Refresh current date and time.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.2'
  scope: 'user'
---

# Always current date and time

Use one fresh local clock anchor for every direct user turn. Apply it through `starting-point`, resolve relative dates and times without changing the user's words, and persist the current acquisition time in the visible reply.

## Which commands does this skill accept?

Treat an ordinary direct user message as `refresh`. These control words exist for inspection and testing.

| Command   | Result                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------- |
| `help`    | Show the trigger, clock fields, timezone order, visible prefixes, failure rule, and anchor state.       |
| `refresh` | Acquire one fresh anchor for the current direct turn, bind it to `starting-point`, and apply the reply. |

If a request matches neither command, use `refresh`. Do not ask the user to choose a command.

## When does it run?

Run before every reply to a direct user message, even when the message has no date or time words. A tool result, system event, or assistant continuation does not start a new clock acquisition. An exact mid-turn out-of-band user-message marker does.

## What is the per-turn contract?

Before interpreting or acting on the newest direct user message:

1. Load `starting-point` through the host's skill-loading capability.
2. When the loader supplies an accessible absolute directory, use it as the process working directory and run `mise run refresh` exactly once.
3. When the loader supplies only a resource address or the directory is inaccessible, run the self-contained Python fallback below exactly once through the host's process runner. A resource address is not a filesystem path.
4. Require one JSON object with `captured_at`, `date`, `time`, `weekday`, `timezone`, `zone_abbreviation`, `utc_offset`, `source`, `yesterday`, and `tomorrow`. The schema is shared with `references/eval-contract.md` through `mise run validate`; reading that resource is not required to acquire an anchor.
5. Add the anchor to the private `starting-point` map as `as_of`.
6. Resolve temporal language before any date-sensitive or time-sensitive tool call.
7. Write the visible date-time prefix in the actual assistant response so session history stores it.

Run with an accessible package directory:

```bash
mise run refresh
```

Otherwise pass this code directly to an installed Python 3 interpreter through standard input or `-c`. It needs no package directory or supporting files. Pass a host-configured timezone with `--timezone America/New_York`, substituting the actual configured IANA zone. Use `python3`, `python`, or `py -3` according to the installed interpreter. Do not run both paths for one anchor.

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

Do not guess an installation path, interpret a resource address as a local path, or use an unresolved skill-directory variable. Never fabricate a timestamp. Reuse an anchor only when its process result occurs after the newest direct user message. Report `temporal-anchor-unavailable: no usable clock runner` only when neither execution path is available; a missing package directory alone is not a clock failure.

The portable script accepts `--timezone <IANA-zone>`, then checks `PROFILE_TIMEZONE`, then uses system-local time. An explicit argument represents a profile configuration supplied by the host and wins over the environment.

If the command fails, returns invalid JSON, or omits a required field, stop date-dependent or time-dependent work and report `temporal-anchor-unavailable:` followed by the short error. Do not guess, reuse an earlier date or time, or fall back to the conversation-start timestamp.

## How is the anchor bound to starting-point?

Add this private structure without exposing the full outcome map:

```text
as_of: captured_at, date, time, weekday, timezone, zone_abbreviation, utc_offset, source
```

Apply it to:

- **Outcome:** Turn relative completion language into an exact date or date-time.
- **Proof:** Separate current observations from evidence gathered earlier.
- **Constraints:** Resolve deadlines, validity windows, and temporal bounds.
- **Starting path:** Distinguish actions available now from later actions.
- **Unknowns:** Keep ambiguous expressions unresolved until one concise question answers them.

## How is temporal language interpreted?

- Preserve the user's original words and authorship.
- Expose the resolved absolute date or date-time when a relative expression affects meaning or action.
- Keep past statements historical and future requests prospective.
- Convert date-sensitive and time-sensitive tool arguments to absolute values and include the timezone when the tool supports it.
- Treat `next Friday` and similar phrases as ambiguous when common conventions yield different dates. Show the candidate dates and ask one concise question.
- Do not ask when the conversation already establishes the convention.
- Reacquire after local midnight. Never infer rollover from elapsed conversation time.

## What is visible in the reply?

Resource gate: run `mise run validate` before using package files named here.

On the first assistant reply for a local date, and again when the local date changes, begin with:

```text
NOW: <weekday>, <full date> at <HH:MM:SS> | <zone abbreviation> | UTC<offset>
```

Begin every normal user-facing reply on that date with:

```text
[YYYY-MM-DD HH:MM:SS <zone abbreviation>] <result or question>
```

Inspect retained assistant messages to decide whether the daily header already appeared. When context compaction makes that uncertain, prefer a repeated current header over a missing or stale header. Prefix an interactive clarification question inside its question text. Do not prefix tool calls or internal notes.

The literal templates also live in `assets/response-prefixes.txt`. When clock acquisition fails, use the failure marker instead of a dated prefix.

## How does resume work?

After resume or context compaction, reacquire the clock before using any retained date or time. If this skill body is unavailable from retained context, reload it before acting. Stored date-time prefixes prove prior turns only.

## Which worked example should you read?

Resource gate: run `mise run validate` before using package files named here.

- Read `examples/help-command.md` for a complete `help` response.
- Read `examples/fresh-direct-turn.md` for one real UTC diagnostic, `as_of` binding, and both visible prefixes.
- Read `examples/invalid-timezone.md` for exit `2`, empty stdout, the failure marker, and recovery.

## Progressive disclosure

Read `references/eval-contract.md` and `evals/cases.json` before testing or changing this skill. Read `references/generation-contract.md` when changing the package structure or checking native-to-port lineage. Load the tests through `mise run test` before changing clock behavior, and rerun that task before implementation changes. Load the rest of `evals/` only when measuring activation, behavior, enrollment, or timing. Do not load these files on ordinary turns.

## Gotchas

Do not skip the clock for messages without temporal words, acquire it after final reasoning, or acquire it twice for one direct turn. Tool results and system events do not start a turn. Preserve the user's words, distinguish historical evidence, clarify ambiguous weekdays, and prefix only visible replies. An invalid configured timezone must fail without silently choosing another zone. Claim parity only when both execution paths pass the retained cases.

## Limitations

The script cannot infer the user's intended timezone from prose. The host must supply an explicit IANA timezone through `--timezone` or `PROFILE_TIMEZONE` when system-local time is not the intended context. The skill can resolve dates and times and prepare absolute tool arguments, but a separate capability owns any real reminder, calendar, or deployment action.

## When is the turn ready?

The turn is ready only when the skill was loaded, one fresh clock call produced every required field after the newest direct message, `as_of` is bound to the private `starting-point` map, temporal language is resolved before date-sensitive or time-sensitive actions, and the actual user-facing response contains the required current date-time prefix. Any stale, missing, duplicate, or failed anchor leaves temporal work blocked.

## Factory execution contract

The accepted outcome is: Bind one fresh clock anchor to each direct turn and resolve relative date language from it. Preserve current clock anchor behavior while changing its smallest owner.

1. Freeze the current package with `mise run ci` and record its digest.
2. Run `mise run domain-research-policy`, then judge the current clock anchor sources and counterevidence.
3. Run `mise run refresh` for the named clock anchor operation. Keep semantic choices with the model.
4. Run `mise run decision-policy`, `mise run ci`, and the behavioral evals. Return to the lowest failed owner.
5. Run `mise run invocation-policy -- <receipt>` and account for every task or its domain-specific non-use.
6. Optionally run `mise run improvement-policy`. Keep one changed dimension only if no protected dimension regresses.

Load `assets/use-case-contract.json` through `mise run use-case-policy` and `evals/evals.json` through `mise run evals` only when their contracts are needed.

Mise owns repeatable mechanics, ordering, receipts, and checks. The model owns interpretation, causal judgment, creative work, and direct perception that code cannot supply. Stop on missing authority, stale evidence, or a failed gate.

