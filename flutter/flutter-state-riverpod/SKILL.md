---
name: flutter-state-riverpod
description: "State management and dependency injection with Riverpod: ViewModels as Notifier/AsyncNotifier, provider types, lifecycle pitfalls, derived state and rebuild control. Use when creating a ViewModel or provider, wiring dependencies, debugging rebuilds or disposal errors, or reviewing Riverpod code."
license: MIT
---

# Flutter State with Riverpod

Riverpod handles both state management and dependency injection. ViewModels are `Notifier`/`AsyncNotifier`; everything injectable is a provider.

## What each tool is for

| Need | Tool |
| --- | --- |
| Screen state + actions | `Notifier` (sync) / `AsyncNotifier` (async) ViewModel |
| Dependency injection | `Provider` returning the concrete implementation typed as the contract |
| Simple UI state (query, tab, sort) | small `Notifier` in the feature's `presentation/providers/` |
| Computed value | derived provider that `watch`es other providers |
| External stream | `StreamProvider` or a `Notifier` subscribing in `build()` |

## ViewModels

Generated with `@riverpod`; the class and its provider stay in the same file.

```dart
@riverpod
class ItemListViewModel extends _$ItemListViewModel {
  @override
  Future<List<Item>> build() {
    return ref.watch(itemRepositoryProvider).findAll();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(itemRepositoryProvider).findAll(),
    );
  }
}
```

A ViewModel may: hold state, run screen actions, call domain contracts, handle loading/success/error, coordinate presentation flows.

A ViewModel must not: use `BuildContext`, build widgets, touch persistence or SQL directly, talk to a platform SDK, depend on a concrete implementation, or define visual styling.

## Dependency injection

```dart
@riverpod
ItemRepository itemRepository(Ref ref) =>
    ItemRepositoryImpl(ref.watch(itemLocalDataSourceProvider));
```

Return the contract type, not the implementation type; that is what makes overriding in tests trivial. Providers for a feature's dependencies live in that feature; global ones live in `core/` next to the class they provide.

Dependencies that must exist before `runApp` (storage, database) are resolved in `main` and injected with `overrideWithValue` on the root `ProviderScope`.

## `read` vs `watch` vs `listen`

- `watch`: inside `build()` of a widget or notifier, to react to changes.
- `read`: inside callbacks and action methods only.
- `listen`: for side effects (navigation, snackbars) reacting to state changes.

Never `watch` inside a callback; never `read` a dependency in `build()` when the state should follow it.

## Lifecycle pitfalls

**Auto-dispose + await.** Any method of an auto-dispose notifier that `await`s before assigning `state` must guard:

```dart
Future<void> save() async {
  await _repository.save(state.value!);
  if (!ref.mounted) return;
  state = AsyncData(...);
}
```

A provider read only via `.notifier` (never watched) can be disposed during the `await`, and assigning `state` afterwards throws at runtime.

**No provider reads in lifecycle callbacks.** Riverpod forbids reading or modifying other providers inside `onDispose`, `onCancel` and `listen` callbacks. Capture what you need once in `build()` and store it in a field:

```dart
@override
State build() {
  final repository = ref.watch(historyRepositoryProvider);
  ref.onDispose(() => repository.flush()); // captured, not re-read
  return const State.initial();
}
```

**keepAlive vs autoDispose.** Auto-dispose is the default. Keep alive only what must survive navigation (session-wide services, long-lived connections), and make sure it releases its resources in `onDispose`.

## Rebuild control

Watch the narrowest slice with `select`, especially for high-frequency streams (playback position, scroll, timers):

```dart
final isPlaying = ref.watch(
  playbackProvider.select((s) => s.isPlaying),
);
```

Other rules:

- Push `watch` down to the smallest widget that needs the value; do not watch at screen level and pass everything down.
- Expose one immutable state object per stream source instead of several parallel providers reading the same stream.
- Derive values in providers, not in `build()` of widgets.

## Async state in the UI

Render `AsyncValue` with a single shared widget mapping `loading`/`error`/`data` to the standard state components, so every screen behaves the same. Use `AsyncValue.guard` in ViewModels instead of manual try/catch that loses the error state.

## Code generation

Re-run code generation after adding, removing or changing the signature of any annotated provider. Commands: `flutter-project-setup`.

## Testing

How ViewModels and providers are tested, including container setup and fakes: `flutter-testing`.

## App lifecycle

Backgrounding and resuming are state changes like any other, and belong in a provider rather than scattered across widgets.

```dart
@riverpod
class AppLifecycle extends _$AppLifecycle {
  @override
  AppLifecycleState build() {
    final listener = AppLifecycleListener(
      onStateChange: (value) => state = value,
    );
    ref.onDispose(listener.dispose);
    return AppLifecycleState.resumed;
  }
}
```

- One listener for the whole app. A `WidgetsBindingObserver` per screen means several components reacting to the same event in an undefined order.
- `paused` is the last reliable point to persist. On both platforms the process can be killed afterwards without further notice, so work deferred to `detached` may never run.
- Resuming is not a reason to refetch everything. Refresh what can be stale and is visible; a blanket invalidation on every resume turns app switching into a loading screen.
- Timers, polling and streams that cost battery stop on `paused` and restart on `resumed`.
- Sensitive screens that must hide their content in the task switcher react to `inactive`, which fires before `paused`.

## Anti-patterns

- One global file holding every provider in the project.
- Business logic in a provider body instead of a repository or use case.
- Mutable fields inside a notifier instead of a new immutable state.
- `ref.read` in `build()` for a value that changes.
- Watching a whole state object to read one boolean.
- Providers exposing implementation types.
