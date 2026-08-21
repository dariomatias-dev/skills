# Design Tokens

Tokens are the single source of visual truth. A value used twice is a token; a value used once may stay inline.

## Authoring rules

- One file per token family, exposed through `abstract final class` with `static const` members.
- Name by role, not by value: `textSecondary`, not `grey600`; `spacingLarge`, not `spacing24`.
- Colors that change with theme are resolved through the theme, never read from a raw constant inside a widget.
- Keep the scales short. Every extra step is a decision someone has to make later.

```dart
abstract final class AppSpacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;
}
```

## Color

Define a light and a dark set with the same role names:

```text
background   surface   surfaceAlt   card
textPrimary  textSecondary  textTertiary
accent       onAccent
divider      shadow
```

Semantic colors (`error`, `success`, `warning`, `info`) are reserved for feedback and never used decoratively. Verify contrast in both themes; text roles must clear WCAG AA against every surface they sit on.

## Spacing

One scale, six steps, the `AppSpacing` set above: `4 8 16 24 32 48`. Add a step only when a real layout cannot be built from the existing ones, and add it to the scale rather than inline at the call site.

Pick one default screen horizontal padding and apply it everywhere; inconsistent gutters are the most visible sign of an unsystematic UI.

## Radius

```text
small  medium  large  extraLarge  full
```

Radius communicates hierarchy: small for inputs and chips, large for cards and sheets, full for pills and avatars.

## Icon sizes

```text
xs  sm  md  lg  xl
```

Icon size pairs with text size. Define the pairing once instead of choosing per call site.

## Layout metrics

Sizes of persistent chrome (app bar height, docked bars, floating overlays, side margins) are tokens, because scrollable content must reserve bottom padding for anything overlaying it. A list hidden behind a floating bar is a token problem, not a screen problem.

## Duration and curves

```text
fast   ~180ms   micro-interactions, state flips
base   ~320ms   standard transitions
slow   ~520ms   large surfaces, sheets
page   ~420ms   route transitions
```

```text
emphasized  Cubic(0.2, 0.0, 0.0, 1.0)    default transitions
decelerate  Cubic(0.05, 0.7, 0.1, 1.0)   elements settling in
spring      Cubic(0.34, 1.35, 0.64, 1.0) confirmations with slight overshoot
```

## Elevation

Prefer explicit shadow tokens over material elevation numbers so the same depth reads correctly in both themes: dark themes need stronger, softer shadows than light ones.

## Typography

Define a named text style set (`displayLarge` through `labelSmall`, or a product-specific set) built on the font family declared by the package. Widgets reference styles by role from the theme; they never build `TextStyle` inline.
