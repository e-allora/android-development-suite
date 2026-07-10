# Project Context

> Shared source of truth for the Android Development Suite. Every skill reads
> this file. Copy it to your repo root as `PROJECT_CONTEXT.md` and keep it
> updated as ADRs change decisions. Do NOT let skills invent conventions that
> contradict this document.

## Product
- App name: [app name]
- One-line purpose: [what problem it solves]
- Target audience: [personas]
- Platforms: [phone, tablet, Wear, TV] — minSdk [26]
- Distribution: [Play Store / open testing / internal]

## Tech Stack (decided — do not relitigate without an ADR)
- Language: Kotlin (2.x)
- UI: Jetpack Compose (Material3)
- Architecture: MVVM + Clean Architecture (multi-module)
- DI: Hilt
- Local data: Room
- Remote data: Retrofit + OkHttp (kotlinx.serialization)
- Async: Kotlin Coroutines + Flow
- Images: Coil
- Navigation: Compose Navigation (type-safe args)
- Maps/graph: [library]

## Conventions
- Package: `com.<company>.<app>`
- Module layout: `:app`, `:core:ui`, `:core:common`, `:core:domain`,
  `:core:data`, `:feature:*`
- Naming: Feature = PascalCase; files `<Feature>ViewModel.kt`,
  `<Feature>Screen.kt`, `<Feature>UiState.kt`, `<Feature>Repository.kt`.
- UiState: one sealed interface per screen (Loading/Error/Success).
- Strings: all in `res/values/strings.xml` (no hardcoded text).
- Tests: JUnit + Truth + MockK + Turbine; Compose UI via
  `createAndroidComposeRule` / Roborazzi.

## Architecture Rules (enforced by android-review-skill)
- UI never imports Retrofit/Room directly.
- `:core:domain` has zero Android dependencies.
- `feature:*` depends only on `:core:domain` + `:core:ui`.
- Single source of truth: network writes update the DB; UI observes the DB.

## CI / Quality Gates
- Lint + Detekt + Ktlint must be clean to merge.
- Minimum coverage: `:core:domain` 90%, `:core:data` 80%, `:feature:*` 70%.
- Merge only after Review approves (no critical/major) and tests pass.

## Release
- Signing: Play App Signing (upload key in CI secrets).
- Versioning: `versionCode = MAJOR*10000 + MINOR*100 + PATCH`.
- Rollout: internal → closed → production 10% → 50% → 100%.

## Open Decisions / ADRs
- [ADR-1: …]  [ADR-2: …]
