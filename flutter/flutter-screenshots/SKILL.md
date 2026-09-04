---
name: flutter-screenshots
description: "Automate app screenshots in Flutter with flutter drive and integration_test: driver wiring, surface conversion, deterministic state, multiple locales and the capture script. Use when generating README or store listing images, adding a screenshot target, or fixing a capture that hangs, comes out blank or differs between runs."
license: MIT
---

# Screenshot Automation

Marketing images taken by hand go stale after the first redesign and are never consistent across locales. Driving the app produces them reproducibly.

This covers capture for README and store listings. Golden tests, which compare pixels to catch regressions, are a different tool covered by `flutter-testing`. The data shown belongs to `flutter-seed-data`.

## The three pieces

```text
test_driver/integration_test.dart      # receives bytes, writes files
integration_test/screenshot_test.dart  # drives the app, requests captures
scripts/screenshot.sh                  # runs the pair against a device
```

The driver is the half that writes to disk. Without it the capture succeeds and produces nothing:

```dart
Future<void> main() async {
  await integrationDriver(
    onScreenshot: (name, bytes, [args]) async {
      final file = File('screenshots/$name.png');
      await file.create(recursive: true);
      await file.writeAsBytes(bytes);
      return true;
    },
  );
}
```

Note the import: `integration_test_driver_extended.dart`, not the plain driver, which has no `onScreenshot` hook.

Run it with `flutter drive`, not `flutter test`. The latter has no driver process, so nothing receives the bytes.

## Two mandatory calls

**`convertFlutterSurfaceToImage`.** On Android the Flutter surface cannot be read back directly, and the capture returns a blank or black image. Call it on the binding once, after the app is running and before the first capture.

**Frame pumping instead of `pumpAndSettle`.** Any looping animation, a pulsing indicator, a carousel, a progress spinner, means the tree never settles and the call hangs until the test times out. Advance a fixed number of frames:

```dart
Future<void> settle() async {
  for (var i = 0; i < 30; i++) {
    await tester.pump(const Duration(milliseconds: 100));
  }
}
```

The fixed count also makes captures reproducible: an animation is always at the same point.

## Deterministic state

A screenshot run must produce identical output every time, or every run shows a diff and the images become noise in review.

Pin everything the image depends on, before pumping the app:

- Theme mode, so a device in dark mode does not produce a light-mode listing.
- Seeded data, which `flutter-seed-data` covers making deterministic.
- Any onboarding or first-run flag, set to completed, so the capture does not start on a welcome screen.
- Providers overridden with the prepared database and preferences, the same way a widget test does it.

Anything read from the real device, the clock, the battery, the locale of the host, will differ between machines and between runs.

## Multiple locales

Cover every supported language as its own test case inside the same target, saving into `screenshots/<locale>/`.

One `flutter drive` invocation, one install, many locales. Restarting the app per language multiplies the slowest part of the run, the install, by the number of languages for no benefit.

## The script

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

DEVICE_ARGS=()
if [[ "${1:-}" != "" ]]; then
  DEVICE_ARGS=(-d "$1")
fi

rm -rf screenshots
mkdir -p screenshots

flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/screenshot_test.dart \
  --dart-define=SEED_ENABLED=true \
  "${DEVICE_ARGS[@]}"
```

- `set -euo pipefail` so a failed capture stops the run instead of leaving a half-updated folder.
- `cd` to the project root so the script works from any directory.
- Clear the output folder first, or a renamed screen leaves its old image behind forever.
- Accept an optional device id, defaulting to the only connected device.
- Keep the run in debug. Seeds are guarded on debug mode, so a release build silently produces screenshots of an empty app rather than failing.

## Choosing what to capture

- One image per screen the listing needs, in the order the store presents them, named so the order is obvious from the filename.
- Capture on one reference device and keep using it. Store listings expect consistent dimensions, and mixing devices produces images that do not line up.
- Show populated states. An empty list is the least persuasive image an app can lead with.
- Never capture a screen showing real personal data.

## Anti-patterns

- `flutter test` instead of `flutter drive`.
- The plain integration driver, whose entrypoint has no screenshot callback.
- Missing `convertFlutterSurfaceToImage`, producing blank images on Android.
- `pumpAndSettle` on a screen with a looping animation.
- Captures that depend on the host clock, host locale or device theme.
- Screenshots committed without regenerating them after a UI change, so the listing shows a version of the app that no longer exists.
- One app install per locale.
