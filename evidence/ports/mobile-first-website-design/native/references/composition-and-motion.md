# Composition and motion

Backlink: [SKILL.md](../SKILL.md). Load after wireframe and identity hashes exist.

## Responsive composition

Start at the smallest breakpoint. Establish one dominant reading path, visible primary action, proof near the claim it supports, and safe text-image separation. Then advance through every larger width.

At each width:

1. preserve the conversion narrative and section obligations
2. verify line length, density, crop, hierarchy, and action visibility
3. add columns only when reading order remains clear
4. keep decorative assets from displacing required content
5. record the adaptation or `UNCHANGED`

A wide screen may expose more context but may not hide information needed on smaller screens. A small screen may serialize columns but may not change meaning.

## Motion thesis

Write one sentence describing the repeated motion language. Use it for state change, causality, orientation, feedback, or one restrained delight moment. Do not add unrelated motion styles.

For every motion record:

- stable element and state IDs
- trigger and user intent
- start and end states
- property, duration, delay, and easing
- interruption behavior
- reduced-motion equivalent
- performance risk

Prefer transforms and opacity. Avoid layout-triggering animation when a composited equivalent exists. Keep interaction responsive while motion runs. Never block navigation or the primary action on animation completion.

## Motion gate

Run opportunity discovery before implementation, then improvement and review after implementation. Inspect motion at every breakpoint and under reduced motion. Fail on missing reduced-motion parity, uninterruptible interaction, unexplained motion, layout shift, or frame instability that breaks the performance budget.
