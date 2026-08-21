# UI States and Feedback

## State components

```text
components/states/
├── app_empty_state.dart
├── app_error_state.dart
├── app_loading_state.dart
├── app_permission_state.dart
└── app_retry_state.dart
```

Every async surface in the app maps to these. No bespoke spinners or one-off error texts.

**Loading.** Several presentations for different contexts: centered indicator, skeleton, in-button loading, section progress, determinate progress for long jobs. Never add artificial delay; local data renders immediately.

**Empty.** Operation succeeded, nothing to show. Explain what is missing and offer the action that fills it.

**Error.** Localized message, retry action when applicable, contextual icon, technical details only in debug builds.

**Permission.** Explain why the permission is needed, offer the grant action, and when permanently denied, offer opening system settings.

**Retry.** For surfaces whose main action is simply repeating an operation.

All copy is passed in by the app; the components hold no strings.

## Choosing a feedback mechanism

| Situation | Mechanism |
| --- | --- |
| Brief, non-blocking confirmation | Toast / snackbar |
| Needs explicit confirmation or is destructive | Dialog |
| Contextual actions or quick selection | Bottom sheet |
| Validation or a failure tied to one element | Inline message |
| Physical confirmation of a small action | Haptics |

Do not route everything through one mechanism.

**Toasts/snackbars.** Variants: success, error, warning, info. One at a time; never for anything the user must act on.

**Dialogs.** Required for destructive and irreversible actions: deleting files, deleting a collection, clearing history, discarding edits. State the consequence, not just "Are you sure?".

**Bottom sheets.** Standardized header, spacing and selection style across every occurrence. Sheets are for choices and actions, not for forms that deserve a screen.

**Inline feedback.** Sits next to the element it refers to: invalid input, empty search result, unavailable resource, unsupported format, failure in one section.

**Haptics.** Sparse, only on meaningful actions, only when supported and enabled in settings.

## Button states

Every button renders `enabled`, `pressed`, `disabled` and `loading`.

- During an async action, block duplicate taps.
- Reflect user intent immediately with an optimistic visual state, while the underlying operation completes.
- Disabled buttons still need an explanation nearby of what would enable them.
