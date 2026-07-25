# Example: finalize and hand off

Guess this removes: how to run the validator from the user's own directory, what exit 2 means against exit 1, where `BRIEF.json` comes from, and how to report a finalized reification whose first milestone is still open because another person has to act.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`. The installed skill for this run sits at `/home/user/workspace/skills/skills/reify`.

## The user says

> ok finalize it and hand it off to my writing partner Dana for next week

## Commands run, with real output

The probe from turn one was absorbed by the sketch, so it moves out of the live set first:

```
$ mv probe-opening.md superseded/probe-opening.md && ls . superseded
.:
part-1-sketch.md
reify-log-lighthouse-summers.md
reify-log-tool-shed.md
superseded

superseded:
probe-opening.md
series-outline.md
EXIT=0
```

Copy the template out of the installed skill. Never fill the file inside the skill directory:

```
$ echo "$SKILL_DIR"
/home/user/workspace/skills/skills/reify
EXIT=0

$ cp "$SKILL_DIR/assets/reification-brief.json" ./BRIEF.json && cat BRIEF.json
{
  "signal": "",
  "outcome": "",
  "done_means": "",
  "first_milestone": "",
  "next_action": "",
  "constraints": [],
  "sources_checked": [],
  "decisions": [
    {
      "id": "D-001",
      "choice": "",
      "reason": "",
      "dependents": [],
      "reversible": true
    }
  ],
  "open_questions": [],
  "status": "active"
}
EXIT=0
```

The relative path fails, because the script lives in the skill and the shell is in the user's directory. This is exit 2, and exit 2 is a wrong command, never a wrong brief:

```
$ python3 scripts/validate_brief.py ./BRIEF.json
python3: can't open file '/home/user/workspace/test/t-reify/examples-run/lighthouse/scripts/validate_brief.py': [Errno 2] No such file or directory
EXIT=2
```

The same brief with the absolute script path gives exit 1, which is a real report about a real file. The template is still empty, so seven fields fail:

```
$ python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json
{"errors": ["done_means must be a non-empty string", "first_milestone must be a non-empty string", "next_action must be a non-empty string", "outcome must be a non-empty string", "signal must be a non-empty string", "decisions[1].choice must be a non-empty string", "decisions[1].reason must be a non-empty string"], "status": "FAIL"}
EXIT=1
```

After filling every field, and after the reopened fields from the revert were closed by `D-005`:

```
$ python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json
{"errors": [], "status": "PASS"}
EXIT=0

$ grep -n "^### D-00\|^- outcome:\|^- done_means:\|^- first_milestone:\|^- status:" reify-log-lighthouse-summers.md
4:- outcome: one short piece of about 1200 words about the gap between flashes, written from facts the author supplies
5:- done_means: one draft of 1000 to 1400 words exists with every bracketed slot replaced by an author-supplied fact, read by one person who is not the author
6:- first_milestone: the author returns the light name or location, the summers, and one other person who was there
17:- status: finalized
21:### D-001 accepted: treat this as a writing outcome
32:### D-002 accepted: write a slot sketch instead of first-person prose
43:### D-003 reverted: shape is a five-part series
50:### D-004 needs-review: part 1 is sized at 700 words
62:### D-005 accepted: shape is the single short piece
69:### D-006 accepted: prepare the handoff, do not send it
EXIT=0

$ grep -n "^- status\|^- milestone" reify-log-lighthouse-summers.md
17:- status: finalized
60:- milestone: open, closes when the author returns the three facts and one reader who is not the author has read the piece.
EXIT=0

$ ls . superseded
.:
BRIEF.json
HANDOFF-dana.md
part-1-sketch.md
reify-log-lighthouse-summers.md
reify-log-tool-shed.md
superseded

superseded:
probe-opening.md
series-outline.md
EXIT=0
```

## The executor replies

> Finalized and packaged. Nothing was sent, and here is why.
>
> What exists: `part-1-sketch.md`, the beat sheet with nine open slots. `BRIEF.json`, the machine checked handoff, which reports `{"errors": [], "status": "PASS"}` at exit 0. `HANDOFF-dana.md`, the packet with the message already written. `reify-log-lighthouse-summers.md`, six decisions, one reverted, one under review, all recoverable.
>
> Why nothing went out: I searched the reachable address sources once each and found no Dana. A first name is not an address, and "hand it off" is permission to prepare, not a resolved recipient. Give me the address or channel and the message goes into drafts for your approval before it moves.
>
> Two states, and they are not the same state. The reification is finalized: one outcome, one completion proof, a next action, and a brief that passes. The first milestone is open: it closes when you return the three facts and one reader who is not you has read the piece. I am not going to call that done because a file exists.
>
> "Next week" is not a date, so I proposed Friday 2026-07-31 and wrote it into the brief as a proposal you can move.
>
> The one thing blocking everything: how do I reach Dana?

Word count of the reply above: 216, inside the 350 word budget.

Every file this run created, with full contents, is in the companion example `examples/finalize-artifacts.md`.
