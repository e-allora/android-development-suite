# Stage 9 — Maintenance

## Goal
A `docs/maintenance-plan.md` that defines how the app is kept healthy
after release: regression tests, migration policy, feature flags, and
the on-call runbook.

## Inputs
- The released app (Stage 8 done).
- The architecture's persistence layer (migrations, schema version).
- The release report (what's in production, what's the rollout state).

## Clarifications to ask
1. **Observability** — Crashlytics (default) vs. self-hosted
   (Sentry/Prometheus) vs. none. Default: Crashlytics unless the app
   is privacy-sensitive.
2. **Feature flag service** — local file-based (default for v1),
   Firebase Remote Config, LaunchDarkly, Flagsmith. Default: local
   file-based.
3. **Update cadence** — every 2 weeks, every month, ad-hoc? Default:
   every 4 weeks for minor, ad-hoc for hotfixes.
4. **On-call** — is the user the on-call, or is there a team?
   Default: user is on-call; runbook must be readable by them.

## Output
- `<root>/docs/maintenance-plan.md`:
  - Monitoring (Crashlytics dashboard, SLOs, alert routing)
  - Regression plan (which tests run on every build, which on every
    release, which nightly)
  - Migration policy (Room schema migration procedure, including
    testing the migration on a backup of production data)
  - Feature flag spec (where flags are defined, how to roll out, how
    to roll back, when to delete)
  - On-call runbook (top 5 user-facing alerts, each with: what it
    means, how to diagnose, step-by-step mitigation, escalation path)
  - Release cadence (next planned release, blockers, known issues)

## Verification
- `docs/maintenance-plan.md` exists, ≥ 80 lines.
- Each top alert in the runbook has a concrete mitigation (not "TBD").
- The migration procedure references the actual schema version
  (cross-check with the architecture's DB section).

## Done report format
```
[Stage 9 — Maintenance] done.
Artifact: <root>/docs/maintenance-plan.md
Verified by: wc -l docs/maintenance-plan.md && grep -c "^## " docs/maintenance-plan.md
Alerts in runbook: <N>
Migrations documented: <N>
Feature flags: <N>
Observability: <provider>
Next release: <date or "TBD">
Limitations: <anything deferred to v1.1>
Pipeline complete.
```

## Next stage
None. The loop closes; the harness flips `current_stage` to `done`.
The next iteration starts a new feature and re-enters Stage 4 (or
earlier if the architecture changes).
