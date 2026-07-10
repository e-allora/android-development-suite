# Release Checklist

> **Reference** — Android Development Suite
> Pre-release verification checklist for shipping Android apps to the Play Store.

---

## 1. Version & Build Config

- [ ] `versionCode` incremented monotonically (no reuse of a previously
      uploaded code).
- [ ] `versionName` follows semantic versioning (`MAJOR.MINOR.PATCH`).
- [ ] `applicationId` matches the production package name.
- [ ] `minSdk` / `targetSdk` / `compileSdk` updated to supported levels.
- [ ] `buildConfig` fields for environment (e.g. `BASE_URL`) point to
      production endpoints.
- [ ] No debug `applicationIdSuffix` or `versionNameSuffix` in the release
      variant.

---

## 2. R8 / ProGuard

- [ ] `release { isMinifyEnabled = true }` set in `app/build.gradle.kts`.
- [ ] `isShrinkResources = true` enabled.
- [ ] `proguard-rules.pro` includes keep rules for:
  - [ ] **kotlinx.serialization** — `@Keep @Serializable` models, `@SerialName`
        companion serializers.
  - [ ] **Retrofit** — service interfaces, generic type parameters.
  - [ ] **Room** — DAO interfaces and entity classes (Room handles most via
        KSP, but verify).
  - [ ] Reflection-based libraries (Gson, Moshi if used).
- [ ] App tested on a **release** build (not just debug) to catch R8 issues.

### Common Keep Rules

```proguard
# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.example.app.**$$serializer { *; }
-keepclassmembers class com.example.app.** {
    *** Companion;
}
-keepclasseswithmembers class com.example.app.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# Retrofit
-keepattributes Signature, Exceptions
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response
-keep,allowobfuscation,allowshrinking class kotlin.coroutines.Continuation

# Room (usually handled by KSP, but verify)
-keep class * extends androidx.room.RoomDatabase { <init>(); }
-dontwarn androidx.room.paging.**

# Hilt (usually safe, but keep @Inject constructors if using reflection)
-keepclassmembers,allowobfuscation class * {
    @javax.inject.Inject *;
}
```

---

## 3. Permissions Audit

- [ ] Review all `<uses-permission>` declarations in `AndroidManifest.xml`.
- [ ] Remove unused permissions.
- [ ] Justify each dangerous permission in the Play Console Data Safety form.
- [ ] Runtime permission flows tested on a clean install.
- [ ] `tools:node="remove"` used for transitive permissions you don't need.

> Run the suite audit CLI:
> `python3 scripts/android_suite_tool.py audit --project-dir . --check-permissions`

---

## 4. App Bundle (AAB)

- [ ] Build the release artifact as an **AAB** (`./gradlew :app:bundleRelease`).
- [ ] Verify the AAB with `bundletool build-apks` and install on a device.
- [ ] Confirm asset packs / dynamic feature modules (if any) are included.
- [ ] Check APK size with `bundletool get-size total`.

---

## 5. Signing

- [ ] Release keystore stored in a secure location (CI secrets, not in repo).
- [ ] `signingConfig` references environment variables, not hardcoded paths.
- [ ] Keystore password, key alias, and key password in CI secrets.
- [ ] APK/AAB verified with `apksigner verify --verbose`.
- [ ] Signing key rotation configured if using Play App Signing (recommended).

### Signing Config Template

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

---

## 6. Store Listing

- [ ] App title, short description, and full description updated.
- [ ] New screenshots for phone, tablet (7" and 10"), and any other form
      factors.
- [ ] Feature graphic uploaded (1024×500).
- [ ] App icon (512×512) matches the launcher icon.
- [ ] Category and tags updated.
- [ ] Privacy policy URL is live and accessible.
- [ ] Contact email / website correct.

---

## 7. Data Safety Form

- [ ] Declared all data types collected (e.g., email, location, photos).
- [ ] Declared all data types shared with third parties.
- [ ] Encryption in transit marked (HTTPS for all network calls).
- [ ] Data deletion option documented if account-based.
- [ ] Reviewed against the actual permissions and SDK data practices.

---

## 8. Testing

- [ ] All unit tests pass (`./gradlew test`).
- [ ] All instrumented tests pass (`./gradlew connectedAndroidTest`).
- [ ] Screenshot tests reviewed (Roborazzi).
- [ ] Tested on at least one small screen and one large screen.
- [ ] Tested on Android 14+ (targetSdk) and Android 8+ (minSdk).
- [ ] Smoke test on a **release** build, not just debug.
- [ ] Deep links and notifications tested.

---

## 9. Crash & ANR Prevention

- [ ] Crash reporting integrated (Firebase Crashlytics, Sentry, etc.).
- [ ] ANR-prone operations (disk I/O, network) moved off the main thread.
- [ ] `StrictMode` reviewed in debug builds for accidental disk/network on main.
- [ ] Out-of-memory scenarios tested (large images, long lists).
- [ ] Background work uses WorkManager, not raw services.

---

## 10. Rollout Strategy

- [ ] Internal testing track (fresh install + upgrade path).
- [ ] Closed testing (alpha) with a small group of testers.
- [ ] Open testing (beta) if applicable.
- [ ] Staged rollout on production (start at 10%, increase to 50%, then 100%).
- [ ] Rollback plan documented (use Play Console "Roll back release").

---

## 11. Post-Release Verification

- [ ] Production build downloaded from the Play Store and smoke-tested.
- [ ] Crash-free users > 99.5% in the first 24 hours.
- [ ] ANR rate below 0.47% (Play Store threshold).
- [ ] Monitor store reviews and respond to issues.
- [ ] Tag the release in git (`git tag v1.x.x`).
- [ ] Update internal release notes / changelog.
- [ ] Schedule a retrospective if major issues were found.
