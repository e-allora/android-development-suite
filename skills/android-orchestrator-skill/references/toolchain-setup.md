# Toolchain Setup — Android builds without an SDK preinstalled

Copy-adaptable, root-free install snippets for when a generic Linux box lacks
the Android toolchain. Created after a session where the build box had neither
the Android SDK nor a Kotlin compiler; the user's standing rule is *"just install
what you need"* (never halt the pipeline to ask permission over a missing
binary, and never declare the task impossible because a tool isn't present).

## Guardrails (from user preference)
- Install into `~/` (e.g. `~/jdk17`, `~/Android/Sdk`, `~/tools/kotlinc`).
  NEVER write into `/opt`, `/usr`, or system paths unless the user explicitly
  approves — a user can block a command touching `/opt`; honor that and pick a
  home-dir path.
- Prefer official self-contained distributions over `apt`: apt's `kotlin` is
  1.3.x, far too old for AGP (which needs Kotlin 2.0.x + JDK 17/21).
- Run long installs in the background (`terminal(background=true,
  notify_on_complete=true)`) and keep authoring source in parallel — the install
  is independent of writing the code.
- If the user blocks a specific destructive command (e.g. `unzip` into `/opt`),
  do NOT retry or rephrase to achieve the same outcome; pause and ask for a
  path they'll accept.

## JDK 17 (Temurin, root-free)
```bash
JDK_DIR=$HOME/jdk17
curl -sL "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse" -o /tmp/jdk17.tar.gz
mkdir -p "$JDK_DIR" && tar -xzf /tmp/jdk17.tar.gz -C "$JDK_DIR" --strip-components=1
export JAVA_HOME="$JDK_DIR"
"$JDK_DIR/bin/java" -version
```

## Android SDK command-line tools (root-free)
```bash
export ANDROID_HOME=$HOME/Android/Sdk
mkdir -p "$ANDROID_HOME/cmdline-tools"
curl -sL -o /tmp/cmdline.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
rm -rf "$ANDROID_HOME/cmdline-tools/latest"
unzip -q /tmp/cmdline.zip -d "$ANDROID_HOME/cmdline-tools"
mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
yes | sdkmanager --sdk_root="$ANDROID_HOME" --licenses >/dev/null
sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools" "platforms;android-35" "build-tools;35.0.0"
```

## Standalone Kotlin compiler (no SDK needed — for JVM-only verification)
Use this to compile + run the **pure-Kotlin domain** (`core:domain` is kept free
of Android deps by design), e.g. to prove a state machine or parser logic
without Gradle/AGP/SDK:
```bash
curl -sL -o /tmp/kotlin.zip "https://github.com/JetBrains/kotlin/releases/download/v2.0.21/kotlin-compiler-2.0.21.zip"
mkdir -p "$HOME/tools/kotlinc" && unzip -q /tmp/kotlin.zip -d "$HOME/tools/kotlinc"
# compile
"$HOME/tools/kotlinc/kotlinc/bin/kotlinc" -include-runtime -d /tmp/app.jar src/**
# run a main / JUnit (add junit jar to classpath)
"$HOME/tools/kotlinc/kotlinc/bin/kotlinc" -classpath /tmp/junit.jar -d /tmp/domtest.jar domain-jvm/test/**
```

## Why this matters (SDK-free domain proof)
The architecture's rule "`:core:domain` has zero Android dependencies" means the
domain layer — models, `TtsPlayer` state machine, `DocumentParser` strategy
interfaces, repository contracts — is plain Kotlin. That part can be:
- extracted into a JVM-only module (`domain-jvm/src` + `domain-jvm/test`),
- compiled with the standalone `kotlin-compiler`, and
- unit-tested on the JVM (JUnit) WITHOUT the Android SDK.
This lets the orchestrator *prove* a meaningful slice of the build green even
before the full Gradle/AGP toolchain is installed — turning "I can't verify it
compiles" into "I verified the core logic compiles and passes."
