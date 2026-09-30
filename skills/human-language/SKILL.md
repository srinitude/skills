---
name: human-language
description: "Use when writing or editing any agent-written text: replies, copy, tool-call prose, and handoffs. Also use when asked to remove AI slop, write plain or natural prose for a grade 6 reader, keep the author's meaning, or check facts, voice, flow, and exact data before release."
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
  scope: 'user'
---

# Human language

## Read the guidance that fits

Read [writing rules and output checks](references/writing-rules.md) before writing. Apply all of those rules throughout the work and run their required gate before each output.

Read [context and event checks](references/context-and-events.md) when there is lots of context or parts conflict, are missing, or change. Also read it when work resumes or you write for another agent. It adds detail; you need not read every source on every turn.

For a voice or rhythm rewrite, a “human, not AI slop” request, or a quality dispute, read [human writing and slop](references/human-writing.md). It gives deeper checks, evidence, and limits. “Human” here is a quality aim, not a claim that a person wrote the text.

For genre choices or older writing examples, read [writing before 2015](references/pre-2015-writing.md). Use the craft that fits the task. Old text is not proof of quality, and old facts are not current advice.

For social posts, captions, or learning from a writing dataset, read [social writing and corpus limits](references/social-writing.md). A reply may need its parent post; a caption may need its image. Do not fill missing context with guesses.

Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

## Test changes and check evidence

On any skill change, run [validation cases](references/validation.md) before calling the skill tested. A checklist alone does not count.

For evidence behind these choices, read [research and limits](references/research.md). To test or maintain the skill, read [validation cases](references/validation.md).

Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

## Package checks and examples

Load `examples/` before your first rewrite with this skill. They show a complete run and the failure this skill most often causes.

Load `evals/cases.json` before testing or changing this skill. It holds the validation cases in machine form. Load `assets/use-case-contract.json` through `mise run use-case-policy` only when you need the package outcome it owns. Run `mise run ci` for the full package gate.
