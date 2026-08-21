---
name: flutter-navigation
description: Typed navigation with go_router and go_router_builder: route classes, per-feature navigators, shell routes, redirects and transitions. Use when adding or changing a route, wiring tab shells, guarding access, customizing page transitions, or fixing go_router_builder generation errors.
license: MIT
---

# Flutter Navigation

`go_router` configured through `go_router_builder`, so every route is a typed class and every call site is compile-checked. Screens never call the router directly; they call a navigator.

## Layout

```text
core/navigation/
├── app_router.dart        # GoRouter provider + typed route classes
├── app_router.g.dart      # generated, never edited
├── route_paths.dart       # raw paths, only for tests/edge comparisons
├── route_redirect.dart    # centralized guards
├── route_transitions.dart # reusable transitions
└── navigators/
    ├── <feature>_navigator.dart
    └── main_shell_navigator.dart
```

Create a navigator per feature that has navigable destinations, named after the destination it leads to, not the caller. Files appear only when routes exist for them.

## Router and routes

The router provider is written by hand rather than generated with `@riverpod`, because it is created once for the life of the app and must not be auto-disposed; a `GoRouter` rebuilt mid-session drops the navigation stack.

```dart
final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: const SplashRoute().location,
    redirect: (context, state) => appRouteRedirect(ref: ref, state: state),
    routes: $appRoutes,
    errorBuilder: (_, _) => const NotFoundScreen(),
  );
});

@TypedGoRoute<SplashRoute>(path: '/splash')
class SplashRoute extends GoRouteData with $SplashRoute {
  const SplashRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) => const SplashScreen();
}

@TypedGoRoute<DetailRoute>(path: '/items/:itemId')
class DetailRoute extends GoRouteData with $DetailRoute {
  const DetailRoute({required this.itemId});

  final String itemId;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      DetailScreen(itemId: itemId);
}
```

Rules that break the build when ignored:

- `part 'app_router.g.dart';` must be declared in the file.
- Every `GoRouteData` subclass declares `with $ClassName` (generated mixin).
- **Exception:** `StatefulShellRouteData` subclasses take no `with`: the generator emits an extension, not a mixin; adding `with` fails analysis with `mixin_of_non_class`.
- Class fields are the path/query parameters, typed, never a string map.
- Nested routes are declared inside the parent annotation: `routes: [TypedGoRoute<Child>(path: 'child')]`.
- Re-run code generation whenever a route is added, removed, or has its parameters changed. Commands and analyzer configuration: `flutter-project-setup`.

`go_router_builder` emits no `// ignore_for_file: type=lint` header, so the generated router relies entirely on the project's analyzer exclusion to stay out of the lint report.

## Navigators

Screens and widgets never call `context.go`/`push` and never instantiate route classes outside `core/navigation/`.

```dart
abstract final class DetailNavigator {
  static Future<void> openDetail(
    BuildContext context, {
    required String itemId,
  }) {
    return DetailRoute(itemId: itemId).push(context);
  }
}
```

- Return `Future<void>` unless a caller actually consumes the `pop` result; do not add a generic `<T>` "just in case".
- Navigators hold no business rules, no repository access, no state, no user feedback.
- When a route gains a parameter, the generated class signature changes and the compiler flags every stale call site. That is the whole point of typed routes over `pushNamed` with a string map.

## Shell routes

For persistent bottom navigation, use `StatefulShellRoute` with one branch per tab. Tab switching (`goBranch`) is not navigation into a feature, so its navigator lives in `core/navigation/navigators/`, not inside a feature.

Nested navigator keys decide what the shell keeps on screen: routes that must cover the shell (full-screen player, modals) declare the root navigator key.

### Persistent chrome outside the shell

A shell's persistent widgets (bottom bar, a docked media bar) stay mounted while a route is pushed on top within the same branch, but a route pushed on the **root** navigator key covers them without unmounting them; they are still there, just off-screen. If that chrome must stay visible on those routes too, give it a second, floating instance there; it is a genuine duplicate, not a way to "reuse" the shell's copy.

That duplication has one recurring failure mode: if the chrome wraps part of its content in a `Hero` (artwork, an avatar), the shell's instance and the floating instance are mounted at the same time and would carry the identical tag. Any navigation between the shell and the floating instance's route is then read as a Hero flight between the two, producing an animation glitch nobody intended. Give the widget a flag to disable its `Hero` and set it on every instance but one, so a given tag is only ever carried by a single mounted widget.

## Redirects

`route_redirect.dart` centralizes guards: onboarding completion, permission gates, session state.

- Compare and return destinations using route classes (`const OnboardingRoute().location`), not raw path constants.
- No slow work, no user feedback, no business rules inside a redirect.
- The intentional import cycle between `app_router.dart` and `route_redirect.dart` is fine: Dart allows cycles between libraries (it is only a problem with `part`/`part of`).
- Base the decision on already-resolved state; a redirect that awaits I/O on every navigation stalls the app.

## Transitions

Custom transitions override `buildPage(context, state)` instead of `build(context, state)`, and pull durations and curves from design tokens, never hardcoded numbers.

Keep reusable transitions in `route_transitions.dart`; a screen that opens from a specific origin (an expanding mini player, for instance) gets its own transition consistent with that origin.

## `route_paths.dart`

Keep it only for the rare cases that need a raw path outside the normal flow: redirect tests, minimal routers built inside widget tests. Production navigation always goes through typed route classes.

## Anti-patterns

- `Navigator.push(MaterialPageRoute(...))` in a feature.
- `context.pushNamed` with `pathParameters` string maps.
- Passing whole entities as route parameters instead of an id.
- Guard logic duplicated inside screens' `initState`.
- A floating duplicate of persistent chrome sharing a `Hero` tag with the shell's own mounted instance.
