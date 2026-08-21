---
name: flutter-error-handling
description: Catch and report failures at the app boundary in Flutter: FlutterError.onError, PlatformDispatcher.onError, release error widgets, logging discipline and what to do with an unrecoverable state. Use when wiring crash reporting, deciding how a failure surfaces to the user, reviewing catch blocks, or auditing logs for sensitive data.
license: MIT
---

# Error Handling

Every failure ends in one of three places: handled locally, shown to the user, or reported and swallowed. The failure with no place is the one that becomes a white screen.

Converting library exceptions into typed application exceptions is covered by `flutter-data-layer`. The visual components for error and retry states are covered by `flutter-design-system`. This skill covers the boundary: what catches what escapes.

## The three entry points

Flutter delivers uncaught errors through separate channels, and wiring only one leaves the others silent.

```dart
void main() {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (details) {
    // errors thrown inside the framework: build, layout, paint
    reportError(details.exception, details.stack);
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    // uncaught asynchronous errors outside the framework
    reportError(error, stack);
    return true;
  };

  runApp(const App());
}
```

| Channel | Catches |
| --- | --- |
| `FlutterError.onError` | Errors thrown during build, layout and paint |
| `PlatformDispatcher.instance.onError` | Uncaught async errors, including futures with no `catchError` |
| Isolate error listener | Errors in isolates you spawn, which neither of the above sees |

Returning `true` from `onError` marks the error handled and stops the default print. Returning `false` lets it propagate to the platform, which on release usually means a crash.

## The release error widget

By default a build failure renders the grey error box in debug and a plain grey area in release. Replace it so the user sees something intelligible:

```dart
ErrorWidget.builder = (details) => const AppErrorScreen();
```

Never show a stack trace or exception message in release. It leaks internal structure, and it means nothing to the person reading it.

## Choosing where a failure is handled

| Failure | Handling |
| --- | --- |
| Expected and recoverable, such as a validation error or empty result | Handled locally, surfaced inline, never reported |
| Expected but blocking, such as no connectivity | Error state with a retry action, not reported as a crash |
| Unexpected but contained, such as one widget failing to render | Reported, degraded region, rest of the screen keeps working |
| Unexpected and unrecoverable, such as a corrupt database on startup | Reported, then an explicit recovery path: clear local state and restart |

An error the user cannot act on should not offer a retry button. Retry that always fails is worse than an honest message.

## Catching

- Never write a bare `catch (_)` that returns null or an empty list. It converts a bug into an empty screen that nobody reports.
- Catch specific types. Catching `Exception` to log and rethrow is acceptable; catching everything to continue is not.
- Preserve the stack trace: `catch (error, stackTrace)` and pass both on. A report without a stack is close to useless.
- Rethrow with `rethrow`, never `throw error`, which resets the stack to the catch site.
- Never catch inside a widget's `build`. The error belongs to whatever produced the data, not to the frame that displayed it.

## Logging

- Log at boundaries: request sent, request failed, migration ran, session expired. Not every function entry.
- Never log tokens, passwords, full request bodies, personal data or precise location. Logs reach crash reports and support tickets.
- Log the failure with its type and context, not a rewritten string. `Failed to load items` without the cause costs another release to diagnose.
- Strip or downgrade debug logging in release builds; verbose logging is a measurable performance cost and an information leak.
- Use one logging abstraction behind a provider so output can be silenced in tests and redirected in release.

## Reporting

- Report unexpected failures only. A handled validation error reported as a crash trains everyone to ignore the dashboard.
- Attach non-sensitive context: screen, action, entity identifier. Not the entity contents.
- Deduplicate by cause, not by message, so an error with a varying id is not counted as thousands of distinct issues.
- Ask before enabling reporting where consent is required, and honor the answer for the whole session.

## Anti-patterns

- `try { ... } catch (_) {}` with an empty body.
- Only `FlutterError.onError` wired, leaving async errors invisible.
- Stack traces or raw exception text shown to users in release.
- The same failure both reported and shown as an error state, producing double noise for one event.
- Logging that includes credentials or full payloads.
- Crash reporting initialized after `runApp`, missing every startup failure.
- A global handler that swallows errors in debug, hiding them from the developer who could fix them.
