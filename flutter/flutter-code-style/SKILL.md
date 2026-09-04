---
name: flutter-code-style
description: "Dart and Flutter coding conventions: naming, immutability, comments, widget composition, and quality gates. Use when writing or reviewing Dart code, naming files/classes/providers, deciding on comments and documentation, or enforcing analyzer and formatting standards."
license: MIT
---

# Flutter Code Style

Language-level conventions. Structural decisions belong to `flutter-architecture`.

## Language

All code is written in English: files, folders, classes, enums, methods, variables, providers, ViewModels, tests, technical docs.

Every user-facing string comes from localization files, never a literal in a widget. Message authoring and formatting: `flutter-i18n`.

## Naming

| Element | Convention | Example |
| --- | --- | --- |
| File / folder | `snake_case` | `item_repository_impl.dart` |
| Class / enum / extension | `UpperCamelCase` | `LibraryRepository` |
| Member / variable / function | `lowerCamelCase` | `loadItems()` |
| Constant | `lowerCamelCase` | `defaultPageSize` |
| Private | leading underscore | `_cache` |

Suffix by role so the file name states what it is: `..._screen.dart`, `..._view_model.dart`, `..._repository.dart`, `..._repository_impl.dart`, `..._data_source.dart`, `..._providers.dart`, `..._service.dart`.

Contract and implementation are separate files: `x_service.dart` (abstract) and `x_service_impl.dart` or `<tech>_x_service.dart` when the name states the technology.

Name things for what they are, not where they are called from.

## Comments

Only doc comments (`///`) that add context the code cannot express: invariants, units, non-obvious trade-offs, platform quirks.

Delete comments that restate the code, commented-out code, and `TODO`s with no owner or issue reference.

## Immutability

- Entities, models and states are immutable. Use `final` fields and `const` constructors.
- Expose `copyWith` for state objects, hand-written or generated.
- Never mutate a list/map held in state; emit a new collection.
- State derived from streams is one immutable snapshot object, not mutable fields scattered across the presentation layer.
- Prefer `const` constructors on widgets everywhere the analyzer allows.

## Determinism

- Never use `Object.hashCode` (or the default `hashCode` on a class that does not override it) as a persisted or transmitted identifier. It is stable only within one process; a different run, isolate or Dart version can assign the same object a different value, so an id derived from it silently changes underneath already-stored data. Hash the actual bytes or fields with an explicit, documented algorithm (an FNV variant, `crypto`'s `md5`/`sha1`) when a deterministic derived key is needed.
- The same rule applies to `identityHashCode` and to relying on `Set`/`Map` iteration order, both of which are implementation details, not a contract.

## Dependencies in code

- Widgets and ViewModels never instantiate concrete dependencies; they receive them through providers.
- Widgets and ViewModels depend on contracts, never on concrete implementations. Which dependencies get an abstraction at all: `flutter-architecture`.

## Widgets

- Split into separate widget classes instead of `_buildX()` helper methods: real classes rebuild independently and can be `const`.
- One public widget class per file, named after the file. A second widget trailing a screen in the same file is invisible from the directory listing and gets duplicated instead of reused.
- Keep a widget file focused; when a build method needs scrolling to read, extract.
- Widgets built for a single screen live in a folder named after that screen, so the ones that are shared are the ones sitting loose beside it.
- No business rules, formatting logic or persistence in widgets.
- No hardcoded colors, spacing, radii, durations or text styles. Token rules: `flutter-design-system`.

## Async

- Use `async`/`await` over raw `Future` chains.
- Never swallow an exception. Catch it where it can be handled, and let it travel typed rather than as a null return.
- Check `mounted` (widget) or `ref.mounted` (auto-dispose notifier) after an `await` before using context or assigning state.
- Cancel subscriptions and timers in `dispose`/`onDispose`.

## Quality gates

The project keeps, at all times:

- zero analyzer errors;
- zero warnings;
- formatted code (`dart format`);
- no dead code;
- no duplicated logic;
- tests for relevant rules and flows.

Run before every commit:

```bash
dart format .
flutter analyze
flutter test
```

Use a strict lint set (for example `very_good_analysis`) and treat a rule you must disable as a decision to document, not a nuisance to silence file by file.
