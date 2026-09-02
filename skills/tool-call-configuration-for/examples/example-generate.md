# Example: generate a read-only tool skill

Guess this example removes: whether a verified read-only profile becomes a complete package rather than generic substituted prose.

## User says

Resource gate: run `mise run validate` before using package files named here.

```
Generate from @evals/fixtures/established-mcp-read.json with @evals/fixtures/behavior-report.json.
```

## Executor replies

```
Generated established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66. Its full pipeline passed. The package retains catalog.lookup, both behavior rules, read-only result validation, safe-retry limits, registry evals, and current lineage.
```

## Commands run

```text
$ mise run tool-call-config generate @evals/fixtures/established-mcp-read.json --behavior @evals/fixtures/behavior-report.json --output ../../.artifacts/tool-call-configuration-for/fixture-read
{"behavior_hash": "cd25b3f22e0afdabc2e88ea6c0d2a124db4e932895c3459735edecfe07fd2c84", "evidence_dir": "/Users/kiren/Documents/Codex/2026-08-27/create-a-comprehensive-platform-agnostic-x20/work/srinitude-skills/.artifacts/tool-call-configuration-for/fixture-read/evidence", "generated_name": "established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66", "skill_path": "/Users/kiren/Documents/Codex/2026-08-27/create-a-comprehensive-platform-agnostic-x20/work/srinitude-skills/.artifacts/tool-call-configuration-for/fixture-read/established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66", "status": "generated", "tool_identity_hash": "a5c2cc66b4bca30f06fb912d8e0b69140c615259ea5c46b65c54c729bda954c3"}
exit 0

$ mise run ci
PASS established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66: 0 problems
checked 9 files, 0 problems
checked 6 files, 0 problems
checked 16 files, 0 placeholders
eval checks: 0 problems
exit 0
```

## Files created

Resource gate: run `mise run validate` before using package files named here.

The generated package contains `SKILL.md`, `mise.toml`, `.github/workflows/ci.yml`, two contract references, one identity asset, three worked examples, six executable or test files, nine eval files, and four generation-evidence files. The exact generated tree and complete contents remain in the command's reported `skill_path`; `evidence/generation-result.json` is:

```json
{
  "behavior_hash": "cd25b3f22e0afdabc2e88ea6c0d2a124db4e932895c3459735edecfe07fd2c84",
  "evidence_dir": "/Users/kiren/Documents/Codex/2026-08-27/create-a-comprehensive-platform-agnostic-x20/work/srinitude-skills/.artifacts/tool-call-configuration-for/fixture-read/evidence",
  "generated_name": "established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66",
  "skill_path": "/Users/kiren/Documents/Codex/2026-08-27/create-a-comprehensive-platform-agnostic-x20/work/srinitude-skills/.artifacts/tool-call-configuration-for/fixture-read/established-mcp-fixture-catalog-owner-fixture-catalog-s-a5c2cc66",
  "status": "generated",
  "tool_identity_hash": "a5c2cc66b4bca30f06fb912d8e0b69140c615259ea5c46b65c54c729bda954c3"
}
```

## What the run proves

The fixture generated a self-contained package and every local job passed. It proves deterministic package behavior for this fixture, not automatic host activation.
