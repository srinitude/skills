# Style-free wireframes

Backlink: [SKILL.md](../SKILL.md). Load before any visual identity work.

## Allowed content

Wireframes may contain:

- conversion narrative and section order
- content hierarchy and copy density
- proof and action placement
- layout topology and responsive reflow
- image-job placeholders with stable IDs
- semantic landmarks and focus order

They may not contain color values or names, typeface choices, image treatment, texture, gradients, shadows, decorative motifs, icon style, logo treatment, or motion styling.

## Candidate procedure

1. Start at the smallest declared width.
2. Produce exactly three candidates with stable IDs `wf-a`, `wf-b`, and `wf-c`.
3. Preserve every section obligation in every candidate.
4. Recompose each candidate at every larger breakpoint in strictly ascending width order.
5. For every width, record all adaptations or the literal status `UNCHANGED`.
6. Reject duplicate, descending, skipped, or unrecorded widths.

## Score

Score each complete breakpoint sequence with integers:

- message clarity: `0..5`
- conversion continuity: `0..5`
- proof placement: `0..5`
- action priority: `0..5`
- scan path: `0..5`
- mobile economy: `0..5`
- responsive continuity: `0..5`
- accessibility structure: `0..5`

External validators may veto but may not change the score. Choose the highest total. Break ties by stable ID in UTF-8 byte order.

## Freeze gate

Run `scripts/validate_packet.py`. Canonicalize the winning sequence, compute its SHA-256, and store it as `wireframe_sha256`. Visual identity must cite that hash. A changed section obligation, hierarchy, primary action, or proof sequence invalidates the hash and every later stage.
