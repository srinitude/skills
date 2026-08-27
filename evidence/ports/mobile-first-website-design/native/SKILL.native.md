---
name: mobile-first-website-design
description: Use when designing landing pages and marketing websites.
version: 1.1.1
author: Kiren Srinivasan
license: MIT
metadata:
  hermes:
    created_with_hermes_commit: bdc5b1f74c26e6240deb8f067ade6dc91c00e8f2
    compatibility_reviewed_with_hermes_commit: bdc5b1f74c26e6240deb8f067ade6dc91c00e8f2
    tags:
      - landing-pages
      - marketing-websites
      - mobile-first
      - responsive-design
      - deterministic-design
    related_skills:
      - one-of-a-kind-designer
      - visual-design-system-extractor
      - product-visual-continuity
---

# Mobile-First Website Design

Create evidence-led marketing surfaces with style-free structure, a separate identity phase, exact image prompts, smallest-to-largest implementation, and replayable release proof.

## When to Use

Use for landing pages, campaign pages, product launches, and marketing websites that need evidence-led responsive design, implementation, or release validation. Use product-interface skills for application task flows and broader design skills for cross-media systems.

## Start contract

Normalize the brief, factual claims, conversion event, audience, visitor state, section obligations, assets, integrations, release target, and every supported width into canonical JSON. Missing facts are `null` plus a blocker. Never invent them.

Load [brief and research](references/brief-and-research.md) and [integrations](references/integrations.md) at job start.

## Fixed workflow

1. Diagnose the visitor state and freeze one five-part conversion narrative.
2. Define every section's question, answer, proof, action, image job, and accessibility obligation.
3. Research every section through available Refero, Mobbin, Lazyweb, and direct first-party web routes in fixed order.
4. Record route status, source ID, visible mechanism, relevance, adaptation, and fallback.
5. Produce exactly three style-free wireframe sequences at the smallest width.
6. Recompose each sequence through every larger breakpoint in ascending order.
7. Score complete sequences, run available judgement skills, choose by score and stable-ID tie break, and freeze `wireframe_sha256`.
8. Only after that hash exists, create and score three visual identity directions.
9. Convert every placeholder into a named image job.
10. Select one exact prompt YAML record and one available tool route per image job.
11. Generate or edit candidates, inspect pixels with `vision_analyze`, and freeze selected asset bytes.
12. Style and implement the smallest width first.
13. Advance through every larger breakpoint, validating each width before the next.
14. Add one repeated motion thesis with interruptible behavior and reduced-motion parity.
15. Sweep every integer CSS width and inspect every breakpoint boundary.
16. Run access, Web Vitals, external judgement, browser, native vision, and replay gates.
17. Permit at most two bounded repair passes, then emit a full, degraded, or blocked release state.

## Structure and style gate

Wireframes may contain hierarchy, section order, copy density, proof placement, action priority, semantic order, layout topology, responsive reflow, and image-job placeholders. They may not contain color, typeface, image treatment, texture, gradients, shadows, decorative motifs, icon style, logo treatment, or motion styling.

Run `scripts/validate_packet.py` before identity work. Styling must cite the approved wireframe hash. Load [wireframe](references/wireframe.md), then [visual identity](references/visual-identity.md).

## Mobile-first gate

- Start structure, style, implementation, motion, and validation at the smallest width.
- Process every unique positive integer width in strictly ascending order.
- Record every adaptation or the literal status `UNCHANGED`.
- A larger width may add space, columns, scale, or peripheral detail. It may not remove required content or weaken the primary action.
- Duplicate, descending, skipped, or unrecorded widths return `BLOCKED_BREAKPOINT_ORDER`.

## Image gate

The package carries all 1,000 exact prompt strings as uncompressed UTF-8 YAML records under `assets/prompts/`. The source prompt path is the canonical ID. Select domain, lane, and perspective from normalized job fields, load the exact YAML `prompt` scalar, verify its byte count and SHA-256, then choose a route from `assets/tool-registry.json`.

Use `image_generate` for direct supported generation or editing. Use Flora `search_docs` and approved Flora `execute` when its current model, canvas, project, technique, or action workflow is required. Use ComfyUI for a local node workflow. Never choose a provider or model on the user's behalf. Load [image routing](references/image-routing.md).

## Integration and degradation gate

Check Refero, Mobbin, Lazyweb, Flora, Impeccable, TasteSkill, and applicable Emil procedures independently. Allowed unavailable statuses are `UNAVAILABLE_AUTH`, `UNAVAILABLE_TRANSPORT`, `UNAVAILABLE_SCHEMA`, `UNAVAILABLE_SKILL`, and `UNAVAILABLE_DISABLED`.

Run every named fallback. Never borrow an unavailable tool's verdict. Research, visual, judgement, and performance floors remain mandatory. Use `PASS_RELEASE` when all routes pass, `PASS_RELEASE_DEGRADED` when fallbacks satisfy every floor, and `BLOCKED_CAPABILITY_FLOOR` otherwise.

Flora uses `https://agents.flora.ai/mcp` with native HTTP OAuth. Its top-level tools are `search_docs` and `execute`. Charged generation requires explicit approval naming cost, batch, workspace, and export effects. Load [integrations](references/integrations.md) and [Emil procedures](references/emil-procedures.md).

## Implementation and performance gate

Implement the smallest width without a media-query dependency, then add ascending `min-width` rules only when content needs them. Run the all-width sweep, keyboard and pixel checks, accessibility checks, and lab metrics at every declared breakpoint.

At the 75th percentile require LCP `<=2.5s`, INP `<=200ms`, CLS `<=0.1`, and the declared FCP and TTFB budgets. Keep CrUX or PageSpeed field data separate. Record `UNAVAILABLE_FIELD_DATA` when absent. Load [implementation and performance](references/implementation-performance.md).

## Judgement and motion

Apply the locked design-engineering, animation, vocabulary, Apple-oriented, opportunity, improvement, prototype, review, UI-library, and toast procedures when their triggers match. Motion must support state, causality, orientation, feedback, or one restrained delight moment. Load [composition and motion](references/composition-and-motion.md) and [judgement](references/judgement.md).

## Determinism

Use sorted UTF-8 JSON, stable IDs, fixed query limits, integer scores, UTF-8 byte-order tie breaks, bounded repair, source locks, and SHA-256. Freeze selected generated bytes. Provider reruns are not replay proof. Never store secrets or fabricate web, browser, vision, validator, access, or performance results.

## Package map

- [validation](references/validation.md) owns fixtures, evidence, repair, and replay.
- [source coverage](references/source-coverage.md) owns revisions, authority, drift, and privacy.
- `scripts/breakpoint_rules.py` enforces ascending completeness.
- `scripts/prompt_corpus.py` verifies and retrieves exact prompt bytes.
- `assets/schemas.json` defines packet structure.
- `assets/source-lock.json` fixes revisions and endpoints.
- `assets/tool-registry.json` names triggers and fallbacks.
- `assets/prompt-manifest.json` and the uncompressed YAML shards under `assets/prompts/` bind every prompt.
- `assets/fixtures/` contains full, degraded, and named failing packets.

## Release

Release only when links and locks resolve, full and degraded fixtures replay byte-identically, every negative fixture returns its named block code, every prompt and tool route verifies, available external validators have no veto, native fallbacks cover unavailable routes, every breakpoint has browser, pixel, access, and performance proof, and the frozen artifact replays without a provider rerun.
