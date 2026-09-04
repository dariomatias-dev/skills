---
name: flutter-responsive-layout
description: "Adapt Flutter layouts across phone, tablet, foldable and desktop window sizes: breakpoints, LayoutBuilder versus MediaQuery, adaptive navigation and input, orientation and text scaling. Use when a layout must work on more than one screen size, when adding tablet or large-screen support, or when reviewing a screen for overflow and cramped spacing."
license: MIT
---

# Responsive Layout

A layout is responsive when it reflows to the space it is given, and adaptive when it changes structure or affordance for the platform it runs on. Both are needed, and they are different decisions.

Space claimed by system bars and the keyboard is covered by `flutter-layout-insets`. Spacing values and component sizes are tokens, covered by `flutter-design-system`.

## Measuring the right thing

| Tool | Reports | Use for |
| --- | --- | --- |
| `LayoutBuilder` | Constraints given to this widget | Any decision about how a widget lays out its own children |
| `MediaQuery.sizeOf` | The window | Screen-level structure decisions only |
| `MediaQuery.orientationOf` | Portrait or landscape | Rare; usually the width already answers the question |

Prefer `LayoutBuilder`. A component that branches on `MediaQuery.sizeOf` is guessing at the space it was given, and it is wrong the moment it is placed in a split view, a dialog, a side panel or a tablet's master pane.

`MediaQuery.sizeOf` is a window measurement, not a device measurement. On a foldable or a desktop window it changes while the app runs, and on a split screen it is a fraction of the display.

## Breakpoints

Define breakpoints once as tokens and branch on them by name, never on raw numbers scattered across screens.

```text
compact    < 600    phone portrait
medium     600-839  small tablet, phone landscape, split view
expanded   >= 840   tablet, desktop window
```

Rules:

- Branch on width, not on a device category. There is no reliable "is tablet" question; there is only how much width this widget has.
- Prefer a layout that flows continuously over one that snaps at a threshold. `Wrap`, `Flexible`, `Expanded` and a max content width handle most cases with no breakpoint at all.
- Constrain line length on wide screens. Text stretched across a full tablet width is technically responsive and unreadable.

## Adaptive structure

What changes at each size is structure, not just scale:

| Size | Navigation | Content |
| --- | --- | --- |
| Compact | Bottom bar or drawer | One pane, detail on a pushed route |
| Medium | Navigation rail | One pane, or list and detail if the content is narrow |
| Expanded | Rail or permanent drawer | List and detail side by side |

When a list and detail appear side by side, the detail is no longer a route. Navigation state and layout become coupled: selecting an item on a wide screen updates a pane, while on a narrow screen it pushes. Decide that in one place, not per list.

Scaling a phone layout up produces a screen with one column of content and enormous empty margins. That is worse than not supporting the size at all.

## Text scaling

- Never disable text scaling. Clamp it if a layout genuinely cannot absorb the largest sizes: `MediaQuery.withClampedTextScaling`.
- Fixed-height containers holding text overflow first. Use minimum heights and let content grow.
- Verify at the largest supported scale, in the longest supported language. Overflow is a combination of both, and it appears in neither alone.

## Input and platform affordances

- Pointer devices need hover states and a visible focus ring; touch does not.
- Keyboard navigation on large screens means real focus traversal and shortcuts for primary actions, not just tab order by accident.
- Right-click and long-press are the same intent on different inputs.
- Scrollbars are expected on desktop and unexpected on touch.

## Verification

The cheapest way to find these bugs is to change the window, not to reason about it:

- Resize the window on desktop, or fold and unfold, while the app is running. Layout must reflow without a rebuild artifact or lost state.
- Rotate on device. State that survives rotation is state held correctly.
- Check the shortest supported height. Vertical space, not width, is what breaks forms and dialogs.

## Anti-patterns

- `MediaQuery.sizeOf` inside a reusable component to decide its own layout.
- Raw pixel thresholds inline, different on each screen.
- `isTablet` helpers derived from a diagonal measurement or the platform name.
- Separate widget trees per size that drift apart in behavior.
- Layouts verified only in portrait, only at default text scale, or only on the largest test device.
- Disabling text scaling to prevent overflow.
- A fixed `width:` where a constraint would do.
