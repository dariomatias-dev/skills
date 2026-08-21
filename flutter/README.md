# Flutter Skills

Skills for building production Flutter apps: feature-first structure, MVVM over a simplified Clean Architecture, Riverpod, typed routing, a packaged design system, and a real test/CI setup.

They are project-agnostic: no app-specific names, entities or domains.

| Skill | Use it for |
| --- | --- |
| [flutter-architecture](flutter-architecture/) | Project structure, layers, feature anatomy, where a file belongs |
| [flutter-code-style](flutter-code-style/) | Naming, immutability, comments, widget composition, quality gates |
| [flutter-state-riverpod](flutter-state-riverpod/) | ViewModels, providers, DI, lifecycle pitfalls, rebuild control |
| [flutter-navigation](flutter-navigation/) | go_router + go_router_builder, navigators, shells, redirects |
| [flutter-design-system](flutter-design-system/) | UI package, tokens, theme, state/feedback components, motion, a11y |
| [flutter-data-layer](flutter-data-layer/) | Repositories, data sources, database, migrations, ids, errors |
| [flutter-testing](flutter-testing/) | Unit, widget, golden and integration tests, fakes and overrides |
| [flutter-i18n](flutter-i18n/) | ARB files, plurals, formatting, locale switching |
| [flutter-project-setup](flutter-project-setup/) | SDK pinning, lints, codegen, assets, CI/CD, release artifacts |
| [flutter-release-notes](flutter-release-notes/) | Store listing text for a release, per-language budget, what to omit |

## Reading order for a new project

1. `flutter-project-setup`: scaffold, tooling, CI.
2. `flutter-architecture`: structure and layer rules.
3. `flutter-design-system`: UI package and tokens.
4. `flutter-state-riverpod` + `flutter-navigation`: app wiring.
5. `flutter-data-layer`: persistence.
6. `flutter-i18n` and `flutter-testing`: applied continuously, not at the end.
7. `flutter-release-notes`: when a build is ready to publish.

## Boundaries between skills

Each rule lives in exactly one skill:

- Structure and layer decisions → `flutter-architecture`
- Language-level conventions → `flutter-code-style`
- Anything visual → `flutter-design-system`
- Anything persisted → `flutter-data-layer`
- Anything provider-shaped → `flutter-state-riverpod`
- Anything route-shaped → `flutter-navigation`
- Anything user-facing text → `flutter-i18n`
- Anything asserted about behavior → `flutter-testing`
- Anything outside `lib/` (tooling, lints, codegen, CI) → `flutter-project-setup`
- Anything the store shows to a user → `flutter-release-notes`
