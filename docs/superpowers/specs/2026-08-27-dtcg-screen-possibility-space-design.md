# DTCG Screen Possibility Space Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Screen Possibility Space.

Load trigger: Use this appendix while implementing or reviewing `assets/screen-possibility-space.json`, `references/screen-decision.md`, Step 07, `E_SCREEN_SPACE`, or their tests. The future package files own runtime procedure. This appendix owns the approved design boundary and source rationale.

## Outcome

The skill must consider the full applicable range of visual effects and physical screen interactions before narrowing. It must remain open to new display, sensing, input, output, and feedback technology without replacing evidence with novelty. The final decisions must stay source-specific, physically operable, accessible, testable, and visible in tokens and proof specimens.

## Completeness Model

No finite list can contain every future screen capability. Completeness therefore means that the run starts from a versioned set of stable axes, gives every core family a disposition, records every discovered extension, and proves that narrowing did not silently lose an applicable result.

The decision unit is:

`surface × viewport × render medium × visual primitive × composition × time × state × input × action × feedback × body × environment × accessibility × task × source intent`

The run must explore meaningful cross-axis combinations. It must not form the full mathematical cross-product when combinations are physically impossible, redundant, unsafe, or unrelated. Each exclusion needs a reason.

## Core Axes

| Axis                         | Core value families                                                                                                                                                                                                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Surface and display          | Flat, curved, dual, folded, rollable, stretchable, transparent, reflective, emissive, projected, head-mounted, light-field, holographic, monochrome, e-paper, standard or high dynamic range.                                                                                                 |
| Viewport and window          | Fixed, fluid, segmented, safe-area constrained, fullscreen, embedded, floating, picture-in-picture, multi-window, multi-display, zoomed, magnified, portrait, or rotated.                                                                                                                     |
| Render medium                | Semantic interface, text, vector, raster, video, canvas, data graphic, 3D scene, live camera, generated texture, or mixed media.                                                                                                                                                              |
| Geometry                     | Point, line, curve, path, shape, glyph, volume, mesh, particle, field, region, boundary, container, or negative space.                                                                                                                                                                        |
| Composition                  | Position, size, proportion, alignment, distribution, grid, flow, wrap, stack, layer, overlap, occlusion, crop, clip, mask, hierarchy, topology, grouping, repetition, rhythm, balance, tension, or sequence.                                                                                  |
| Typography and language      | Family, variable axis, weight, width, slant, optical size, grade, case, scale, tracking, spacing, measure, leading, alignment, writing mode, script, language, direction, decoration, emphasis, or text motion.                                                                               |
| Color, light, and material   | Hue, lightness, chroma, alpha, contrast, gamut, dynamic range, gradient, blend, filter, shadow, glow, blur, grain, pattern, texture, reflection, refraction, translucency, illumination, or material cue.                                                                                     |
| Depth and space              | Layer depth, elevation, perspective, parallax, camera, field of view, stereo disparity, occlusion, scale, world anchor, hit surface, lighting estimate, or spatial audio relation.                                                                                                            |
| Time and motion              | Delay, duration, rate, easing, path, keyframe, spring, inertia, oscillation, transition, morph, reveal, disappearance, scroll linkage, view linkage, loop, interruption, continuity, causality, or reduced-motion form.                                                                       |
| Content and data             | Label, prose, code, image, sound, video, metric, category, order, part-to-whole, network, geography, time series, uncertainty, distribution, comparison, annotation, live status, or provenance.                                                                                              |
| State and feedback           | Default, hover, focus, active, pressed, selected, checked, expanded, disabled, visited, loading, progress, success, warning, error, empty, offline, permission, conflict, undo, redo, preview, committed, or synchronized.                                                                    |
| Input source                 | Finger, multi-touch, stylus, mouse, trackpad, keyboard, switch, gamepad, remote, wheel, voice, gaze, head pose, hand pose, body gesture, motion sensor, camera, proximity, pressure, force, tilt, twist, contact geometry, or assistive technology.                                           |
| Action grammar               | Point, target, select, activate, hold, repeat, chord, hover, focus, dwell, type, dictate, draw, ink, erase, scrub, steer, drag, drop, pan, scroll, swipe, fling, pinch, zoom, rotate, resize, reorder, reveal, inspect, compare, edit, undo, confirm, cancel, or dismiss.                     |
| Physical feedback            | Visual response, sound, vibration, force, friction, stiffness, shape, temperature, electrical touch, electroadhesion, ultrasound, pseudo-haptic illusion, or combined feedback.                                                                                                               |
| Body and posture             | One hand, two hands, thumb, finger, pen grip, seated, standing, walking, mounted device, left or right hand, reach zone, tremor, limited dexterity, fatigue, occlusion, contact angle, or grip change.                                                                                        |
| Environment                  | Ambient light, glare, noise, motion, vibration, gloves, moisture, outdoors, vehicle, public setting, privacy need, distance, viewing angle, network loss, power limit, or thermal limit.                                                                                                      |
| Accessibility and adaptation | Keyboard, switch, screen reader, braille, voice control, zoom, reflow, high contrast, forced colors, color-vision difference, low vision, reduced motion, reduced transparency, captions, description, sign language, simplified presentation, alternate timing, or alternate pointer action. |
| Task and intent              | Read, scan, find, learn, decide, monitor, compare, move through, communicate, create, manipulate, configure, transact, recover, play, perform, collaborate, simulate, or explore.                                                                                                             |

