# Stage 8 — Release

## Goal
A `docs/release-report.md` confirming the AAB is in Play Console, the
store listing is published (or staged), and the rollout is configured.

## Inputs
- The signed release AAB (Stage 7 done).
- Play Console access (the user has the account).
- The brand assets (icon, feature graphic, screenshots) — from
  PROJECT_CONTEXT.md or the UX spec.
- The data-safety form answers (collected in Stage 1 / 2; confirm
  with the user before submitting).

## Clarifications to ask
1. **Rollout %** — start at 1% (default), 5%, 10%, or 100%? Default:
   1% with bump to 5% / 20% / 100% over 7 days.
2. **Release name** — internal "1.0.0" + user-facing "First release" /
   "v1.0"? Default: "1.0.0 (1)" with release name "Initial release".
3. **Release notes** — included in `docs/release-notes-1.0.0.md`,
   user-facing language. Must mention new features, fixes, and any
   breaking changes.
4. **Data safety form** — confirm with the user. The agent must not
   guess on data collection (especially location, PII, financial).

## Output
- `<root>/docs/release-report.md`:
  - Release version + build number
  - AAB path + size
  - Play Console URL (if uploaded)
  - Store listing fields (title, short description, full description)
  - Data safety form (collected + confirmed)
  - Rollout configuration (% ramp, monitoring period, abort criteria)
  - Release notes
- `<root>/docs/release-notes-1.0.0.md` — release notes for the
  user-facing changelog.

## Verification
- `docs/release-report.md` exists, filled in, all fields non-empty.
- The AAB exists at the path stated in the report.
- If Play Console was actually uploaded to: Play Console URL is in the
  report (this stage cannot be done in this environment; flag as a
  limitation if so).

## Done report format
```
[Stage 8 — Release] done.
Artifact: <root>/docs/release-report.md
Verified by: wc -l docs/release-report.md && cat docs/release-report.md | head
Version: 1.0.0 (build 1)
AAB: <path>
Play Console: <URL or "not uploaded in this environment">
Rollout: 1% -> 5% -> 20% -> 100% over 7 days
Data safety: confirmed with user
Release notes: docs/release-notes-1.0.0.md
Limitations:
  - Play Console upload not done in this headless environment; the
    AAB is ready at <path> for the user to upload manually, OR
    user must run the upload command themselves
Open issues: <N>
Next: 9_maintenance
```

## Next stage
Stage 9 — Maintenance. The maintenance engineer writes the regression
plan, the feature-flag spec, the migration policy, and the on-call
runbook.
