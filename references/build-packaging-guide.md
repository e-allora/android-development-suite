# Build & Packaging Guide

Companion to `android-build-skill`. Produces reproducible, release-ready builds.

## Gradle / AGP

- Use a **version catalog** (`gradsle/libs.versions.toml`) for all versions.
- AGP 8.x, Kotlin 2.x, Compose BOM aligned.
- KSP (not kapt) for Room/Hilt codegen.
- `compileSdk`/`targetSdk` = latest stable; `minSdk` per audience (26 common).

## Build Types

```kotlin
buildTypes {
    debug {
        isMinifyEnabled = false
        applicationIdSuffix = ".debug"
    }
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro",
        )
        signingConfig = signingConfigs.getByName("release")
    }
}
```

## Product Flavors (only if the product needs them)

```kotlin
flavorDimensions += "tier"
productFlavors {
    create("free") { dimension = "tier"; applicationIdSuffix = ".free" }
    create("pro")  { dimension = "tier"; applicationIdSuffix = ".pro" }
}
// Or environment dimension: create("staging") / create("prod")
```

## Versioning

- `versionCode`: monotonic `int` (`MAJOR*10000 + MINOR*100 + PATCH`).
- `versionName`: semver string.
- Bump `versionCode` on *every* Play upload (Google rejects reuse).

## Signing

```kotlin
signingConfigs {
    create("release") {
        storeFile = file(System.getenv("KEYSTORE_FILE") ?: "debug.keystore")
        storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
        keyAlias = System.getenv("KEY_ALIAS") ?: ""
        keyPassword = System.getenv("KEY_PASSWORD") ?: ""
    }
}
```

- Prefer **Play App Signing**: upload key held by Google, rotation possible.
- Never commit keystores; inject via CI secrets.

## R8 / ProGuard Keep Rules

- kotlinx.serialization, Retrofit (`Call`/`Response`/`Continuation`),
  Room (`RoomDatabase` init), Hilt/Dagger (`@Inject` members).
- Test release builds on a device — R8 can silently break reflection.

## CI Pipeline (GitHub Actions)

Lint → static analysis → unit tests → build AAB → upload artifact. Secrets
injected for signing. See `android-build-skill` for the full YAML and the
QA skill for the test/coverage gate.

## Quality Gates (pre-build)

- `lint` clean · `detekt`/`ktlintCheck` clean · `testDebugUnitTest` green ·
  `versionCode` incremented · no secrets in VCS.
