---
name: flutter-forms
description: Build forms in Flutter without leaks or validation noise: controller and focus node lifecycle, validation timing, server-side field errors, keyboard actions and submission state. Use when creating or reviewing a form, a text field, an input validator, or debugging a disposed controller or lost focus.
license: MIT
---

# Forms and Input

A form is a lifecycle problem before it is a validation problem. Most form bugs are a controller that outlived its widget or an error shown at the wrong moment.

Where the error message appears and how it looks are covered by `flutter-design-system`; keyboard insets are covered by `flutter-layout-insets`.

## Lifecycle

`TextEditingController` and `FocusNode` are listenable objects owned by the widget that creates them. Both must be disposed.

```dart
class _FormState extends State<SignInForm> {
  final _emailController = TextEditingController();
  final _emailFocus = FocusNode();

  @override
  void dispose() {
    _emailController.dispose();
    _emailFocus.dispose();
    super.dispose();
  }
}
```

| Rule | Reason |
| --- | --- |
| Create in `State`, never in `build` | A controller rebuilt every frame loses the cursor position and the current text |
| Dispose every controller and focus node | They hold listeners; without disposal the widget is retained and the listener fires against dead state |
| Remove listeners you added, before disposing | `dispose` on the controller does not undo a listener you attached to something else |
| Do not put a controller in a `Notifier` or provider | It is UI state tied to one widget's lifetime, and providers outlive widgets |

When the initial value arrives asynchronously, set `controller.text` once when it resolves, guarded so a user who has already typed is not overwritten mid-edit.

## Validation timing

`autovalidateMode` decides when a field turns red, and the default choice is usually wrong.

| Mode | Use for |
| --- | --- |
| `disabled` | Validation only on submit. Correct for short forms |
| `onUserInteraction` | Fields with a format the user can get wrong while typing, such as email. Errors appear only after the field has been touched |
| `always` | Rarely correct. It marks empty required fields as invalid before the user has done anything |

Never validate a field the user has not reached yet. A form that opens with three red errors reads as broken.

Validate on submit regardless of mode: per-field validation is a convenience, not a guarantee.

## Validators

- A validator returns a localized message or null. It performs no side effects, no state changes and no network calls.
- Keep validators pure and shared, so the same rule is not reimplemented per screen with slightly different bounds.
- Trim before validating, and decide explicitly whether whitespace-only input counts as empty.
- Validate the domain rule, not the widget: minimum length and format belong to the value, and the same rule applies if the value ever arrives from elsewhere.

## Server-side errors

Client validation cannot know that an email is already registered. When the server returns field errors, they must land on the fields, not in a snackbar that disappears while the user is looking at the form.

Keep a map of field errors in the form state, clear a field's error when its value changes, and reserve the general banner for errors that belong to no single field.

## Keyboard and focus

- Set `textInputAction` so the keyboard offers the right action: `next` for intermediate fields, `done` or `send` on the last one.
- Move focus explicitly with `onFieldSubmitted` and `FocusScope`; do not rely on the platform guessing the traversal order.
- Match `keyboardType` to the content, and set `autofillHints` so the platform can fill credentials, addresses and one-time codes.
- Obscured password fields must not enable autocorrect or suggestions.
- Dismiss the keyboard when the user taps outside only if the form has no other tappable content; an aggressive dismiss handler swallows taps meant for the fields themselves.

## Submission

- Submission has four states: idle, submitting, failed, succeeded. The button reflects them, and duplicate taps are blocked while submitting.
- Disable the fields during submission, or accept that the payload can change after it was read.
- On failure, keep every value the user entered. A form that clears itself after a network error is the fastest way to lose a user.
- Navigate away only after the result is confirmed, never optimistically from the tap handler.
- Warn before discarding a dirty form on back navigation, using the confirmation pattern the app already uses.

## Anti-patterns

- A controller or focus node without a matching `dispose`.
- Controllers created inside `build`.
- `autovalidateMode: always` on a form with required fields.
- Validators that call a repository or set state.
- Server field errors surfaced as a toast instead of on the field.
- A submit button that stays enabled during submission.
- Reading values from controllers scattered across the tree instead of one form state object.
- Regular expressions copied for email validation that reject valid addresses; prefer a permissive check and let the server confirm.
