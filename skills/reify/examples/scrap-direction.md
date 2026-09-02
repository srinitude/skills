# Example: scrap a direction

Guess this removes: what `scrap` writes, what it must not do, and how a scrapped state travels in the brief. A scrapped brief validates at exit 0, so a downstream reader can tell abandoned work from live work.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/malls`. The installed skill for this run sits at `/home/user/workspace/skills/skills/reify`.

## The user says

> forget the mall zine. I am not going back out to shoot more, so it is dead. keep the reasoning though

## Commands run, with real output

```
$ grep -n "^- status\|^- next_action" reify-log-abandoned-malls.md
7:- next_action: none, the direction is scrapped
16:- status: scrapped
EXIT=0

$ mise run validate-brief ./BRIEF.json
{"errors": [], "status": "PASS"}
EXIT=0

$ ls
BRIEF.json
reify-log-abandoned-malls.md
EXIT=0
```

Nothing was deleted, nothing was printed, nothing was ordered, and no message was sent. Scrap stops work; it does not clean up after the user.

## The executor replies

> Scrapped, and the reasoning is kept.
>
> Recorded as `D-002`: the zine stops because 4 usable frames cannot fill 16 pages while `D-001` holds, and `D-001` is your own constraint, only frames you already took. Status in `reify-log-abandoned-malls.md` is now `scrapped`, `next_action` is none, and the brief carries the same status, so anyone who opens `BRIEF.json` can see this is abandoned and not merely stalled. It validates clean, exit 0.
>
> Nothing else happened. No file deleted, no print ordered, no message sent.
>
> The recovery path is one move, so this is reversible rather than gone: `revert D-001` allows one shooting trip, which reopens `outcome` and `first_milestone` and puts the 20 frame contact sheet back in play. The four frames stay where they are in the meantime.
>
> One line worth keeping in view: the open question in the record is whether an autumn trip is worth it. That is the only thing between this and a live project.

Word count of the reply above: 165, inside the 350 word budget.

## Files this run created

`reify-log-abandoned-malls.md`:

```markdown
# Reification record: abandoned malls

- signal: "photos of dead malls, maybe a zine"
- outcome: a 16 page photo zine of three closed malls the author has already photographed
- done_means: 16 pages laid out from existing photographs, printed once
- first_milestone: a contact sheet of the strongest 20 frames
- next_action: none, the direction is scrapped
- sources_checked:
  - photo directory: reachable, 4 usable frames, far short of 20
  - conversation history: reachable, no other source named
- constraints:
  - only photographs the author already took may be used
- decisions: see below
- open_questions:
  - whether a return trip is worth it, revisit in autumn
- status: scrapped

## Decisions

### D-001 accepted: zine built only from existing frames

- choice: no new shooting trip.
- reason: the author said the trips are over.
- dependents: D-002
- reversible: true

### D-002 accepted: scrap the direction and keep the reasoning

- choice: stop work, keep the record and the contact sheet, perform no further effect.
- reason: 4 usable frames cannot fill 16 pages, and the constraint from D-001 blocks getting more.
- dependents:
- reversible: true

## Progress

- scrap: status set to scrapped. No file deleted, no print ordered, no message sent. Recovery path: revert D-001 to allow a shooting trip, which reopens outcome and first_milestone. Next check: none until the author revisits this.
```

`BRIEF.json`, validated at exit 0:

```json
{
  "signal": "photos of dead malls, maybe a zine",
  "outcome": "A 16 page photo zine of three closed malls, built only from photographs the author already took.",
  "done_means": "16 pages laid out from existing frames and printed once.",
  "first_milestone": "A contact sheet of the strongest 20 frames.",
  "next_action": "None. The direction is scrapped. Reviving it means reverting D-001 to allow one shooting trip.",
  "constraints": [
    "Only photographs the author already took may be used.",
    "No print order, no purchase, no message was performed."
  ],
  "sources_checked": [
    "photo directory: reachable, 4 usable frames against the 20 the milestone needs",
    "conversation history: reachable, no other photo source named"
  ],
  "decisions": [
    {
      "id": "D-001",
      "choice": "Build only from existing frames.",
      "reason": "The author said the trips are over.",
      "dependents": ["D-002"],
      "reversible": true
    },
    {
      "id": "D-002",
      "choice": "Scrap the direction and keep the reasoning.",
      "reason": "Four frames cannot fill sixteen pages while D-001 holds.",
      "dependents": [],
      "reversible": true
    }
  ],
  "open_questions": ["Whether a return trip in autumn is worth it"],
  "status": "scrapped"
}
```
