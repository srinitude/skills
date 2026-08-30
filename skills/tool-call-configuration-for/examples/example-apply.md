# Example: apply and repeat

Guess this example removes: whether the supported apply path edits one canonical target and becomes a no-op on final bytes.

## User says

```
Apply @behavior.json to skill-factory for exact exec_command calls.
```

## Executor replies

```
Applied all eight instruction-only rules to skill-factory, ran the focused test and full target pipeline, then repeated the same command. The second run returned no-op with no changed files.
```

## Commands run

```text
$ python3 skills/tool-call-configuration-for/scripts/tool_call_config.py apply @.artifacts/tool-call-configuration-for/real-apply/exec-command-tool.json --target skill-factory --skills-root skills --behavior @.artifacts/tool-call-configuration-for/real-apply/behavior.json --integration @.artifacts/tool-call-configuration-for/real-apply/integration-plan.json --evidence .artifacts/tool-call-configuration-for/real-apply/evidence
{"status":"applied","changed_files":["SKILL.md","evals/cases.json","evals/contract.md","evals/evals.json","references/exec-command-configuration.md","scripts/tests/test_exec_command_configuration.py"],"tool_identity_hash":"7335f79289938cb2c3bac054e714f1725a2dc5334d0e0f591fc1100794adf2f6","behavior_hash":"908b0ae6a8559c28d68097e7fdd9d081d3ef33a4cb9bd249fdff4b4379edb5b3"}
exit 0

$ python3 skills/tool-call-configuration-for/scripts/tool_call_config.py apply @.artifacts/tool-call-configuration-for/real-apply/exec-command-tool.json --target skill-factory --skills-root skills --behavior @.artifacts/tool-call-configuration-for/real-apply/behavior.json --integration @.artifacts/tool-call-configuration-for/real-apply/integration-plan.json --evidence .artifacts/tool-call-configuration-for/real-apply/idempotence-evidence
{"behavior_hash":"908b0ae6a8559c28d68097e7fdd9d081d3ef33a4cb9bd249fdff4b4379edb5b3","changed_files":[],"status":"no-op","target":"/Users/kiren/Documents/Codex/2026-08-27/create-a-comprehensive-platform-agnostic-x20/work/srinitude-skills/skills/skill-factory","tool_identity_hash":"7335f79289938cb2c3bac054e714f1725a2dc5334d0e0f591fc1100794adf2f6"}
exit 0
```

## Files created

The first run created `references/exec-command-configuration.md` and `scripts/tests/test_exec_command_configuration.py`, then changed `SKILL.md` and three eval files while rebuilding `evals/source-lineage.json`. The complete plan, profiles, pre-hashes, post-hashes, validation transcripts, and result JSON remain under `.artifacts/tool-call-configuration-for/real-apply/`. The second run created evidence only and changed no target file.

## What the run proves

The hash-bound workflow applied one exact-tool configuration, target validation passed, and the repeated target mutation was a no-op. It does not prove automatic call interception.
