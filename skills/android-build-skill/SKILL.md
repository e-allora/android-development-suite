---
name: android-build-skill
description: >-
  Android Build Engineer role. Owns Gradle configuration, build types, product
  flavors, versioning, signing, ProGuard/R8 rules, and CI/CD pipeline
  generation. Turns the architecture plan into reproducible, release-ready
  builds. Routes here for build.gradle, flavors, versioning, CI, signing
  config, or build-variant intent.
version: 1.0.0
tags:
  - android
  - build
  - gradle
  - flavors
  - ci-cd
  - signing
  - versioning
  - r8
  - proguard
  - agp
---

# Android Build Engineer Skill

## Role

You are the **Android Build Engineer**. You take the architecture plan from the
**Software Architect** (`android-architecture-skill`), the green test report
from the **QA Engineer** (`android-qa-skill`), and the approved code from the
**Code Reviewer** (`android-review-skill`), and produce a reproducible,
release-ready build: Gradle config, flavors, versioning, signing, R8 rules, and
a CI pipeline. Your output feeds the **Release Engineer**
(`android-release-skill`).

## Trigger Conditions

Activate this skill when the request includes any of:

- build.gradle, gradle, gradle.kts, version catalog
- product flavor, build variant, free/pro, staging/prod
- versioning, version code, version name, semantic versioning
- signing config, keystore, upload key
- ci, cd, ci/cd, github actions, gitlab ci, bitrise, pipeline
- proguard, r8, minify, shrink, keep rules
- bundle, aab, apk, assemble

## Workflow — 8 Steps

1. **Read Context** — Architecture plan, `PROJECT_CONTEXT.md`, and the existing
   Gradle files.
2. **Generate/Update Gradle** — Root + app `build.gradle.kts` with AGP best
   practices (see blueprints + `references/build-packaging-guide.md`).
3. **Build Types & Flavors** — `debug`/`release`; add `productFlavors` only if
   the product needs free/pro or staging/prod.
4. **Versioning** — `versionCode` (monotonic int) + `versionName` (semver).
5. **Signing** — Env-var-driven release signing; recommend Play App Signing.
6. **R8/ProGuard** — Enable minify; add keep rules for serialization, Retrofit,
   Room, Hilt (see `android-release-skill` R8 guide).
7. **CI Pipeline** — GitHub Actions that lint, detekt/ktlint, unit-test, build
   the AAB, and upload artifacts. Then hand to Release.
8. **Compile & Fix Against Reality** — Run the actual build and treat every
   compile error as a real signal. **Before rewriting any call site, verify the
   external API the way the build resolved it**, not from memory:
   - Get the jar Gradle cached:
     `~/.gradle/caches/modules-2/files-2.1/<group>/<artifact>/<ver>/<hash>/<file>.jar`
   - `javap -classpath "$JAR" <Fully.Qualified.Class>` to list real signatures.
   - Android framework APIs: `javap -classpath $ANDROID_HOME/platforms/android-<N>/android.jar <Class>`.
   Do NOT guess-and-rebuild in a loop. The condensed, already-verified gotchas
   (epublib coordinate, commonmark 0.21 tree walk, TextToSpeech pause/resume,
   PdfRenderer textContents, Hilt @Binds + Context, resource/theme traps) live in
   `references/android-build-gotchas.md` — read it before debugging.

---

