# Apply contract

Read this file before profiling or mutating an existing skill. `apply` is a first-class checked path, not a manual copy step.

## Integration profile

Record the canonical target path, name, description, purpose, grammar, triggers, anti-triggers, governed tool calls, nearest trigger neighbors, protected behavior, exact insertion or merge points, conflicts, required files, intended changed-file set, prohibited files, rollback boundary, and validation commands. Mark each change `add`, `replace`, `merge`, `move`, or `preserve` with its behavior rule and verification method.

## Plan schema

Use `tool-call-config/integration-plan/v1`. Bind it to `tool_identity_hash` and `behavior_hash`; record SHA-256 `expected_hashes`, `declared_files`, ordered `operations`, `dispositions`, `validation_commands` as argv arrays, and optional `lineage` configuration. Supported operations are `add`, `insert_before`, `insert_after`, `replace_text`, and `json_append`.

Every insertion carries a stable marker. Every write stays under the resolved skills root and inside `declared_files`. A symlinked target, escape path, changed expected hash, missing anchor, undeclared write, or failed validation stops the run. Validation failure restores the complete declared-file snapshot.

## Meaning-preserving mutation

Keep the target name and primary outcome unless tool-call activation changes. Put prerequisites before the first affected call. Move long schema or recovery detail to one-level-deep references with an explicit load condition. Merge at the existing canonical owner, reconcile superseded rules, and leave unrelated tools and files unchanged.

## Idempotence

Run the same command again after successful validation. A correct second run returns `status: no-op`, reports no changed files, and leaves all declared hashes unchanged. A traceable no-change result is acceptable only when every rule and required lifecycle field is already satisfied.
