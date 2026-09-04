---
name: flutter-design-system
description: "Flutter design system as a standalone local package: tokens, theme, component boundaries, motion and accessibility. Use when creating or extending a UI package, adding a shared component, defining tokens or themes, deciding where a widget belongs, or reviewing UI for hardcoded styling."
license: MIT
---

# Flutter Design System

The design system lives in its own local package (for example `packages/app_ui`), so it can be analyzed, tested and reused independently of the app.

```text
packages/app_ui/
├── lib/
│   ├── app_ui.dart          # the only public entry point
│   └── src/
│       ├── animations/
│       ├── components/
│       ├── icons/
│       ├── theme/
│       ├── tokens/
│       ├── typography/
│       └── widgets/
├── assets/fonts/
├── test/
├── analysis_options.yaml
└── pubspec.yaml
```

## Package rules

The package depends only on `flutter` and strictly visual libraries. It must **not** depend on:

- the state management library;
- the router;
- platform SDKs;
- database or key-value storage;
- the app's localization files.

Consequences:

- **No hardcoded text.** Every visible string arrives as a parameter; translation stays with the app.
- **No domain entities.** Components receive primitives or presentation models declared inside the package.
- **No state or navigation.** Components emit callbacks; the app decides what happens.
- `app_ui.dart` exports the public API only. The app never imports from `src/`.
- Fonts are declared in the package's own `pubspec.yaml`. A Flutter package that declares fonts exposes them to every app depending on it, which also keeps the package's golden tests self-contained.

## `components/` vs `widgets/`

| | `components/` | `widgets/` |
| --- | --- | --- |
| Purpose | Anything with the product's visual identity | Structure, layout, composition only |
| Tokens | Defines or consumes them | Must not declare colors, typography, radii, shadows or durations |
| Golden test | Required | Not required |

Suggested component groups: `artwork/`, `buttons/`, `cards/`, `dialogs/`, `feedback/`, `headers/`, `inputs/`, `media/`, `navigation/`, `sheets/`, `states/`.

Each group exposes a barrel exporting only its public components. Barrel naming and the cases where one must not exist: `flutter-architecture`.

## Where a widget belongs

| Widget | Location |
| --- | --- |
| Styled, reusable, stateless about the domain | design system `components/` |
| Layout-only helper | design system `widgets/` |
| Depends on providers/state management | app `core/widgets/` |
| Depends on a feature's entities or ViewModel | that feature's `presentation/widgets/` |

If a component needs a domain entity to render, it is in the wrong place. Pass a presentation model instead.

## Floating and overlay content

A widget positioned outside the screen's own `Scaffold` (a floating duplicate of persistent chrome shown on routes that don't include that `Scaffold`, a custom `OverlayEntry`, anything stacked above the normal tree) is not guaranteed a `Material` ancestor just because it visually sits on top of a screen that has one. Wrap its content in its own `Material(type: MaterialType.transparency)`.

Skipping it does not throw. It silently falls back to Flutter's default text style, which shows up as an unexpected colored underline or missing ink response on tap, a bug that ships easily because the widget still looks and behaves correctly at a glance, only failing under a pixel-level comparison.

## Tokens and theme

All shared visual values are tokens; a one-off value may stay inline only when it is genuinely not a reusable pattern.

```text
tokens/
├── app_colors.dart      app_metrics.dart
├── app_curves.dart      app_radius.dart
├── app_durations.dart   app_sizes.dart
├── app_elevations.dart  app_spacing.dart
```

`tokens/` holds scalar values only. Text styles are composed objects, so they live in `typography/`, built from the token scales and the package's font family, and reach widgets through the theme rather than through a direct import.

The theme is built from the tokens and typography set and ships light and dark modes; the app only consumes the exported theme. App-specific values that `ThemeData` has no slot for go into a `ThemeExtension`, not a global singleton.

Scales, defaults and the token authoring rules: [tokens.md](references/tokens.md).

## UI states and feedback

Standard components for loading, empty, error, permission and retry states, plus the rules for choosing between toast, dialog, sheet, inline message and haptics: [ui-states-and-feedback.md](references/ui-states-and-feedback.md).

## Motion

- Animation reflects real state, not decoration.
- Durations and curves come from tokens; no magic numbers.
- Continuous animations stop when the widget is not visible.
- Decorative animations are disabled when the system requests reduced motion (`MediaQuery.disableAnimationsOf(context)`).
- One shared entrance animation for lists (staggered, first display only) and one shared press response for interactive elements, so behavior is uniform.

## Accessibility

- Semantic labels on controls and list items; state changes announced.
- Minimum touch target of 48dp.
- Sufficient contrast in both themes, asserted on the tokens rather than inspected per component.
- Text scaling clamped once at the root, and layouts that survive the clamped maximum.
- Predictable focus order.
- Never convey meaning by color alone.

The rules per case, the clamp and the contrast matrix test: [accessibility.md](references/accessibility.md).

## Testing

Where component and screen goldens live, and how to keep them stable: `flutter-testing`.

## Anti-patterns

- Raw `Color(0x...)`, `EdgeInsets.all(13)`, `Duration(milliseconds: 250)` inside a screen.
- A component reading a provider or navigating on its own.
- Literal user-facing text inside the package.
- Widget variants created by copy-paste instead of parameters.
- Importing `package:app_ui/src/...` from the app.
- Floating or overlay content assumed to inherit `Material` from a sibling `Scaffold` instead of declaring its own.
