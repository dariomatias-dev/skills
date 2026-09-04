---
name: flutter-data-layer
description: "Data layer for Flutter apps: repositories, data sources, local database with Drift, key-value storage, entities vs models, identifiers, error mapping, and user-facing backup/export/import. Use when persisting data, designing a repository, writing a database schema or migration, choosing where data belongs, wrapping a platform SDK, or building a backup or restore flow."
license: MIT
---

# Flutter Data Layer

Data flows one way: repository contract (domain) → repository implementation (data) → data source → storage engine. Nothing above the repository knows which engine is underneath.

## Responsibilities

| Piece | Layer | Job |
| --- | --- | --- |
| Entity | `domain/entities` | Immutable core representation, independent of persistence and widgets |
| Repository contract | `domain/repositories` | The vocabulary the app uses to ask for data |
| Repository impl | `data/repositories` | Orchestrates data sources, maps models ↔ entities, maps errors |
| Data source | `data/data_sources` | One storage engine or platform API, nothing else |
| Model | `data/models` | Serialization shape, only when it differs from the entity |

If a model is a field-for-field copy of an entity, delete it and persist the entity directly.

## Repositories

- Contracts expose domain language (`findAll`, `save`, `remove`), never SQL, queries or platform terms.
- Return entities or domain results, never raw rows, `Map<String, dynamic>`, or library types.
- Keep them thin: orchestration and mapping, not business rules that belong in a use case.
- Return `Stream` when the UI must follow changes (a reactive database query), `Future` for one-shot reads.

## Choosing a storage engine

| Data | Engine |
| --- | --- |
| Small scalar preferences, flags, last-session pointers | key-value storage |
| Collections, relations, anything queried, sorted or joined | local relational database |
| Large binaries (images, audio, exports) | filesystem, with the path referenced in the database |
| Credentials, tokens, encryption keys | platform secure storage, never plain key-value |

Never store a collection in key-value storage, and never store a blob in the database.

## Secrets

Plain key-value preferences are not encrypted. On Android they are a world-readable-by-root XML file, and on a rooted or backed-up device their contents are recoverable. A session token written there is a credential leak waiting for the right device.

Secrets go through the platform keystore, behind their own contract so the storage mechanism stays swappable and fakeable:

```dart
abstract interface class SecureStorage {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
  Future<void> delete(String key);
}
```

- Keep secrets out of the local database as well; encrypting the database is a separate decision and does not make it the right home for a token.
- Sign-out clears every secret, not only the access token. A refresh token that survives sign-out re-authenticates the previous user.
- Secure storage can fail or return null after an OS restore, a keystore reset or a biometric change. Treat that as a signed-out session, not as a crash.
- API keys compiled into the app are readable by anyone who unpacks it. Inject them at build time to keep them out of source control, and treat any key that must stay secret as a server responsibility.

## Key-value storage

Wrap the platform preference API behind a minimal contract:

```dart
abstract interface class KeyValueStorage {
  String? getString(String key);
  Future<void> setString(String key, String value);
  bool? getBool(String key);
  Future<void> setBool(String key, {required bool value});
  Future<void> remove(String key);
}
```

- Features never import the preferences package directly.
- Keys live in one constants file, never inlined at call sites.
- The contract exposes only the operations the project actually uses.

## Local database

Schema design, indexes, transactions, reactive queries and migrations are covered by `flutter-database`. From the data layer's side the rule is simply that features never write SQL: they call repositories, which call DAOs.

## Identifiers

- Persisted entities use a generated identifier (UUID v7 is a good default: sortable by creation time).
- Generation is centralized behind an injectable contract so tests can produce deterministic ids.
- Records derived from an external source (filesystem, remote API, platform index) also store a **stable source key**. Re-scanning matches on the source key, so user-created data (tags, collections, history) survives re-indexing.

## Reconciliation with an external source

When rebuilding an index from a source that can change underneath the app:

1. Keep the identifiers of records already known (matched by source key).
2. Insert records that are new.
3. Mark missing records as absent rather than deleting them.
4. Preserve everything users created on top of them.
5. Delete permanently only after the user confirms.

Absent records must be visibly flagged in the UI and must never break flows that reference them.

## Error handling

```text
core/errors/
└── app_exception.dart
```

- Library and platform exceptions are converted to app exceptions at the data source or repository boundary; they never leak into ViewModels or widgets.
- Use distinct types for distinct handling (permission failure, missing file, storage failure, decoding failure), since each drives a different UI state and message.
- Carry a cause and stack trace for logging, and keep user-facing text in localization, not in the exception.
- Never `catch` and return `null` to hide a failure.

## Caching

Cache derived expensive artifacts (thumbnails, extracted metadata, parsed documents) on disk with the source key as identity, and expose a way to clear the cache. Never cache in a static global; put it behind a provider so it can be replaced in tests.

## Anti-patterns

- ViewModels calling data sources or DAOs directly.
- SQL strings inside a feature.
- Models and entities duplicated with no serialization difference.
- Business rules inside a repository implementation.
- Storing JSON blobs in preferences to avoid writing a table.
- Schema changes without a migration.
