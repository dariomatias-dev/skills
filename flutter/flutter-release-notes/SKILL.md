---
name: flutter-release-notes
description: Write store release notes for a mobile app release: what to include, the user-perceived benefit test, section structure, per-language character budget and the Google Play language tag format. Use when preparing a release, writing "what's new" text, converting a changelog or commit log into store copy, or reviewing release notes before publishing.
license: MIT
---

# Release Notes

Store release notes describe what changed **for the person using the app**. They are not a changelog, and they are not a summary of the work done.

Scope is the listing text. The release pipeline that produces the build is covered by `flutter-project-setup`.

## The inclusion test

Before writing an item, answer one question:

> Does the user notice this while using the app?

If no, omit it or restate it as the effect the user perceives.

| Change | Release note |
| --- | --- |
| Reworked connection pooling | Faster, more stable loading |
| Added query result caching | Lists open more quickly |
| Replaced the image decoder | Images appear without flicker |
| Migrated to a new state management library | Omit |
| Raised test coverage to 80% | Omit |

Never publish an item that only makes sense to someone who read the diff.

## Never include

Refactoring, architecture, dependency upgrades, API changes, database schema, build configuration, tests, logging, documentation, repository tooling, store screenshots.

None of it is visible inside the app. Listing it spends the character budget without telling the user anything.

## Structure

Fixed section order, each section named in the target language:

```text
What's new
Improvements
Fixes
```

| Rule | Reason |
| --- | --- |
| Omit a section with no items | An empty heading reads as an unfinished release |
| No version number | The store displays the version separately |
| No colon after a heading | The heading is a label, not a lead-in |
| Blank line after each heading and between sections | The store renders the field as plain text with no styling |
| One bullet per change, one sentence per bullet | Two changes in one bullet make both easy to miss |
| Bullet character `•` | The field does not render Markdown lists |

## Character budget

Google Play allows **500 Unicode characters per language**. The limit is enforced per language tag, not per submission. Text over the limit does not publish as written.

Count the entire block before finalizing, including tags, headings, blank lines and bullet characters. If the count reaches 500, remove items and recount. Repeat until under the limit.

- Target 3 to 6 items. Treat 8 as a rare ceiling, not a default.
- When trimming, drop the least user-visible item first, not the most recently added one.
- Keep at least one item per section that survives.

## Output format

Emit the notes inside a fenced code block so the text can be copied in one action. Nothing outside the fence: no introduction, no closing comment.

Each language tag sits alone on its own line, as Google Play requires. The first heading starts on the line immediately after the opening tag, and the closing tag follows the last bullet immediately. Leading and trailing blank lines count against the 500 character budget.

````text
```
<en-US>
What's new

• Support for light, dark and automatic themes.
• Search by name in the item list.

Improvements

• Lists open more quickly.

Fixes

• Selected filters are no longer lost when returning to the list.
</en-US>
```
````

## Multiple languages

One tag block per store language, stacked in the same fenced block. Section headings are translated along with the items:

```text
<en-US>
What's new

• Support for light, dark and automatic themes.

Fixes

• Selected filters are no longer lost when returning to the list.
</en-US>
<pt-BR>
Novidades

• Suporte aos temas claro, escuro e automático.

Correções

• Os filtros selecionados não são mais perdidos ao voltar para a lista.
</pt-BR>
```

Translate the meaning, not the words. The 500 character budget applies per language, so a bullet that fits in one language may have to be cut in another where the same idea needs a longer sentence.

## Style

| Prefer | Avoid |
| --- | --- |
| Support for light, dark and automatic themes. | Implemented theme support. |
| Search by name in the item list. | Refactored the search component. |
| Faster queries. | Performance improvements. |

Write the result, not the action. The engineering voice (`Implemented`, `Refactored`, `Migrated`, `Fixed an issue where`) describes the work; the user cares about the state of the app after the update.

## Anti-patterns

- `Bug fixes.`, `Various improvements.`, `Minor adjustments.` Filler that consumes budget and communicates nothing.
- Emojis, promotional language, review requests, thanking users for their patience.
- Repeating the same generic entry every release.
- Announcing a feature that is behind a flag and not yet reachable.
- Copying commit subjects verbatim.
