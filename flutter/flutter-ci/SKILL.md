---
name: flutter-ci
description: "Continuous integration and delivery for Flutter: the pipeline jobs, running the same checks locally, code generation and coverage gates, dependency vulnerability scanning, caching and speed, and tag-triggered release artifacts. Use when writing or fixing a workflow, adding a check, diagnosing a failure that only happens in CI, or speeding up a slow pipeline."
license: MIT
---

# Continuous Integration

Project bootstrapping is covered by `flutter-project-setup`; what deserves a test is covered by `flutter-testing`. This skill covers the pipeline and the local command that must agree with it.

## One gate, two places

The most expensive failure mode in CI is a check that exists only in CI. It is found after the push, by whoever is waiting on the review, and the fix cycle is a full pipeline run each time.

Give the repository one script that runs exactly what the pipeline runs, and have the pipeline call it or mirror it step for step. When the two drift, the local run stops being trusted and everyone pushes to find out.

```bash
./scripts/verify.sh            # format, analyze, test, coverage
./scripts/verify.sh --all      # everything, not just changed packages
./scripts/verify.sh --gen      # regenerate first
```

Useful properties for that script:

- `set -euo pipefail`, and `cd` to the repository root so it runs from anywhere.
- Scope to the packages with pending changes by default, with a flag for everything. A gate slow enough to skip is a gate nobody runs.
- Use the pinned SDK when the version manager is present, falling back to the bare tools when it is not, so CI and contributors without it behave the same.
- No flag that skips tests in the final check. A quick mid-change mode is fine as long as it is documented as not the gate.

Workflows can also be run locally with `act` before pushing, which catches a broken workflow file without burning a pipeline run.

## The jobs

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true
      - run: flutter pub get
      - run: flutter pub get --directory packages/app_ui
      - run: dart format --set-exit-if-changed .
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: git diff --exit-code
      - run: flutter analyze
      - run: flutter test --coverage
      - run: flutter test --directory packages/app_ui
      - run: flutter build apk --debug
```

Every step is a gate, and each catches something the others cannot:

| Step | Catches |
| --- | --- |
| `dart format --set-exit-if-changed` | Formatting drift, without a bot rewriting the branch |
| Code generation, then `git diff --exit-code` | Committed generated output that no longer matches its source |
| `flutter analyze` on app and packages | A package that only breaks when analyzed on its own |
| Tests with coverage | Regressions, and coverage falling below the threshold |
| A build | Code that analyzes and tests but does not compile for a device |

`concurrency` with `cancel-in-progress` stops the queue filling with superseded runs of the same branch.

## Code generation in CI

Regenerating and asserting an empty diff is what keeps committed output honest. Without it a stale `.g.dart` compiles fine, passes every test, and diverges from its source until someone regenerates months later and gets an unexplained diff.

Whether generated files are committed at all is one decision applied everywhere. If they are not committed, CI generates before analyzing and the diff assertion does not apply.

## Coverage

Enforce the threshold in the pipeline rather than reporting it, or it becomes a number nobody reads.

Exclude generated sources, localization output and schema declarations before measuring. Counting them makes the figure move on its own: adding an annotated class raises coverage without a single new test. What belongs in the count is covered by `flutter-testing`.

Fail the build below the threshold, and treat lowering the threshold as a decision that needs a reason in the commit.

## Dependency vulnerability scanning

Run a lockfile vulnerability scan (`osv-scanner` or equivalent) as its own job, against every `pubspec.lock` in the repository, including local packages. Report it rather than gate on it at first: a scanner surfacing a transitive advisory with no fix available yet should not block every pull request until the upstream releases one. Move it to gating once the project has a process for triaging and, when appropriate, suppressing a specific advisory.

## Speed

- Cache the SDK and the pub cache. A cold install dominates a short pipeline.
- Run independent jobs in parallel, and shard a long test suite with `--total-shards` and `--shard-index`.
- Put the fastest checks first: format and analyze fail in seconds and save a full test run.
- Integration tests on an emulator are the slowest job by an order of magnitude. Run them on a schedule or on the main branch rather than on every push, if the wait is blocking reviews.

## Failures that only happen in CI

| Symptom | Cause |
| --- | --- |
| Golden diffs only in CI | Fonts not loaded in the test, or a different renderer on the runner |
| Widget test times out waiting for a transient message | The CI emulator runs with animations disabled, so the message never animates in as expected |
| Passes locally, fails on the runner | A test depending on the machine clock, timezone, locale or file order |
| Fails only on the first run of the day | A cache that was populated by a previous, different pipeline |

Diagnosing an intermittent failure is covered by `flutter-testing`.

## Releases

Trigger delivery from a version tag, never from a branch push:

- Build the release artifact and name it with the version.
- Attach it to the workflow run and to a release.
- Keep signing material in repository secrets, never in the repository.
- Publishing to a store is a separate, deliberate workflow. A tag should not push to production unless the project explicitly decided it should.

## Anti-patterns

- A check that exists in CI and has no local equivalent.
- A local script that runs a subset, so green locally means nothing.
- Formatting fixed by a bot that pushes to the branch, instead of failing the check.
- Generated output committed with no regeneration check.
- Coverage reported but not enforced, or enforced without excluding generated code.
- Secrets in workflow files rather than in secrets.
- A pipeline with no concurrency control, running every superseded commit to completion.
- Emulator-based integration tests on every push, making the pipeline slow enough that people stop reading it.
