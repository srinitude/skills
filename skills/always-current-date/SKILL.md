---
name: always-current-date
description: 'Use when replying. Refresh date through starting-point.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Always current date

Use one fresh local clock anchor for every direct user turn. Apply it through `starting-point`, resolve relative dates without changing the user's words, and keep dated assistant output in session history.

## Which commands does this skill accept?

Treat an ordinary direct user message as `refresh`. These control words exist for inspection and testing.

| Command   | Result                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------- |
| `help`    | Show the trigger, clock fields, timezone order, visible prefixes, failure rule, and anchor state.       |
| `refresh` | Acquire one fresh anchor for the current direct turn, bind it to `starting-point`, and apply the reply. |

If a request matches neither command, use `refresh`. Do not ask the user to choose a command.

## When does it run?

Run before every reply to a direct user message, even when the message has no date words. A tool result, system event, or assistant continuation does not start a new clock acquisition. An exact mid-turn out-of-band user-message marker does.

## What is the per-turn contract?

Before interpreting or acting on the newest direct user message:

1. Load `starting-point` through the host's skill-loading capability.
2. Set `SKILL_DIR` to this skill's absolute directory and run the bundled script exactly once through an available process runner.
3. Parse the JSON and require every field in `references/eval-contract.md`.
4. Add the anchor to the private `starting-point` map as `as_of`.
5. Resolve temporal language before any date-sensitive tool call.
6. Write the visible date prefix in the actual assistant response so session history stores it.

Run on macOS or Linux:

```bash
python3 "$SKILL_DIR/scripts/current_anchor.py"
```

Run on Windows PowerShell:

```powershell
python "$env:SKILL_DIR\scripts\current_anchor.py"
```

Use `python` or `py -3` only when it is the installed interpreter. Never guess a path or pass a fabricated timestamp. Reuse an anchor only when its process result occurs after the newest direct user message.

The portable script accepts `--timezone <IANA-zone>`, then checks `PROFILE_TIMEZONE`, then uses system-local time. An explicit argument represents a profile configuration supplied by the host and wins over the environment.

If the command fails, returns invalid JSON, or omits a required field, stop date-dependent work and report `temporal-anchor-unavailable:` followed by the short error. Do not guess, reuse an earlier date, or fall back to the conversation-start date.

## How is the anchor bound to starting-point?

Add this private structure without exposing the full outcome map:

```text
as_of: captured_at, date, weekday, timezone, utc_offset, source
```

Apply it to:

- **Outcome:** Turn relative completion language into an exact date.
- **Proof:** Separate current observations from evidence gathered earlier.
- **Constraints:** Resolve deadlines, validity windows, and date bounds.
- **Starting path:** Distinguish actions available now from later actions.
- **Unknowns:** Keep ambiguous expressions unresolved until one concise question answers them.

## How is temporal language interpreted?

- Preserve the user's original words and authorship.
- Expose the resolved absolute date when a relative expression affects meaning or action.
- Keep past statements historical and future requests prospective.
- Convert date-sensitive tool arguments to absolute dates and include the timezone when the tool supports it.
- Treat `next Friday` and similar phrases as ambiguous when common conventions yield different dates. Show the candidate dates and ask one concise question.
- Do not ask when the conversation already establishes the convention.
- Reacquire after local midnight. Never infer rollover from elapsed conversation time.

## What is visible in the reply?

On the first assistant reply for a local date, and again when the local date changes, begin with:

```text
TODAY: <weekday>, <full date> | <timezone> | UTC<offset>
```

Begin every normal user-facing reply on that date with:

```text
[YYYY-MM-DD <zone abbreviation>] <result or question>
```

Inspect retained assistant messages to decide whether the daily header already appeared. When context compaction makes that uncertain, prefer a repeated current header over a missing or stale header. Prefix an interactive clarification question inside its question text. Do not prefix tool calls or internal notes.

The literal templates also live in `assets/response-prefixes.txt`. When clock acquisition fails, use the failure marker instead of a dated prefix.

## How does resume work?

After resume or context compaction, reacquire the clock before using any retained date. If this skill body is unavailable from retained context, reload it before acting. Stored date prefixes prove prior turns only.

## Which worked example should you read?

- Read `examples/help-command.md` for a complete `help` response.
- Read `examples/fresh-direct-turn.md` for one real UTC diagnostic, `as_of` binding, and both visible prefixes.
- Read `examples/invalid-timezone.md` for exit `2`, empty stdout, the failure marker, and recovery.

## Progressive disclosure

Read `references/eval-contract.md` and `evals/cases.json` before testing or changing this skill. Read `references/generation-contract.md` when changing the package structure or checking native-to-port lineage. Load `scripts/tests/` before changing script behavior and run those tests before implementation changes. Load the rest of `evals/` only when measuring activation, behavior, enrollment, or timing. Do not load these files on ordinary turns.

## Gotchas

- Do not skip the clock because the direct message has no date words.
- Do not treat tool output, a system event, or assistant continuation as a new direct user message.
- Do not call the clock after final reasoning or call it twice in one direct turn.
- Do not rewrite the user's temporal words after resolving them.
- Do not present older evidence as current proof.
- Do not silently choose one meaning for an ambiguous weekday phrase.
- Do not prefix tool calls or internal notes.
- Do not silently fall back after an invalid configured timezone.
- Do not claim hook parity when either route misses a case.

## Limitations

The script cannot infer the user's intended timezone from prose. The host must supply an explicit IANA timezone through `--timezone` or `PROFILE_TIMEZONE` when system-local time is not the intended context. The skill can resolve dates and prepare absolute tool arguments, but a separate tool owns any real reminder, calendar, or deployment action.

## When is the turn ready?

The turn is ready only when the skill was loaded, one fresh clock call produced every required field after the newest direct message, `as_of` is bound to the private `starting-point` map, temporal language is resolved before date-sensitive actions, and the actual user-facing response contains the required current prefix. Any stale, missing, duplicate, or failed anchor leaves date-dependent work blocked.
