---
name: flutter-layout-insets
description: Handle system UI insets in Flutter layouts: safe areas, status bar, navigation bar, display cutout, keyboard insets and Android edge-to-edge. Use when content sits under a system bar or the keyboard, when choosing between SafeArea and MediaQuery padding, when a list is clipped at the top or bottom, or when adapting an app to Android 15 edge-to-edge enforcement.
license: MIT
---

# Layout and System Insets

The system draws over the app: status bar, navigation bar, display cutout, keyboard. Content must move out of the way without losing the ability to paint underneath.

Scope is the space the platform claims. Space claimed by the app's own chrome, such as a docked bar or a floating overlay, is a token decision covered by `flutter-design-system`.

## The four measurements

Reading the wrong one is the single most common cause of inset bugs.

| Property | What it reports | Changes with keyboard |
| --- | --- | --- |
| `MediaQuery.viewPaddingOf` | Space covered by system UI, regardless of anything else | No |
| `MediaQuery.paddingOf` | `viewPadding` minus what `viewInsets` already covers | Yes, bottom drops to zero |
| `MediaQuery.viewInsetsOf` | Space fully obscured by system UI, in practice the keyboard | Yes |
| `MediaQuery.systemGestureInsetsOf` | Area reserved for system gestures such as back swipe | No |

The relationship is what trips people up: when the keyboard opens, `padding.bottom` goes to zero because `viewInsets.bottom` has taken over that space. Code that reserves bottom spacing from `padding` loses it the moment a field is focused. Code that must keep reserving it reads `viewPadding` instead.

Prefer the `Of` accessors (`MediaQuery.paddingOf(context)`) over `MediaQuery.of(context).padding`. The former subscribes only to that one property, so a keyboard opening does not rebuild every widget that only cared about the status bar.

## `SafeArea`

`SafeArea` is padding derived from `MediaQuery.padding`, nothing more. It is the right tool when the widget it wraps should simply be pushed inward.

```dart
SafeArea(
  top: false,          // an app bar already consumed the top inset
  child: content,
)
```

Rules:

- **Never nest it.** The inner instance sees the padding already consumed by the outer one, resolves to zero, and silently does nothing. The bug appears later when the outer one is removed.
- **Disable the sides that another widget already handles.** `Scaffold` with an `AppBar` consumes the top inset; wrapping the body in a full `SafeArea` is a no-op at best and confusing to read.
- **Do not wrap a scrollable in it.** `SafeArea` around a `ListView` pads the viewport, so content is clipped at the boundary while scrolling instead of passing under the system bar. Pad the list instead:

```dart
ListView(
  padding: EdgeInsets.only(
    bottom: MediaQuery.viewPaddingOf(context).bottom,
  ),
  children: items,
)
```

That single distinction, padding the viewport versus padding the content, decides whether a list looks correct while it scrolls.

## Android edge-to-edge

Apps targeting Android 15 (API 35) get edge-to-edge **enforced**, with no opt-out. Consequences:

| API | Status on Android 15 |
| --- | --- |
| `setStatusBarColor` | Deprecated, no effect |
| `setNavigationBarColor` | No effect under gesture navigation; still applies under 3-button navigation |
| `setNavigationBarDividerColor` | Deprecated and disabled |
| `setDecorFitsSystemWindows` | Deprecated and disabled |

Also, every non-floating window behaves as `LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS`: `SHORT_EDGES`, `NEVER` and `DEFAULT` are all interpreted as `ALWAYS`, so the cutout area is always part of the window.

Set the mode explicitly and style the bars through the overlay style rather than colors:

```dart
SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
SystemChrome.setSystemUIOverlayStyle(
  const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,   // Android
    statusBarBrightness: Brightness.light,      // iOS
    systemNavigationBarColor: Colors.transparent,
    systemNavigationBarIconBrightness: Brightness.dark,
  ),
);
```

Icon brightness is inverted between the platforms: on Android it describes the icons, on iOS it describes the background behind them. Setting only one of the two produces invisible icons on the other platform.

When the overlay style must follow the theme, drive it from the theme rather than setting it once at startup, or the icons stay dark after a switch to a dark background.

## Navigation mode

Gesture navigation and 3-button navigation reserve different amounts of space, and the user can switch at any time. A layout verified in one mode can be broken in the other.

- Never hardcode a bottom offset. Read the inset.
- Anything interactive within roughly 48dp of the bottom edge competes with the back gesture. Check `systemGestureInsets` for horizontal swipe conflicts, or move the target.
- Test both modes, plus a device with a display cutout in landscape, where the cutout inset moves to the side.

## Keyboard

- `Scaffold.resizeToAvoidBottomInset` defaults to `true`, which shrinks the body by `viewInsets.bottom`. Set it to `false` only when the layout handles the keyboard itself, for example a full-screen image behind a floating field.
- A field that lands under the keyboard is almost always a scrollable that was not given the inset. Add `viewInsets.bottom` to the scroll padding, and let `Scrollable` bring the focused field into view.
- Bottom sheets and dialogs need the keyboard inset applied explicitly; they are not part of the `Scaffold` body.
- On a screen with a fixed bottom action, reserve `max(viewInsets.bottom, viewPadding.bottom)` so the action clears both the keyboard and the navigation bar without stacking the two.

## Anti-patterns

- Nesting `SafeArea`.
- `SafeArea` wrapping a scrollable instead of padding its content.
- Reading `padding` where the value must survive the keyboard opening, or `viewPadding` where it must not.
- `MediaQuery.of(context).padding` in a widget that rebuilds on every keyboard frame.
- Hardcoded status bar or navigation bar heights, including constants copied from a design file.
- Styling system bars with the deprecated color APIs instead of `SystemUiOverlayStyle`.
- Testing only on one navigation mode, one orientation, or one device without a cutout.
