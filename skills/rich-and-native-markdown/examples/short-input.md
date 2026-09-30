# Example: a short input

- This example answers one question: does a two-fact note need extra forms, and what does the file checker say about headings with nothing under them?
- It follows native case B01 (`RNM-001` in the evals).

## The request

- User: "Use rich-and-native-markdown. Turn this into Markdown for CommonMark: Bring a pen. The class starts at 9:00 AM."

## The run

- The executor wrote each draft to `.artifacts/example/reminder.md` and checked it with this manifest, `.artifacts/example/manifest.json`:

```json
{
  "files": ["reminder.md"],
  "entrypoints": ["reminder.md"],
  "dependencies": [],
  "core_reasons": {},
  "structure": {"paragraphs": {}}
}
```

- Each check ran from the skill folder with `mise run -q check-markdown -- .artifacts/example --manifest .artifacts/example/manifest.json`.
- The checker prints absolute paths. The skill-folder prefix is removed below; nothing else is changed.

### First draft: the common failure

- The draft keeps both facts and adds no table, image, or checklist. Its H1 and H2 hold no content of their own. This is the failure this skill most often causes: headings added to meet the H1, H2, and H3 minimum, with nothing between them.

```markdown
# Class reminder

## Before class

### What to bring

- Bring a pen.

### When it starts

- The class starts at 9:00 AM.
```

- Output of `mise run -q check-markdown` for this draft, exit code 1:

```text
{
  "scope": "mechanical checks only",
  "errors": [
    ".artifacts/example/reminder.md:1: heading needs non-heading content before the next heading or EOF",
    ".artifacts/example/reminder.md:3: heading needs non-heading content before the next heading or EOF"
  ],
  "needs_review": [
    "Structure mode checks non-quoted heading levels, content presence, and standalone prose; review meaning, filler, required deeper sections, ordered steps versus unordered rules, container headings, and exact example boundaries",
    "Read all prose dependencies and external dependencies through their full closure; confirm the manifest has every required edge and that navigation labels are true",
    "Verify syntax, anchors, readability, and preserved meaning in the actual target renderer"
  ],
  "files": [
    {
      "path": ".artifacts/example/reminder.md",
      "lines": 11,
      "sha256": "c358f4be567e86d5c2c9f38e1a03a2df2755e694d8a97a7414697c33a680b09d"
    }
  ],
  "cycles": []
}
[check-markdown] ERROR task failed
```

### Repaired draft

- The repair gives the H1 one line of real content, keeps the pen under the H2, and puts the start time in its own H3. Both facts and the exact time stay the same.

```markdown
# Class reminder

- This note has one thing to bring and one start time.

## Before class

- Bring a pen.

### Start time

- The class starts at 9:00 AM.
```

- Output of `mise run -q check-markdown` for this draft, exit code 0:

```text
{
  "scope": "mechanical checks only",
  "errors": [],
  "needs_review": [
    "Structure mode checks non-quoted heading levels, content presence, and standalone prose; review meaning, filler, required deeper sections, ordered steps versus unordered rules, container headings, and exact example boundaries",
    "Read all prose dependencies and external dependencies through their full closure; confirm the manifest has every required edge and that navigation labels are true",
    "Verify syntax, anchors, readability, and preserved meaning in the actual target renderer"
  ],
  "files": [
    {
      "path": ".artifacts/example/reminder.md",
      "lines": 11,
      "sha256": "e32c8789d83d023bcc38312d1f18b53b165f60b004636662e9c62c3eedb53981"
    }
  ],
  "cycles": []
}
```

## The reply

- The executor returned the repaired Markdown above and this note: "Target: CommonMark. Both facts and the 9:00 AM time are unchanged. The file checker passed. Its three review items are still open: meaning, the manifest's reading edges, and a check in the real renderer."
