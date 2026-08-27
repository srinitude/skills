# Category taxonomy

Use this as a coverage checklist, not a quota. Include a category only when the source or requested product state supports it, and record omitted categories with reasons.

| Family             | Candidate categories                                                   | DTCG representation                                               |
| ------------------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Color              | palette, text, surface, border, action, status, data, overlay, focus   | `color`; gradients use `gradient`                                 |
| Typography         | family, weight, size, line height, tracking, composed roles            | atomic types plus `typography`                                    |
| Space and size     | spacing rhythm, inset, stack, gap, control size, content width         | `dimension` or `number` when unitless                             |
| Shape              | corner radius, border width and style, outline                         | `dimension`, `strokeStyle`, `border`                              |
| Depth and material | shadow, scrim, opacity, blur intent, texture intent                    | `shadow`, `color`, `number`; unsupported effects in `$extensions` |
| Motion             | duration, easing, delay, transition roles                              | `duration`, `cubicBezier`, `transition`                           |
| Imagery            | crop, aspect, focal alignment, treatment, icon family                  | supported atomic tokens plus namespaced `$extensions`             |
| Layout             | grid, container, columns, safe zones, breakpoints, density             | dimensions and namespaced `$extensions`                           |
| Components         | text, surface, border, icon, state, size, transition per reusable part | aliases to semantic and primitive tokens                          |

## Required hierarchy

Start with observed primitives. Add semantic roles that express purpose without naming a component. Add component or pattern aliases when the evidence shows repeated use. A flat palette is not a full system, while a deep component tree without observed consumers is fabrication.

## State coverage

When interaction states are visible or specified, cover default, hover, active or pressed, focus, selected, disabled, loading, error, success, warning, and information only as applicable. Do not guess unseen states. Mark missing state evidence in the report.

## Mode and theme coverage

Create modes or themes only when the source includes them or the user requests them. Keep semantic names stable across modes and place mode-specific values in a documented extension or separate resolver-ready files. Never present an inferred dark mode as observed.

## Platform independence

Use logical roles such as `inset-inline`, `surface-raised`, and `text-primary` instead of framework, device, or component-library names. Keep source units where observed, use aliases for derived roles, and put platform transforms outside the canonical source file.

## Experimental partition

Every final token file contains a top-level `experimental` group with at least two tokens from two distinct strategies in `assets/exploration-strategy-catalog.json`. These values remain standard DTCG tokens or documented extensions, carry hypotheses and bounded contexts, and stay separate from production semantic aliases until validated. Omission, sidecar-only suggestions, raw-JSON-only artifact coverage, and silent deletion after a failed review are invalid.
