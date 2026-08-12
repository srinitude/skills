---
name: visual-design-system-extractor
description: Use when the user asks to analyze reference images, screenshots, moodboards, style frames, brand boards, cinematic stills, or product UI shots to infer a production-grade design system, design tokens, brand/art direction, cinematic language, worldbuilding, motion rules, or YAML style specification. Handles multimodal visual extraction into valid YAML for UI/UX, brand, motion, creative direction, AI generation, and design-engineering workflows. Not for generating images or ordinary frontend implementation unless visual references must be reverse-engineered first.
license: Apache-2.0
compatibility: For deterministic validation, requires Python 3.9+. Use uv with requirements.txt for the bundled PyYAML validator when available, or an installed PyYAML environment as fallback.
---

# Visual Design System Extractor

## Core Contract

For extraction tasks, return only parser-valid YAML unless the user explicitly asks for another format. Do not wrap the YAML in markdown fences, add prose before or after it, summarize the images separately, or return YAML that failed validation.

Use the bundled schema skeleton as the canonical contract. Determinism means the same visual evidence produces the same top-level sections, nested fields, key order, confidence labels, not-applicable objects, and validator behavior. Judgment is allowed only inside field values, and every judgment must be grounded in visible reference evidence.

## Deterministic Workflow

Use the same sequence for every comprehensive extraction:

1. Confirm at least one visual reference is available. If none is attached or reachable, ask for the image, screenshot, moodboard, style frame, or URL before inventing a system.
2. Load the schema efficiently: run `python3 scripts/schema_tools.py skeleton --output /tmp/visual-design-system-skeleton.yaml`, then read targeted detail from `references/extraction-schema.md` only when a field meaning is unclear.
3. Copy the skeleton's key order exactly into the candidate YAML. Do not rename keys, reorder keys, omit required fields, or add top-level sections unless the user explicitly requests a narrower custom artifact.
4. Fill `meta`, `source_analysis`, and `confidence_scores` first, separating directly observed facts, inferred system logic, and speculative extrapolations.
5. Fill evidence-backed visual foundations: `color_system`, `typography`, `spacing`, `layout`, `grid_system`, `sizing`, `borders`, `radii`, `shadows`, `gradients`, `materials`, `textures`, and `lighting`.
6. Fill experiential layers: `motion`, `animation`, `camera`, `composition`, `environment`, `setting`, `wardrobe`, `props`, `iconography`, `illustration_style`, `photography_style`, `cinematic_style`, `rendering_style`, and `surface_treatment`.
7. Fill product and implementation layers: `accessibility`, `interaction_design`, `ui_patterns`, `sound_design`, `narrative_tone`, `emotional_palette`, `worldbuilding`, `styling_rules`, `dos_and_donts`, `token_dependencies`, `dynamic_tokens`, `responsive_rules`, `state_variants`, `platform_adaptations`, `ai_generation_prompts`, and `implementation_notes`.
8. Fill `typography.font_families.rare_unique_candidates` with distinctive typeface candidates grounded in visible reference evidence. Each candidate must include `family`, `role`, `classification`, `fallback_stack`, `pairs_well_with`, `visual_grounding`, `rarity_reason`, `pairing_logic`, `use_constraints`, `confidence`, and `inference_basis`.
9. For unsupported or invisible categories, keep the field and fill the standard not-applicable object from `references/extraction-schema.md`; do not use `null`, empty strings, or placeholder words.
10. Run the YAML validity gate before returning the final answer.

## Determinism Rules

- Use the exact top-level and nested schema from `references/extraction-schema.md`.
- Use only the confidence enum `low`, `medium`, or `high`.
- Use the same not-applicable object shape everywhere: `applicability`, `confidence`, and `inference_basis`.
- Treat `source_analysis.observed`, `source_analysis.inferred`, and `source_analysis.speculative` as separate evidence buckets, not interchangeable notes.
- Put optional additions inside the nearest existing mapping using snake_case keys; never create a new top-level section for convenience.
- If two values are equally plausible, choose the one with stronger direct visual evidence and record the weaker alternative in `inference_basis` only when useful.

## Speed Rules

