---
name: flutter-seed-data
description: Populate a Flutter app's local database with development data: seed structure, the release-build guard, idempotency, and running seeds as a standalone script without a device. Use when adding sample data for local development, building a demo state, preparing data for screenshots, or reviewing seed code for safety.
license: MIT
---

# Seed Data

Seeds fill a local database with realistic data so a developer, a designer or a screenshot run sees a populated app instead of an empty state.

They are development tooling. The rules below exist because a seed that escapes into a real build writes to a real user's database.

## Safety first

| Rule | Reason |
| --- | --- |
| Seeds never run unless explicitly enabled | The default must be off, so forgetting the flag is harmless rather than destructive |
| Gate on a compile-time flag, not a runtime setting | A runtime toggle ships the seed code and its data in the release binary |
| Refuse to run in release mode, even when enabled | Two independent guards, because one of them will eventually be misconfigured |
| Never seed a remote backend | A seed pointed at a shared environment is other people's data |

```dart
const seedEnabled = bool.fromEnvironment('SEED_ENABLED');

if (seedEnabled && kDebugMode) {
  await runDevSeeds(database);
}
```

Enabled per run, never committed as a default:

```bash
flutter run --dart-define=SEED_ENABLED=true
```

Tree shaking removes the seed path from a build where the constant is false, so the sample data does not ship.

## Structure

One seed per aggregate, each owning its own data, behind a common contract:

```dart
abstract interface class Seed {
  Future<void> run();
}
```

- A runner executes them in dependency order: a seed that references another entity runs after the one that creates it.
- Feature-specific seeds live with their feature, in `data/seeds/`. The contract and the runner are shared infrastructure in `core/`.
- Seeds write through the same DAOs and repositories as the app. A seed with its own SQL drifts from the schema and stops failing when a migration is missing.

## Idempotency

Running twice must not double the data.

- Check before inserting, or clear the seeded tables first. Decide which, and apply it consistently.
- Use fixed identifiers for seeded records so a rerun replaces rather than appends, and so a screenshot run produces the same output every time.
- Seeded records are indistinguishable from real ones to the rest of the app. If they need to be recognizable, that is a flag on the row, not a naming convention in the text.

## Standalone execution

A seed that runs only inside the app forces a full launch cycle for a data change. Make it runnable as a plain Dart script:

```bash
dart run scripts/seed.dart
```

Desktop and CI have no SQLite binding by default, so the script initializes the FFI implementation before touching the database. This is what makes seeding possible with no emulator, no device and no build.

## Writing the data

- Realistic volume. Three records hide pagination bugs, overflow and empty-space problems that fifty would expose.
- Realistic content: long names, accented characters, the longest supported language, empty optional fields.
- Deterministic. Inject the clock and the id generator so dates and identifiers are stable, otherwise screenshots differ on every run.
- Dates relative to a fixed reference rather than to now, or the data drifts out of the interesting range as time passes.
- Cover the states the UI must render: complete and incomplete, read and unread, overdue and upcoming. Seeds exist to make edge cases visible, not to look tidy.

## Anti-patterns

- Seeds guarded only by a comment, or by an `if` on a variable someone can flip.
- Seed code importing test packages, which pulls them into the app's dependency graph.
- A seed that clears the database unconditionally at startup.
- Data so uniform that every list item is the same width.
- Personal or copyrighted content used as sample data, which then appears in a screenshot in the store listing.
- Seeds maintained separately from the schema, so they break silently after a migration.
