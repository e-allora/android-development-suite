# Android Build Gotchas (verified, not guessed)

Condensed knowledge bank from a real end-to-end build of a Compose/Hilt/Room
app on a fresh headless Linux box. The unifying lesson: **verify the
external API against the jar Gradle actually resolved before rewriting call
sites.** `javap` the cached jar; never guess signatures.

## 1. Root-free toolchain (all under $HOME, no sudo)

- JDK 17 (Temurin):
  `curl -sL "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse" -o jdk17.tar.gz`
  -> extract to `~/jdk17` (`--strip-components=1`).
- Android SDK cmdline-tools:
  `dl.google.com/android/repository/commandlinetools-linux-<ver>_latest.zip`
  -> `~/Android/Sdk/cmdline-tools/latest`; then
  `yes | sdkmanager --sdk_root=$ANDROID_HOME --licenses` and
  `sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" "platforms;android-35" "build-tools;35.0.0"`.
- Gradle binary (avoids missing wrapper):
  `services.gradle.org/distributions/gradle-<ver>-bin.zip` -> `~/tools/gradle-<ver>`.
  Drive with `export ANDROID_HOME=~/Android/Sdk JAVA_HOME=~/jdk17 PATH=$JAVA_HOME/bin:$PATH`
  then `~/tools/gradle-8.12/bin/gradle :app:assembleDebug --no-daemon`.

## 2. Verify external APIs with javap (do this before fixing errors)

Gradle caches resolved jars at
`~/.gradle/caches/modules-2/files-2.1/<group>/<artifact>/<ver>/<hash>/<file>.jar`.
List real signatures: `javap -classpath "$JAR" <Fully.Qualified.Class>`.
This caught every wrong assumption below without a guess-and-rebuild loop.

## 3. Verified 3rd-party coordinate / API corrections

- **epublib**: the artifact is `com.positiondev.epublib:epublib-core:3.1`
  (NOT `nl.siegmann:epublib`). The Java package path stays
  `nl.siegmann.epublib.*`, so existing imports keep working.
  - It transitively pulls `kxml2` + `xmlpull`, which collide on
    `org.xmlpull.v1.XmlPullParser` -> **exclude** `group="xmlpull", module="xmlpull"`.
  - Read text: `Resource.getInputStream()` -> `Jsoup.parse(html).text()`.
  - TOC: `book.tableOfContents.tocReferences` is `List<TOCReference>`;
    each has `getTitle()`, `getResource()`, `getChildren()`.
  - Spine: `book.spine.spineReferences`, each `getResource()`.
- **commonmark 0.21**: `Node` has `getFirstChild()` / `getNext()` /
  `accept(Visitor)` but **no** `getChildren()`. `AbstractVisitor` defines
  only the concrete `visit(Text)`, `visit(Heading)`, ... — there is **no**
  `visit(Node)`. Walk the tree manually with `getFirstChild()`/`getNext()`;
  use `Text.literal` and `Heading.level`.
- **android.speech.tts.TextToSpeech**: there is **no** `pause()` / `resume()`.
  Implement pause as `tts.stop()` while holding a PAUSED state; implement
  resume as re-queueing from the saved segment index.
- **android.graphics.pdf.PdfRenderer.Page**: there is **no** `getText()`.
  Use `page.textContents` -> `List<PdfPageTextContent>`, each with `getText()`.
- **Kotlin coroutines**: `suspendCancellableCoroutine { cont -> ... }`
  must `import kotlin.coroutines.resume` and guard with `if (cont.isActive) cont.resume(...)`.
- **Hilt bindings**:
  - `@Binds` requires the implementation to have an `@Inject constructor`.
    A parser with no deps still needs `@Inject constructor()` for `@Binds` to bind it.
  - Provide `android.content.Context` via
    `@Provides fun appContext(@ApplicationContext c: Context): Context`
    in a `@InstallIn(SingletonComponent::class)` module.

## 4. Android resource errors (real ones hit)

- A theme derived from a plain `android:Theme.*` has **no** `?attr/colorPrimary`.
  Point splash `windowSplashScreenBackground` at a literal `@color/...` instead.
- The manifest references `@mipmap/ic_launcher` — if you never created
  launcher icons, add `mipmap-anydpi-v26/ic_launcher.xml` (adaptive-icon)
  plus a `@drawable/ic_launcher_foreground` vector, or the resource link fails.
