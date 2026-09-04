---
name: flutter-project-setup
description: "Bootstrapping and tooling for Flutter projects: SDK pinning, dependencies, dependency-update automation, analysis options, code generation, assets and platform manifests. Use when starting a project, adding a local package, configuring lints or build_runner, setting up Dependabot or Renovate, or declaring a permission or background mode in AndroidManifest.xml or Info.plist. Pipeline jobs and CI checks are covered by flutter-ci."
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

## Dependency updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pub"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pub"
    directory: "/packages/app_ui"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot is configuration, not a pipeline job: it opens pull requests, it does not run checks or gate a merge. One entry per `pubspec.yaml` in the project (root and every local package), plus one for the workflow files themselves. The gate that decides whether an update PR is safe to merge is the normal CI run, covered by `flutter-ci`.

Renovate is the alternative, configured through `renovate.json` instead of a GitHub-specific file; pick either, not both. Its advantage over Dependabot here is `packageRules`: a project with dependencies pinned for a documented reason (an analyzer version conflict, an EOL package, a native toolchain ceiling) can disable or group updates for exactly those packages by name, instead of relying on someone noticing the pin and closing the PR by hand every time it recurs.

Whichever tool is used, cross-reference it with the reasoning: a pin justified in a dependency-notes document (`markdown-architecture-doc`) but not reflected in the automation config still generates a pull request nobody should merge, over and over.

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

A strict lint set will disagree with decisions the project made deliberately, and the fix is to disable the rule once with the reason recorded, not to bend the code:

```yaml
linter:
  rules:
    # Single-method contracts exist so tests can substitute the platform
    # implementation. They are deliberate, not accidental abstractions.
    one_member_abstracts: false
```

That specific rule is worth knowing about before it fires: `very_good_analysis` flags an abstract class with one member, which is exactly the shape of the platform contracts a testable app needs. Deleting the contract to satisfy the lint removes the seam the tests depend on.

Treat every disabled rule the same way. An `analysis_options.yaml` with silent exclusions is a file nobody can audit later.

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

## Platform manifests

Every OS-level capability the app uses (camera, location, background audio, notifications, media library access) needs a matching declaration on each platform, or the feature fails at runtime with no compile-time warning:

| Platform | File | Declares |
| --- | --- | --- |
| Android | `android/app/src/main/AndroidManifest.xml` | Permissions, foreground service types, exported components |
| iOS | `ios/Runner/Info.plist` | Usage description strings (one per permission, shown to the user), background modes |

- One permission, one line, one reason: each entry should trace back to a single feature. A permission with no corresponding runtime request in the Dart code raises the app's risk profile for no functional benefit, and app store review can reject it on that basis alone.
- iOS usage description strings are user-facing copy, not internal documentation: write what the person granting the permission actually needs to know, and localize them the same way any other user-facing string is localized.
- A build tool constraint that lives in the native project (a `compileSdk` floor forced by a plugin, a minimum OS version) belongs in a comment in that native file, cross-referencing the CI workflow env var or variable that must move with it. The two drift silently otherwise: a plugin bump raises the floor, the native file is updated, and the pipeline keeps building against the old one until a version-mismatch failure with no obvious cause.
- A capability that keeps running while the app is backgrounded (audio playback, location tracking, a long download) needs the corresponding platform declaration (a foreground service type on Android, a background mode on iOS) in addition to the runtime permission; the permission alone does not keep the process alive.

## Repository files

```text
LICENSE
README.md          # base language, with a language switcher at the top
README.<locale>.md # one per supported language
CHANGELOG.md
docs/
├── architecture.md
├── contributing.md
└── security.md
```

Pick a license explicitly (MIT is a reasonable default for open projects) and keep the changelog updated per release. Readme structure is covered by `markdown-readme`; the architecture document by `markdown-architecture-doc`; contributing and security by `markdown-community-health`.

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

The pipeline, the local command that must run the same checks, the generation and coverage gates, and tag-triggered releases are covered by `flutter-ci`.

## Scripts

Development helpers live in `scripts/`. Anything a developer runs more than twice belongs there, documented in the README.

Three helpers most projects end up needing: the verification gate, covered by `flutter-ci`, populating a local database for development, covered by `flutter-seed-data`, and capturing store and README images, covered by `flutter-screenshots`.
