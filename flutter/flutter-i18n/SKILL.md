---
name: flutter-i18n
description: Internationalization for Flutter apps with flutter_localizations, intl and ARB files: setup, message authoring, plurals and placeholders, locale switching and formatting. Use when adding user-facing text, adding a locale, formatting dates/numbers/durations, or reviewing code for hardcoded strings.
license: MIT
---

# Flutter Internationalization

Every user-facing string comes from ARB files. A literal string in a widget is a bug.

## Setup

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: any

flutter:
  generate: true
```

```yaml
# l10n.yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
nullable-getter: false
```

```text
lib/l10n/
├── app_en.arb        # base locale
├── app_es.arb
├── app_pt_BR.arb
└── app_zh.arb
```

English is the base locale; every other file is a translation of it. Wire `localizationsDelegates` and `supportedLocales` in the root app widget.

## Writing messages

```json
{
  "itemCount": "{count, plural, =0{No items} =1{1 item} other{{count} items}}",
  "@itemCount": {
    "description": "Number of items in the current collection",
    "placeholders": { "count": { "type": "int" } }
  }
}
```

Rules:

- Key by meaning, not by screen: `deleteConfirmation`, not `settingsScreenText3`.
- Always fill `description`; it is the only context a translator gets.
- Use ICU plurals and selects; never concatenate fragments to build a sentence, since word order differs per language.
- Pass values as placeholders with explicit types; do not interpolate in Dart before passing.
- Keep punctuation inside the message.

## Formatting

Dates, numbers, durations, percentages and counts go through `intl` with the active locale, never manual `toString()` or hand-rolled padding.

```dart
DateFormat.yMMMd(locale).format(date);
NumberFormat.decimalPattern(locale).format(value);
```

Duration formatting has no `intl` helper: write one shared formatter and reuse it everywhere so the app never mixes styles.

## Locale switching

- The selected locale is user preference: persist it and apply it through the root app widget's `locale`.
- Default to the system locale on first run, falling back to the base locale when unsupported.
- Text rendered outside the widget tree (notifications, platform media metadata, share sheets, home-screen widgets) must also use the selected locale, not the system one.
- Layout must survive language switching: no fixed-width containers sized for one language, and support RTL if a supported locale requires it.

## In the design system package

The UI package never imports the app's localization; components receive text as parameters. The reasoning and the rest of the package boundary: `flutter-design-system`.

## Quality

- Enable `use_build_context_synchronously`-safe access: read `AppLocalizations.of(context)` before an `await`, not after.
- Keep every ARB file with the same key set; a missing key silently falls back to the base language.
- Check in CI that translations are complete and that no source file contains a user-facing literal.
- Do not describe capabilities the product does not have. Copy is part of the product contract, not filler.
