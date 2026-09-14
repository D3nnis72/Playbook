---
name: visual-interaction-verification
description: Use when changing UI layout, animation, responsive behavior, or deployed rendering and correctness depends on what users see over time or across viewports.
---

# Visual interaction verification

## Overview

A final screenshot can prove a resting layout, but not animation order, intermediate states, clipping, responsive regressions, or deployment asset mismatches. Treat visible states over time and across relevant environments as part of the user-facing contract.

## When to use

Use this skill for:

* CSS, layout, z-index, SVG, mask, transition, reveal, scroll, or motion changes.
* Reports that something pops in, remains visible, appears too early, is clipped, or works locally but not after deployment.
* Shared UI changes where a component can render through several routes, locales, breakpoints, or build targets.

Do not add frame-by-frame verification for a static copy or token change that cannot affect layout, state, timing, or rendering.

## Define the visual contract first

Write the smallest useful matrix before implementation:

| Surface | Initial state | Intermediate state | Final state | Variants |
|---------|---------------|--------------------|-------------|----------|
| component or route | visible, hidden, enabled, or positioned | order, delay, duration, opacity, or movement | resting position and interaction | viewport, locale, reduced motion, build |

Include positive and negative assertions. State what must appear, what must stay absent, which control must be usable, and which neighboring elements must not change. For a shared primitive, list every relevant consumer instead of checking only the first route.

## Verify observable states

1. Run focused tests and inspect the actual render path before changing timing or styles.
2. In a real browser, capture the initial state, each critical transition, and the final state. Use a meaningful DOM or state condition when possible. Do not replace a missing state check with one arbitrary sleep.
3. Check representative desktop and mobile viewports, relevant breakpoints, repeated entry, reload, and reduced-motion behavior. Look for clipping, overflow, stacking, stale text, disabled controls, and unexpected elements.
4. When local and deployed behavior differ, compare the deployed commit, rendered HTML, loaded CSS and JavaScript assets, cache state, console output, and built artifact before changing component code.
5. Record any browser, device, network, or deployment boundary that could not be tested. Do not claim visual correctness beyond that boundary.

## Common mistakes

* A correct final screenshot hides a broken sequence. Capture at least one intermediate state for every ordered interaction.
* A component test proves markup, not pixels or timing. Pair it with browser evidence when the requirement is visual.
* A desktop pass can hide a mobile regression. Recheck every changed responsive branch.
* A local pass does not prove deployment parity. Inspect the served asset graph before blaming the source component.

**REQUIRED BACKGROUND:** Use `verification-before-completion` before claiming the change is complete. Use `systematic-debugging` when the observed visual result contradicts the intended contract.
