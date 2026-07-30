---
name: always-current-date
description: "Use when replying. Refresh date through starting-point."
version: 1.0.1
author: Kiren Srinivasan
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [date, time, timezone, temporal-context]
    related_skills: [starting-point]
    created_by: agent
    created_with_hermes_commit: 41f2196c530b3359d9a7fc9c7bd41e9ddd7882c5
    compatibility_reviewed_with_hermes_commit: 41f2196c530b3359d9a7fc9c7bd41e9ddd7882c5
---

# Always current date

## Outcome

Use one fresh local clock anchor for every direct user turn. Apply it through `starting-point`, resolve relative dates without changing the user's words, and keep dated assistant output in session history.

## Trigger

This skill applies before every reply to a direct user message, even when the message contains no date words. A tool result, system event, or assistant continuation does not start a new clock acquisition. An exact mid-turn out-of-band user-message marker does.

## Per-turn contract

Before interpreting or acting on the newest direct user message:

1. Load `starting-point` with `skill_view`.
2. Read this skill's concrete absolute directory from the loaded skill context.
3. Set that directory as the process runner's working directory and acquire the clock once for this direct turn.
4. Parse the JSON and require every field named in [the evaluation contract](references/eval-contract.md).
5. Add the anchor to the private starting-point map as `as_of`.
6. Resolve temporal language before any date-sensitive tool call.
7. Write the visible date prefix in the actual assistant response so session persistence includes it.

Run on macOS or Linux with that working directory:

```bash
python3 scripts/current_anchor.py
```

Run on Windows with that working directory and the interpreter command available to Hermes:

```powershell
python scripts/current_anchor.py
```

Use `py -3` instead of `python` when that is the installed command. Do not use a skill-directory shell variable or guess an installation path. If the loaded context does not supply a concrete skill directory, report `temporal-anchor-unavailable: skill directory missing` and stop date-dependent work. Never pass a fabricated timestamp to the script. Reuse an anchor only when its tool result occurs after the newest direct user message.

If the command fails, returns invalid JSON, or omits a required field, stop date-dependent work and report `temporal-anchor-unavailable:` followed by the short error. Do not guess, reuse an earlier date, or fall back to the conversation-start date.

## Starting-point binding

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

## Temporal interpretation

- Preserve the user's original words and authorship.
- Expose the resolved absolute date when a relative expression affects meaning or action.
- Keep past statements historical and future requests prospective.
- Convert date-sensitive tool arguments to absolute dates and include the timezone when the tool supports it.
- Treat `next Friday` and similar phrases as ambiguous when more than one common convention yields a different date. Show the candidate dates and ask one concise question.
- Do not ask when the conversation already establishes the convention.
- Reacquire after local midnight. Never infer rollover from elapsed conversation time.

## Visible response contract

On the first assistant reply for a local date, and again when the local date changes, begin with:

```text
TODAY: <weekday>, <full date> | <timezone> | UTC<offset>
```

Begin every normal user-facing reply on that date with:

```text
[YYYY-MM-DD <zone abbreviation>] <result or question>
```

Inspect retained assistant messages to decide whether the daily header already appeared. When compaction makes that uncertain, prefer a repeated current header over a missing or stale header. Prefix a `clarify` question inside its question text. Do not prefix tool calls or internal notes.

When clock acquisition fails, use the failure marker instead of a dated prefix.

## Compression and resume

After resume or context compression, reacquire the clock before using any retained date. If this skill appears as `[SKILL_PRUNED]`, reload it before acting. Stored date prefixes are evidence of prior turns only.

## Progressive disclosure

`PD-101`: [`references/eval-contract.md`](references/eval-contract.md) and [`references/eval-cases.json`](references/eval-cases.json) own required fields, acceptance, and pressure cases. Load them before testing or changing this skill. This file owns runtime behavior and links to both owners.
