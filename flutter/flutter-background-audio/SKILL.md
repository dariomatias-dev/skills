---
name: flutter-background-audio
description: "Background audio playback in Flutter: the player engine behind a contract, the OS media session bridge (notification, lock screen, headset controls), audio session configuration, interruption and routing handling, foreground service requirements and testing playback without a device. Use when adding or reviewing playback, wiring audio_service or audio_session, debugging playback that stops when the app is backgrounded, a media notification that lags or drains battery, or a player that cannot be tested without an emulator."
license: MIT
---

# Background Audio

Playback that survives backgrounding is not a feature of the player library. It is a contract with the operating system: a foreground service or background mode keeps the process alive, a media session publishes what is playing, and an audio session negotiates the output device with every other app on the device.

Getting one of the three wrong produces a failure that never appears in a widget test: playback that dies on lock, controls that do nothing, or a battery complaint.

Platform manifest entries are covered by `flutter-project-setup`; the three-outcome permission contract by `flutter-architecture`; how playback state reaches widgets by `flutter-state-riverpod`; the startup guard around initialization by `flutter-error-handling`.

## The three objects

Playback is three responsibilities, and collapsing them into one class is what makes it untestable.

| Object | Owns | Knows about |
| --- | --- | --- |
| Player service | Loading sources, transport controls, queue order, emitting state | The audio library only |
| Media session handler | Publishing state to the OS, receiving OS commands | The player service contract and the media session library |
| Session coordinator | Audio focus, interruptions, output routing | The player service contract and the audio session library |

```text
core/audio/
├── audio_player_service.dart        # contract + state snapshot + enums
├── <library>_player_service.dart    # implementation, the only file importing the engine
├── media_session_handler.dart       # bridge to the OS media session
├── audio_session_coordinator.dart   # focus, interruptions, routing
├── queue_media_item.dart            # presentation model published to the OS
└── audio_providers.dart
```

The contract declares its own enums for processing state and repeat mode rather than re-exporting the library's. A contract that returns the engine's types has not isolated anything: every caller still depends on the package, and a fake has to import it.

## One snapshot, not many streams

Expose a single immutable snapshot object and one stream of it, not a stream per property.

```dart
class AudioPlaybackSnapshot {
  const AudioPlaybackSnapshot({
    required this.processingState,
    required this.playing,
    required this.position,
    required this.duration,
    required this.bufferedPosition,
    required this.speed,
    required this.currentIndex,
    required this.queueLength,
    required this.loopMode,
    required this.shuffleModeEnabled,
  });

  const AudioPlaybackSnapshot.initial() : /* ... */;

  final AudioProcessingState processingState;
  final bool playing;
  final Duration position;
  final Duration? duration;
  // ...
}

abstract interface class AudioPlayerService {
  AudioPlaybackSnapshot get snapshot;
  Stream<AudioPlaybackSnapshot> get snapshotStream;
  Stream<PlaybackException> get errorStream;
}
```

| Rule | Reason |
| --- | --- |
| Keep a synchronous `snapshot` getter beside the stream | Callers that need the current value must not wait for the next emission, and a `StreamBuilder` with no initial value renders an empty frame first |
| `playing` and `processingState` are independent | A player can be `playing == true` while buffering. Deriving one from the other produces a pause button that flickers on every stall |
| Merge the library's separate streams into the snapshot in the implementation | The engine emits position, playing, speed, loop and shuffle on different streams; joining them at the boundary keeps that mess in one file |
| Widgets watch a slice, never the whole snapshot | Position updates several times per second. Rebuild rules: `flutter-state-riverpod` |

`errorStream` is separate and must not close `snapshotStream`. A single unreadable file is an item to skip, not the end of the session.

## Initialization order

The media session must be initialized before the first frame, and it can fail on a real device. Resolve it in `main`, inside the startup guard, and inject the result.

