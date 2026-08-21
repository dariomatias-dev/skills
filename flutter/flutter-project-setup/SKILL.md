---
name: flutter-project-setup
description: Bootstrapping and tooling for Flutter projects: SDK pinning, dependencies, analysis options, code generation, assets, CI/CD workflows and release artifacts. Use when starting a project, adding a local package, configuring lints or build_runner, or writing GitHub Actions pipelines for a Flutter app.
license: MIT
---

# Flutter Project Setup

Everything a project needs before feature work starts.

## SDK and dependencies

Pin the Flutter version per project in `pubspec.yaml`, and point the local version manager (FVM or equivalent) at that same constraint:

```yaml
environment:
  sdk: ^3.9.0
  flutter: 3.35.0
```

One pin, read by both sides: CI resolves it with `flutter-version-file: pubspec.yaml`, the developer machine resolves it through the version manager. A second pin stored somewhere else drifts from this one silently.

The versions above are an example; pin whatever the project is on. Dart 3.7 is the floor, since the wildcard parameters used in these skills (`(_, _) =>`) do not parse below it.

Keep dependency choices explicit in `pubspec.yaml` grouped by purpose, and prefer one library per responsibility. Reference stack for this project style:

| Purpose | Library |
| --- | --- |
| State management + DI | `flutter_riverpod` ^3.0.0 + `riverpod_annotation` |
| Navigation | `go_router` + `go_router_builder` |
| Local database | `drift` + `sqlite3_flutter_libs` |
| Key-value storage | `shared_preferences` |
| Localization | `flutter_localizations` + `intl` |
| Identifiers | `uuid` |
| Lints | `very_good_analysis` |
| Tests | `flutter_test`, `mocktail`, `integration_test` |
| Codegen | `build_runner`, `riverpod_generator`, `drift_dev`, `json_serializable` |

Add `freezed` only when it removes a meaningful amount of hand-written code; a `copyWith` on two fields does not justify it.

Never add a dependency for something the SDK already does well, and remove anything unused; an unused dependency is still a build cost and a supply-chain surface.

Codegen packages can pin conflicting `analyzer` version ranges against each other (a database generator and a router generator are a common pair to clash). When `pub get` refuses to resolve, follow the version `pub` itself suggests instead of guessing an older pin; it already computed the range every package in the project actually allows.

## Local packages

The design system (and any other reusable module) is a local package under `packages/`, wired as a path dependency:

```yaml
dependencies:
  app_ui:
    path: packages/app_ui
```

Each package has its own `pubspec.yaml`, `analysis_options.yaml` and `test/`, and must analyze and test independently.

## Analysis options

```yaml
include: package:very_good_analysis/analysis_options.yaml

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - "**/*.drift.dart"
    - lib/src/gen/**
  errors:
    invalid_annotation_target: ignore
```

The `**/*.g.dart` glob is what covers generators that emit no `ignore_for_file` header of their own (`go_router_builder` is the common one); generators that do emit a header would pass without it. The exclusion holds for `part` files too, so a generated part is not reported through its parent library.

Keep the package's options file consistent with the app's.

## Code generation

```bash
dart run build_runner build --delete-conflicting-outputs
dart run build_runner watch --delete-conflicting-outputs
```

- Generated files sit next to their source, and are never edited by hand. Placement rules: `flutter-architecture`.
- Commit generated files only if CI does not regenerate them. Pick one policy and apply it everywhere.

## Assets

```text
assets/
├── icons/
└── images/
```

Declare assets in `pubspec.yaml` and reference them through generated accessors rather than string paths. Fonts used by the design system are declared in that package's `pubspec.yaml`, not in the app root.

## Repository files

```text
LICENSE
README.md          # base language, with a language switcher at the top
README.<locale>.md # one per supported language
CHANGELOG.md
```

Pick a license explicitly (MIT is a reasonable default for open projects) and keep the changelog updated per release.

## Entry point

`main.dart` stays minimal: bind widgets, resolve dependencies that must exist before the first frame, and inject them into the root scope.

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = await SharedPreferencesStorage.create();

  runApp(
    ProviderScope(
      overrides: [keyValueStorageProvider.overrideWithValue(storage)],
      child: const App(),
    ),
  );
}
```

The root widget wires theme, router and localization, nothing else.

## Continuous integration

Run on pull requests and pushes to main branches:

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true
      - run: flutter pub get
      - run: flutter pub get --directory packages/app_ui
      - run: dart format --set-exit-if-changed .
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter analyze
      - run: flutter test
      - run: flutter test
        working-directory: packages/app_ui
      - run: flutter build apk --debug
```

Every step is a gate: formatting, generation, analysis of app and packages, tests including goldens, and a build that proves the project still compiles.

`--directory` is a `pub` option, so `flutter pub get --directory <path>` is valid while `flutter test --directory <path>` fails with `Could not find an option named "--directory"`. Run a package's tests through `working-directory` instead.

## Continuous delivery

Triggered by version tags (`v1.2.0`):

- build the release artifact;
- name it with the version;
- attach it to the workflow run and to a GitHub release.

Store signing material in repository secrets, never in the repo. Publishing to a store is a separate, deliberate workflow, never automatic from a tag unless the project explicitly wants that.

## Scripts

Development helpers live in `scripts/`. Anything a developer runs more than twice belongs there, documented in the README.

Two helpers most projects end up needing: populating a local database for development, covered by `flutter-seed-data`, and capturing store and README images, covered by `flutter-screenshots`.
