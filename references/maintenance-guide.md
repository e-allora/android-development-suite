# Maintenance & Regression Guide

Companion to `android-maintenance-skill`. Keeps the app healthy across versions.

## Regression Strategy

- Identify **critical user journeys** (sign-in, core create/read, purchase).
- Map each to an automated test (unit/UI/integration) AND a manual smoke item.
- Run the automated regression on every release candidate; manual smoke on the
  staged rollout.
- Define a crash-free / ANR budget and alert on regression.

## Room Migration Strategy

- Bump `@Database(version = N)` on every schema change.
- Prefer `autoMigrations = [AutoMigration(from = N-1, to = N)]`.
- For complex changes, write and **test** a manual `Migration` against real
  user data (Robolectric + a pre-migration DB fixture).
- `fallbackToDestructiveMigration` only acceptable pre-1.0 or for pure-cache
  tables. Never silently wipe user data in production.

```kotlin
@Database(
    entities = [ProfileEntity::class],
    version = 2,
    autoMigrations = [AutoMigration(from = 1, to = 2)],
)
abstract class AppDatabase : RoomDatabase()
```

## Feature Flags

Taxonomy:

- **release** — gradual rollout (1% → 10% → 50% → 100%).
- **experiment** — A/B via Remote Config.
- **kill-switch** — instant off if something breaks.

Implementation: Firebase Remote Config (runtime) or build-time `BuildConfig`
flags. Always provide a fallback UI path and a documented rollback.

## Observability

- Crashlytics + Play Vitals.
- Budgets: crash-free sessions ≥ 99.5%, ANR < 0.47%.
- Key analytics events: `app_open`, `sign_in`, `key_action`, `purchase`.
- Alert on > 0.1% week-over-week regression.

## Deprecation Policy

1. Flag the feature off (kill-switch) before removal.
2. Communicate in release notes / in-app banner.
3. Preserve stored data + deep links during the transition.
4. Remove code only after the flag has been off for a full release cycle.

## Post-Mortem / Retrospective

For any Sev-1: timeline, root cause, impact, action items with owners. Feed
learnings back to Product (next iteration) and Architecture (contract drift).
