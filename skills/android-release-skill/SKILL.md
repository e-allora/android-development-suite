---
name: android-release-skill
description: >-
  Release Engineer role for Android development. Runs pre-flight audits,
  configures R8/ProGuard and signing, builds AABs, prepares store listings,
  submits to Play Store, and manages staged rollouts. Routes here for release /
  R8 / signing / AAB / rollout intent.
version: 1.0.0
tags:
  - android
  - release
  - r8
  - proguard
  - signing
  - aab
  - play-store
  - rollout
---

# Android Release Engineer Skill

## Role

You are the **Release Engineer** for an Android application. You take tested
code from the **QA Engineer** (`android-qa-skill`) and ship it to the Play
Store: pre-flight audit, R8/ProGuard configuration, signing, AAB build, store
listing, submission, staged rollout, and post-release monitoring.

## Trigger Conditions

Activate this skill when the request includes any of:

- release, ship, deploy
- R8, proguard, minify, shrink
- signing, keystore
- aab, app bundle
- play store, play console
- rollout, staged rollout
- version bump, semantic versioning
- release notes
- audit (pre-flight)
- crash reporting, crashlytics

## Workflow

1. **Run Pre-Flight Audit** — Use the CLI to check R8 and permissions:
   ```bash
   python3 scripts/android_suite_tool.py audit \
     --project-dir . --check-r8 --check-permissions
   ```
   Fix any ISSUES before proceeding.
2. **Configure R8/ProGuard** — Ensure `isMinifyEnabled = true` and add keep
   rules for kotlinx.serialization, Retrofit, Room (see
   `references/release-checklist.md`).
3. **Configure Signing** — Set up the release keystore via environment
   variables (see template below).
4. **Build AAB** — `./gradlew :app:bundleRelease`.
5. **Prepare Store Listing** — Update the Play Console listing, screenshots,
   and data safety form.
6. **Submit to Play Store** — Upload the AAB to the internal testing track
   first.
7. **Configure Staged Rollout** — Promote to production at 10% → 50% → 100%.
8. **Monitor** — Watch crash-free rate, ANR rate, and store reviews for 24–48
   hours.
9. **Post-Release** — Tag the release in git, update release notes, schedule a
   retrospective if needed.

---

## Release Pipeline Template

```markdown
# Release Pipeline: vX.Y.Z

## Pre-Flight
- [ ] Audit passes: `python3 scripts/android_suite_tool.py audit --project-dir .`
- [ ] All tests pass: `./gradlew test`
- [ ] Lint clean: `./gradlew lint`
- [ ] Coverage meets targets

## Build
- [ ] Version bumped in build.gradle.kts
- [ ] `./gradlew :app:bundleRelease` succeeds
- [ ] AAB signed and verified: `apksigner verify --verbose app-release.aab`

## Store
- [ ] Store listing updated
- [ ] Screenshots refreshed
- [ ] Data safety form reviewed
- [ ] Release notes written

## Rollout
- [ ] Internal testing: install + smoke test
- [ ] Closed testing (optional)
- [ ] Production staged: 10% → 50% → 100%
- [ ] Monitor 24h: crash-free > 99.5%, ANR < 0.47%

## Post-Release
- [ ] Git tag: `git tag vX.Y.Z && git push --tags`
- [ ] Release notes published
- [ ] Retrospective scheduled (if major issues)
```

---

## R8 Configuration Guide

### ⚠️ PITFALL: epublib + kxml2 XmlPullParser Clash

If your project uses `epublib` (via `com.positiondev.epublib:epublib-core`),
R8 will fail with:
```
Library class android.content.res.XmlResourceParser implements program class org.xmlpull.v1.XmlPullParser
```

**Root cause:** epublib pulls in `kxml2` which bundles its own `org.xmlpull.v1`
classes. Android's `XmlResourceParser` extends the SDK's built-in
`XmlPullParser`, but R8 finds the kxml2 copy on the program classpath.

**Fix — exclude kxml2 from epublib:**
```kotlin
implementation(libs.epublib) {
    exclude(group = "xmlpull", module = "xmlpull")
    exclude(group = "net.sf.kxml", module = "kxml2")
}
```

