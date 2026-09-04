---
name: flutter-networking
description: "Remote data access in Flutter: HTTP client behind a contract, timeouts and cancellation, retry policy, status code to exception mapping, token refresh without stampedes, DTO parsing and pagination. Use when calling an API, designing a remote data source, handling request failures or authentication, or reviewing networking code."
license: MIT
---

# Networking

Remote access is one more data source behind a repository. Nothing above the repository knows a request was made.

Local persistence and the typed exception hierarchy are covered by `flutter-data-layer`; this skill covers what is specific to talking to a server.

## The client is a dependency, not a global

Wrap the HTTP library behind a contract, the same way every other platform dependency is wrapped:

```dart
abstract interface class HttpClient {
  Future<JsonMap> get(String path, {JsonMap? query, CancellationToken? cancel});
  Future<JsonMap> post(String path, {Object? body, CancellationToken? cancel});
}
```

- Features never import the HTTP library. Swapping it, or faking it in tests, must not touch a single data source.
- The contract exposes no type from the chosen library, cancellation included. A parameter typed with the library's own cancellation class puts the dependency back into every caller the contract was written to protect.
- One configured instance, provided by a provider, holding base URL, default headers, timeouts and interceptors. A client constructed per call leaks connections and loses connection reuse.
- Pick one library and use it everywhere. Mixing `package:http` for some calls and a heavier client for others means two timeout configurations, two error shapes and two places to add a header.

## Timeouts

Two separate limits, and both are needed:

| Limit | Guards against |
| --- | --- |
| Connect timeout | A host that never completes the handshake |
| Receive timeout | A connection that opens and then stalls mid-body |

A request with no timeout hangs until the OS gives up, which can be minutes. The UI shows a spinner for that entire time, and the user's only recourse is to kill the app.

Long uploads and downloads need their own longer values, set per request rather than by raising the global default.

## Cancellation

Every request started from a screen must be cancellable, and cancelled when the screen goes away. Otherwise a user who opens and leaves a list five times has five in-flight requests competing for bandwidth, and the last response to arrive wins regardless of which screen is showing.

Tie the cancellation token to the provider or controller lifecycle so disposal cancels the work. Cancellation is not an error: it must not surface as a failure state or a logged exception.

## Retry

Retry is not a default. It is a decision per request.

| Rule | Reason |
| --- | --- |
| Only idempotent requests | Retrying a payment or a create endpoint can duplicate the operation |
| Only transient failures: timeouts, connection loss, 502/503/504 | A 400 or 422 returns the same result every time; retrying wastes time and hides the real error |
| Exponential backoff with jitter | Constant-interval retries from many clients converge into a synchronized wave against a server that is already struggling |
| A hard attempt cap | Unbounded retry turns a brief outage into a battery drain and an unresponsive screen |
| Never retry a 401 as a network failure | It means the token needs refreshing, which is a different flow |

An endpoint that is not idempotent but must survive retries needs an idempotency key agreed with the server, not client-side cleverness.

## Status codes to exceptions

Map at the client boundary so no layer above ever inspects a status code:

| Status | Meaning for the app |
| --- | --- |
| 400, 422 | Invalid request or validation failure. Carry the server's field errors, they belong in the form |
| 401 | Credentials missing or expired. Triggers refresh, then sign-out if refresh fails |
| 403 | Authenticated but not allowed. Never resolved by retrying or refreshing |
| 404 | Absent resource. Frequently a normal empty state, not an error screen |
| 409 | Conflict. Usually needs a user decision, not a retry |
| 429 | Rate limited. Respect `Retry-After` if present instead of guessing |
| 5xx | Server failure. Retryable, and the only class where a generic message is honest |

Distinguish "no connectivity" from "server returned an error". They read the same in a naive catch and need different messages and different actions.

## Authentication

Attach the token in one interceptor, never per call site.

**Refresh must be single-flight.** When a screen fires several requests and the token has expired, every one of them returns 401 at roughly the same moment. Without a guard, each triggers its own refresh: the server sees a burst of refresh calls, all but one of the rotated tokens are invalidated, and the user is signed out at random. Hold one refresh future, have every waiting request await that same future, then replay them with the new token.

Other rules:

- One retry after a successful refresh. If the replayed request 401s again, sign out.
- Refresh failure is terminal: clear the session, clear cached user data, and route to the entry point.
- Never write tokens to logs, crash reports or analytics.
- Where tokens are stored, and what sign-out must clear, is covered by `flutter-data-layer`.

## Parsing

- DTOs live in the data layer and exist to mirror the wire format, including its inconsistencies. The entity stays clean; the mapping absorbs the mess.
- Never let a `Map<String, dynamic>` travel above the data source.
- Treat every field as untrusted. A null in a field the contract promised is a parsing failure with a clear message, not a crash three screens later.
- Parse large payloads off the main thread. Decoding a multi-megabyte response on the UI isolate drops frames; move it with `compute` and measure before assuming it is needed.
- An unknown enum value from the server must degrade to a documented fallback rather than throw. Servers add cases without asking.

## Pagination

- Cursor-based paging survives insertions during scroll; offset paging silently repeats or skips items when the underlying list changes.
- Keep the page request in the repository, not in the widget's scroll listener.
- A failed page load is a retry affordance on that page, not an error screen replacing the results already on screen.
- Guard against firing the same page twice when the scroll threshold triggers on consecutive frames.

## Testing

Tests never touch the network. The client contract is faked, and error paths are exercised by returning failures from the fake. Strategy and test doubles are covered by `flutter-testing`.

## Anti-patterns

- The HTTP library imported inside a feature.
- Requests with no timeout, or no cancellation tied to the screen lifecycle.
- `catch (_) { return null; }` collapsing every failure into an empty state.
- Retry on everything, including validation errors and non-idempotent writes.
- Refresh logic duplicated across call sites instead of one interceptor with single-flight.
- Status codes checked in a ViewModel or a widget.
- Base URL or API keys hardcoded in Dart instead of injected build configuration.
- Logging full request and response bodies in release builds.
