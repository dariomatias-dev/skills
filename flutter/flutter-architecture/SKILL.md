---
name: flutter-architecture
description: "Feature-first project structure for Flutter apps using MVVM over a simplified Clean Architecture. Use when creating a Flutter project, adding a feature, deciding where a file belongs, choosing whether to add a layer/abstraction/use case, or reviewing structural consistency."
license: MIT
---

# Flutter Architecture

Feature-first structure, MVVM in the presentation layer, simplified Clean Architecture underneath. Layers exist to make code testable and replaceable, never as ceremony.

## Core principle

Add a layer only when it buys testability, substitution, or a real business rule. Every abstraction must answer: *what breaks if I delete it?*

## Repository layout

```text
.
├── .github/workflows/
├── android/ ios/
├── assets/
├── lib/
│   ├── main.dart
│   ├── l10n/
│   └── src/
│       ├── app.dart          # root widget: theme, router, localization
│       ├── core/
│       ├── features/
│       └── gen/              # generated asset/font references
├── packages/
│   └── app_ui/               # design system as a local package
├── test/
├── analysis_options.yaml
└── pubspec.yaml
```

`packages/` sits beside `lib/`, never inside it. The app declares each one as a path dependency; the wiring is in `flutter-project-setup`.

## `core/`

Technical, cross-cutting infrastructure. No feature business rules.

```text
core/
├── constants/      # technical constants only, never user-facing text
├── database/       # db config, tables, DAOs, providers
├── errors/         # app exception types
├── extensions/     # extensions used by more than one feature
├── navigation/     # router, typed routes, navigators
├── audio/          # playback engine, media session, audio focus
├── permissions/    # platform permission abstraction
├── providers/      # global providers with no better home (clock, observers)
├── services/       # id generation, platform readers, caches
├── storage/        # key-value persistence abstraction
└── widgets/        # structural widgets that depend on state management
```

The permission wrapper is worth spelling out, because a boolean is not enough. The contract must distinguish three outcomes, since each leads to a different flow:

| Outcome | What the app can do |
| --- | --- |
| Granted | Proceed |
| Denied | Ask again, after explaining why the permission is needed |
| Permanently denied | Asking again is a no-op; the only path is opening system settings |

An app that treats permanent denial as a normal denial shows a request dialog that never appears, leaving the user pressing a button that does nothing. Ask at the moment the feature needs the permission, not on startup, and keep the app usable in a reduced form when the answer is no.

Rules:

- Create a folder only when it has real content.
- Theme, tokens and visual components live in the design system package, not in `core/`.
- `core/providers/` is not a dumping ground: a provider lives next to the class it provides.
- Every third-party platform SDK is wrapped here. Features never import a platform package directly.

## `features/`

One folder per functional module. Identical internal shape everywhere:

```text
feature/
├── data/
│   ├── data_sources/
│   ├── models/
│   ├── providers/
│   └── repositories/
├── domain/
│   ├── entities/
│   └── repositories/       # contracts only
└── presentation/
    ├── providers/
    ├── screens/
    ├── view_models/
    └── widgets/
```

Create only the folders a feature actually needs. Group related concerns into one feature when they share the same data source and repositories instead of splitting into thin modules.

## Layer flow

```text
Screen → ViewModel → Repository contract → Repository impl → Data source → Platform/DB/Storage
```

- UI never touches repositories, data sources, database, storage or platform SDKs directly.
- ViewModels depend on contracts, never on implementations.
- Cross-feature access goes through the other feature's domain contract, never its data sources or widgets.

## Use cases

There is no default `use_cases/` folder. A ViewModel may call a repository contract directly.

Add a use case only when at least one holds:

- a real business rule lives in the operation;
- it composes several repositories/services;
- two or more ViewModels need the same action;
- the logic deserves isolated tests.

A class that only forwards one call to one repository is not a use case. Delete it.

When one does clear the bar, it lives in the feature's `domain/`, beside the entities and contracts it composes, as one file per operation named after the operation (`create_backup.dart`, `restore_backup.dart`). It is domain logic, so it must not import anything from `data/` or `presentation/`. A `use_cases/` subfolder is worth creating only once there are enough of them that the folder listing is hard to read; three files do not qualify.

## Abstractions

Write an `abstract interface class` when:

- the implementation depends on the platform (audio, camera, location, permissions, filesystem);
- tests need a substitute;
- more than one implementation genuinely exists.

Do not write one for a single in-process implementation that will never be swapped.

## Dependency injection placement

- Global dependencies: in `core/`, in a provider file next to the class it provides.
- Feature dependencies: inside the feature, under `data/providers/`.
- Classes and their DI providers live in separate files, except generated ViewModel providers, which stay in the ViewModel file.

```text
core/storage/
├── key_value_storage.dart          # contract
├── shared_preferences_storage.dart # implementation
└── storage_providers.dart          # providers

features/<feature>/data/
├── data_sources/<x>_local_data_source.dart
├── data_sources/<x>_local_data_source_impl.dart
└── providers/<feature>_data_providers.dart
```

## Barrels

Allowed for public component groups, named after the folder (`buttons/buttons.dart`).

Never create a barrel:

- for a single-file folder;
- for internal implementations;
- for repositories or data sources;
- when it can introduce an import cycle;
- as one global file exporting the whole project.

The only whole-package barrel is the design system package entry point.

## Generated code

- `.g.dart`, `.freezed.dart`, `.drift.dart` sit next to their source file.
- `gen/` holds generated asset and font references.
- Generated files are never edited by hand and are excluded from the analyzer where the generator does not emit its own ignore header.

## Anti-patterns

- Empty folders created "to follow the structure".
- Pass-through use cases, services or wrappers.
- Interfaces with one implementation and no substitution need.
- Business rules inside widgets, or `BuildContext` inside ViewModels.
- Models duplicating entities field-for-field with no serialization difference.
- Features importing another feature's `data/` or `presentation/`.
- Abstractions for functionality that does not exist yet.

## Checklist for a new feature

1. Does it belong in an existing feature? Prefer growing one over creating a thin module.
2. Define entities and repository contracts in `domain/`.
3. Implement data sources and repositories in `data/`, expose them via feature providers.
4. Build the ViewModel over the contracts; keep screens dumb.
5. Add a use case only if it clears the bar above.
6. Add tests alongside: repository, ViewModel, key widgets.