- Preserve the same functionality, schema content, level of detail, and accuracy as the full reference workflow.
- Read `references/extraction-schema.md` at most once per task. For targeted lookups, prefer `python3 scripts/schema_tools.py section "Nested Field Fill Details"` or `rg` over reopening the full file.
- Draft the complete YAML in one pass from the skeleton, then validate once. Re-run validation only after fixing reported errors.
- Do not browse, research fonts, or fetch external references unless the user explicitly asks. Font choices must be grounded in the provided images, not external popularity checks.
- Do not do separate per-section validation passes. Use the bundled validator as the single mechanical gate.
- Keep the full schema, detail level, confidence handling, rare-font structure, and evidence grounding intact; speed comes only from avoiding repeated reading and repeated validation.

## YAML Validity Gate

When shell or file tools are available, validate every YAML extraction, including inline chat responses:

1. Draft the candidate YAML in a temporary file.
2. Run:

```bash
uv run --with-requirements requirements.txt python scripts/validate_design_system_yaml.py /tmp/visual-design-system-extraction.yaml
```

3. If validation fails, fix the YAML and repeat the command until it passes.
4. Return the validated YAML content only, without the validation report.

If `uv` is unavailable but `PyYAML` is installed, run:

```bash
python3 scripts/validate_design_system_yaml.py /tmp/visual-design-system-extraction.yaml
```

The validator rejects markdown fences, tabs, duplicate keys, invalid YAML, non-mapping roots, missing or extra top-level sections, wrong top-level order, bare null top-level section placeholders, missing source-analysis separation, malformed not-applicable objects, invalid confidence labels, missing rare-font candidate structure, and common UI defaults used as rare candidates.

## Schema Reference

Use `references/extraction-schema.md` as the source of truth for the canonical section taxonomy, deterministic nested field skeleton, field-level fill details, naming rules, and final self-check. Use `scripts/schema_tools.py` to extract only the skeleton or specific reference sections when that is faster than reading the whole file.

Use `references/agent-skills-compliance.md` only when editing, reviewing, packaging, or validating this skill. Do not load it during ordinary image extraction.

## Package Maintenance

For edits to this skill package, the extraction-only YAML response contract does not apply. Treat package maintenance as test-driven process documentation:

1. Establish the RED state before editing: validator output, missing trigger behavior, stale package guidance, broken script behavior, or the explicit user-requested gap.
2. Make the smallest package change that fixes that RED state. Keep `SKILL.md` focused on the runbook, keep long schema or compliance detail in `references/`, and keep executable checks in `scripts/`.
3. Preserve portability: use relative paths from the skill root, keep support files under `scripts/`, `references/`, `assets/`, or `agents/`, and update `agents/openai.yaml` only when frontmatter or Codex UI metadata changes.
4. Validate in this order when applicable: `skills-ref validate <skill-root>`, Python compile and `--help` for changed scripts, parser checks for edited YAML or JSON resources, the smallest behavioral YAML extraction or validator fixture, then cleanup of generated artifacts such as `__pycache__`.
5. Report changed files and fresh validation evidence. If the official validator cannot run, state that limitation and use the narrowest available fallback without weakening any existing package checks.

## Output Rules

- Use lowercase snake_case keys.
- Use spaces only for indentation. Never use tabs.
- Do not repeat the same key in a mapping.
- Quote strings that contain `: `, percent signs, leading zeros, or ambiguous punctuation.
- Use lists for ordered options and mappings for reusable token groups.
- Fill lists with concrete, reusable strings or mappings; leave an empty list only when the field is truly not applicable.
- Fill mappings with semantic token objects using `value`, `usage`, `confidence`, and `inference_basis` unless the schema reference defines a more specific shape.
- For not-applicable fields, use an object with `applicability`, `confidence`, and `inference_basis` instead of `null`, empty strings, or vague filler.
- Keep confidence values to `low`, `medium`, or `high`.
- Include `hex`, `rgb`, `hsl`, `usage`, `confidence`, and `inference_basis` for color tokens when color is inferred.
- Point every extrapolated claim back to visible evidence in `inference_basis`.
- Do not cite unrelated style movements, brands, films, artists, or products unless the visual evidence supports the comparison.
- If the user asks for implementation-ready output, include token dependencies, platform adaptations, responsive rules, state variants, and implementation notes.
