# Example: finalize with an open first milestone

Guess this removes: how to report a finalized reification whose first milestone is still open because the author has to do the test, how the brief validator behaves across exit 2, exit 1, and exit 0, and what the finalized record header looks like.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/weekly-cli`. The installed skill for this run sits at `/home/user/workspace/skills_repo/skills/reify`. This continues the run in `examples/new-from-source-file.md`.

## The user says

> ok the four sections are right. finalize it. I will test it on one real week of notes myself next week.

## Commands run, with real output

The template is copied out of the installed skill, never filled inside it:

```
$ echo "$SKILL_DIR"
/home/user/workspace/skills_repo/skills/reify
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
python3: can't open file '/home/user/workspace/test/t-reify/examples-run/weekly-cli/scripts/validate_brief.py': [Errno 2] No such file or directory
EXIT=2
```

The same empty template with the absolute script path gives exit 1, a real report about a real file. Seven fields fail because the template is still blank:

```
$ python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json
{"errors": ["done_means must be a non-empty string", "first_milestone must be a non-empty string", "next_action must be a non-empty string", "outcome must be a non-empty string", "signal must be a non-empty string", "decisions[1].choice must be a non-empty string", "decisions[1].reason must be a non-empty string"], "status": "FAIL"}
EXIT=1
```

After filling every field and aligning the record header to the same values, the brief passes:

```
$ python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json
{"errors": [], "status": "PASS"}
EXIT=0

$ grep -n "^- outcome:\|^- done_means:\|^- first_milestone:\|^- next_action:\|^- status:\|^### D-\|^- milestone" reify-log-weekly-cli.md
4:- outcome: a CLI that turns one week of markdown notes into a one-page summary, built only after the four-section shape is agreed and tested
5:- done_means: the CLI runs against one real week of the author notes and produces a one-page summary the author reads and keeps
6:- first_milestone: the author runs the four-section shape against one real week of notes and keeps or changes the section list
7:- next_action: the author tests the agreed shape by hand on one real week of notes, then decides whether a CLI is the right tool
20:- status: finalized
24:### D-001 accepted: treat the summary content as the thing to reify first
35:### D-002 accepted: finalize the shape as a handoff the author tests next week
42:- milestone: open, closes when the author runs the shape against one real week of notes and keeps or changes the section list.
EXIT=0

$ ls
BRIEF.json
notes
probe-summary-shape.md
reify-log-weekly-cli.md
EXIT=0
```

## The executor replies

> Finalized, and the milestone is reported open, because a passing file is not a completed test.
>
> What exists: `probe-summary-shape.md`, the four-section shape you accepted. `BRIEF.json`, the machine-checked handoff, which reports `{"errors": [], "status": "PASS"}` at exit 0. `reify-log-weekly-cli.md`, two decisions, both reversible.
>
> Two states, and they are not the same state. The reification is finalized: one outcome, one completion proof, a next action, and a brief that passes. The first milestone is open: it closes when you run the four sections against one real week of notes and keep or change the list. I am not going to call that done because a file exists.
>
> Nothing was built. The default path held: the shape is agreed and tested by hand before any CLI is the right tool. "Next week" is not a date, so I left the milestone open rather than inventing one; say the date and I write it into the brief as a proposal you can move.
>
> The one open thing: which real week do you test it on?

Word count of the reply above: 199, inside the 350 word budget.

## Files this run created

`BRIEF.json`, validated at exit 0:

```json
{
  "signal": "a thing that turns my messy weekly notes into one clean page, maybe a CLI",
  "outcome": "A CLI that turns one week of markdown notes into a one-page summary, built only after the four-section shape is agreed and tested.",
  "done_means": "The CLI runs against one real week of the author's notes and produces a one-page summary the author reads and keeps.",
  "first_milestone": "The author runs the four-section shape against one real week of notes and keeps or changes the section list.",
  "next_action": "The author tests the agreed shape by hand on one real week of notes, then decides whether a CLI is the right tool.",
  "constraints": [
    "The summary content is reified before any tool is built, because the user's named blocker is content, not tooling.",
    "About 200 weeks of notes exist, so input material is available.",
    "No CLI is built until the four-section shape is agreed and tested on one real week."
  ],
  "sources_checked": [
    "working directory: reachable, one notes file present, no prior record",
    "notes/weekly-ideas.txt: reachable, read in full, names the real blocker as summary content",
    "starting-point skill: present, applied to derive target, constraints, proof, and first milestone"
  ],
  "decisions": [
    {
      "id": "D-001",
      "choice": "Reify the one-page summary shape before building any CLI.",
      "reason": "The notes file names the blocker as deciding what the summary should contain, and 200 weeks of notes already supply input.",
      "dependents": ["D-002"],
      "reversible": true
    },
    {
      "id": "D-002",
      "choice": "Finalize the four-section shape as a handoff the author tests next week.",
      "reason": "The author accepted the shape and will test it by hand on one real week of notes before any tool is built.",
      "dependents": [],
      "reversible": true
    }
  ],
  "open_questions": [
    "Whether the author wants numbers in the summary, or prose and bullets only"
  ],
  "status": "finalized"
}
```

Record entries appended by this turn:

```markdown
### D-002 accepted: finalize the shape as a handoff the author tests next week

- choice: freeze the one-page summary shape as the agreed outcome and hand it off as files plus a brief, no CLI built yet.
- reason: the author accepted the four-section shape and will test it by hand on one real week of notes before any tool is built.
- dependents:
- reversible: true

- milestone: open, closes when the author runs the shape against one real week of notes and keeps or changes the section list.

## Progress (finalize)

- step 11: BRIEF.json copied from the skill template and filled with the ten record fields. Relative script path returned exit 2, a wrong path, not a brief problem. Absolute path on the empty template returned exit 1 with seven field errors. Filled brief returned {"errors": [], "status": "PASS"} at exit 0.
- step 12: status finalized, first milestone open. The milestone depends on the author testing the shape on one real week of notes, so it is reported open, not done.
```
