# Headless TTS Refactor — VoxBook Session Transcript (condensed)

Source session: 2026-07-09, VoxBook (`com.voxbook.ttsreader`) single-module
Jetpack Compose offline TTS reader. The TtsPlayer implementation directly
instantiated `android.speech.tts.TextToSpeech` in its constructor, making the
entire playback state machine impossible to unit-test on a headless Linux VM.

## Before

```kotlin
@Singleton
class TtsPlayerImpl @Inject constructor(
    private val context: Context,          // Android-only dep, uninjectable in tests
) : TtsPlayer {
    private val tts = TextToSpeech(context) { status -> ... }
    // ~100 lines of state machine, segment queueing, pause/resume
}
```

Unreachable from JUnit because `TextToSpeech` needs a real device.

## After — canonical layout

### 1. Pure interface in `core/domain/tts/TtsEngine.kt`

```kotlin
interface TtsEngine {
    data class Voice(val id: String, val locale: String, val label: String)

    interface Listener {
        fun onUtteranceStart(utteranceId: String)
        fun onUtteranceDone(utteranceId: String)
        fun onUtteranceError(utteranceId: String)
    }

    suspend fun init(): Boolean
    fun loadVoices(): List<Voice>
    fun setRate(rate: Float)
    fun setVoice(voiceId: String?)
    fun enqueue(utteranceId: String, text: String)
    fun stop()
    fun shutdown()
    fun addListener(listener: Listener)
    fun removeListener(listener: Listener)
}
```

No Android imports. The inner `Voice`/`Listener` types are pure Kotlin.

### 2. Real impl in `core/data/tts/RealTtsEngine.kt`

Thin pass-through to `android.speech.tts.TextToSpeech`:
- `init()` wraps `suspendCancellableCoroutine { ... TextToSpeech(ctx) { ... } }`
- `addListener` converts the Android `UtteranceProgressListener` callbacks into
  the `TtsEngine.Listener` interface.
- `setVoice`, `setRate`, `enqueue`, `stop`, `shutdown`, `loadVoices` each have a
  one-line body.

### 3. Refactored `TtsPlayerImpl.kt`

```kotlin
@Singleton
class TtsPlayerImpl @Inject constructor(
    private val engine: TtsEngine,
) : TtsPlayer {
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    private val _state = MutableStateFlow(PlayerState(TtsState.IDLE))   // ← explicit initial!
    override val state: StateFlow<PlayerState> = _state.asStateFlow()

    init {
        engine.addListener(object : TtsEngine.Listener { ... })   // register before init()
    }

    override suspend fun init(): Boolean { /* set INITIALIZING, engine.init(), loadVoices */ }
    // speak, pause, resume, stop, seekToSegment, setRate, setVoice, shutdown
}
```

## Hilt DI module — add a second @Binds

`TtsModule.kt` before: only bound `TtsPlayerImpl → TtsPlayer`.
After (added the engine binding):

```kotlin
@Module @InstallIn(SingletonComponent::class)
abstract class TtsModule {
    @Binds @Singleton abstract fun ttsEngine(impl: RealTtsEngine): TtsEngine
    @Binds @Singleton abstract fun ttsPlayer(impl: TtsPlayerImpl): TtsPlayer
}
```

## Compile errors captured (and fixes)

1. **`[Dagger/MissingBinding] TtsPlayerImpl cannot be provided`** → added
   `@Binds RealTtsEngine → TtsEngine`.
2. **`[Dagger/MissingBinding] CoroutineScope cannot be provided`** → constructor
   had `private val scope: CoroutineScope = CoroutineScope(...)`. Hilt does not
   honor default-value constructors; move the scope to a property.
3. **`No value passed for parameter 'state'`** on `MutableStateFlow(PlayerState())`
   → `PlayerState` requires a `TtsState` argument explicitly.

## Fake in `app/src/test/java/.../FakeTtsEngine.kt`

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
    override fun removeListener(l: TtsEngine.Listener) { listeners -= l }
    override fun loadVoices() = listOf(
        TtsEngine.Voice("en-US-1", "en-US", "English US 1"),
        TtsEngine.Voice("en-GB-1", "en-GB", "English UK 1"),
    )
    override fun setRate(rate: Float) {}
    override fun setVoice(voiceId: String?) {}
    override fun shutdown() {}

    fun fireDone(id: String) = listeners.forEach { it.onUtteranceDone(id) }
    fun fireError(id: String) = listeners.forEach { it.onUtteranceError(id) }
}
```

Test fires `fakeEngine.fireDone("2")` synchronously — state machine transitions
verified with plain JUnit + `kotlinx-coroutines-test`.

## Test file count

`TtsPlayerImplTest.kt`: 16 tests covering init/failure/empty/speak/pause/resume/stop/seek/utteranceStart/Done/last/error/shutdown. All passing on headless Linux, no emulator.

## Honest remaining gap

Real audio output, voice selection on hardware, and PDF text extraction
(`PdfRenderer`) remain device-only. Covered by instrumented `androidTest` once
a local emulator or physical device is available (not in this session).

## Lesson

The refactor pattern (interface + real + fake + `@Binds`) is reusable for every
Android-framework-coupled class in the codebase. The skill
`android-testability-skill` documents the canonical workflow, pitfalls
(CoroutineScope default values, Hilt's handling of them, explicit initial
states, listener registration ordering), and file layout.
