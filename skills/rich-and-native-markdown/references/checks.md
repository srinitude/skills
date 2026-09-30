# Run the file and link checks

- The script checks facts a program can test.

## Purpose and reading route

- **Reading trigger:** Read before running or changing the file checker.
- **Prerequisites:** No other package file must be loaded first. Required companion skills must already be active.

- Read this file before running the checker or changing its rules.
- It does not judge clear writing, preserved meaning, true reading needs, or support in every Markdown app.

## Run

- The bundled helpers need Python 3.11+ and `markdown-it-py`.
- Run the helpers through Mise from the skill folder. `mise.toml` pins Python 3.12 and installs `markdown-it-py` into the package's own virtual environment.
- Pass absolute paths, since Mise runs each task from the skill folder.
- If Python is unavailable, use equivalent tools for every required check.
- Report any check you cannot perform; an unavailable tool is not a pass.
- The script reports a missing parser as an error.
- The script itself installs nothing. `ROOT` means the folder that holds the full Markdown output set.

### Run the commands

```text
mise run check-markdown -- ROOT --manifest PATH
mise run test
```

- The checker prints JSON.
- Exit code 0 means its mechanical checks passed.
- A nonzero exit code means an error or a failed check.
- Always finish each `needs_review` item before accepting the full result.

## Make the manifest

- Read [manifest fields](manifest.md) before preparing the file inventory, required-read edges, and any justified paragraph exceptions.
- Enable its optional structure checks for this skill and every governed output set.

## Lines and splitting

- Every Markdown file under `ROOT` is checked, even if the manifest omits it.
- The count includes blanks, frontmatter, fences, and a final line without a newline.
- CRLF and CR line endings are read as newlines.
- Unicode paragraph marks are not treated as physical newlines.
- Empty files have zero lines.

- At 150 lines, a file needs a reviewed reason in `core_reasons`:

```json
{"guide.md": "All remaining text is core; splitting the exact table would break it."}
```

- Use the file path as the key.
- The reason must be true for the current content.
- The checker only tests that a reason exists; you judge whether it is sound.
- At 200 lines the check fails, even with a reason.
- The maximum is 199.
- Review a split before the next addition reaches 150; the script cannot predict an edit that has not yet been made.

## Links and headings

- The installed parser reads CommonMark.
- With `structure` enabled, require one H1, H2 and H3, valid active parents, and content between headings and before EOF. Review filler, heading meaning, deeper topic needs, and supported HTML or container headings separately; a parser cannot prove them.
- The checker follows inline and reference links, image paths, and HTML `href` and `src` attributes.
- It ignores literal links inside fenced code, indented code, and inline code.

- Local relative links must exist.
- Markdown fragments must match a heading ID or an HTML `id` or named anchor.
- Plain headings use GitHub-style lowercase IDs: `Hello World` becomes `hello-world`; repeated headings gain `-1`, `-2`, and so on.
- Punctuation is removed and spaces become hyphens.
- Verify special characters, embedded HTML, and app-specific heading rules in the actual renderer.

- CommonMark itself does not set heading IDs.
- The default `heading_ids` value is `github-style`, a limited convention rather than a claim of exact app support.
- For another scheme, use `"heading_ids": "explicit"` to turn off guessed heading IDs.
- Supply verified IDs with `"anchors": {"guide.md": ["start", "step-one"]}`.
- HTML IDs still count.
- Check supplied IDs in the renderer; the script trusts this map.
- An unmatched Markdown fragment fails instead of being assumed valid.

- External URLs are not fetched.
- A link that starts with `/` may name a website route, so it is sent to manual review.
- Non-Markdown fragments need review too.
- Directories must exist; the script does not guess their index page.

- Wiki links, footnotes, attribute blocks, directives, shortcodes, and includes have dialect rules.
- Some visible forms trigger review notes.
- This is not a full detector: inspect all syntax the CommonMark parser does not understand.
- Check these forms with the real renderer or a separate tool for that dialect.

## Reading cycles

- The checker resolves `.` and `..` and follows symlinks before it checks edges.
- It checks the whole declared required graph, including external chains.
- Self links and direct or indirect required cycles fail.
- Navigation edges are excluded only because the reviewer marked them optional.

- A shared source may serve several readers.
- That is allowed when no required path leads back to itself.
- A completed read may happen again later.
- Only a return to a file on the current active reading path forms a cycle.
- Neither a manifest nor a passed script proves that navigation labels are honest.

## Final review

- Use the actual renderer to check what the reader sees.
- Read all source text too.
- Check meaning, exact data, definitions, reading triggers, linked context, and plain language across the full set.
- Keep proof of what you read and tested.
- Do not call these script results a complete language or dependency audit.

### Check the helper itself

- The runnable self-test uses temporary files and needs permission to create symbolic links.
- If that permission is missing, report the test as blocked.
- It covers line limits, local links, anchors, code examples, declared graph cycles, shared reads, and bad manifests.
- It does not test every renderer or judge a document's meaning.

- The code-limit check uses Python's parser.
- It checks each script for at most 200 physical lines, 30 lines per function or class, and three nested control blocks.
- Each function or class starts a new nesting scope.
- The graph test also checks a 1,500-edge chain and cycle without recursive calls.
