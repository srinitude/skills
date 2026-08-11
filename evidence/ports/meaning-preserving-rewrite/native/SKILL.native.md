---
name: meaning-preserving-rewrite
description: "Use when simplifying policy Markdown without meaning loss."
version: 2.2.0
author: Kiren Srinivasan
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [plain-language, policy, plans, soul, agents, rewrite, voice]
    related_skills: [plan, global-coding-policy, obsidian, humanizer, hermes-skill-lifecycle, simplify-skill]
    created_by: agent
    created_with_hermes_commit: unknown
    compatibility_reviewed_with_hermes_commit: 33f8e96a72945afb29f3bc9ef9991940f0bedcf7
---

# Meaning-Preserving Plain-Language Rewrite

## Outcome

Rewrite plans, SOUL, AGENTS, notes, reports, and templates in clear human prose without dropping, weakening, broadening, or hiding any rule or decision.

## When to use

Use when:

- The user asks for simpler policy or plan wording.
- A policy artifact must adopt the profile voice.
- Shortening must preserve every source clause.
- A package needs a baseline, meaning ledger, rewrite, and proof.

Don't use for ordinary code refactors or one-off creative copy.

## Main-progress gate

Apply SOUL's `Main-progress gate` before any independent, delegated, scheduled, or background review. This rule overrides review language in linked files.

If the gate fails, perform the same structured checks in the main agent and label the review non-independent. Keep final status BLOCKED only when the user, approval contract, or external standard explicitly requires a separate human or service.

## Writing standard

- Start with the result or rule.
- Use common words, active voice, and natural contractions.
- Keep one rule per bullet when possible.
- Name the owner, file, command, count, or check.
- Define technical terms on first use.
- Preserve exact paths, commands, hashes, setting names, source quotes, backups, and raw output.
- Keep requirement strength explicit with `must`, `must not`, `may`, or `prefer`.
- Keep exceptions as narrow as their sources.
- Don't depend on old chat context.
- Don't use em or en dash characters, blocked wording, filler, hedges, or polished closers.
- Keep headings padded with blank lines and keep each paragraph separate.
- Use unordered lists for unordered points and ordered lists for procedures or ranked items.
- Keep each governed Markdown file at most 200 lines and below 20,000 characters. Start progressive disclosure at 150 lines and move only branch-specific detail to an existing support owner.
- Never remove readability spacing or collapse prose into list-like sentences to satisfy a size limit.

Load `references/voice-check.md` for the exact scan contract.

## Procedure

### 1. Capture the baseline

- Load `global-coding-policy` before writing Markdown.
- Read live sources. Don't reconstruct them from memory.
- Record each present source's path, hash, bytes, lines, headings, and mode.
- Mark future paths absent instead of inventing hashes.
- Copy live targets to owner-only backups and prove byte identity.
- Record the installed Hermes commit and source worktree state when Hermes behavior matters.
- Stop on unexplained source drift.

Load `references/baseline-task.md` for the schema and checks.

### 2. Build the meaning ledger

Give every source clause a stable ID. Split paragraphs that contain several rules.

For each clause record its source, exact text, meaning, strength, destination, replacement, action, and review state. Allowed actions are `keep`, `split`, `move`, and `clarify`. Never use `drop`.

Add each new voice rule and the rule that the same voice applies to every planned artifact. Keep map and tuple shapes consistent when building the ledger programmatically.

Load `references/ledger-template.md` for field shapes and target matching.

### 3. Check current sources

When the rewrite claims full Hermes docs or primitive coverage, fetch live `/docs`, `/docs/llms.txt`, and `/docs/llms-full.txt`. Parse Markdown destinations, record source markers, and document real aliases. Don't invent pages or trust a stale snapshot.

Load `references/hermes-docs-inventory.md` for this branch.

### 4. Rewrite

- Preserve every ledger meaning and strength. When the target is a Hermes skill or the change includes package structure or child-skill extraction, load `simplify-skill` if it is not active. This skill keeps clause-level meaning and voice ownership; `simplify-skill` owns package-level mode and decomposition decisions.
- Put always-needed rules in the parent artifact.
- Move branch-specific detail only to an owner-appropriate linked file.
- Keep one canonical owner for every procedure.
- Update ledger targets after each wording or section change.
- Diff live files against backups and tie each material block to ledger IDs.

### 5. Validate

Run focused checks for:

- Ledger coverage, unique IDs, allowed actions, and exact target presence.
- Line and character limits, links, context loading, hashes, modes, and secret safety.
- Voice on prose only. Skip YAML, fenced code, inline code, exact quotes, backups, and raw output.
- Clear grammar on a full readback.
- Human and machine report agreement.
- Separate component and whole-change status.

Never run a global contraction or punctuation replacement across mixed prose and code. Patch the specific prose occurrence, then recheck nearby code examples and syntax.

Temporary verifiers must run from an OS temp path, stay within coding limits, and be deleted. Label focused checks as ad hoc rather than suite green.

Use the `Main-progress gate` for any separate reviewer. Load `references/final-validation.md` for packet and report formats, but keep this skill's gate and fallback authoritative.

## Common failures

- Hashing a path that doesn't exist yet.
- Omitting a source bullet or a narrow exception.
- Replacing a precise rule with a vague summary.
- Leaving stale ledger text after a wording fix.
- Scanning blocked-term test data or inline code as prose.
- Corrupting code examples through whole-file prose cleanup.
- Reporting a component PASS as whole-change PASS.
- Claiming independent review when the main agent performed it.
- Keeping an independent review mandatory after the `Main-progress gate` fails without an external requirement.
- Leaving temporary builders or stale review packets.

## Support files

- `references/baseline-task.md`
- `references/hermes-docs-inventory.md`
- `references/ledger-template.md`
- `references/voice-check.md`
- `references/final-validation.md`

## Verification checklist

- [ ] Baseline and owner-only backups verified before edits
- [ ] Ledger covers every source clause and new voice rule
- [ ] No rule, exception, or strength was lost
- [ ] Every target matches the final live wording
- [ ] Voice and grammar checks passed on prose only
- [ ] Headings, paragraphs, and lists use readable Markdown structure
- [ ] Progressive-disclosure moves preserve ownership and backlinks
- [ ] Code examples stayed exact and syntactically valid
- [ ] All governed Markdown stays below the profile limits
- [ ] Any async review passed SOUL's `Main-progress gate`
- [ ] Component and whole-change status remain separate
- [ ] Temporary files were removed
