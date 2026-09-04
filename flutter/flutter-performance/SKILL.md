---
name: flutter-performance
description: "Performance work in Flutter: measuring in profile mode, moving CPU work off the UI isolate with compute and isolates, long scans that report progress, batching database writes, decoding images at the size they are drawn, scrolling cost in long lists, startup time and memory. Use when the app stutters, a scan or import freezes the UI, a list scrolls badly, memory grows with scrolling, startup is slow, or when reviewing code that processes many records or large files."
license: MIT
---

# Performance

Performance work has one entry condition: a measurement. Optimizing code that was never profiled trades readability for nothing, and the bottleneck is regularly not where it feels like it is.

Motion and frame budget during an animation are covered by `flutter-animation`; rebuild scope by `flutter-state-riverpod`; query shape and indexes by `flutter-database`; throttling updates pushed to a platform channel by `flutter-background-audio`; pipeline duration by `flutter-ci`.

## Measure first

- Profile in **profile mode** on a physical device. Debug builds carry assertions, no JIT warmup guarantees and unoptimized code; a debug measurement says almost nothing about a release build.
- Read the timeline, not the feeling. The DevTools performance view separates the two threads that produce a frame, and they fail for different reasons.

| Thread over budget | Cause | Direction |
| --- | --- | --- |
| UI | Dart work: building, layout, parsing, sorting, a synchronous read | Do less per frame, or move it off the isolate |
| Raster | Painting cost: `saveLayer`, opacity and clip layers, large blurs, shader compilation on first play | Change what is painted, not how it is computed |

A stutter that only happens the first time an effect appears is shader compilation, not the code around it. Reproduce it on a physical device before changing anything.

Record the number before and after. "Feels smoother" is not a result, and a change with no measured effect is a change to revert.

## Work that belongs off the UI isolate

Dart is single-threaded per isolate: any synchronous work blocks frames for exactly as long as it runs. `await` alone does not help, since an `async` function still runs its body on the same isolate.

| Work | Where it runs |
| --- | --- |
| Platform channel calls, file I/O, database queries | Already off the UI thread. Awaiting them does not block frames |
| Parsing a large payload, hashing, image manipulation, sorting tens of thousands of records | The UI isolate, unless moved. These are what `compute` is for |
| A long sequence of small awaited calls | The UI isolate, between awaits. Moving each one changes nothing; batching them does |

```dart
final parsed = await compute(_parseCatalog, bytes);
```

`compute` spawns an isolate, copies the argument in and the result out, and shuts it down. That cost is real, so it pays off for one large job and loses for many small ones. For repeated work, keep a long-lived isolate instead of spawning per call.

Two constraints that turn into runtime errors rather than compile errors:

- **Plugins do not work in a spawned isolate by default.** The background isolate has no binary messenger until one is installed, so a plugin call throws. Pass a `RootIsolateToken` from the caller and initialize it (`BackgroundIsolateBinaryMessenger.ensureInitialized`) before touching any plugin.
- **Only certain values cross an isolate boundary**, and large byte buffers are copied unless transferred explicitly. Copying a large list of objects can cost more than the work being moved; measure the transfer, not just the computation.

The database engine often has its own answer: a background-isolate connection keeps every query off the UI isolate without any manual isolate management. Prefer it over hand-rolling one.

## Long scans and imports

A job that walks the filesystem, reads metadata from thousands of files and writes them to a database is the shape most likely to freeze an app. It has four requirements, and dropping any one of them produces a distinct complaint.

| Requirement | Dropped |
| --- | --- |
| Report progress | The user sees a frozen screen and force-quits mid-write |
| Commit in batches | Every record costs a disk sync, and the run takes minutes instead of seconds |
| Be cancellable | Leaving the screen keeps the device busy, and the work cannot be stopped |
| Be resumable or idempotent | An interrupted run leaves half a library and no way to finish it |

```dart
const _commitBatchSize = 100;

Stream<IndexingProgress> index(List<SourceFile> files) async* {
  for (var start = 0; start < files.length; start += _commitBatchSize) {
    final batch = files.sublist(start, start + _commitBatchSize);
    final progress = <IndexingProgress>[];

    await _database.transaction(() async {
      for (final file in batch) {
        progress.add(await _indexOne(file));
      }
    });

    yield* Stream.fromIterable(progress);
  }
}
```

