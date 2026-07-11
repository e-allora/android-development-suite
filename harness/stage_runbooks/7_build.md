# Stage 7 — Build

## Goal
A release AAB that builds clean, signs with the right key, and the CI
pipeline that produces it on every tag.

## Inputs
- The QA-passed code.
- The signing config (key alias, store path, passwords — all in env
  vars or a secrets manager, NEVER in `gradle.properties` or
  `local.properties`).
- The architecture's decision on flavors and build types.

## Clarifications to ask
1. **Signing key source** — local keystore, or Google Play App Signing
   with upload key? Default: Play App Signing (upload key only on
   the dev machine; Play handles the app key).
2. **Flavors** — none (single flavor, default), or paid/free / dev/
   staging/prod? Default: dev + prod.
3. **R8** — on for release (default, recommended), or off (for easier
   debugging)? Default: on.
4. **CI provider** — GitHub Actions (default), GitLab CI, Bitrise,
   CircleCI? Default: GitHub Actions.

## Output
- `<root>/app/build.gradle.kts` — updated with signing config (env-var
  sourced), flavors, R8/ProGuard rules.
- `<root>/.github/workflows/release.yml` — builds the release AAB on
  tag push.
- `<root>/docs/build.md` — what the build does, how to reproduce it
  locally, what the CI does.

## Verification
- `./gradlew :app:assembleRelease` exits 0, produces an AAB.
- `bundletool build-apks --bundle=...aab` succeeds.
- AAB is signed (verify with `apksigner verify` or
  `bundletool`).
- `git secrets` / `gitleaks` finds no committed keystores or tokens.

## Done report format
```
[Stage 7 — Build] done.
Artifact: <root>/app/build/outputs/bundle/release/app-release.aab
Verified by:
  - ./gradlew :app:assembleRelease -> exit 0
  - ls -la app/build/outputs/bundle/release/app-release.aab
  - apksigner verify app-release.aab -> exit 0
AAB size: <MB>
Signed by: <key alias>
R8: enabled
Flavors: dev, prod
CI: GitHub Actions (release.yml)
Limitations:
  - Real-device install not done in this environment
  - No Play Console upload yet (Stage 8)
Open issues: <N>
Next: 8_release
```

## Next stage
Stage 8 — Release. The release engineer uploads to Play Console,
writes the store listing, and configures the staged rollout.
