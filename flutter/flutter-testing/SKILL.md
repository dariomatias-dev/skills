---
name: flutter-testing
description: Testing strategy for Flutter apps: unit, widget, golden and integration tests, fakes for platform services, and provider overrides. Use when writing or reviewing tests, deciding what deserves a test, setting up test doubles, or debugging flaky widget and golden tests.
license: MIT
---

# Flutter Testing

Tests are written alongside the feature, not after it. Test behavior and rules, not implementation details.

## What to test

| Priority | Examples |
| --- | --- |
| Always | Repositories, DAOs and migrations, ViewModels, mappers/serialization, business rules, computed statistics, route guards |
| Usually | Design system components, state/feedback components, key screens, navigation flows, forms |
| Rarely | Trivial widgets with no logic |
| Never | Generated code, framework APIs, third-party library internals |

If a test only restates the implementation line by line, it has no value.

## Test doubles

- **Fake**: a working in-memory implementation of a contract. Default choice for repositories, storage and platform services.
- **Mock** (`mocktail`): for verifying interactions or simulating failures.
- Every platform-dependent service (audio, permissions, filesystem, camera, location) ships a fake so flows can be tested without a device. That is the main reason those contracts exist.
- In-memory database for DAO tests; no test touches real device storage.

```dart
class FakeItemRepository implements ItemRepository {
  final List<Item> items = [];

  @override
  Future<List<Item>> findAll() async => List.unmodifiable(items);
}
```

## Unit tests

Riverpod ViewModels are tested through a container with overridden dependencies:

```dart
test('loads items', () async {
  final container = ProviderContainer.test(
    overrides: [itemRepositoryProvider.overrideWithValue(FakeItemRepository())],
  );

  final state = await container.read(itemListViewModelProvider.future);

  expect(state, isEmpty);
});
```

`ProviderContainer.test()` registers its own `addTearDown(container.dispose)` and fails the run if any container was left undisposed, which is why it is preferred over a plain `ProviderContainer` plus a manual teardown.

Cover the failure path, not only the happy path: a ViewModel that never emits `AsyncError` in tests is untested.

## Widget tests

- Pump the widget inside a `ProviderScope` with overrides, the app theme, and the localization delegates.
- Set a realistic phone viewport when persistent overlays (docked bars, floating players) cover content; layout bugs only appear on short screens.
- Prefer finding by semantics/label over by widget type.
- With continuous animations, `pumpAndSettle` never returns: advance a fixed number of frames with `pump(Duration)` instead.
- Test what the user observes: rendered text, enabled state, callbacks fired, not internal state fields.

## Golden tests

- Use the official Flutter golden APIs.
- Component goldens live in the design system package; screen goldens live in the app.
- Cover both light and dark themes for anything with a color decision.
- Freeze animations by pumping a fixed frame count, and load fonts explicitly so text renders identically in CI.
- Add a golden only where the visual result carries real value; goldens for trivial layouts are pure maintenance cost.

## Integration tests

Run `integration_test` over the flows that would break the product:

- first-run and permission granting;
- the main navigation path;
- create/edit/delete of the primary entity;
- background or platform-integrated behavior;
- session restore after a restart;
- locale switching.

Seed data into an in-memory database inside the test rather than depending on real device content.

## Organization

```text
test/
├── core/
├── features/<feature>/{data,domain,presentation}/
└── helpers/          # pump helpers, fakes, fixtures

packages/app_ui/test/  # component + golden tests, run independently
```

Mirror the `lib/` structure; name files `<source>_test.dart`.

## Rules

- No `Future.delayed` to "wait" for something. Use `fakeAsync`, controllers or pumped frames.
- Each test is independent and deterministic; inject clocks and id generators instead of using real time and random values.
- Always `addTearDown` for subscriptions and databases; containers get it from `ProviderContainer.test()`.
- A flaky test is a broken test: fix or delete it.
