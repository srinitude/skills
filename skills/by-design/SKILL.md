---
name: by-design
description: 'Use when any request arrives, and especially when it touches a screen, component, flow, brand, layout, typography, colour, motion, copy, icon, form, table, dashboard, navigation, onboarding, pricing, checkout, notification, accessibility, design system, or brief. Use when choosing between directions, when shaping something unbuilt, when reviewing, critiquing, or shipping work, and during ordinary design conversation. A request that holds no design surface costs one command and nothing else. Keywords: design, redesign, review, crit, critique, feedback, mockup, wireframe, prototype, trade-off, decision, rationale, pre-ship, ready to ship, looks generic, which direction, style guide, design token.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# By design

Read this rule first, because every step below serves it: **one row per decision, and one question at most per reply.**

This skill runs wherever Python 3.11 or newer and a shell are available. It uses the standard library only and needs no network access.

The name is the question this skill asks of every choice in a piece of work. Was it by design, or did it arrive with a template and stay?

This skill surfaces decisions rather than reviewing designs. Critique, choosing a direction, and shaping unmade work are the same act at three moments: after a decision, during it, and before it. So the job is one sentence. Find the decisions in this work, name what each one trades away, and say which ones nobody actually decided.

That last part carries the value. Weak design usually comes from choices nobody experienced as choices, such as a grid carried over from another page or a tone borrowed from a competitor.

## Which commands does this skill accept?

| Command | What it does                                                                         |
| ------- | ------------------------------------------------------------------------------------ |
| help    | Show this table and one line per command.                                            |
| watch   | Default. Record decisions to the ledger and reply with one question at most.         |
| judge   | Read an existing screen, component, flow, or copy block and fill the ledger from it. |
| choose  | Lay out the trade-off between two or more directions and leave the choice open.      |
| shape   | Open ledger rows as empty slots for work that does not exist yet.                    |
| audit   | Test which stated constraints in a brief are real and which are hardened choices.    |
| ask     | Return the full slice of questions and leave the ledger untouched.                   |

Run watch when the user names no command. Pick the posture from what arrives, using this table, and treat the user's words as stronger than the attachment.

| What arrives                                                | Posture |
| ----------------------------------------------------------- | ------- |
| one artifact, such as a screenshot, a link, or a copy block | judge   |
| two or more options, or a stated fork                       | choose  |
| intent alone, with nothing built                            | shape   |
| a brief or a list of stated rules                           | audit   |
| a request for questions, phrased as give me or list         | ask     |

## How do I run this skill?

Run every step in order. Each step names one action and the result it must produce. When a result differs from the one named, fix it and run that step again before moving on.

