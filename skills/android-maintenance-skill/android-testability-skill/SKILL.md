---
name: android-testability-skill
description: >-
  Introduce dependency-inversion boundaries to make Android-framework-coupled
  code (TextToSpeech, Camera, Bluetooth, Location, MediaPlayer, etc.) unit-
  testable on a plain JVM — no emulator, no Robolectric. Pattern: interface +
  real impl (data layer) + fake impl (test fixtures) + Hilt @Binds. Routes here
  when a class has `new TextToSpeech(context)`, `Camera2` opens, `MediaPlayer`
  constructed, or anything that "works but cannot be unit-tested on headless
  Linux".
version: 1.0.0
tags:
  - android
  - testability
  - dependency-inversion
  - abstractions
  - fake
  - junit
  - coroutines-test
---

# Android Testability Refactor Skill

## Role

You are a **Testability Refactor Engineer**. You rescue a production Android
class that depends directly on a framework object (`TextToSpeech`,
`MediaPlayer`, `Camera`, `BluetoothAdapter`, `LocationManager`, etc.) and make
its *pure logic* (state machine, queueing, retry, error recovery) verifiable
with plain JUnit on the JVM. The Android-specific call site is pushed into a
small production impl; a fake impl stands in during tests.

## Trigger Conditions

Activate when any of these are true:

- A class instantiates an Android framework object (`new TextToSpeech(ctx)`) in
  its constructor or `init` block, and you were told "we cannot unit-test this
  without Robolectric / an emulator".
- A test needs a fake whose callbacks fire deterministically, but the real
  object has async or one-shot side effects that can't be replayed.
- The class mixes state-machine logic (testable) with side effects (not
  testable on headless CI).
- The user asks "how do I headless-test the TTS / camera / audio layer?".

## When NOT to activate

- Pure domain logic already has no framework dependencies — just write a unit
  test, no refactor needed.
- You're adding a *feature*; refactoring for testability should be a separate
  commit.
- The framework API is stable and only used once — isolating it into an
  interface is over-engineering.

## Workflow — 5 Steps

1. **Identify the boundary.** Find every call site of the framework object
   inside the class. List what the class *consumes* (inputs) and what it
   *expects back* (callbacks, async completions).
2. **Define the interface** in `core/domain/.*` (pure Kotlin, no Android
   imports). Include:
   - The minimal set of methods the class actually calls — nothing more.
   - An inner `Listener` / `Callback` interface for asynchronous events.
   - `data class Voice` / event payloads as plain data, NOT framework types.
3. **Extract the real implementation** into `core/data/.*` (Android allowed).
   - Keep it as thin as possible: translate framework callbacks into your
     listener, never compute business logic here.
   - Capture real-world gotchas (e.g., `TextToSpeech` has no `pause`/`resume`)
     by documenting them in the impl's KDoc.
4. **Write a fake** in `app/src/test/java/...`. The fake must:
   - Record every call (e.g., `val enqueueCalls: MutableList<Pair<String, String>>`)
     so tests can assert interactions.
   - Expose helper methods (`fireDone(id)`, `fireError(id)`) to replay
     callbacks synchronously.
   - Return deterministic fixtures (voices, voices, status codes).
5. **Wire via Hilt** in the existing module — add a second `@Binds` for the
   new interface → real impl. The test constructor takes the interface directly;
   no Hilt test module needed.

## Pitfalls (from real sessions)

- **NEVER put a default `CoroutineScope(...) = ...` in the `@Inject`
  constructor.** Hilt/Dagger cannot satisfy default-value constructors at
  compile-time — you'll get `[Dagger/MissingBinding] CoroutineScope cannot be
  provided`. Move the scope to a property inside the class body:
  ```kotlin
  @Inject constructor(private val engine: TtsEngine) : TtsPlayer {
      private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
  }
  ```
  This keeps unit tests working (they inject just `engine`) AND DI working
  (Hilt resolves only `engine`).

- **Explicit initial state.** State data classes often require a non-default
  constructor argument (`PlayerState(state = TtsState.IDLE)`). The initial
  `MutableStateFlow(PlayerState())` call fails to compile. Always pass the
  explicit initial value.

- **Listener registration in `init`.** Register the fake's listener inside
  the production class's `init` block so the fake is ready to observe
  callbacks BEFORE `engine.init()` completes. This lets tests fire
  `onUtteranceStart/Done/Error` synchronously and assert state transitions.

- **`@Singleton` on the impl, not the interface.** Put `@Singleton` on the real
  class's class-decl. The module's `@Binds` re-inherits the scope, but the
  annotation is only legal on the concrete class.

- **Do not refactor two boundaries at once.** One class, one interface, one
  fake, one commit. Resist the temptation to also refactor the ViewModel in
  the same change — test the refactor in isolation first.

## File layout (canonical)

```
app/src/main/java/.../
  core/
    domain/tts/TtsEngine.kt          ← pure Kotlin interface
    data/tts/RealTtsEngine.kt        ← wraps android.speech.tts.TextToSpeech
    data/tts/TtsPlayerImpl.kt        ← @Inject constructor(engine: TtsEngine)
    di/TtsModule.kt                  ← @Binds RealTtsEngine → TtsEngine
                                      ← @Binds TtsPlayerImpl → TtsPlayer
app/src/test/java/.../
  core/domain/tts/FakeTtsEngine.kt   ← implements TtsEngine, records calls
  core/data/tts/TtsPlayerImplTest.kt ← plain JUnit, no emulator
```

## Test fixture pattern (FakeTtsEngine sketch)

```kotlin
class FakeTtsEngine : TtsEngine {
    var initResult = true
    var initCalls = 0
    var stopCalls = 0
    val enqueueCalls = mutableListOf<Pair<String, String>>()
    val listeners = mutableListOf<TtsEngine.Listener>()

    override suspend fun init(): Boolean { initCalls++; return initResult }
    override fun enqueue(id: String, text: String) { enqueueCalls += id to text }
    override fun stop() { stopCalls++ }
    override fun addListener(l: TtsEngine.Listener) { listeners += l }
    // ... other overrides noop ...

    fun fireDone(id: String) = listeners.forEach { it.onUtteranceDone(id) }
    fun fireError(id: String) = listeners.forEach { it.onUtteranceError(id) }
}
```

## Verification recipe

After refactor, run (in this order, do not combine until each passes):

1. `./gradlew clean` — forces full recompilation, catches stale generated code
   from previous Hilt graph.
2. `./gradlew :app:compileDebugKotlin` — interface + impl + module wiring.
3. `./gradlew :app:compileDebugUnitTestKotlin` — fake compiles against new
   interface.
4. `./gradlew :app:testDebugUnitTest --tests "*TtsPlayerImplTest"` — the new
   tests pass on plain JVM.
5. `./gradlew :app:testDebugUnitTest` — full regression, nothing broke.

If step 1 or 2 fails with `[Dagger/MissingBinding]`, re-read the Pitfalls
section above 99% of the time it's either a missing `@Binds` in the module or
a default-value constructor parameter that Hilt cannot resolve.

## Cross-References

| Neighbour skill | Why |
|-----------------|-----|
| `android-architecture-skill` | This refactor is a consequence of a good layer separation; consult it when deciding WHERE to put the interface. |
| `android-qa-skill` | Tests produced here feed the QA skill's verification loop. |
| `android-build-skill` | If the refactor touches `build.gradle.kts` deps, build skill decides. |
| `android-development-skill` | Developer implements the refactor following this skill's workflow. |

Reference transcript: `references/headless-tts-refactor.md` — verbatim of the
VoxBook session that produced this skill, including the exact error messages
from which the pitfalls were extracted.
