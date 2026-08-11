---
name: meaning-preserving-rewrite
description: 'Use when rewriting rules without meaning loss.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Meaning-preserving rewrite

## Outcome

Rewrite policies, plans, standards, notes, reports, and templates in clear prose without dropping, weakening, broadening, or hiding a rule or decision.

## Trigger and boundary

Use when a user asks for simpler policy or plan wording, a governed artifact needs a stated voice, shortening must preserve every clause, or a package needs a baseline, ledger, rewrite, and proof.

Do not use for ordinary code refactors, routine summaries with permission to omit detail, or one-off creative copy.

## Required composition

Read [dependency reconciliation](references/dependency-reconciliation.md) before work that also changes a skill package or depends on a host writing policy. This skill owns clause-level meaning and voice. A package simplification peer owns package modes and decomposition when one is installed.

If no equivalent owner exists, keep the package boundary unchanged. Do not invent a missing dependency or weaken a branch to avoid it.

## Writing standard

- Start with the result or rule.
- Use common words, active voice, and natural contractions.
- Keep one rule per bullet when possible.
- Name the owner, file, command, count, or check.
- Define a technical term on first use.
- Preserve exact paths, commands, hashes, setting names, source quotes, backups, and raw output.
- Keep requirement strength explicit with `must`, `must not`, `may`, or `prefer`.
- Keep exceptions as narrow as their sources.
- Do not depend on prior conversation context.
- Avoid em and en dash characters, filler, hedges, and polished closers.
- Keep readable spacing between headings, paragraphs, and lists.
- Put always-needed rules in the parent file. Move branch detail only to an owner-appropriate linked file with a backlink.
- Keep each governed Markdown file below its host limits. Never remove readable spacing only to pass a size limit.

Read [voice checks](references/voice-check.md) before the final prose scan.

## Procedure

### 1. Capture the baseline

1. Read the live sources instead of reconstructing them from memory.
2. Record each present source path, hash, bytes, lines, headings, and mode.
3. Mark a future path absent instead of inventing its hash.
4. Copy each live target to an owner-only backup and prove byte identity.
5. Record source and repository state when their behavior affects the rewrite.
6. Stop on unexplained source drift.

Use [the baseline and ledger contract](references/baseline-and-ledger.md) for fields and checks.

### 2. Build the meaning ledger

Give every source clause a stable ID. Split a paragraph when it contains several rules.

For each clause record the source, exact text, meaning, requirement strength, destination, replacement, action, and review state. Allowed actions are `keep`, `split`, `move`, and `clarify`. Never use `drop`.

Add each new voice rule and the rule that the same voice applies to every planned artifact. Keep map and tuple shapes consistent in generated ledgers.

### 3. Check current sources

When a rewrite claims complete official documentation or primitive coverage, inventory the current official source set before writing. Do not trust a stale snapshot or invent a page. Follow [the documentation inventory contract](references/docs-inventory.md).

### 4. Rewrite

1. Preserve every accepted meaning and its requirement strength.
2. Keep always-needed rules in the parent artifact.
3. Move branch-specific detail only to an owner-appropriate linked file.
4. Keep one canonical owner for each procedure.
5. Update ledger targets after every wording or section change.
6. Diff live files against backups and tie each material block to ledger IDs.

### 5. Validate

Check all of these:

- Complete ledger coverage, unique IDs, allowed actions, approved review states, and exact target presence.
- Line and character limits, links, context loading, hashes, modes, and secret safety.
- Voice on prose only. Skip exact quotes, backups, raw output, inline code, and code fences that must remain exact.
- Clear grammar on a full readback.
- Agreement between human and machine reports.
- Separate component result and whole-change status.

Never run a global contraction or punctuation replacement across mixed prose and code. Patch the exact prose occurrence, then recheck nearby code and syntax.

Temporary verifiers belong in an operating-system temp location and must be deleted after use. Label a focused probe as ad hoc rather than suite green.

Use [the validation contract](references/validation-contract.md) for review packets and closeout. If waiting for a separate reviewer would stop authorized main work and no external rule requires one, run the same checks in the main worker and label the result non-independent.

## Proof threshold

Return `PASS` only when:

- Every source clause has an approved mapping and no action is `drop`.
- Every replacement keeps the source meaning, scope, exception, and strength.
- Baseline and backup hashes still match.
- Every linked target exists and matches the ledger.
- Voice, grammar, security, and package checks pass.
- A component result is not presented as whole-change proof.
- Temporary verification files are gone.

Use `PARTIAL` when bounded component proof passes but the whole threshold is incomplete. Use `BLOCKED` when source drift, missing authority, inaccessible evidence, or an unresolved dependency prevents a safe rewrite.

## Common failures

- Hashing a path that does not exist yet.
- Omitting a source bullet or narrow exception.
- Replacing an exact rule with a vague summary.
- Leaving stale ledger text after a wording fix.
- Scanning checker data or inline code as prose.
- Corrupting code examples through whole-file cleanup.
- Reporting a component PASS as whole-change PASS.
- Claiming independent review when the main worker performed it.
- Leaving temporary builders or stale review packets.

## Package resources

Use `assets/meaning-ledger-template.json` as a field template. Read `examples/policy-rewrite.md`, `examples/blocked-drift.md`, or `examples/package-reconciliation.md` for visible runs. Package maintainers use `references/`, `scripts/`, `scripts/tests/`, and `evals/`, then run `mise run ci`; ordinary rewrites do not load those paths.
