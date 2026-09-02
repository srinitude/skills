# Enhance a task prompt

Read this example when unsure what a complete normal run looks like: a bare task arrives, the whole message is the prompt, and the reply is an enhanced prompt in the delivery shape, never the task's output.

The user's words:

```
write code to dedupe my csv
```

Step 1 isolates the whole message as the prompt and saves it to a scratch file, `prompt.txt`, holding exactly that one line. Step 2 reads it as a coding prompt for a coding target. Step 3 runs the deterministic checks:

```
$ mise run check-prompt prompt.txt
note    no success criteria detected; state how the target knows it is done

No action findings. Notes feed step 3's findings list; semantic checks stay with you.
$ echo $?
0
```

```
$ mise run context-checks coding
[coding]
- Language and version pinned.
- Environment and dependencies stated.
- Inputs, outputs, or the interface defined.
- Error handling and edge cases mentioned.
- Testing or acceptance criteria stated.
- Anything that must not be touched, named.

Apply every matching context, usually one, sometimes two for a prompt that spans them. Name each in "What changed".
$ echo $?
0
```

The visible reply, filled from `assets/delivery-template.md` and saved as the scratch draft `delivery.txt`:

Here is the enhanced prompt:

```
Write a Python 3 script that removes duplicate rows from a CSV file.

Context: the file may be large (up to ~1M rows) and has a header row.

Requirements:
- Take input and output file paths as command-line arguments.
- Treat two rows as duplicates when every column matches exactly; keep the
  first occurrence.
- Preserve the header and the original column order.
- Stream the file rather than loading it fully into memory.
- Print a one-line summary: rows read, duplicates removed, rows written.

Use only the standard library. Include brief usage instructions.
```

**What changed**

- Validated as a coding prompt.
- Pinned the language and the command-line interface.
- Defined "duplicate" and which occurrence to keep.
- Added scale, memory, and output expectations.
- Constrained dependencies to the standard library.

**Open questions**

- Should duplicates match on every column, or on a key column?

Step 6 runs both deterministic passes on the draft reply before sending:

```
$ mise run check-delivery delivery.txt
pass  lead-in line "Here is the enhanced prompt:" present
pass  a fenced block follows the lead-in
pass  the fence is not empty
pass  "What changed" has 2 to 6 bullets (found 5)
pass  "Open questions" has at least one bullet
pass  no secret-shaped strings in the reply
all shape checks passed
$ echo $?
0
```

```
$ mise run check-prose delivery.txt
measure sentence-length spread 4.0 (low spread = uniform rhythm; weigh lightly)
measure em-dashes per 1000 words 0.0 (weak signal alone)
measure numerals per 1000 words 6.5 (few = little checkable detail; genre-dependent)
measure three-item lists 1 (a habit only when most lists come in threes)

Signals, not verdicts. Judge clusters against the genre's own norms.
No convergence: no rework required by this check.
$ echo $?
0
```

The only files this run creates are the two scratch files shown above, `prompt.txt` and `delivery.txt`, whose full contents appear in this example. The user runs the enhanced prompt wherever they choose.
