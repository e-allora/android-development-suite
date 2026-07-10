# R8 / ProGuard Gotchas for Android

## kxml2 XmlPullParser conflict with epublib

epublib pulls in `net.sf.kxml:kxml2` which bundles its own `org.xmlpull.v1.XmlPullParser`.
Android SDK already has `android.content.res.XmlResourceParser` which extends XmlPullParser.
R8 sees two copies and fails with:

```
Library class android.content.res.XmlResourceParser implements program class org.xmlpull.v1.XmlPullParser
```

**Fix:** Exclude BOTH xmlpull and kxml2 from epublib in `build.gradle.kts`:

```kotlin
implementation(libs.epublib) {
    exclude(group = "xmlpull", module = "xmlpull")
    exclude(group = "net.sf.kxml", module = "kxml2")
}
```

The epublib Author class still works because kxml2 is only needed at runtime
for XML parsing, and Android's built-in XmlPullParser handles it.

## ProGuard keep rules to suppress warnings

```proguard
# Let Android SDK supply XmlPullParser
-dontwarn org.xmlpull.v1.**
-dontwarn org.kxml2.**
-keep class org.xmlpull.v1.** { *; }
```

## Release build checklist
- Always test on a **release** build, not debug — R8 issues only surface with minification
- `./gradlew :app:bundleRelease` for AAB; `assembleRelease` for APK
- Verify with `lintRelease` before building
- The `isMinifyEnabled = true` + `isShrinkResources = true` combo catches R8 issues