The future asset must store stable identifiers and an extension protocol. It may add a value family only with a dated source, definition, parent axis, physical or perceptual basis, test method, and compatibility notes. It must not delete a core family during a run.

## Applicability Ledger

Every axis and value family receives one disposition:

| Disposition      | Meaning                                                                            | Required result                                                              |
| ---------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `applicable`     | The input, intended output, device class, or experiment makes the family relevant. | At least one invariant, experiment, or token decision plus a proof specimen. |
| `not_applicable` | The family cannot affect the bounded run.                                          | Specific reason tied to source intent and output context.                    |
| `unknown`        | Evidence or capability detection is insufficient.                                  | Dated probe, owner, stop rule, and `BLOCKED` until resolved or bounded out.  |
| `extension`      | Current research reveals a family outside the frozen catalog.                      | Full extension record before it can become applicable.                       |

Narrowing removes candidates, not records. Rejected and blocked tuples remain in the possibility ledger with their reasons.

## Candidate Decision Record

Each candidate tuple records:

- stable ID, catalog version, run date, and source identity relation
- exact axis values, intended task, and user or system intent
- predicted visual, behavioral, perceptual, motor, or tactile effect
- required hardware, software, sensors, permissions, and environmental conditions
- input equivalence, output fallback, degraded mode, and no-support behavior
- accessibility, safety, privacy, power, thermal, bandwidth, and latency effects
- baseline, control, variables, measurement, threshold, falsifier, and rollback
- DTCG token paths, proof specimens, states, viewports, and interactions
- maturity class, availability evidence, uncertainty, and final disposition

## Sight, Perception, And Touch Invariants

These are vetoes when applicable, not a style template.

| Class      | Invariant                    | Required check                                                                                                                                |
| ---------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Sight      | Acuity and scale             | Text, marks, targets, detail, viewing distance, zoom, and low vision preserve the claimed information.                                        |
| Sight      | Contrast and light           | Foreground, background, non-text state, glare, gamut, dynamic range, forced colors, and grayscale preserve meaning.                           |
| Sight      | Occlusion and crowding       | Overlap, clipping, density, edge position, masks, and nearby features do not hide required content or create a false reading.                 |
| Sight      | Motion and change            | Timing, continuity, interruption, flash, reduced motion, and change visibility support the task without harm.                                 |
| Perception | Grouping and hierarchy       | Proximity, similarity, enclosure, continuity, alignment, common motion, and negative space produce the intended groups and reading order.     |
| Perception | Attention and discrimination | Salience, feature conjunctions, competing signals, uncertainty, and data encodings let people find and compare the needed information.        |
| Perception | Meaning and prediction       | Labels, state, cause and effect, feedback, consistency, recognition, and error messages support the intended action without hidden inference. |
| Perception | Memory and sequence          | Instructions, choices, steps, history, undo, and progress do not require people to remember hidden state or reconstruct missing context.      |
| Touch      | Target acquisition           | Target size, distance, spacing, posture, reach, error rate, and alternate activation support the task.                                        |
| Touch      | Path steering                | Narrow paths, drag corridors, and continuous gestures account for path width, length, interruptions, and motor variation.                     |
| Touch      | Contact physics              | Contact geometry, perceived input point, finger posture, occlusion, moisture, gloves, grip, pressure, and device movement are tested.         |
| Touch      | Feedback and recovery        | Down, move, capture, cancel, up, confirmation, undo, timeouts, lost input, and device loss stay visible and recoverable.                      |
| Access     | Input equivalence            | Dragging, multi-pointer, motion, hover, gaze, voice, and gesture actions have an operable alternative unless essential.                       |
| Access     | Focus and semantics          | Roles, states, names, relationships, focus order, focus visibility, and reading order survive every visual state.                             |
| Access     | Responsive form              | Reflow, zoom, text resize, orientation, viewport segments, hinges, safe areas, and window modes retain content and function.                  |
| System     | Multisensory agreement       | Visual, audio, tactile, and spatial cues either agree or document purposeful dissonance and its effect.                                       |
| System     | Performance                  | Latency, frame pacing, dropped input, sensor uncertainty, power, heat, and network degradation stay within frozen limits.                     |

