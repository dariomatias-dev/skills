# Accessibility

Every rule here is a property of the design system package, not of a screen. A component that is accessible once is accessible everywhere it is used; a screen that fixes it locally fixes it once.

## Semantics

The framework infers semantics from the widgets it knows. A control built from `GestureDetector`, `InkWell` on a `Container` or a custom `Pressable` is, to a screen reader, an unlabeled area of the screen.

```dart
Semantics(
  button: true,
  label: semanticLabel,
  enabled: onPressed != null,
  child: Pressable(onTap: onPressed, child: /* ... */),
)
```

| Case | Rule |
| --- | --- |
| Icon-only control | A label is mandatory. The icon carries no text, so without one the control announces nothing |
| Toggle, switch, checkbox | Expose the state (`toggled`, `selected`), never fold it into the label. "Shuffle on" as a label makes the state part of the name and unreadable when it changes |
| Disabled control | `enabled: false`. Lowering opacity is a visual cue only, and a screen reader will still offer the control as actionable |
| Composite list row | `MergeSemantics`, so the row reads as one item instead of four unrelated nodes in sequence |
| Decorative image or artwork placeholder | `ExcludeSemantics`, so the reader does not stop on it |
| Meaningful image | A label describing what it conveys, not the filename or the word "image" |
| Progress or position indicator | A label with a formatted value. A raw bar reports nothing |

Labels are user-facing text: they come from localization, and they are parameters into the package, never literals inside it.

## Announcing what only appeared briefly

A toast, a snackbar or an inline confirmation that fades is invisible to a screen reader unless it is announced. Any outcome the user only learns about through a transient message needs an explicit announcement alongside it.

```dart
SemanticsService.announce(message, Directionality.of(context));
```

Announce the outcome, not the mechanics: what succeeded or failed, in the same words the visible message uses. An announcement fired on every state change, rather than on the outcome, turns into noise the user cannot skip.

## Touch targets

Minimum 48dp in both dimensions, regardless of the size of the thing being drawn. A 24dp icon needs padding or a fixed-size box around it, and that size is a token, not a literal at the call site.

Two adjacent controls that each meet the minimum but overlap at the edges are still a problem: keep the spacing token between them, so a mistap lands on nothing rather than on the wrong action.

## Text scaling

The system text scale can go far past what any layout was designed for. Clamp it once, at the root, rather than defending against it per screen:

```dart
builder: (context, child) {
  final mediaQuery = MediaQuery.of(context);
  return MediaQuery(
    data: mediaQuery.copyWith(
      textScaler: mediaQuery.textScaler.clamp(
        maxScaleFactor: AppTypography.maxTextScaleFactor,
      ),
    ),
    child: child!,
  );
}
```

- Rebuild the whole `MediaQueryData` with `copyWith`. Constructing a fresh one drops every other value (padding, insets, platform brightness) and produces layout bugs far from the change.
- The clamp is an upper bound, chosen so the densest screen still fits; a value near 1.3 is a common ceiling. Clamping to 1.0 is not accessibility support, it is opting out of it.
- Nothing below the root re-clamps. A second clamp deeper in the tree is invisible in review and impossible to reason about.
- Layouts must survive the clamped maximum without overflow. Fixed-height rows containing text are the usual first casualty.

## Contrast

Contrast is a property of the token pairs, so test the tokens instead of inspecting components by eye.

Assert every text color against every surface it can legitimately sit on, in both themes:

```dart
for (final theme in {'light': AppColors.light, 'dark': AppColors.dark}.entries) {
  for (final background in backgrounds.entries) {
    for (final text in textColors.entries) {
      test('${theme.key}: ${text.key} on ${background.key} meets 4.5:1', () {
        expect(contrastRatio(text.value, background.value),
            greaterThanOrEqualTo(4.5));
      });
    }
  }
}
```

| Content | Minimum ratio |
| --- | --- |
| Normal text | 4.5:1 |
| Large text (roughly 18pt, or 14pt bold) | 3:1 |
| Icons and control boundaries that carry meaning | 3:1 |

One matrix test catches a palette regression that would otherwise require reviewing every golden by eye. It also fails at the moment the token changes, which is when the decision is still being made.

## Meaning without color

Never encode state in color alone: a colored dot needs a shape, an icon or text beside it. The same rule covers charts, status lists and validation states.

Colorblind users are the stated reason, but the practical one is broader: a color read on a dimmed screen in sunlight is the same failure.

## Motion

Decorative motion is disabled when the platform asks for it, checked through `MediaQuery.disableAnimationsOf(context)`. Motion that carries information (a progress indicator, a loading state) stays, at reduced amplitude if needed.

## Focus and order

- Focus order follows visual order. A component that reorders its children for layout reasons has to say so, or traversal jumps around the screen.
- A dialog or sheet traps focus while open and returns it where it came from on close.
- Any interactive element reachable by pointer is reachable by keyboard and by switch control.

## Testing

- Find widgets by semantic label rather than by type, so a test fails when a control loses its label.
- Keep the contrast matrix in the design system package, where the tokens are defined.
- Golden tests do not verify accessibility. A component can be pixel-perfect and unreachable.
