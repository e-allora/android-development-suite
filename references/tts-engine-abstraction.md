# TtsEngine Abstraction Pattern

Proven in the VoxBook Android pilot. Makes Android framework-dependent code
testable on plain JVM without Robolectric or emulator.

## Problem
Android system services (TextToSpeech, PdfRenderer, LocationManager) cannot be
instantiated on JVM. Direct instantiation in constructors makes classes
untestable without Robolectric.

## Solution
1. Define a pure-Kotlin interface in `domain/` with no Android imports.
2. Implement the interface in `data/` with the real Android service.
3. Inject the interface via constructor (Hilt `@Binds`).
4. Write a `Fake*` implementation in `src/test/` that tracks calls and fires
   callbacks synchronously.

## VoxBook Example

```
domain/tts/TtsEngine.kt     ← interface (pure Kotlin, no Android)
data/tts/RealTtsEngine.kt   ← wraps android.speech.tts.TextToSpeech
data/tts/TtsPlayerImpl.kt   ← depends on TtsEngine, not TextToSpeech
test/.../FakeTtsEngine.kt   ← tracks calls, fires callbacks for assertions
di/TtsModule.kt             ← @Binds TtsEngine → RealTtsEngine
```

## Key Design Rules
- Interface must have a `Listener` nested interface for callback registration.
- `addListener/removeListener` pattern, not a single callback.
- Fake fires callbacks synchronously — tests don't need async infrastructure.
- DI module binds the abstraction, not the concrete class.

## Applicability
Any Android system service: TextToSpeech, PdfRenderer, LocationManager,
BluetoothAdapter, CameraManager. Works anywhere Android framework classes
are instantiated directly in constructors.