An invariant vetoes a physically or perceptually failed use. It does not pick an aesthetic, forbid unfamiliar structure, or reward convention. A new design may use tension, ambiguity, unusual rhythm, or controlled dissonance when the intended reading stays testable and the required task still works.

## Technology Watch

Each run refreshes a dated watchlist across official standards, deployed compatibility data, primary research, and relevant prototypes. It classifies each technology before it influences a decision.

| Maturity                                  | Allowed use                                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Stable standard with verified support     | Production candidate after all ordinary gates pass.                                             |
| Deployed but partial or platform-specific | Production candidate only with detection, fallback, and support boundary.                       |
| Active draft                              | Experimental candidate; no standard or availability claim.                                      |
| Research prototype                        | Experimental specimen only; require reported setup, sample limits, and replication uncertainty. |
| Speculative concept                       | Idea-generation input only; no functionality or feasibility claim.                              |

The 2024 through 2026 watchlist includes declarative popovers and invokers, anchor positioning, view and scroll-linked transitions, wide-gamut and high-dynamic-range color, local GPU and neural acceleration, foldable posture and segmented viewports, XR layers, depth, hit testing, lighting, hand, gaze, and voice input, whole-hand capacitive sensing, passive-surface touch, on-body input, electroadhesive touch, electrical and ultrasound haptics, pseudo-haptic visual effects, tactile arrays that render shape, stiffness, and friction, and research on light-field, holographic, transparent, rollable, stretchable, and shape-changing displays.

Novelty never overrides maturity. A new capability enters production selection only when support, source fit, human benefit, privacy, latency, accessibility, safety, fallback, and proof all pass independently. Otherwise it stays experimental or is rejected.

## Decision Sequence

1. Freeze catalog version, date, intended outputs, device bounds, and proof requirements.
2. Inspect all input modalities and source intent before selecting a screen family.
3. Detect available hardware and software capabilities without treating detection as quality proof.
4. Complete the applicability ledger for every core family and extension.
5. Generate source-derived candidate tuples before taste filtering.
6. Apply physical, accessibility, safety, privacy, and conformance vetoes.
7. Run the technology watch and attach maturity records to affected candidates.
8. Explore unusual cross-axis combinations in a separate divergent phase.
9. Freeze experiments, render matched alternatives, and inspect actual pixels and interactions.
10. Narrow through non-compensatory gates, comparative strong-vision judgment, and falsification.
11. Propagate retained and rejected records into tokens, evidence, proof specimens, and review.
12. Recheck current bytes and fail if any applicable family or fallback disappeared.

## Creative Freedom

The axes define questions, not an aesthetic. The skill may invent unfamiliar compositions, interactions, mappings, motion systems, sensory correspondences, and token categories. It may violate convention when the departure is intentional, testable, source-derived, and does not make a required task unsafe or inoperable. At least one experiment must combine distant axes or use a recent capability, but retention still depends on evidence.

## Failure And Tests

Return `BLOCKED: E_SCREEN_SPACE` for a missing axis, silent omission, unsupported `not_applicable`, unresolved `unknown`, absent fallback, maturity inflation, or narrowing that loses an applicable result.

Focused tests must reject a flat unversioned list, a recent technology accepted only because it is new, a prototype presented as deployed, a gesture without an equivalent path, a visual effect without reduced-motion and forced-color behavior, touch decisions that ignore contact geometry, foldable layouts that ignore the hinge, and proof specimens that do not exercise the declared tuple. A positive fixture must include every axis disposition, one extension, one rejected recent technology, one retained experimental technology, fallbacks, located visual review, and exact agreement across tokens, evidence, and proof.

## Research Owner

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) owns stable sources and evidence classes. The [technology research appendix](2026-08-27-dtcg-technology-research-basis.md) owns the dated watchlist and refresh limits.
