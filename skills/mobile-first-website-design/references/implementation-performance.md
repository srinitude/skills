# Implementation and performance

Resource gate: run `mise run validate` before using package files named here.

Backlink: [SKILL.md](../SKILL.md). Load before code changes.

Follow the active repository context and coding policy. Inspect existing components, dependencies, and conventions before editing. Use platform primitives unless a library comparison proves a better fit.

## Smallest-to-largest implementation

1. Implement the smallest declared width without a media query dependency.
2. Validate layout, content, interaction, access, images, and metrics.
3. Add the next ascending `min-width` breakpoint only when content needs it.
4. Revalidate every completed width after each change.
5. Continue until the largest width passes.

Reject duplicate, descending, skipped, or unrecorded widths. Do not use device names as layout proof. Record the exact CSS width and height.

## All-width sweep

Sweep every integer CSS width from the declared minimum through maximum. At each width, detect horizontal overflow, clipped content, overlap, unreachable controls, invalid fixed positioning, and broken image crop. Run full browser, vision, and accessibility checks at each declared breakpoint plus one pixel below, at, and one pixel above every boundary.

## Accessibility

Require semantic landmarks, heading order, keyboard reachability, visible focus, accessible names, status announcements, error recovery, sufficient contrast, target size, zoom and reflow support, alt-text decisions, and reduced-motion parity. Automated checks supplement, not replace, keyboard and pixel inspection.

## Web Vitals release thresholds

Use the 75th percentile. Keep lab and field evidence separate.

| Metric | Good | Needs improvement | Poor |
|---|---:|---:|---:|
| LCP | `<=2.5s` | `>2.5s` and `<=4.0s` | `>4.0s` |
| INP | `<=200ms` | `>200ms` and `<=500ms` | `>500ms` |
| CLS | `<=0.1` | `>0.1` and `<=0.25` | `>0.25` |
| FCP | `<=1.8s` | `>1.8s` and `<=3.0s` | `>3.0s` |
| TTFB guidance | `<=0.8s` | `>0.8s` and `<=1.8s` | `>1.8s` |

Measure lab metrics at every declared breakpoint under the frozen test profile. Record tool and version, URL or artifact hash, viewport, network and CPU profile, run count, raw values, aggregate, and measured-at value. Core Web Vitals must be good at every breakpoint. FCP and TTFB are supporting diagnostics and must meet the declared budget or have an approved exception.

Use separate mobile and desktop CrUX or PageSpeed field data when available. Record `UNAVAILABLE_FIELD_DATA` when it is absent. Never substitute lab data for field data.

## Media and code budgets

Size responsive images to placement, avoid layout shifts with dimensions or aspect ratio, lazy-load noncritical media, prioritize the real LCP resource, subset and preload fonts only when justified, defer noncritical code, and keep motion on the compositor where possible. A repair must rerun every affected width and metric.
