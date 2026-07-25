# Example: new, from a vague memory

Guess this removes: where the record file goes, what it holds after turn one, and what the first reply looks like inside the 350 word budget.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`.

## The user says

> I keep thinking about the lighthouse from summers when I was a kid. I don't know if this is a story, a project, or just a feeling. Help me make something of it.

## Commands run, with real output

```
$ pwd && ls -a
/home/user/workspace/test/t-reify/examples-run/lighthouse
.
..
EXIT=0

$ ls reify-log-*.md 2>/dev/null || echo "no record in this directory"
no record in this directory
EXIT=0
```

The record is written next, then the probe object.

```
$ ls -la
total 12
drwxr-xr-x 2 user user 4096 Jul 25 21:15 .
drwxr-xr-x 3 user user 4096 Jul 25 21:15 ..
-rw-r--r-- 1 user user 1110 Jul 25 21:15 reify-log-lighthouse-summers.md
EXIT=0

$ grep -n "^- status" reify-log-lighthouse-summers.md
17:- status: active
EXIT=0

$ wc -w probe-opening.md
67 probe-opening.md
EXIT=0

$ grep -c "\[" probe-opening.md
2
EXIT=0
```

## The executor replies

> The strongest thing you said is that you keep coming back to it. That is a return, and a return is a shape.
>
> Here is a provisional shape instead of a questionnaire, plus the smallest object that can test it. I wrote `probe-opening.md`, a working title and three lines, and every fact I do not have is a bracket:
>
> > The light came around every [interval] seconds at [lighthouse name], and you could set a night by it. What stays is not the beam. It is the gap.
>
> Read that as a probe, not a draft. Nothing in it claims anything about your life: I checked this directory and the conversation first and found no earlier lighthouse material, so nothing here is yours yet.
>
> Default path: one short piece of about 1200 words about the interval between flashes. It is the cheapest way to find out whether the material holds. One alternative changes the completion proof rather than the wording, so it is worth naming: a five part linked series, which means five drafts before you know anything.
>
> One question, and only because the answer changes the form: does the gap between flashes match what you actually remember, or was the thing you kept the tower itself?
>
> Record: `/home/user/workspace/test/t-reify/examples-run/lighthouse/reify-log-lighthouse-summers.md`, status `active`, one decision, `D-001`.
>
> Next action: you answer that one question, and I write the sketch from your material.

Word count of the reply above: 244, inside the 350 word budget.

## Files this run created

`reify-log-lighthouse-summers.md`:

```markdown
# Reification record: lighthouse summers

- signal: "I keep thinking about the lighthouse from summers when I was a kid."
- outcome: undecided, provisional: one short piece about the interval between flashes
- done_means: undecided
- first_milestone: undecided
- next_action: user confirms whether the probe reads true
- sources_checked:
  - working directory: reachable, empty, no prior record
  - conversation history: reachable, no earlier lighthouse material
- constraints:
  - no lighthouse name, coast, years, or people supplied by the user yet
  - no first-person biographical fact may be invented
- decisions: see below
- open_questions:
  - which lighthouse, which years, who else was there
- status: active

## Decisions

### D-001 accepted: treat this as a writing outcome

- choice: read "make something of it" as producing a readable artifact.
- reason: the user's own three options were all expressive framings.
- dependents:
- reversible: true

## Progress

- step 3: record created at ./reify-log-lighthouse-summers.md. Next check: the probe object exists and carries slots, not invented fact.
```

`probe-opening.md`:

```markdown
# Working title: Four Seconds

The light came around every [interval] seconds at [lighthouse name], and you could set a night by it. What stays is not the beam. It is the gap.

Slots to fill before this becomes prose: [lighthouse name], [coast or town], [which summers], [who else was on the rocks].

Probe only. Written now, not recalled. Nothing here is a claim about your life.
```

This probe is later absorbed by `part-1-sketch.md` and moved to `superseded/`. See `examples/finalize-handoff.md` for that move.
