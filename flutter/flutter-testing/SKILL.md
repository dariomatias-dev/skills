---
name: flutter-testing
description: "Testing strategy for Flutter apps: unit, widget, golden and integration tests, fakes for platform services, provider overrides, and a whole-graph wiring smoke test. Use when writing or reviewing tests, deciding what deserves a test, setting up test doubles, verifying the provider graph wires together, or debugging flaky widget and golden tests."
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
- Every platform-dependent service (audio, permissions, filesystem, camera, location) ships a fake so flows can be tested without a device. That is the main reason those contracts exist. A fake that also records what it emitted lets a test assert on the sequence rather than only the final value.
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

## Provider graph

A unit test overrides one dependency and proves one ViewModel; it says nothing about whether the rest of the graph actually wires together, since the pieces it does not touch are never constructed. A wiring mistake (a provider reading the wrong instance, a circular `watch`, an argument in the wrong order) compiles, passes every unit test, and only surfaces on a device.

Add one test that builds the real, production `ProviderContainer`, overriding only the leaf providers that need a platform resource (the database file location, the key-value store), and reads every other provider in the graph:

```dart
test('every provider resolves to its production implementation', () {
  final container = ProviderContainer(
    overrides: [
      databaseProvider.overrideWithValue(openTestDatabase()),
      keyValueStorageProvider.overrideWithValue(FakeKeyValueStorage()),
    ],
  );
  addTearDown(container.dispose);

  for (final provider in allProviders) {
    expect(container.read(provider), isA<ExpectedProductionType>());
  }
});
```

This is not a substitute for feature tests. It catches one class of failure only: the object graph fails to construct, or constructs the wrong implementation, before a single feature test would ever notice.

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
- Test the color tokens themselves for contrast (WCAG ratio) once, in the design system package. A single passing test on the token values catches a contrast regression that would otherwise require inspecting every component's golden by eye.

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

## Coverage

Coverage measures which lines ran, not whether the assertions were meaningful. It is useful as a floor that stops untested code from landing, and misleading as a target.

Exclude before measuring:

- Generated sources. They mirror hand-written declarations, so counting them makes the number rise when an annotated class is added and no test is written.
- Localization output.
- Schema and table declarations, which are data rather than logic.

Without those exclusions the figure drifts on its own and stops meaning anything.

Pick a threshold the project can hold and enforce it in the pipeline; the gate itself is covered by `flutter-ci`. A file with no logic worth testing is excluded deliberately and visibly, never covered by a test written only to move the percentage.

## Stability

A flaky test is a broken test. It is worse than a missing test, because a suite that fails at random trains the team to rerun the job instead of reading the failure, and a real regression then passes unnoticed among the reruns.

Flakiness is almost never random. It is a hidden dependency on something the test does not control.

| Source | Symptom | Fix |
| --- | --- | --- |
| Real clock | Passes locally, fails on a slow CI machine | Inject a clock; drive time with `fakeAsync` |
| Real randomness | Fails once every few hundred runs | Inject the generator, or seed it explicitly |
| Test order | Passes alone, fails in the suite | Move shared setup into `setUp`, never mutable state in `setUpAll` |
| Leaked state | Failure appears in the test after the culprit | `addTearDown` for every subscription, container, database and override |
| Unordered collections | Fails on a different platform or SDK | Sort before comparing, or compare as sets |
| Unawaited futures | Assertion runs before the work completes | Await everything, and fail the test on unawaited errors |
| Animations | `pumpAndSettle` times out | Advance a fixed number of frames instead |
| Fonts not loaded | Golden diffs only in CI | Load fonts explicitly in the test setup |
| Ambient locale or timezone | Formatting assertions differ per machine | Pin both in the test |

## Diagnosing a flaky test

1. Reproduce before fixing. A test that fails once in fifty runs is not fixed by a change that has not been run fifty times.

   ```bash
   for i in $(seq 1 50); do flutter test test/path/to/file_test.dart || break; done
   ```

2. Check order dependence by randomizing:

   ```bash
   flutter test --test-randomize-ordering-seed random
   ```

   A suite that only passes in declaration order has shared state. Record the failing seed and reuse it to reproduce.

3. Isolate: run the single test alone. Passing alone and failing in the suite confirms leakage rather than a bug in the test itself.

4. Fix the dependency, not the symptom. Adding a delay, a retry or a longer timeout hides the leak and it returns later in a different test.

Never mark a test as skipped to unblock a merge without an issue recording why. A skipped test is invisible; an untracked skipped test is permanent.
