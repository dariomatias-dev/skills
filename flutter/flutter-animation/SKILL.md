---
name: flutter-animation
description: "Implement animations in Flutter without leaks or jank: choosing implicit versus explicit, AnimationController lifecycle, limiting rebuilds, Hero flights, list and page performance. Use when writing an animated widget, debugging a ticker or dispose error, fixing dropped frames during motion, or reviewing animation code."
license: MIT
---

# Animation

This skill covers the mechanics: how to build an animation that disposes cleanly and holds its frame budget. Frame cost that is not caused by an animation, along with profiling method, isolates and memory, is covered by `flutter-performance`.

Whether something should animate at all, how long it should take and which curve it uses are policy decisions covered by `flutter-design-system`. Route transitions are covered by `flutter-navigation`.

## Choosing the mechanism

| Situation | Use |
| --- | --- |
| A value changes and should move to its new state | Implicit: `AnimatedContainer`, `AnimatedOpacity`, `AnimatedAlign` |
| An arbitrary widget should animate on a value change | `TweenAnimationBuilder` |
| Continuous, repeating, reversible, or driven by gesture | Explicit: `AnimationController` |
| Two widgets swap in place | `AnimatedSwitcher` |
| Children enter and leave a list | `AnimatedList` or `AnimatedSize` |

Reach for implicit first. An explicit controller is a `State`, a mixin, a lifecycle and a dispose obligation; take that on only when the animation must be driven rather than triggered.

## Controller lifecycle

```dart
class _PulseState extends State<Pulse> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: AppDurations.base,
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

| Rule | Reason |
| --- | --- |
| Always `dispose()` the controller | The ticker keeps firing on a disposed `State`, leaking the widget and throwing on the next `setState` |
| `SingleTickerProviderStateMixin` for one controller, `TickerProviderStateMixin` for several | The single variant asserts if a second ticker is created, which catches an accidental duplicate |
| Never start an animation in `build()` | `build` runs many times per interaction and each call restarts or stacks the animation |
| Guard with `mounted` after an `await` before driving a controller | An `await` between the trigger and the call gives the widget time to be removed |
| Never call `forward()` on a disposed controller | Wrap the trigger, not the controller, when a screen can leave mid-flight |

`vsync` is what stops the animation when the widget's route is covered: `TickerMode` disables tickers in an inactive subtree. Driving an animation from a `Timer` instead of a controller bypasses that and keeps burning frames behind another screen.

## Limiting rebuilds

An `AnimationController` notifies on every frame. Rebuilding a large subtree 60 times per second is the most common source of animation jank.

Pass the static part through `child` so it is built once:

```dart
AnimatedBuilder(
  animation: _controller,
  child: const ExpensiveContent(),   // built once
  builder: (context, child) => Opacity(
    opacity: _controller.value,
    child: child,                    // reused every frame
  ),
)
```

Further rules:

- Put `AnimatedBuilder` as deep as possible, wrapping only the widget whose properties change.
- Prefer the dedicated transition widgets, `FadeTransition`, `SlideTransition`, `ScaleTransition`, over rebuilding with `Opacity` or `Transform`. They animate at the render layer and skip the rebuild entirely.
- `RepaintBoundary` around a moving subtree keeps its repaints from invalidating the rest of the screen. It is not free: apply it to a genuinely independent moving layer, not to every widget.
- Never call `setState` from an animation listener to redraw. That is the manual version of what `AnimatedBuilder` does correctly.

## Lists

- Items animating on entry must animate once. Keying the animation to the build means every scroll back into view replays it, which reads as a glitch.
- A stateful animation inside a scrollable is disposed when the item scrolls out of the cache extent. That is usually correct; if the state must survive, the item needs an explicit keep-alive, and that cost has to be justified.
- Give animated list items a stable `Key`. Without one, reordering animates the wrong element into the wrong place.

## Hero

- A tag identifies one flight. Two mounted widgets carrying the same tag at the same time make the framework attempt a flight between them, producing an animation nobody asked for.
- When a widget can legitimately appear twice, such as persistent chrome duplicated outside a shell route, give it a flag to disable its `Hero` and set it on every instance but one.
- `Hero` animates between routes only. Two widgets on the same screen need an explicit transition instead.

## Performance

- Verify in profile mode. Debug builds are not representative, and animation is exactly where the gap is widest.
- The first run of an animation can stutter while its shaders compile. If a specific transition stutters only on its first play on a physical device, that is the cause, not the animation code.
- Animating `Opacity` on a large subtree forces an offscreen layer. `FadeTransition`, or animating a color's alpha, avoids it.
- Prefer animating transform and opacity over layout properties. Animating width, padding or a flex factor re-runs layout every frame.
- Long or infinite animations must stop when the content is not visible, which `TickerMode` handles as long as the animation is controller-driven.

## Anti-patterns

- An `AnimationController` without a matching `dispose`.
- Animation state driven by `Timer` or `Future.delayed` instead of a controller.
- `AnimatedBuilder` wrapping the whole screen when one widget moves.
- Duration or curve literals inline instead of tokens.
- Chained `Future.delayed` calls to stagger a sequence, where an `Interval` on one controller expresses it declaratively and stays cancellable.
- Animations that ignore the platform's reduced motion setting.