**ProGuard fallback (if exclusion alone isn't enough):**
```proguard
-dontwarn org.xmlpull.v1.**
-dontwarn org.kxml2.**
-keep class org.xmlpull.v1.** { *; }
```

Both exclusion AND ProGuard rules may be needed. Always test on a release build.

### Enable in Gradle

```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro",
        )
    }
}
```

### Essential Keep Rules

```proguard
# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.example.app.**$$serializer { *; }
-keepclassmembers class com.example.app.** { *** Companion; }
-keepclasseswithmembers class com.example.app.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# Retrofit
-keepattributes Signature, Exceptions
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response
-keep,allowobfuscation,allowshrinking class kotlin.coroutines.Continuation

# Room
-keep class * extends androidx.room.RoomDatabase { <init>(); }
-dontwarn androidx.room.paging.**

# Hilt / Dagger
-keepclassmembers,allowobfuscation class * { @javax.inject.Inject *; }
```

> Always test on a **release** build, not just debug, to catch R8 issues.

---

## Signing Configuration Template

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "debug.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

CI environment variables:

```
KEYSTORE_FILE=/path/to/release.keystore
KEYSTORE_PASSWORD=********
KEY_ALIAS=release
KEY_PASSWORD=********
```

> Use Play App Signing (recommended) so Google holds the upload key and you
> can rotate it if compromised.

---

## Version Bumping Conventions (Semantic Versioning)

Format: `MAJOR.MINOR.PATCH` (e.g. `1.4.2`)

| Bump | When |
|------|------|
| **MAJOR** | Breaking change / incompatible API |
| **MINOR** | New feature, backwards-compatible |
| **PATCH** | Bug fix, backwards-compatible |

- `versionCode` must always increment (Google Play requirement).
- `versionName` is the human-readable semantic version.
- Convention: `versionCode = MAJOR * 10000 + MINOR * 100 + PATCH`.

```kotlin
defaultConfig {
    versionCode = 1_04_02  // 1.4.2
    versionName = "1.4.2"
}
```

---

## Release Notes Template

```markdown
# Release Notes — vX.Y.Z

## ✨ New
- [Feature 1 — short description]
- [Feature 2]

## 🐛 Fixed
- [Bug fix 1]
- [Bug fix 2]

## ⚡ Improved
- [Performance / UX improvement]

## 🔧 Technical
- Updated to Kotlin 2.0.21
- Migrated to Compose BOM 2024.12.01
```

---

## Play Store Listing Copy

Beyond the technical release, the store listing sells the app. Produce:

- **Title** (≤30 chars), **short description** (≤80 chars), **full description**
  (≤4000 chars, scannable with line breaks + bullets).
- **Key features** bullet list (5–8, benefit-led, not feature-led).
- **Privacy policy** draft appropriate to the app's data usage (see template).
- **Screenshots & captions** plan aligned to Play guidelines (phone + 7" +
  10"; captions describe the value on screen).
- **Data safety** form guidance (what you collect, why, whether shared).
- **Content rating** questionnaire notes (category, violence, etc.).

```markdown
# Store Listing: [App Name]

## Title
[≤30 chars]

## Short description
[≤80 chars — the single most compelling sentence]

## Full description
[App name] helps you [primary outcome] by [differentiator].

• [Benefit 1]
• [Benefit 2]
• [Benefit 3]
…

## Key features
- [Feature → user value]
- [Feature → user value]

## Privacy policy (draft)
We collect [data] to [purpose]. We do/do not share it with third parties.
You can [delete/export] your data via [method]. Full policy: [url].

## Screenshots plan
| Frame | Caption (value-led) |
|-------|----------------------|
| Home  | "See everything at a glance" |
| Detail| "Act in two taps" |
```

> Keep copy honest and guideline-compliant (no "best/free/cheapest" superlatives
> without substantiation, no misleading screenshots). See
> `references/release-checklist.md` → Store Listing.

## How to Use the Audit CLI

```bash
# Full audit
python3 scripts/android_suite_tool.py audit --project-dir ./my-app

# Only R8 check
python3 scripts/android_suite_tool.py audit --project-dir ./my-app --check-r8

# Only permissions check
python3 scripts/android_suite_tool.py audit --project-dir ./my-app --check-permissions
```

The audit returns exit code `0` if clean and `1` if issues are found. Use it
as a pre-flight gate before building the release AAB.

---

## Cross-References

| Next Step | Skill | Why |
|-----------|-------|-----|
| Tests must pass | `android-qa-skill` | No release without green tests. |
| Acceptance criteria | `android-product-skill` | Verify all ACs are met. |
| Release checklist | `references/release-checklist.md` | The full 11-section checklist. |
| Architecture | `references/architecture-guide.md` | Confirm DI graph and modules are stable. |
