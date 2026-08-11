# Meaning ledger template

Save as JSON under the task report directory (example: `.hermes/reports/<task>/meaning-ledger.json`).

## Entry fields

- `id` — stable clause ID (example: `SRC-014`)
- `source_file` — absolute path of the original file
- `original` — exact original clause
- `meaning` — what the rule requires
- `strength` — one of: must, must_not, may, prefer, mixed (use `mixed` only when sibling targets disagree)
- `new_file` / `new_section` / `new_text` — single-target summary fields (keep for grep and short entries)
- `targets` — preferred multi-target array. Each item: `new_file`, `new_section`, `new_text`, `strength`. Use one target per live bullet after a split.
- `action` — one of: keep, split, move, clarify (never drop). Use `split` when one source clause maps to more than one live bullet.
- `review` — same_meaning or failed (or the local synonym `same meaning` if the task already standardized that spelling; stay consistent inside one ledger)
- `routing_rationale` — optional; required when ownership moves or a bridge remains in AGENTS while SOUL stays authoritative

## Example entry (single target)

```json
{
  "id": "SRC-014",
  "source_file": "/absolute/path/identity.md",
  "original": "exact original clause",
  "meaning": "what the rule requires",
  "strength": "must",
  "new_file": "/absolute/path/identity.md",
  "new_section": "Routing",
  "new_text": "plain-language replacement",
  "action": "clarify",
  "review": "same_meaning",
  "targets": [
    {
      "new_file": "/absolute/path/identity.md",
      "new_section": "Routing",
      "new_text": "plain-language replacement",
      "strength": "must"
    }
  ]
}
```

## Example entry (split into short live bullets)

```json
{
  "id": "SRC-021",
  "source_file": "/absolute/path/SOUL.md",
  "original": "combined source clause",
  "meaning": "force and scope of every forbidden skill content type",
  "strength": "mixed",
  "new_section": "Skill creation",
  "new_text": "- Don't put task progress in a skill.\n- Don't put outcomes in a skill.\n- Route each of those items to its canonical owner or discard it.",
  "action": "split",
  "review": "same_meaning",
  "targets": [
    {
      "new_file": "/absolute/path/SOUL.md",
      "new_section": "Skill creation",
      "new_text": "Don't put task progress in a skill.",
      "strength": "must_not"
    },
    {
      "new_file": "/absolute/path/SOUL.md",
      "new_section": "Skill creation",
      "new_text": "Don't put outcomes in a skill.",
      "strength": "must_not"
    },
    {
      "new_file": "/absolute/path/SOUL.md",
      "new_section": "Skill creation",
      "new_text": "Route each of those items to its canonical owner or discard it.",
      "strength": "must"
    }
  ]
}
```

## Document wrapper

```json
{
  "task": "policy-rewrite",
  "source_files": [],
  "future_files": [],
  "coverage_required": 1.0,
  "coverage_method": "How every clause was enumerated (bullet walk, paragraph splits, voice rules).",
  "entries": []
}
```

Optional `future_files` lists planned destinations not yet present. Always set `coverage_method`.

## Reviewer rules

- Fail if any original clause lacks an entry.
- Fail if any SOUL/AGENTS bullet was skipped (enumerate by live line walk).
- Fail if a voice brief is present but the meta “same voice on plan + all planned artifacts” rule has no entry.
- Fail if any entry is weaker, broader, vaguer, or needs prior chat context.
- Fail if meanings are not unique across the full ledger (same concept from different sources still needs source-specific wording).
- Fail if wrapper `checks` counts disagree with re-parsed entry arrays (no stale hardcodes under PASS).
- Fail if `DOC-###` router metadata disagrees with the primitive catalog split (null owner ⇒ four nulls; shared ⇒ catalog fields + ordered inventory URLs).
- Fail if ledger `GCP-*` entries are not deep-equal to inventory `semantic_entries`.
- Split multi-rule sentences into multiple IDs before acceptance.
- After a live rewrite that shortens compound bullets, fail if any target `new_text` is missing from the live file. Remap splits before review passes.
- Moves must name the new canonical owner and leave a minimal router link if needed.
- Bridge rows in AGENTS (skills, sessions, Honcho, Obsidian) need their own targets when they remain as workspace routers under SOUL authority.
- Fail if IDs are not unique or if any `review` is not same-meaning before rewrite.
- When a distribution or export ledger stores `source_text` / `target_text` / `new_text` **without** Markdown list markers while the live line still starts with `- ` or `* `, strip one leading bullet from the live line before equality checks. That de-marking is intentional ledger normalization, not a content defect. Fail only after normalize if the remaining rule text differs, or if IDs, file hashes, coverage, or `review` status fail.
- For `generalize` / placeholder export rows (profile name, home path, workspace root, GitHub owner/identity), do not require raw string equality. Compare a meaning-normalized form: map every backtick span to `` `<value>` ``, then apply the ledger's recorded voice maps (examples: `this profile's` → `the profile's`; concrete host paths → placeholders; concrete GitHub owner/identity → workspace-configured wording). Raw compare on those rows is a false FAIL.

## DOC and GCP extensions (complete-coverage plans)

Optional fields on `DOC-###` rows:

- `detail_owner`, `proposed_live_text_role`, `shared_router_primitive_ids` — mirror the primitive catalog or all JSON null
- `detail_destination` — null for non-shared rows; otherwise include `canonical_live_docs_urls` from docs inventory order

Wrapper `checks` must be derived after the body is correct. Procedure: `ledger-evidence-truth.md`.
