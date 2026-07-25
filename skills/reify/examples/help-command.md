# Example: the help command

Guess this removes: what `help` prints, and how the executor reports the state of a record it did not create in this session.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`.

## The user says

> help

## Commands run, with real output

```
$ ls reify-log-*.md
reify-log-lighthouse-summers.md
EXIT=0

$ grep -n "^- signal\|^- outcome\|^- status\|^### D-" reify-log-lighthouse-summers.md
3:- signal: "I keep thinking about the lighthouse from summers when I was a kid."
4:- outcome: undecided, provisional: one short piece about the interval between flashes
17:- status: active
21:### D-001 accepted: treat this as a writing outcome
EXIT=0
```

The script help text is part of the same answer when the user asks about the handoff step.

```
$ python3 "$SKILL_DIR/scripts/validate_brief.py" --help
usage: validate_brief.py [-h] brief

Validate a saved reification brief.

The input is a JSON object holding the reification record fields:
signal, outcome, done_means, first_milestone, and next_action strings,
constraints, sources_checked, decisions, and open_questions lists, and
a status of active, finalized, or scrapped. Each decisions entry is an
object with id, choice, reason, dependents, and reversible. Pass - to
read the object from stdin. The report is JSON on stdout.

Exit codes:
  0  the brief passes
  1  the brief is invalid or cannot be read
  2  command usage is invalid, including a wrong script path

Example:
  SKILL_DIR=/path/to/skills/reify
  python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json

positional arguments:
  brief       JSON file path, or - for stdin

options:
  -h, --help  show this help message and exit
EXIT=0
```

## The executor replies

> Six commands, and one record already open in this directory.
>
> | Command                | Result                                                                        |
> | ---------------------- | ----------------------------------------------------------------------------- |
> | `help`                 | this list plus the current record state                                       |
> | `new <thought>`        | start from a loose thought, memory, or fragment                               |
> | `continue <record>`    | resume a saved record, for example `continue reify-log-lighthouse-summers.md` |
> | `revert <decision-id>` | undo one recorded choice, for example `revert D-001`                          |
> | `finalize`             | freeze the outcome and build the artifact or handoff                          |
> | `scrap`                | mark the direction scrapped and stop                                          |
>
> Current state, read from `reify-log-lighthouse-summers.md`: signal is the lighthouse from childhood summers, outcome is still undecided with one provisional shape on the table, status is `active`, and one decision exists, `D-001`, treating this as a writing outcome. Decision IDs match `D-` plus three digits and count up per record, so the next one here is `D-002`.
>
> A second record also lives in this directory, `reify-log-tool-shed.md`, and it is a separate reification. Say which one you mean, or just talk and I will use the lighthouse one, since it is the one with an open question.
>
> Next action on the lighthouse record: you tell me whether the probe opening reads true, and I write from there.

## Files this run created

None. `help` reads state and writes nothing.
