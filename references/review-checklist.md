# Code Review Checklist & Static Analysis

Companion to `android-review-skill`. The reviewer enforces these rules and
gates merges on open *critical*/*major* issues.

## Architecture Conformity

- UI layer never imports Retrofit/Room/OKHttp directly.
- `domain` module has zero Android framework dependencies.
- Dependency rule honored: `feature:* → core:domain, core:ui`; `:app → all`.
- No layer leakage (e.g., a ViewModel calling an `@Dao` directly).

## Kotlin Idioms

- Prefer `val`; avoid `var` at class scope.
- No `!!`; use `?.let`, `checkNotNull`, or `require`.
- Expected failures modeled as `Result<>`/sealed errors, not thrown exceptions.
- Use scope functions (`let/run/apply`) without nesting past 2 levels.

## Lifecycle Safety

- Collect `StateFlow` with `collectAsStateWithLifecycle()` (UI) /
  `repeatOnLifecycle` (effects).
- No `viewModelScope.launch` that ignores cancellation.
- `DisposableEffect`/`LaunchedEffect` cleaned up; no leaked listeners.
- `remember` keys correct; no `remember { mutableStateOf() }` captured wrongly.

## Coroutines & Threading

- IO on `Dispatchers.IO`; UI on `Dispatchers.Main`.
- No `runBlocking` on the main thread.
- Structured concurrency: child failures handled; `supervisorScope` where needed.
- Inject `CoroutineDispatcher` (or `StandardTestDispatcher`) for testability.

## Error Handling

- Boundaries convert exceptions → `Result`/sealed error.
- User-facing messages localized (string resources).
- No swallowed `catch (e: Exception) {}`.
- Network failures degrade gracefully (offline cache, retry).

## Security

- No hardcoded API keys / secrets. Use `BuildConfig` + CI secrets or a
  secrets backend.
- HTTPS + cert pinning for sensitive endpoints.
- Exported components (`exported=true`) require permission or validation.
- Deep-link / intent extras validated before use.

## Compose Performance

- Stable parameters; wrap unstable lambdas or hoist.
- `derivedStateOf` for derived state; `remember` for expensive computations.
- Correct `key`/`itemKey` in `Lazy*` lists.
- Side effects only in `LaunchedEffect`/`DisposableEffect`/`produceState`.

## Static Analysis Tooling

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.detekt)
    alias(libs.plugins.ktlint)
}
detekt {
    toolVersion = "1.23.7"
    buildUponDefaultConfig = true
    config.setFrom("config/detekt/detekt.yml")
}
ktlint { version.set("1.3.1"); filter { include("**/kt") } }
```

Run as a CI gate: `./gradlew detekt ktlintCheck`. Both must be clean to merge.

## Severity Model

- **critical** — crash / data loss / security hole / architecture violation.
- **major** — correctness bug / lifecycle leak / untested critical path.
- **minor** — style / naming / micro-optimization (track, don't block).
