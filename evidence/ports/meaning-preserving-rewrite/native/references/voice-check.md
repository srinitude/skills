# Voice check for policy and plan rewrites

Use when validating prose under `meaning-preserving-rewrite`. Scan **prose only**.

## Skip these regions

- Fenced blocks labeled as test data or checker input
- Inline backtick code, exact source quotations, and code fences that must stay verbatim
- Backup copies of old files
- Raw command or tool output quoted as evidence

Never fix prose with a global replacement across mixed prose and code. Patch specific prose, then recheck nearby code examples and syntax.

## Checker test data

```text
blocked words: delve | dive into | tapestry | testament | realm | journey | landscape | navigate | underscore | robust | seamless | leverage | elevate | embark | unlock | unleash | harness | foster | crucial | vital | pivotal | nuanced | intricate | meticulous | profound | vibrant | showcase | streamline | empower | holistic | resonate | boasts | comprehensive | cutting-edge | game-changer | unwavering | bustling
blocked phrases: when it comes to | in today's world | look no further | shed light on | pave the way | a testament to | plays a crucial role | in conclusion | in summary | dive deeper | take it to the next level
blocked closers: No rush | Let me know | Feel free to | I hope this helps | happy to help | What comes to mind? | I'll run with it
```

## Also fail on

- Em dash (`—`) or en dash (`–`) characters
- Stiff full forms when a contraction is natural: bare `Do not`, `does not`, `is not`, `cannot`, `will not` in prose (paths and quotes exempt)
- Zero contractions in a long humanized document (expect multiple natural ones)
- Voice applied only to the plan while SOUL/AGENTS/notes/reports stay stiff
- Plan missing a statement that the same voice covers planned artifacts and future templates
- Unclear or awkward grammar, even if the meaning is recoverable
- Compressed imperatives that hide subject or strength (`Keep X above mandatory`)
- Pointers without a clear local referent (`above`, `this`, `those` with no nearby anchor)

## How to store the live lists in a plan

```text
blocked words: ...
blocked phrases: ...
blocked closers: ...
```

Label the fence as checker test data, not prose.

## Suggested scan shape

1. Split out fenced blocks; keep only non-fence prose for term matching.
2. Count blocked words/phrases/closers with word-boundary or phrase match.
3. Count `—` / `–`.
4. Count natural contractions (`don't`, `it's`, `we'll`, ...).
5. Read each rule aloud for clarity. Fail unclear or awkward sentences even when term lists are clean.
6. Confirm governed files stay below 150 lines and 20,000 characters after the voice pass.
7. Include final report strings when present: `VALIDATION.md` prose, and string values inside `final-validation.json`, `independent-review.json`, and ledger `meaning` / `routing_rationale` fields. Keep the scope count honest in the human report.
8. Record PASS/BLOCKED with evidence in `VALIDATION.md`. After any post-scan wording fix in a scanned report, rescan that file before final PASS.