```dart
Future<void> _start() async {
  final playerService = LibraryPlayerService();

  final sessionCoordinator = AudioSessionCoordinator(playerService);
  await sessionCoordinator.initialize();

  final handler = await AudioService.init(
    builder: () => MediaSessionHandler(playerService),
    config: const AudioServiceConfig(
      androidNotificationChannelName: 'Playback',
    ),
  );

  runApp(
    ProviderScope(
      overrides: [
        audioPlayerServiceProvider.overrideWithValue(playerService),
        audioHandlerProvider.overrideWithValue(handler),
      ],
      child: const App(),
    ),
  );
}
```

- Configure the audio session before the media session. The handler broadcasts state as soon as it is built, and a session that is not configured yet gives the OS a media notification for a player it cannot route.
- `AudioService.init` may only be called once per process. Calling it again after a hot restart or a retry throws; the retry path must reuse the handler it already built.
- These are `keepAlive` dependencies by nature. Wiring them as auto-dispose providers ends playback the moment the last screen watching them is popped.

## Bridging to the OS media session

The handler is a translation layer in both directions: OS commands come in, player state goes out. It holds no business rules.

```dart
class MediaSessionHandler extends BaseAudioHandler {
  MediaSessionHandler(this._playerService) {
    _subscription = _playerService.snapshotStream.listen(_onSnapshot);
    _broadcast(_playerService.snapshot);
  }

  @override
  Future<void> play() => _playerService.play();

  @override
  Future<void> skipToNext() => _playerService.seekToNext();
}
```

- Override every transport method the notification exposes. An unimplemented one is a control the user can press that silently does nothing.
- The OS queue and the engine queue are two copies of the same list. Every queue edit updates both, in the same method, or the notification shows the wrong track after a reorder.
- Publish the current item after any change to the queue or the index, not only on track change. A removal shifts the index without emitting one.
- Map the library's repeat and shuffle enums explicitly in both directions. The media session has values the engine does not (a group repeat mode, for instance) and the switch must decide what they mean rather than defaulting.
- Cancel the subscription and dispose the engine in the handler's own dispose, in that order. Disposing the engine first leaves a listener on a dead object.

### Throttling the state broadcast

The engine reports a new position several times per second. Pushing each one across the platform channel is a measurable battery cost, and the OS does not need them: it extrapolates the displayed position from the last published position, its timestamp and the speed.

Broadcast only when something the OS cannot infer has changed:

```dart
bool _isSignificant(AudioPlaybackSnapshot next) {
  final prev = _lastBroadcast;
  final prevTime = _lastBroadcastTime;
  if (prev == null || prevTime == null) return true;

  if (prev.playing != next.playing ||
      prev.processingState != next.processingState ||
      prev.speed != next.speed ||
      prev.currentIndex != next.currentIndex ||
      prev.queueLength != next.queueLength ||
      prev.loopMode != next.loopMode ||
      prev.shuffleModeEnabled != next.shuffleModeEnabled ||
      prev.duration != next.duration) {
    return true;
  }

  final elapsed = DateTime.now().difference(prevTime);
  final expected =
      prev.position + (prev.playing ? elapsed * prev.speed : Duration.zero);
  return (next.position - expected).abs() > const Duration(seconds: 2);
}
```

The drift comparison is what keeps seeks visible: a seek moves the position further than normal progression explains, so it broadcasts, while ordinary playback ticks do not. A fixed interval throttle cannot make that distinction and delays every seek by up to its interval.

Do not apply this throttle to the in-app UI. The progress bar reads the snapshot stream directly; only the platform channel needs protecting.

## Audio focus, interruptions and routing

Configure the session once, for the category the app actually is. A player configured as ambient audio is silenced by the phone's silent switch; a recorder category disables playback routing.

```dart
await session.configure(const AudioSessionConfiguration(
  avAudioSessionCategory: AVAudioSessionCategory.playback,
  avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.duckOthers,
  androidAudioAttributes: AndroidAudioAttributes(
    contentType: AndroidAudioContentType.music,
  ),
  androidWillPauseWhenDucked: true,
));
```