The batch size is a trade, and it is worth a comment where the constant is declared: every commit costs a disk sync, so larger batches are faster, and progress can only be reported once a batch has committed, so larger batches make the progress bar advance in coarser steps.

Progress is emitted **after** the commit, never before. Reporting a record as done before its transaction commits means an interrupted run has reported work that no longer exists.

## Images

Decoding is where an image-heavy list actually spends its memory. Embedded artwork and photos routinely arrive at a thousand pixels a side and get drawn at forty.

```dart
final decodeSize = (size * MediaQuery.devicePixelRatioOf(context)).round();

Image.file(
  File(path),
  width: size,
  height: size,
  cacheWidth: decodeSize,
  cacheHeight: decodeSize,
  gaplessPlayback: true,
);
```

| Rule | Reason |
| --- | --- |
| Decode at the drawn size, scaled by the device pixel ratio | The image cache stores decoded pixels. Full-resolution decoding for a thumbnail multiplies memory by the ratio squared |
| Only pass a decode size when it is actually known | An image that fills whatever space it is given has no correct fixed size, and guessing one produces a blurry result |
| `gaplessPlayback` when the source can change in place | Without it the widget shows a blank frame between the old and the new image |
| Cache derived thumbnails on disk, keyed by a stable source key | Re-extracting artwork on every scroll is a decode and an I/O per frame. Where that cache lives: `flutter-data-layer` |
| Generated placeholders must be deterministic | A placeholder derived from a random value changes on every rebuild. Derive it from a documented hash of the identifier, never from `hashCode` (`flutter-code-style`) |

## Lists

- Always build lazily (`ListView.builder`, slivers). A list that constructs every child up front pays for the whole collection to show ten rows.
- Give rows a fixed extent when they have one. `itemExtent` (or `prototypeItem`) lets the viewport skip measuring every child, which is the difference between smooth and sticky on a long list.
- Never `shrinkWrap` a list inside another scrollable. It lays out every child to measure itself, which defeats laziness entirely. Use slivers in a single scroll view instead.
- Stable keys on rows that can reorder; without them the framework reuses the wrong element and rebuilds more than it needs to.
- Keep row widgets `const` where possible and push provider watches down to the smallest widget that needs the value (`flutter-state-riverpod`).
- Avoid keep-alives on list items unless the state is genuinely expensive to rebuild. They pin every visited row in memory for the life of the list.

## Startup

- First frame time is dominated by whatever `main` awaits. Only what the first frame truly needs is resolved before `runApp`; everything else is started after it.
- Deferred work belongs after the first frame, not in a widget's `initState` that runs during it.
- A synchronous read of a large stored value at startup is a frozen splash screen. Read it lazily, or read a small pointer and defer the rest.
- Measure startup on a cold launch on a mid-range device. A warm launch on a fast phone hides the problem entirely.

## Memory

- Cancel every stream subscription, timer and controller. A leak in Flutter is usually a listener holding a disposed widget's state, and it shows up as memory that only grows.
- Watch the image cache first when memory grows with scrolling; it is the largest consumer in most apps and it is bounded by decoded size, not file size.
- Unbounded in-memory caches keyed by a growing collection are a leak with a friendly name. Give every cache a bound or a disk backing.
- Reading an entire file into memory to process it linearly is avoidable with a stream. It also fails on exactly the large input that motivated the optimization.

## Guarding a fix

A performance fix with no test is a fix that gets reverted by the next refactor.

- Assert the property that made it fast: the number of queries issued, the batch size committed, the decode dimensions requested, that a cache was hit rather than recomputed.
- Do not assert on wall-clock duration in a unit test. It is the flakiest possible assertion and it fails on a busy CI runner for no reason (`flutter-testing`).
- Record the measurement and the device in the commit message. The next person to touch it needs the baseline, not the adjective.

## Anti-patterns

- Optimizing without a profile-mode measurement, and reporting the result as a feeling.
- Measuring in debug mode.
- `compute` for work too small to pay for the isolate spawn and the copy.
- A spawned isolate calling a plugin with no root isolate token installed.
- A long job with no progress, no cancellation and one transaction around the whole thing.
- Progress reported before the write commits.
- Full-resolution decoding for thumbnails.
- `shrinkWrap: true` to make a nested list compile.
- An in-memory cache with no bound.
- A performance fix with no test asserting the property that made it fast.