0. Gate the request. Run `python3 scripts/gate.py --text "<the request>"`. A line starting with `not-design` ends the run here, and this skill contributes nothing to the reply. A line starting with `design` continues to step 1. Result: one verdict line, and on `not-design` no further step runs.
1. Read the ledger. Run `python3 scripts/ledger.py show --file decision-ledger-<slug>.md`. Exit 1 means the ledger is new, so run `python3 scripts/ledger.py init --file decision-ledger-<slug>.md --slug <slug>`. Result: the file exists and you can list the decisions already in it.
2. Name the posture in one clause, using the second table above. Result: a posture name you can write into the reply.
3. Read the artifact for its coordinates. When the artifact is a picture, first write two lines: what this is, and what state it is in, choosing from populated, empty, error, loading, offline, disabled, or mid-flow. A picture carries its state and a description of a picture usually loses it, and the state is often the decision. Then run `python3 scripts/locate.py --file <artifact>`, or pass the request with `--text`, passing those state words to `--hint` when they matter. Result: a ranked list, each place carrying its score, how many terms earned it, and which ones. A `weak read` line on stderr means the ranking should not be trusted, either because one term carried the top place or because the top two are too close to separate. When it appears, name the artifact type yourself and run it again with `--hint "<the words for what this is>"`, which is how a discipline the vocabulary does not cover still lands.
4. Pull the questions. Run `python3 scripts/slice.py --category "<category>" --stage <stage> --match "<a noun from the artifact>" --limit 20`. Result: exit 0 and a list of questions. Read stderr: a `widened:` line means the pin loosened, so say that in the reply. A match that finds only one or two questions loosens the other pins first and keeps the match, because the word from the artifact is the pin worth holding. A `dropped match` line means the shelf does not talk about your craft in your craft's words, so say that in the reply and write the rest of the rows from the work rather than from the slice. Pass `--match` with a word the artifact itself uses, because the category alone returns what is common rather than what is here.
5. Group the questions into decisions. Several questions usually point at one choice. Turn every observation into the decision it implies before you drop it: an unlabelled grid is not a defect to mention, it is the decision nobody made about how the grid is read aloud. Result: a short list of decisions, each shorter than the list of questions, and nothing observed that has no row.
6. Write one row per decision. Run `python3 scripts/ledger.py add --file decision-ledger-<slug>.md --decision "<text>" --chosen "<text>" --trades "<text>" --risks "<text>" --origin <deliberate, inherited, or open>` and, when a question from step 4 raised the row rather than the artifact, `--source "<question id and url>"`. Result: one appended line per decision, and a file that says which rows came from looking and which came from the library.
7. Count what you wrote. Run `python3 scripts/ledger.py count --file decision-ledger-<slug>.md --decision "<text>"`, and `show` to count the rows and the inherited ones for the reply line. Result: numbers taken from a command rather than from memory, which step 10 then checks against the file.
8. Ask the script whether to speak, and which row. Run `python3 scripts/speak.py --file decision-ledger-<slug>.md --rank` to order the inherited rows by how little is known about each, then run `python3 scripts/speak.py --file decision-ledger-<slug>.md --decision "<the first ranked row>" --origin inherited --live yes`. Result: an ordered list, then a line starting with ask or hold. Put one question in the reply when that line starts with ask.
9. Draft the reply from assets/reply-template.md. Result: four lines, each filled.
10. Check the draft. Run `python3 scripts/check_reply.py --file <draft path>`, adding `--full-slice` for the ask posture and `--ledger-dir <folder>` when the ledger does not sit beside the draft. This reads the ledger named in the reply and checks its counts against the file, so a number nobody ran fails here. Result: the line `draft passed every rule`. Any other line names what to fix, so fix it and run this again.

## When does this skill speak?

Step 8 answers this, and the script holds the counts so the answer stays the same each time. Speak when a decision is live, the choice arrived inherited, and the ledger has seen it fewer than three times. Stay quiet in every other case and write the row anyway. Silence is the common and correct outcome.

References for the reasoning behind that rule sit in references/interruption.md.

## What loads when?

- references/coordinates.md: read at step 3, for the 35 category names, the eight lenses, and the widening ladder.
- references/interruption.md: read when the reasoning behind step 8 matters, or when a user asks why the skill stayed quiet.
- references/ledger-format.md: read at step 6, for what belongs in each column.
- assets/gate-terms.yaml: the vocabulary step 0 matches against, read by the gate.
- assets/terms-index.yaml: the terms counted from the questions, per category, read by scripts/locate.py at step 3.
- assets/trade-terms.yaml: the words a discipline uses for its own work, written by hand, read alongside the counted terms at step 3. Add to this file when a discipline lands on the wrong shelf, then run scripts/bench.py.
- assets/disciplines.yaml: the occupation names themselves, mapped to the shelf each craft's decisions live on, read at step 3 and weighted above the trade words.
- references/disciplines.md: read when the work is not a screen, when a craft is not listed, or when step 3 cannot place the artifact.
- references/generation-contract.md: read before changing this skill's layout, task graph, or checks, for the rules the structure has to satisfy.
- references/decisions.md: read when you need to know why this skill is built the way it is, before changing a script, a threshold, or the vocabulary.
- references/decisions-field.md: read alongside references/decisions.md when the question is about a measure, a fixture, or how far the library reaches across crafts.
- assets/index.yaml: the category index, read by the scripts.
- assets/questions/: one file per category, holding all 16,112 questions. The scripts read these, and a reply quotes only the selected rows.
- assets/reply-template.md: read at step 9.
- scripts/: run these. `--help` on any of them prints flags, exit codes, and an example.
- scripts/crafts.py: run to see how far this skill reaches across design occupations, and `--thin` to list the crafts their own shelf serves thinly.
- scripts/tests/: run `python3 -m unittest discover -s scripts/tests -p 'test_*.py'` after changing any script.
- examples/: read the file matching the command being run, read examples/example-widened-slice.md before trusting any slice, read examples/example-weak-read.md when step 3 prints a weak read line, and read examples/example-image-artifact.md when the work arrives as a picture, and read examples/example-no-question.md when the ledger holds no inherited row.
- evals/: read when measuring this skill rather than using it.
- scripts/bench.py: run after any change to the vocabulary, the term index, or the scoring, and after any run on real design work.

