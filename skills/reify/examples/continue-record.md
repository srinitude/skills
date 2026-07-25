# Example: continue a saved record

Guess this removes: what string `continue` takes, and what to do when the directory holds more than one record.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`. A second, unrelated record was created here in between, `reify-log-tool-shed.md`, so this run shows the collision case rather than the easy one.

## The user says

> continue the lighthouse thing

## Commands run, with real output

```
$ ls reify-log-*.md
reify-log-lighthouse-summers.md
reify-log-tool-shed.md
EXIT=0

$ sed -n "1,20p" reify-log-lighthouse-summers.md
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

EXIT=0

$ grep -n "^- open_questions" -A 2 reify-log-lighthouse-summers.md
15:- open_questions:
16-  - which lighthouse, which years, who else was there
17-- status: active
EXIT=0
```

Two records match the glob, so the argument matters. The resolved command is `continue reify-log-lighthouse-summers.md`. Had the user typed only `continue` with two records present, the reply lists both and stops rather than picking one.

## The executor replies

> Resuming `reify-log-lighthouse-summers.md`. The other record here, `reify-log-tool-shed.md`, stays untouched and separate.
>
> Where we left it: signal is the lighthouse from childhood summers, outcome is still open with one provisional shape, one decision recorded, `D-001`, treating this as a writing outcome rather than an archive or a keepsake. Status `active`.
>
> The one settled thing I am not asking again: you already said the return matters more than the tower, so the interval between flashes stays the spine unless you move it.
>
> The one open question is unchanged, and it is the only thing blocking prose: which lighthouse, which summers, and who else was there. Nothing in the file invents any of those, and nothing will.
>
> Next action: give me any one of those three facts and part 1 gets written from your material. If you would rather leave the facts out, I can keep working in bracketed slots for as long as you want, and the piece stays honest and unfinished until you fill them.

Word count of the reply above: 178, inside the 350 word budget.

## Files this run created

None. `continue` reads the record and writes only the progress entry it appends after the next consequential step.

The second record that made this case interesting, `reify-log-tool-shed.md`, in full:

```markdown
# Reification record: tool shed

- signal: "the shed could be a workshop"
- outcome: undecided
- done_means: undecided
- first_milestone: undecided
- next_action: measure the shed
- sources_checked:
  - working directory: reachable, one other record present
- constraints:
  - separate record because the signal differs from the lighthouse record
- decisions: see below
- open_questions:
  - is the floor sound
- status: active

## Decisions

### D-001 accepted: keep this in its own record

- choice: new file rather than a section inside reify-log-lighthouse-summers.md.
- reason: one record holds one active reification.
- dependents:
- reversible: true

## Progress

- step 3: record created at ./reify-log-tool-shed.md. Next check: a measurement exists.
```

Both records number decisions from `D-001`. IDs are per record, so `D-001` in the shed record and `D-001` in the lighthouse record are different decisions and `revert D-001` needs the record named with it.