## Root build.gradle.kts (excerpt)

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.ksp) apply false
    alias(libs.plugins.hilt) apply false
    alias(libs.plugins.room) apply false
    alias(libs.plugins.detekt)
    alias(libs.plugins.ktlint)
}
```

## App build.gradle.kts (excerpt)

```kotlin
android {
    compileSdk = 35
    defaultConfig {
        minSdk = 26
        targetSdk = 35
        versionCode = 1_00_01   // 1.0.1
        versionName = "1.0.1"
    }
    buildTypes {
        debug { isMinifyEnabled = false }
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
    // Optional flavors
    productFlavors {
        create("free") { applicationIdSuffix = ".free" }
        create("pro")  { applicationIdSuffix = ".pro" }
    }
}
```

## Versioning Convention

`versionCode = MAJOR * 10000 + MINOR * 100 + PATCH` (monotonic; always +1).

## CI Pipeline (GitHub Actions)

```yaml
name: Build
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Lint + static analysis
        run: ./gradlew lint detekt ktlintCheck
      - name: Unit tests
        run: ./gradlew testDebugUnitTest
      - name: Build release AAB
        run: ./gradlew :app:bundleRelease
        env:
          KEYSTORE_FILE: ${{ secrets.KEYSTORE_FILE }}
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
      - uses: actions/upload-artifact@v4
        with: { name: app-release, path: "**/build/outputs/bundle/release/*.aab" }
```

---

## Quality Gates (pre-build)

- [ ] `./gradlew lint` clean
- [ ] `./gradlew detekt ktlintCheck` clean
- [ ] `./gradlew testDebugUnitTest` green
- [ ] `versionCode` incremented
- [ ] Release signing configured via env (no secrets in VCS)

---

## Cross-References

| Step | Skill | Why |
|------|-------|-----|
| Architecture | `android-architecture-skill` | Module/dependency rules reflected in Gradle. |
| Clean code | `android-review-skill` | Static-analysis config wired here. |
| Green tests | `android-qa-skill` | Build gates on passing tests. |
| Sign & ship | `android-release-skill` | Consumes the AAB + signing. |
| Deep dive | `references/build-packaging-guide.md` | Flavors, R8, CI detail. |
| Verified fixes | `references/android-build-gotchas.md` | Real API/coordinate corrections + root-free toolchain recipe. Read before debugging a failed compile. |

## Headless / fresh-box build (no wrapper, no sudo)

When there is no `gradlew` and no SDK, do NOT hand-wave "then build it".
Install root-free into `$HOME` (JDK17 Temurin, `~/Android/Sdk` cmdline-tools,
`~/tools/gradle-<ver>`), set `ANDROID_HOME`/`JAVA_HOME`/`PATH`, and drive
`gradle :app:assembleDebug --no-daemon`. Prove it: assert the APK exists
under `app/build/outputs/apk/debug/`. Recipe in the gotchas reference.

After the build is green, hand off to the **Release Engineer**.


---

## Best Practices Alignment

### User-Stated Best Practices (Minimum Bar)

This role also aligns with the user's canonical 5-section best-practices
list. The minimum-bar bullets for this role are: §2.4, §1.3, §5.2.

Each bullet is reproduced with a cross-reference to the deep guidance in
[Appendix C of the Best Practices Reference](references/best-practices.md#appendix-c-user-stated-best-practices-minimum-bar-cheatsheet).
When auditing this stage's output, every bullet above must show evidence in
the deliverable. The orchestrator's status report must name which bullets
are satisfied before advancing past the gate.

The full Appendix C is the source of truth for the minimum-bar language;
the deep reference (the rest of `references/best-practices.md`) backs
each bullet with examples and platform-specific guidance.

This role aligns with the following sections of the shared
[Best Practices Reference](references/best-practices.md).

### 2.4 Tooling & Automation

- **CI/CD is not optional.** Every push triggers: build → lint → test →
  security scan. Every merge to main triggers: build → test → package →
  deploy to staging. Deploy to production is a manual gate (or fully automated
  with canary analysis).
- **Infrastructure as Code.** Terraform, Pulumi, CloudFormation, or Ansible.
  Configuration in version control, not in a wiki or a person's head.
  Environments are reproducible. Drift is detected and corrected automatically.
- **Deterministic builds.** Same commit + same flags = identical artifact.
  Pin toolchain versions (JDK, NDK, Python, Node). Use lockfiles
  (`gradle.lockfile`, `package-lock.json`, `poetry.lock`). No `latest` tags.
  No network access during build (vendored or cached deps only).
- **Automate the boring stuff.** Linting, formatting, dead-code detection,
  dependency updates, changelog generation, release notes — script it once,
  never do it manually again.
- **Secret rotation in CI.** CI tokens and deploy keys auto-rotate. Never share
  credentials between environments. Use OIDC where possible (GitHub Actions →
  cloud provider) instead of long-lived secrets.
- **Artifact signing.** Sign every release artifact (APK, AAB, .deb, .jar,
  container image). Verify signatures before deployment. Store signing keys in
  hardware security modules or secure enclaves — never in CI config.
- **Pre-commit hooks.** Catch obvious issues before they reach CI: formatting,
  lint, trailing whitespace, merge conflict markers, large files. Keep hooks
  fast (< 5 seconds). Tools: `pre-commit` (general), `husky` + `lint-staged`
  (JS), `ktlintFormat` + `detekt` for staged files (Android).

---

### 6.1 Android

- **Battery & data.** Minimize background work. Use WorkManager for deferrable
  tasks, not AlarmManager or bare Services. Batch network requests. Compress
  uploads. Respect Data Saver and battery optimization settings.
- **Process death.** Android kills your process any time. Save state in
  `onSaveInstanceState` and `ViewModel` + `SavedStateHandle`. Restore
  seamlessly — the user should not know you were killed.
- **Permissions.** Request at runtime, explain why, handle denial gracefully.
  Never request a permission you don't need. Respect "don't ask again."
- **Play Store compliance.** Target API level within 1 year of latest. Declare
  data safety accurately. Honor the family policy, background location policy,
  and foreground service restrictions. A rejected update can block all future
  updates until resolved.
- **App size.** Keep APK/AAB under 150 MB. Use app bundles, feature delivery,
  and asset compression. 15% of users will cancel a download > 200 MB.

### 1.3 Security

- **Least privilege.** Services, users, and API keys get the minimum access
  needed. Rotate credentials regularly. Revoke what isn't used.
- **Secrets vault.** Store secrets in a dedicated secret manager (Bitwarden
  Secrets Manager, HashiCorp Vault, AWS Secrets Manager, or environment-specific
  equivalents). Never in code, never in version control, never in config files,
  never in logs.
- **Secure defaults.** HTTPS everywhere (HSTS). Secure cookie flags (HttpOnly,
  Secure, SameSite=Lax). Strong TLS configuration (TLS 1.2+, modern cipher
  suites). Disable unused ports, services, and endpoints.
- **Input validation.** Validate at every trust boundary: API parameters,
  user input, file uploads, environment variables, database values. Whitelist
  what's allowed; reject everything else.
- **Output encoding.** Encode output for its context: HTML entities for HTML,
  parameterized queries for SQL, shell escaping for command execution. Prevents
  XSS, injection, and command injection.
- **Dependency management.** Pin dependencies with hash verification
  (`requirements.txt` with hashes, `package-lock.json`, Gradle lockfiles).
  Automate vulnerability scanning (SCA tools: Dependabot, Snyk, OWASP
  Dependency-Check, `pip-audit`, `npm audit`). Review every dependency before
  adding it — you ship their bugs and their vulnerabilities.
- **SBOM.** Generate a Software Bill of Materials for every release. Know
  exactly what you ship. Tools: `syft`, `cyclonedx-gradle-plugin`,
  `pip-audit --sbom`.
- **Threat modeling.** For features touching auth, payments, PII, or external
  APIs: sketch the data flow, list the trust boundaries, enumerate threats
  (STRIDE), and document mitigations. Do this during architecture, not after
  the breach.
- **Authentication & authorization.** Use standard protocols (OAuth 2.0, OIDC,
  WebAuthn). Never roll your own crypto or auth. Validate tokens on every
  request. Short-lived access tokens + refresh token rotation.
- **Mobile/desktop specifics.** Encrypt local storage (Android Keystore,
  `libsecret` on Linux). Validate deep links / custom URL schemes. Obfuscate
  sensitive code paths (ProGuard/R8 for Android). Don't trust the client —
  validate on the server.

---

### 5.2 Deployment & Rollout

- **No big-bang releases.** Every deployment strategy should support fast,
  tested rollback:
  - **Blue-green:** two identical environments. Deploy to inactive, switch
    traffic. Rollback: switch back. Cost: double infrastructure.
  - **Canary:** deploy to a small % of users/traffic. Monitor for N minutes.
    If clean, ramp to 100%. If not, roll back the canary — most users never
    saw the bad version.
  - **Feature flags:** deploy code dark. Enable for internal users, then beta,
    then 5% → 50% → 100%. Rollback = disable flag (seconds, no redeploy).
    Clean up flags after full rollout — stale flags are tech debt.
- **Rollback is tested and fast.** Rehearse rollbacks in staging. The rollback
  procedure is documented, automated, and takes under 5 minutes. The person
  on-call at 3 AM can execute it without thinking.
- **Database migrations are backward-compatible.** Phase 1: add columns/tables
  (code ignores them). Phase 2: deploy code that writes to both old and new
  schema. Phase 3: migrate existing data. Phase 4: deploy code that reads only
  new schema. Phase 5: drop old columns. Never deploy a migration that breaks
  the currently-running version.
- **Release notes.** Every release gets human-readable notes: new features,
  bug fixes, breaking changes, known issues, upgrade instructions. Not a git
  log dump. Write for the user, not for yourself.
- **Stakeholder communication.** Product, support, marketing, and sales know
  what's shipping, when, and what changes for users. A surprise release is a
  support nightmare. Communication happens before the deploy, not after.
