# Example: new, from a named source file

Guess this removes: what to do when the user points at a readable file instead of restating the thought, how `starting-point` is applied when it is present, and what the first reply and probe look like when the real blocker is content rather than tooling.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/weekly-cli`. The installed skill for this run sits at `/home/user/workspace/skills_repo/skills/reify`.

## The user says

> there is a rough thought in notes/weekly-ideas.txt about a CLI that turns my weekly notes into a one-page summary. I think it might become something useful. Help me make it concrete.

## Commands run, with real output

The user named a file, so the file is read before any question is asked:

```
$ pwd && ls -a
/home/user/workspace/test/t-reify/examples-run/weekly-cli
.
..
notes
EXIT=0

$ ls reify-log-*.md 2>/dev/null || echo "no record in this directory"
no record in this directory
EXIT=0

$ cat notes/weekly-ideas.txt
ideas i keep not finishing:

- a thing that turns my messy weekly notes into one clean page
- maybe a CLI? just feed it a folder of markdown notes for the week
- it groups by project, pulls out decisions, lists what's blocked
- i have like 200 weeks of these notes, never go back and read them
- the blocker: i can never decide what "summary" should contain
EXIT=0
```

The notes name the real blocker, so `starting-point` is checked next and applied, then the record and the probe are written:

```
$ ls /home/user/workspace/skills_repo/skills/starting-point/SKILL.md && echo "starting-point present"
/home/user/workspace/skills_repo/skills/starting-point/SKILL.md
starting-point present
EXIT=0

$ ls -la reify-log-weekly-cli.md
-rw-r--r-- 1 user user 1663 Aug 30 01:16 reify-log-weekly-cli.md
EXIT=0

$ grep -n "^- status" reify-log-weekly-cli.md
20:- status: active
EXIT=0

$ wc -w probe-summary-shape.md
227 probe-summary-shape.md
EXIT=0

$ grep -c "\[" probe-summary-shape.md
0
EXIT=0

$ ls *.md
probe-summary-shape.md
reify-log-weekly-cli.md
EXIT=0
```

The bracket count of zero is the check, not decoration: every section in the probe traces to the notes file the user supplied, so nothing is invented.

## The executor replies

> You said the part worth pulling is the one-page summary, and your own notes name the one thing blocking it: you can never decide what the summary should contain. That is a content question, not a tooling question, so no CLI is built yet.
>
> I read `notes/weekly-ideas.txt` first, so nothing here asks you to repeat what you wrote. You named two sections already, decisions and what is blocked. I wrote `probe-summary-shape.md`, a concrete one-page shape with four sections you can react to: projects, decisions, blocked, and carried forward. The last two are the cheapest test of whether a one-pager is worth reading at all.
>
> Default path: define the shape, test it by hand on one real week of notes, then decide whether a CLI is even the right tool. One alternative changes the proof rather than the wording: build the CLI now and let the output shape itself, which means shipping a tool before you know what it should print.
>
> One question, only because it changes the form: do you want numbers in this summary, or prose and bullets? Your notes never mention hours, mood, or metrics, so they are left out, but if you want them the shape is a different one.
>
> Record: `/home/user/workspace/test/t-reify/examples-run/weekly-cli/reify-log-weekly-cli.md`, status `active`, one decision, `D-001`, treating the summary content as the thing to reify first.
>
> Next action: you react to the probe, and I tighten the shape from your answer.

Word count of the reply above: 254, inside the 350 word budget.

## Files this run created

`reify-log-weekly-cli.md`:

```markdown
# Reification record: weekly cli

- signal: "a thing that turns my messy weekly notes into one clean page, maybe a CLI"
- outcome: undecided, provisional: a CLI that turns one week of markdown notes into a one-page summary
- done_means: undecided
- first_milestone: undecided
- next_action: user reacts to the one-page summary shape
- sources_checked:
  - working directory: reachable, one notes file present, no prior record
  - notes/weekly-ideas.txt: reachable, read in full, five lines, names the real blocker
  - conversation history: reachable, no earlier weekly-cli material
  - starting-point skill: present in the skill catalog, applied to derive target, constraints, proof, and first milestone
- constraints:
  - "maybe a CLI" is a candidate path, not a fixed constraint until the summary content is known
  - about 200 weeks of notes exist, so input material is available
  - the user's own named blocker is deciding what the summary should contain
- decisions: see below
- open_questions:
  - what sections the one-page summary should contain, which is the user's named blocker
- status: active

## Decisions

### D-001 accepted: treat the summary content as the thing to reify first

- choice: reify the one-page summary shape before building any CLI, because the user's blocker is content, not tooling.
- reason: the notes file names the blocker as "I can never decide what summary should contain," and 200 weeks of notes already supply input.
- dependents:
- reversible: true

## Progress

- step 3: record created at ./reify-log-weekly-cli.md. Next check: a one-page summary shape exists and carries a concrete section list the user can react to.
```

`probe-summary-shape.md`:

```markdown
# One-page weekly summary: proposed shape

Probe, not a product. Read it as a concrete guess at what "summary" should contain, then react to it.

## Sections, in reading order

1. This week by project: one line per project you touched, what moved.
2. Decisions made: bullets, the calls you committed to this week.
3. What is blocked: the item, and the one thing it is waiting on.
4. Carried forward: anything from last week that is still open, so nothing falls silently.

## Why these four

You named two of them in the notes: decisions and what is blocked. The other two are the cheapest test of whether a one-pager is worth reading at all: projects tell you what moved, carried forward tells you what did not.

## What this shape is missing on purpose

No hours, no mood, no metrics. If the first reaction is "I need numbers," that is a different summary and a different reification.

## The test

Run this shape against one real week of your notes. If you finish reading the one page and want to keep it, the shape holds. If you skip a section every time, that section is wrong and we cut it.

Default path: build nothing yet. Define the shape, test it by hand on one week, then decide whether a CLI is even the right tool.
```

This probe is finalized in `examples/finalize-open-milestone.md`, where the four-section shape is frozen and the first milestone is left open because the author still has to test it on a real week.
