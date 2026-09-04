---
name: flutter-database
description: "Local relational database in Flutter with Drift: schema and index design, DAOs, transactions, reactive queries, and migrations that preserve user data. Use when creating or changing a table, writing a migration, debugging a slow or repeated query, or reviewing schema changes before a release."
license: MIT
---

# Local Database

The database is an engine behind the data layer. Which data belongs in it, and how repositories expose it, is covered by `flutter-data-layer`; this skill covers the engine itself.

Everything here exists because of one asymmetry: application code can be fixed in the next release, and a botched migration cannot. The data is already gone.

## Layout

```text
core/database/
├── app_database.dart
├── tables/
├── daos/
└── database_providers.dart
```

- One DAO per aggregate, not one per screen. A DAO shaped by a screen is rewritten every time the UI changes.
- Features never write SQL. They call repositories, which call DAOs.
- The database is provided once, through a provider. Opening a second connection to the same file invites locking errors.
- A raw, byte-for-byte backup of the file (a `VACUUM INTO`-style copy) and its restore path are covered by `flutter-data-layer`; restoring one replaces the provider's backing store, so the connection must be reopened rather than reused.

## Schema

| Decision | Rule |
| --- | --- |
| Nullability | Declare it deliberately. A nullable column that is never null becomes a null check in every read forever |
| Foreign keys | Declare them with an explicit cascade behavior, and enable enforcement; SQLite ignores foreign keys unless the pragma is on |
| Indexes | Index what you filter, sort and join on. An unindexed lookup on a growing table degrades silently |
| Composite indexes | Column order matters: an index on (a, b) serves a query filtering on a, but not one filtering only on b |
| Enums | Store a stable string or integer, never the Dart index. Reordering the enum silently rewrites the meaning of existing rows |
| Dates | One representation, chosen once, stored in UTC. Mixed epoch and text columns make queries and comparisons unreliable |

Indexes are not free: they cost write time and space. Add them for a query that exists, not for one that might.

## Migrations

Every schema change after the first release ships a migration. Bumping `schemaVersion` without one fails silently for users with the old database installed, and their app breaks on the query that expects the new column.

```dart
@override
MigrationStrategy get migration => MigrationStrategy(
  onCreate: (m) => m.createAll(),
  onUpgrade: (m, from, to) async {
    if (from < 2) await m.addColumn(items, items.archivedAt);
    if (from < 3) await m.createIndex(itemsByStatus);
  },
);
```

| Rule | Reason |
| --- | --- |
| Sequential `if (from < n)` blocks, never `if (from == n)` | A user can upgrade from any older version, including one several releases behind |
| Each step additive where possible | Adding a column is safe; changing a type is a table rewrite |
| A new non-null column needs a default | Existing rows have no value for it, and the migration fails without one |
| Never edit a migration that has shipped | Devices that already ran it will not run it again, so the fix must be a new step |
| Test every path, not just the latest | Generate schema fixtures per version and assert an upgrade from each one |

Dropping or retyping a column in place depends on the SQLite version bundled with the device, which you do not control, so treat those changes as a create-copy-drop-rename cycle everywhere. Drift's table migration helper performs it; the important part is that it is a full table rewrite, so it is slow on large tables and must be inside a transaction.

Before a destructive change, decide what happens to the data that does not fit. Silently discarding rows during a migration is a data loss bug that no test catches unless you write it.

## Queries

- Expose `watch` queries for anything the UI displays. A stream that updates on write removes the entire class of stale-screen bugs.
- Select the columns you need. `SELECT *` on a table with a large blob loads it on every row.
- Avoid the N+1 pattern: one query for a list followed by one query per item. Use a join or a single batched lookup.
- Use transactions for multi-table writes so a failure halfway does not leave half the change committed.
- Use batch inserts for bulk work. Inserting a thousand rows one statement at a time is dominated by transaction overhead. Choosing a batch size for a long import that also reports progress: `flutter-performance`.
- Paginate at the query level with limit and offset or a cursor, never by loading everything and slicing in Dart.

## Testing

- Run against an in-memory database, created fresh per test.
- Test migrations with the generated schema fixtures, upgrading from each released version and asserting both the resulting schema and that existing rows survived.
- Assert on data through the DAO, not by reading raw rows, so the test breaks when the DAO contract breaks.

The wider strategy, including what deserves a test at all, is covered by `flutter-testing`.

## Anti-patterns

- `schemaVersion` bumped with no matching migration step.
- `if (from == n)` chains that skip users on older versions.
- Editing a migration that shipped, instead of adding a new one.
- Storing an enum by its Dart index.
- Local timestamps mixed with UTC in the same column.
- SQL in a feature, or a DAO returning raw maps.
- A migration that drops a column without deciding what happens to its data.
- Indexes added defensively for queries that do not exist.
