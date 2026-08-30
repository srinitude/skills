# Rewrite to READY

Guess this example removes: whether an already explicit prompt should be expanded, and whether the rewriter performs the requested file operation.

## User says

```
/only-one-interpretation rewrite Context: The eventual executor is working in /workspace/project on 2026-09-02 UTC. Rewrite task: Read only /workspace/project/input.csv as UTF-8. Create /workspace/project/output.csv as UTF-8 by keeping the header and the first occurrence of each row when every field matches exactly. Use Python 3.13 and only its standard library. Do not change or delete input.csv or any other file. If input.csv is missing, unreadable, or invalid CSV, create nothing and report the error. Success requires output.csv to parse as CSV, preserve the input column order, and contain no duplicate data rows under the stated equality rule. Return the created path, rows read, duplicates removed, and rows written. Do not run this task while rewriting it.
```

## Visible reply

````
```
Context: The eventual executor works in `/workspace/project` on 2026-09-02 UTC.

Required behavior:
- Read only `/workspace/project/input.csv` as UTF-8 CSV.
- Use Python 3.13 and only its standard library.
- Create `/workspace/project/output.csv` as UTF-8 CSV. Preserve the header and original column order. Treat two data rows as duplicates only when every field matches exactly, and keep the first occurrence.

Prohibited behavior:
- Do not change or delete `/workspace/project/input.csv` or any other file.
- Do not execute this task while rewriting it.

Failure behavior: If `input.csv` is missing, unreadable, or invalid CSV, create no file and report the error.

Output: Return the created path, rows read, duplicates removed, and rows written.

Acceptance criteria: `output.csv` parses as CSV, preserves the input column order, and contains no duplicate data rows under the stated equality rule.
```
````

## Commands and files

No shell command ran, so there is no process exit code. No file was created or changed. The fenced text is the rewritten prompt, not an execution result.
