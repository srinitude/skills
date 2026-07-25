# Example: thin facts, so no invention

Guess this removes: what to write when the user asks for prose about their own life and has supplied no name, place, date, or person. This is the failure this skill causes most often: fluent first-person memoir that reads like memory and is entirely invented.

The rule is hard. Never write an invented biographical fact in the user's voice. Write slots, keep the object small, and ask for the two or three facts that unlock real writing.

Working directory for this run: `/home/user/workspace/test/t-reify/examples-run/lighthouse`.

## The user says

> yeah that reads right. just write it out properly, you know what I mean

## What the user has supplied, in full

A lighthouse. Childhood summers. Nothing else. No name, no coast, no years, no other person, no rule, no house. Prose of 700 words needs about a dozen facts, so 700 words here would be about a dozen inventions.

## Commands run, with real output

```
$ wc -w part-1-sketch.md
155 part-1-sketch.md
EXIT=0

$ grep -oE "\[[a-z ]+\]" part-1-sketch.md | sort -u
[coast or town]
[distance from the water]
[interval]
[lighthouse name]
[what the light means to you now]
[what you were not allowed to do after dark]
[where you stand today]
[which years]
[who else was on the rocks]
EXIT=0

$ grep -nE "19[0-9]{2}|20[0-9]{2}" part-1-sketch.md || echo "no invented year present"
no invented year present
EXIT=0

$ grep -nc "^I " part-1-sketch.md || echo "no invented first person memory sentence"
0
no invented first person memory sentence
EXIT=0

$ sed -i '0,/^- dependents:$/s/^- dependents:$/- dependents: D-002/' reify-log-lighthouse-summers.md
EXIT=0

$ grep -n "D-002" reify-log-lighthouse-summers.md
25:- dependents: D-002
32:### D-002 accepted: write a slot sketch instead of first-person prose
EXIT=0
```

The last two commands are the check, not decoration: zero invented years and zero first-person memory sentences is the pass condition for this step.

## The executor replies

> I know the shape you mean, and I will not fake the facts to get there.
>
> Written out properly needs about a dozen specifics I do not have: which light, which coast, which summers, who else was on the rocks, what the rule was. If I write 700 fluent words now, roughly a dozen of them are invented facts about your childhood in your own voice, and you would spend longer deleting them than writing the piece.
>
> So `part-1-sketch.md` is the beat sheet instead, 155 words, nine brackets. Every bracket is a question, and nothing in brackets came from you:
>
> > Open on the rock: the light at [lighthouse name] turns every [interval] seconds, and the cove goes dark between turns.
>
> Three facts unlock the real thing, and they are the cheapest three you have:
>
> 1. the name of the light, or the town it stands off.
> 2. which summers, even as a range.
> 3. one other person who was there.
>
> Give me those and part 1 gets written from your material. Recorded as `D-002`, reversible: if you would rather I write invented placeholder prose and you strike through what is wrong, say so and I will revert it.
>
> Record updated: `reify-log-lighthouse-summers.md`, status `active`, next check is your three facts.

Word count of the reply above: 233, inside the 350 word budget.

## Files this run created

`part-1-sketch.md`:

```markdown
# Four Seconds, part 1 sketch

Slots, not facts. Every bracket is a question for you, and nothing in brackets was supplied by you.

1. Open on the rock: the light at [lighthouse name] turns every [interval] seconds, and the cove goes dark between turns.
2. Place it: [coast or town], the summers of [which years], the house at [distance from the water].
3. People it: [who else was on the rocks], and the rule about [what you were not allowed to do after dark].
4. Turn it: the gap between flashes is the part you remember, and a lighthouse is identified by its gaps.
5. Close it: [what the light means to you now], from [where you stand today].

Three facts unlock real prose: the name or location of the light, the summers, and one other person who was there. Give me those and part 1 gets written from your material, not from invention.
```

Record entry appended by this turn:

```markdown
### D-002 accepted: write a slot sketch instead of first-person prose

- choice: part 1 ships as a five-beat sketch with bracketed slots and a three-fact request.
- reason: the user supplied no name, place, years, or people, and invented biography would be a false memory in the user's own voice.
- dependents:
- reversible: true

## Progress

- step 7: part-1-sketch.md created, 155 words, 9 bracketed slots, zero invented years, zero first-person memory claims. Next check: the user returns the three facts.
```

## The wrong version, for contrast

The failing move is a 730 word first-person draft that names a year, a parents' marriage, a brother, and a lit window in the keeper's quarters, then apologizes for the invention in a footer. A footer does not undo it: the file still reads as the user's memory, and it travels to whoever the user forwards it to. Invention plus a disclaimer is still invention. Slots plus one question cost the user ten seconds and cost nothing in trust.