Two event streams must be handled, and each maps to a different user expectation:

| Event | Handling |
| --- | --- |
| Interruption begins (call, another app takes focus) | Pause |
| Interruption ends | Resume only if the interruption was flagged as temporary and the user had not paused manually |
| Becoming noisy (headphones unplugged, Bluetooth disconnected) | Pause immediately, never resume |

Becoming noisy is the one every project forgets, and the failure is loud in the literal sense: the track continues on the phone speaker in a public place. It is a platform event, not a routing change the player reports.

Resuming after an interruption is a decision, not a default. Auto-resuming after a call the user chose to answer is usually correct; auto-resuming after another media app took over is not.

## Staying alive in the background

The runtime permission and the platform declaration are two separate things, and each fails differently:

| Missing | Symptom |
| --- | --- |
| Foreground service type on Android | Playback is killed shortly after the app is backgrounded, with no error |
| Background mode on iOS | Audio stops at lock, and the media session disappears |
| Notification permission | Playback works, but no controls in the shade or on the lock screen |
| Media button receiver declaration | Headset and Bluetooth buttons do nothing |

Manifest and plist entries: `flutter-project-setup`.

The notification permission is not a blocker. Model it separately from the permission that gates the content itself: media access blocks the library and belongs in onboarding, while notification access only decides whether the controls are reachable, and the app must stay fully usable when it is denied. A permission wrapper that returns a plain boolean cannot express the `notApplicable` case, which is what every platform version without that permission returns; treating that as denied shows a request prompt that never appears.

## Failures during playback

- A file that fails to load emits on `errorStream` and leaves the queue intact. The listener skips the item, keeps the queue consistent and reports it, rather than tearing down the session.
- Content read from an external index can disappear between the scan and the play. Treat a missing source as an expected outcome, not a crash. Reconciliation of an index against its source: `flutter-data-layer`.
- Convert engine exceptions into a typed application exception at the implementation boundary, like any other data source.

## Session restore

Restoring the previous queue and position on launch is a persistence concern, not a player concern: the player is handed a queue and an initial position, and knows nothing about where they came from.

- Persist the queue, the current index and the position, and restore them without starting playback. An app that resumes audio by itself on launch is a bug report.
- Load the queue with the position applied at load time rather than seeking after play starts. Seeking afterwards is audible.
- The last reliable moment to persist is the `paused` lifecycle state. Lifecycle handling: `flutter-state-riverpod`.

## Testing

The whole point of the contract is that nothing above it needs a device.

- Ship an in-memory fake of the player service. Give it a way to emit arbitrary snapshots and errors, and a recorded history of what it emitted, so a test can assert on the sequence rather than the final value.
- Test the handler against the fake: an OS command reaches the player, a player snapshot reaches the media session, and a queue edit updates both copies.
- Test the throttle directly. It is pure logic over two snapshots and a clock, and it is the piece most likely to silently start dropping seeks.
- Test the session coordinator by injecting a session whose event streams the test controls, then assert playback paused.
- Integration tests cover what a fake cannot: that the process survives backgrounding and that the notification appears. Everything else belongs in unit tests. Strategy: `flutter-testing`.

## Anti-patterns

- The audio library imported outside its implementation file.
- One class that is the player, the media session handler and the session coordinator at once.
- A stream per playback property, joined in widgets.
- Publishing every position tick to the media session.
- A fixed interval throttle on state broadcasts, delaying seeks.
- Queue edits applied to the engine but not to the published queue, or the reverse.
- Interruption handling without the becoming-noisy event.
- Auto-resuming after every interruption regardless of its cause.
- Auto-dispose providers holding the player or the handler.
- `AudioService.init` called on a retry path that already initialized it.
- A playback failure that clears the queue instead of skipping the item.
