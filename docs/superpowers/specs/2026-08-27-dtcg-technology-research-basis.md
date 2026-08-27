# DTCG Technology Research Appendix

Date: 2026-08-27

Status: Current source basis for approved implementation

Parents and backlinks:

- [DTCG Research Basis Appendix](2026-08-27-dtcg-research-basis.md), Recent Technology Watch.
- [DTCG Screen Possibility Space Appendix](2026-08-27-dtcg-screen-possibility-space-design.md), Technology Watch.

Load trigger: Use this appendix when refreshing current screen, input, output, sensing, graphics, or haptic technology. The main research appendix owns evidence classes and runtime refresh rules. This file owns the dated technology source list.

## Rule

Recent sources widen candidate space. They do not prove production fitness. Every item keeps its maturity, support boundary, fallback, risks, and test method.

## Current Watch

| Technology family | Current evidence | Decision use |
| --- | --- | --- |
| Declarative overlays and relationships | [Popover API compatibility](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API), [invoker commands](https://open-ui.org/components/invokers.explainer/), [interest invokers](https://open-ui.org/components/interest-invokers.explainer/), and [anchor positioning draft](https://www.w3.org/TR/css-anchor-position-1/) | Test native top-layer, anchor, focus, dismissal, and input-equivalent behavior. Keep support and maturity limits. |
| View and scroll-linked change | [View transitions compatibility](https://developer.mozilla.org/en-US/docs/Web/API/ViewTransition) and [CSS module index](https://www.w3.org/Style/CSS/specs.en.html) | Test state continuity and motion with reduced-motion, interruption, and fallback checks. |
| Wide color and high dynamic range | [CSS Color 4](https://www.w3.org/TR/css-color-4/) and [Media Queries 5](https://www.w3.org/TR/mediaqueries-5/) | Test perceptual color spaces and HDR with contrast, gamut mapping, forced-color, and standard-range fallback. |
| Local graphics and inference | [WebGPU report index](https://www.w3.org/TR/?filter-tr-name=WebGPU) and [WebNN](https://www.w3.org/TR/webnn/) | Use high-rate graphics or local inference only with performance, power, privacy, support, and non-accelerated fallback. |
| Foldable and segmented screens | [Device Posture](https://www.w3.org/TR/device-posture/) and [Media Queries 5](https://www.w3.org/TR/mediaqueries-5/) | Test hinge-aware topology, multi-region composition, and posture changes. Keep required content out of occluded regions. |
| Spatial sensing and rendering | [WebXR](https://www.w3.org/TR/webxr/), [depth sensing](https://www.w3.org/TR/webxr-depth-sensing-1/), and [lighting estimation](https://www.w3.org/TR/webxr-lighting-estimation-1/) | Test world anchors, occlusion, light matching, gaze, hands, and spatial layers with privacy, uncertainty, comfort, and non-XR alternatives. |
| Whole-hand capacitive input | [Magical Touch](https://arxiv.org/abs/2605.12902) | Treat arbitrary contact geometry and intensity as a research prototype. Require the exact hardware and preserve study limits. |
| Passive and on-body touch | [TouchInsight](https://arxiv.org/abs/2410.05940) and [EgoTouch](https://arxiv.org/abs/2509.01786) | Test physical surfaces, several fingers, force, angle, and motion while preserving sensing limits. |
| Tactile surface rendering | [Electrostatic tactile display](https://arxiv.org/abs/2411.05149), [electroadhesion study](https://arxiv.org/abs/2409.18725), and [ArrayTac](https://arxiv.org/abs/2603.13829) | Keep friction, shape, stiffness, and texture in the experimental lane unless the exact hardware is present and verified. |
| Mid-air and visual haptics | [Pseudo-haptics review](https://arxiv.org/abs/2406.01102), [electrical haptics review](https://arxiv.org/abs/2504.21477), and [object-plus-gesture study](https://arxiv.org/abs/2503.02973) | Test sensory mappings for calibration, mismatch, fatigue, safety, and alternate feedback. |
| Spatial multimodal interaction | [Spatial interaction review](https://arxiv.org/abs/2502.07598) and [gesture-recognition review](https://arxiv.org/abs/2501.11992) | Combine gaze, hand, head, voice, object, and body input only with occlusion, discoverability, uncertainty, and equivalent paths. |

Transparent, light-field, holographic, rollable, stretchable, thermal, shape-changing, neural, and other emerging interfaces remain watch families. A run must retrieve current primary evidence before moving any of them beyond speculative or experimental status.

## Counterchecks

- A deployed API is not proof of equal support across platforms.
- A standards draft is not a stable conformance target.
- A research prototype is not a product feature.
- Hardware access does not prove safety, comfort, or user benefit.
- Novel input still needs an equivalent path unless the input is essential.
- A visual effect still needs standard-range, reduced-motion, forced-color, and no-support behavior when applicable.

## Refresh

Save retrieval date, source version, maturity, support evidence, hardware needs, privacy and safety risks, fallback, test method, and final disposition. Keep inaccessible, stale, or conflicting items `BLOCKED`.
