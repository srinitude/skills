# Describe files and their reading dependencies

- The manifest is a JSON file.

## Purpose and reading route

- **Reading trigger:** Read before building or checking a Markdown manifest.
- **Prerequisites:** None within this package. The checker guide supplies the command to run.

## Make the manifest

- Paths are relative to `ROOT` unless absolute.
- List every Markdown file in `ROOT`, including nested files and `.MD` files.
- The checker compares the list with files on disk.

```json
{
  "files": ["guide.md", "detail.md"],
  "entrypoints": ["guide.md"],
  "dependencies": [
    {
      "from": "guide.md",
      "to": "detail.md",
      "kind": "required",
      "reason": "Read this detail before the matching task."
    }
  ],
  "core_reasons": {}
}
```

### Classify reading edges

- Use `required` when the target must be read to understand or follow the source.
- This includes a prose instruction without a Markdown link.
- Use `navigation` only for an optional route that supplies no needed context.
- Give every edge a plain reason.
- A label does not prove the choice is right.

### Include the full dependency chain

- Follow required edges outside `ROOT` too.
- Add their outgoing required edges until the full chain ends.
- Use absolute paths for these external files.
- The checker reads each named endpoint and fails on missing or unreadable files.
- It cannot find unlisted prose rules or prove that this chain is complete.
- You must read the sources and check that every required edge is listed.

- List the starting files in `entrypoints`.
- Every governed Markdown file must be reachable from them through local Markdown links or declared edges of either kind.
- If this field is absent or empty, reachability is left for manual review.
- Each file result gives its line count and SHA-256 hash for the exact bytes read.
- A hash marks a version; it does not show that anyone understood its content.

## Optional structure checks

- Add `structure` to require one top-level H1, at least one H2 and H3, active parent chains without skipped levels, content after each heading, and list-based guidance. Omit it only when those project rules do not apply to the output.
- Use `"structure": {"paragraphs": {}}` when no standalone prose is justified.
- For each justified paragraph, record its relative file path, one-based source line, exact parser text, and a specific reason. Example:

```json
{"structure": {"paragraphs": {"guide.md": [
  {"line": 7, "text": "A connected explanation.", "reason": "The causal explanation loses its connection if split into rules."}
]}}}
```

- Invalid or stale exceptions fail. A matching record cannot prove that its reason is sound; review it in context.
- Literal blocks, quotes, tables, metadata, and paragraphs inside lists are not standalone prose faults. They still need meaning and language review.
- Raw HTML requires manual review. Do not hide editable rules in HTML or another excluded form to bypass the rule.