## How does real work stay in this skill?

Every real design task run through this skill becomes a permanent fixture, so a later change cannot quietly undo what this one fixed. Run these steps at the end of any run on real work.

1. Save the brief in the words that discipline actually used, at `evals/files/brief-<nn>-<slug>.txt`. Result: a file that reads like the request rather than like a test.
2. Record the shelf that turned out to be right, as one new key in `evals/files/briefs.json`. Result: one key added and no existing key changed.
3. Add any request the gate should have turned away to `evals/files/non-design.json`. Result: one more request the gate has to stop.
4. Run `python3 scripts/bench.py`. Exit 1 names every measure that fell, so fix the cause and run it again. Result: the line `exit 0`, meaning no measure sits below the recorded baseline.
5. Run `python3 scripts/bench.py --update` only after step 4 passed and only when this run added a fixture. Result: a baseline no later run may fall below.

The baseline in `evals/baseline.json` holds the gate measures and, for each fixture, the rank position of the shelf that was right. Position is the sensitive part. A weakened vocabulary moves a shelf from second place to fifth long before it leaves the top three, and only the position notices that.

Never lower a recorded number to make a run pass. A measure that fell is a report about the change, not about the fixture.

## Does this work for my craft?

Yes, and the fastest route is to say what you do. `assets/disciplines.yaml` maps two hundred occupation names to the shelf their decisions live on, from art director to naval architect to floral designer, so naming the craft lands the slice in one step. Measured across sixty five occupations, each given one line of real work in its own trade language, every one passes the gate, sixty two land the right shelf first and all sixty five land it in the top three.

The method is craft agnostic and the library is not evenly deep. Nine of the sixty five crafts are thinly served by the shelf they belong on, and they are named in references/disciplines.md rather than left to be discovered mid run. It is thickest around screens, brands and product and thinner around flowers, tailoring and lighting rigs. When the shelf is thin, the columns still hold, so read the slice as prompts and write the rest of the rows from the work. references/disciplines.md carries the placement table for a craft that is not listed, and the two lines to add so the next person does not have to.

## What belongs to another skill?

Facts belong elsewhere. A skill that captures design context owns tokens, screen inventories, acceptance criteria, and stated rules. This skill owns decisions. The seam matters: every stated rule in a brief is a choice somebody made and then wrote down as a constraint, which is what the audit posture tests. A skill that enumerates screen states owns the state list, and this skill attaches decisions to those states.

## Gotchas

- Step 0 continues by default. It stops only when a request names another craft and holds no design surface, because design conversation runs on ordinary words and a list of design nouns cannot recognise all of it.
- Choosing the category by hand sends the slice to the wrong shelf. Step 3 reads the artifact instead, which is why it comes before step 4 rather than inside it.
- Step 3 proposes and you decide. Measured against twenty six briefs from twenty six disciplines, the right shelf came first twenty four times and appeared in the top three every time. It reads two vocabularies, one counted from the questions and one written by hand for the words a discipline uses, so a brief in trade language such as lower thirds, a kill feed, or an alerting sound for a bus still lands. No ranking that was wrong stayed silent, so treat a weak read line as the instruction to pass `--hint` rather than as a note.
- A category with no `--match` returns what is common in that category rather than what is in front of you. Pass a noun the artifact uses.
- Read stderr at step 4. A widened slice looks the same as a precise one and answers a broader question.
- Group before writing. Twenty questions about a checkout screen usually reduce to four or five decisions.
- Anything you noticed and did not write down is lost. The ledger holds choices, so phrase the observation as the choice it implies and give it a row, rather than keeping it in the reply or dropping it.
- Leave the chosen column empty during choose and shape. The empty cell is the deliverable.
- Expect inherited rows. A ledger where every row reads deliberate is a sign the audit skipped step 5, and a ledger with none of them cannot earn a question, which step 10 enforces. The word none is the whole fourth line in that case.
- Match a category name exactly. An unmatched name exits 2 and prints the name it received.
- Slice output replaces long dashes with a comma or a colon. The stored files keep their punctuation.

## When is this skill done?

On a `not-design` verdict the work is done at step 0, with nothing written and nothing said. Otherwise the work is done when the ledger holds one row per decision, every row carries an origin, the reply follows the template with counts taken from commands run in this turn, and `python3 scripts/check_reply.py` printed `draft passed every rule`.
