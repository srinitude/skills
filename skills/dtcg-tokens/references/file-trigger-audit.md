# File trigger audit

Read this file in Step 24 before package completion. It owns the whole-directory current-byte readback performed by `mise run audit-files` with `assets/file-trigger-policy.json`, checked against the historical source map in `evals/source-lineage.json`.

## What a trigger means

A trigger is the event that makes a file enter real work. Valid modes are skill activation, an explicit instruction load, a command run, a code import, test discovery, fixture selection, or configuration entry.

## Audit rule

The auditor reads every regular file under the skill root. It excludes no source file. Generated cache bytes are a failure. Each file must be a root, have a direct textual or import consumer, or match one bounded discovery rule whose consumer exists.

## Review the report

Read every route in the JSON report. Check the file path, mode, trigger, and consumers. A file is orphaned when no real route reaches it. A file is over-triggered when a broad rule loads it outside its need. A file is under-triggered when its stated condition cannot reach it. Repair the earliest route owner and rerun the audit.

## Completion

Pass only when the report reads every current file, returns no generated cache, no missing consumer, and no unrouted file. The audit proves reachability, not content quality. The normal tests, vision review, evidence checks, and human readback remain required.
