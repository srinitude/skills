# Worked example

This example shows the shape of a correct delivery. Its content is illustrative only. Compose your own text fresh each time.

**Input:** "write code to dedupe my csv"

**Output, an enhanced prompt, not code, in the delivery shape:**

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
