# Every design craft, and where its decisions live

Load this when the work is not a screen, when the person names a craft this skill has not seen, or when step 3 cannot place the artifact.

## What this skill claims, and what it does not

The job is craft agnostic. Every discipline makes choices, every choice trades something away, and in every discipline some choices arrive inherited rather than made. That part holds for a florist and for a design system team equally.

The library is not evenly deep. It was harvested from published practice, which is thickest around screens, brands and product, and thinner around flowers, tailoring, naval interiors and lighting rigs. So the honest claim is this: the method reaches every craft, the vocabulary reaches every craft, and the depth of the questions varies by craft. When the questions on a shelf are thinner than the work in front of you, the columns still hold: what was chosen, what it trades away, what it risks, and whether anybody decided it.

## Naming your craft is the fastest route

Resource gate: run `mise run validate` before using package files named here.

`assets/disciplines.yaml` maps two hundred occupation names to the shelf their decisions live on, from art director to naval architect. Saying what you do lands the slice in one step, because naming the craft is the strongest signal there is about where the questions are.

Measured across sixty five occupations, each given one line of real work in that trade's own words: every one passes the gate, sixty two land the right shelf first, and all sixty five land it in the top three.

## When the craft is not listed

Place the work by what kind of thing it is, not by the job title.

| The work is mostly about                           | Shelf                                     |
| -------------------------------------------------- | ----------------------------------------- |
| an object someone holds, wears or unwraps          | Physical product, packaging and print     |
| a place people move through                        | Spatial, ambient and built space          |
| something that unfolds in time                     | Motion, film and moving image             |
| something heard or felt                            | Sound and haptics                         |
| words a person reads and acts on                   | Voice, tone and UI copy                   |
| pictures, marks and photographs                    | Icons, illustration and photography       |
| letterforms and text setting                       | Typography and editorial typesetting      |
| what a thing is called and how it sits in a family | Naming and brand architecture             |
| what the thing stands for against its category     | Brand distinctiveness and positioning     |
| something other people build on                    | Design systems and developer surfaces     |
| how the work gets made and agreed                  | Design process, stakeholders and journeys |

Then add your craft to `assets/disciplines.yaml`, add the words your trade uses to `assets/trade-terms.yaml`, and run `mise run bench`. The measure only moves up.

## The crafts this library serves thinly

Placing a craft is not the same as serving it. Nine of the sixty five measured crafts send fewer than three of their own words into five or more questions on the shelf they belong on: drafting, fashion design, industrial design, interior design, lighting design, medical device design, patternmaking, toy design and urban planning. The pattern is plain. This library was harvested from published practice, and published practice is thickest where the work is a screen.

Re-routing them was tried and refused. The shelf whose questions share the most words with an industrial design brief is accounts and security, and for a lighting rig it is typography. Word overlap is a good way to generate candidates and a bad way to decide, so these crafts stay on the shelf their decisions actually belong to, and the thinness is reported rather than hidden.

## What to do when a shelf is thin for your craft

Run the slice anyway and read what comes back as prompts rather than as answers. A question written about a checkout that asks what the interface does when the person is in a hurry is the same question a signage designer asks at a junction. Where the question does not transfer, write the row from the work: the columns are the method, and the library is the accelerator.
