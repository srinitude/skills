# Example: new, from a decision that needs picking

Guess this removes: what the first reply and record look like when the vague idea is a choice between forms rather than a piece of writing, and what the probe object is when the decision is the thing being tested.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/coffee-log`. The installed `starting-point` skill was present, so its five point map (outcome, proof, constraints, starting path, unknowns) was applied privately to set the target, completion proof, and first milestone.

## The user says

> I keep a text file of every coffee I try, origin, roast, how I brewed it, a one line verdict. Two years now. I want to turn it into something others could use but I can't tell if that's a searchable site, a static page, or just a cleaned spreadsheet. Help me decide what it should actually be.

## Commands run, with real output

```
$ pwd && ls -a
/home/user/workspace/test/t-reify/examples-run/coffee-log
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
total 16
drwxr-xr-x 2 user user 4096 Aug 30 07:33 .
drwxr-xr-x 3 user user 4096 Aug 30 07:33 ..
-rw-r--r-- 1 user user 1650 Aug 30 07:34 probe-shape-comparison.md
-rw-r--r-- 1 user user 1869 Aug 30 07:33 reify-log-coffee-log.md
EXIT=0

$ grep -n "^- status" reify-log-coffee-log.md
18:- status: active
EXIT=0

$ wc -w probe-shape-comparison.md
294 probe-shape-comparison.md
EXIT=0

$ grep -oE "\[[a-z ]+\]" probe-shape-comparison.md | sort -u
[do the verdicts need to be searchable as free text]
[entry count]
[field list per line]
[how many entries]
[what fields each line carries]
EXIT=0

$ grep -nE "19[0-9]{2}|20[0-9]{2}" probe-shape-comparison.md || echo "no invented year present"
no invented year present
EXIT=0

$ grep -nc "^I " probe-shape-comparison.md || echo "no invented first person memory sentence"
0
no invented first person memory sentence
EXIT=0
```

## The executor replies

> The strongest thing you said is that you already have the data: two years of entries you wrote yourself. That is not an idea looking for material, it is material looking for a form.
>
> Here is a provisional form instead of a questionnaire, plus the smallest object that can test it. I wrote `probe-shape-comparison.md`, a one page comparison of your three options against the data you have, and every fact I do not have is a bracket:
>
> > Under 50 entries and the fields are clean columns, the spreadsheet already is the answer. 50 to a few hundred with free text verdicts, the static page filters and sorts with no backend. Hundreds and growing with full text search, then the site earns its weight.
>
> Read that as a probe, not a draft. I checked this directory and the conversation first and found no earlier coffee log material, so nothing here is yours yet.
>
> Default path: the static page. It is the form that serves others with no account, no app, and no backend, and it fits a two year personal log. One alternative changes the completion proof rather than the wording, so it is worth naming: a cleaned spreadsheet, which counts as done when one export exists rather than when one reader confirms they can filter in a browser.
>
> One question, and only because the answer picks the form: how many entries are in the file, and what fields does one line actually carry? One real line from the file settles it.
>
> Record: `/home/user/workspace/test/t-reify/examples-run/coffee-log/reify-log-coffee-log.md`, status `active`, two decisions, `D-001` and `D-002`.
>
> Next action: you give me the count and one real line, and the comparison collapses to one form.

Word count of the reply above: 297, inside the 350 word budget.

## Files this run created

`reify-log-coffee-log.md`:

```markdown
# Reification record: coffee log

- signal: "I keep a text file of every coffee I try. Two years now. I want to turn it into something others could use but I can't tell if that's a searchable site, a static page, or just a cleaned spreadsheet."
- outcome: undecided, provisional: a static page generated from the existing log file that one other person can open and search
- done_means: undecided
- first_milestone: undecided
- next_action: user confirms the count and format of the existing log entries so the generator can be sized
- sources_checked:
  - working directory: reachable, empty, no prior record
  - conversation history: reachable, two years of entries mentioned, no count or format given
- constraints:
  - only the user's own existing log entries may be used
  - no first-person biographical fact may be invented
  - no publication, hosting account, or deploy without the user naming the target and authorizing it
- decisions: see below
- open_questions:
  - how many entries exist, and what fields each line actually carries
- status: active

## Decisions

### D-001 accepted: treat this as a decision between three concrete forms

- choice: read "something others could use" as picking one concrete form from the user's own three options, then proving it on the existing data.
- reason: the user named three forms and asked to be helped to decide.
- dependents: D-002
- reversible: true

### D-002 accepted: probe is a shape comparison, not a draft

- choice: first object is a one-page comparison of the three forms against the existing data, with the unknowns as slots.
- reason: the decision is between forms, so the smallest test is a comparison, not one finished form.
- dependents:
- reversible: true

## Progress

- step 3: record created at ./reify-log-coffee-log.md. Next check: the probe object exists and carries slots, not invented fact.
```

`probe-shape-comparison.md`:

```markdown
# Which form should the coffee log take?

A comparison of the three forms against the data you already have. Every unknown is a slot, not a fact.

## The three forms, tested against the existing log

1. Cleaned spreadsheet. Lowest effort. Survives if the log is already close to columns: origin, roast, brew method, verdict. Fails as "something others could use" if others do not have your spreadsheet app, or if the verdicts are free text that does not filter.
2. Static page. One HTML file generated from the log. Others open it in a browser, no account, no app. Filters and sorts for free. Needs a generator script and a real count of entries to size it.
3. Searchable site. Adds a backend or a client-side index over the page. Worth it only if the entry count is in the hundreds and people search often. Overbuilt below that.

## The one unknown that decides it

[how many entries] and [what fields each line carries]. Everything else flows from that.

- Under ~50 entries and the fields are clean columns: the spreadsheet already is the answer, and "something others could use" means exporting it once.
- 50 to a few hundred, free-text verdicts: the static page. Search and filter without a backend.
- Hundreds and growing, you want full-text search across verdicts: then the site earns its weight.

## Slots to fill before a form is chosen

[entry count], [field list per line], [how many people you mean by "others"], [do the verdicts need to be searchable as free text].

Probe only. Nothing here is a claim about your data. The next move is yours: give me the count and one real line from the file, and the comparison collapses to one form.
```

The finalize for this record, including the exit 1 and exit 2 branches and a passing brief, follows the same steps as `examples/finalize-handoff.md` and is not repeated here. The difference is the handoff is an executable one: the generator script that turns the log into the static page, prepared and not deployed because no hosting target was named.
