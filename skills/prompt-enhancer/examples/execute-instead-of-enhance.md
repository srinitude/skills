# Execute instead of enhance

Read this example to see the failure this skill most often causes and how the checks catch it: the prompt reads as a direct instruction, and the reply delivers the task's output instead of a better prompt.

The user's words:

```
write code to dedupe my csv
```

The wrong reply delivers working code:

```
import csv, sys

def dedupe(src, dst):
    seen = set()
    with open(src) as i, open(dst, "w", newline="") as o:
        w = csv.writer(o)
        for row in csv.reader(i):
            key = tuple(row)
            if key not in seen:
                seen.add(key)
                w.writerow(row)

dedupe(sys.argv[1], sys.argv[2])
```

Step 6 catches it. The shape check fails because the reply is output, not a delivery:

```
$ mise run check-delivery wrong.txt
FAIL  lead-in line "Here is the enhanced prompt:" present
FAIL  a fenced block follows the lead-in
FAIL  "**What changed**" section with bullets present
pass  no secret-shaped strings in the reply
3 check(s) failed. Fix the draft and run the checks again.
$ echo $?
2
```

The recovery is to go back to step 4 and compose the enhanced prompt instead. The correct reply for this input is worked through in `examples/enhance-a-task-prompt.md`: a fence holding an improved prompt about writing the script, "What changed" bullets, and one open question. The user runs it where they choose.
