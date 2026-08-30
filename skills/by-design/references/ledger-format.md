# Ledger format

## The file

One ledger per project, named `decision-ledger-<slug>.md`, kept in the working directory and appended to across sessions. `scripts/ledger.py init` writes the header. Every later row comes from `add`.

## The columns

| Column                  | What fills it                                                          | Empty when                                              |
| ----------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------- |
| The decision            | your words, naming the choice rather than the artifact                 | never                                                   |
| What was chosen         | read from the work, or stated by the user                              | the choice is still open                                |
| What it trades away     | the `tension` field of the matching corpus question                    | no question matched                                     |
| What it risks           | the `failure_it_catches` field of that question                        | no question matched                                     |
| Deliberate or inherited | your judgment, one of deliberate, inherited, open                      | never                                                   |
| What would change it    | the evidence that would reverse the choice                             | the choice is inherited and unexamined                  |
| Source                  | the id and url of the question that raised it, as `Q06418 https://...` | the row came from the work rather than from the library |

## How the posture fills it

- judge: every column filled, chosen read from the artifact.
- choose: chosen left empty on purpose, trades away and risks filled for each option.
- shape: rows open as slots, with only the decision and an origin of open.
- audit: one row per stated constraint in the brief, origin set to inherited when nobody can say who chose it.

## Naming a decision well

Name the choice, never the object. "Row height on the orders table" is a decision. "The orders table" is not. A good name survives the redesign that changes the artifact, which is what makes the ledger worth appending to.

## The column that does the work

Deliberate or inherited is the one column no brief and no review carries. Marking every row deliberate is the tell that the audit did not happen. Inherited is the common case, and a ledger with none of them is a result worth doubting rather than a clean bill of health.

## Why the source column matters

A reader coming back to this file in a month cannot otherwise tell which rows came from looking at the work and which came from the library. Both are worth having and they are not the same evidence. A row with an id can be traced to a sourced question and its recorded failure; a row with an empty source column was seen in the artifact by whoever wrote it.
