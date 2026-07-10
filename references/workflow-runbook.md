# Workflow Runbook — End-to-End Android Pipeline

How to drive the Android Development Suite as a single agentic process from
idea → Play Store → maintenance. Every stage is a skill; each hands a concrete
artifact to the next.

## The Pipeline (9 stages → 9 skills)

```
1. Product      android-product-skill       → PRD, user stories, ACs, backlog, roadmap
2. Architecture android-architecture-skill  → module tree, DI graph, data-layer, contracts, ADRs
3. UX           android-ux-skill            → screen catalog, nav graph, theming, a11y spec
4. Development  android-development-skill   → feature code (scaffold CLI + blueprints)
5. Review       android-review-skill        → review report (critical/major gate)
6. QA           android-qa-skill            → test plan, unit/UI/integration, CI, coverage gate
7. Build        android-build-skill         → Gradle, flavors, signing, R8, CI pipeline
8. Release      android-release-skill       → audit, AAB, store listing, staged rollout
9. Maintenance  android-maintenance-skill   → regression, migration, flags, observability
```

Stages 1→2→3 can run in parallel after Product (Architecture and UX both only
need the PRD). Development can fan out per feature. After Development, the loop
**Review → Dev(fix) → QA** repeats until green.

## Shared Artifact: PROJECT_CONTEXT.md

Create `PROJECT_CONTEXT.md` at the repo root from
`templates/PROJECT_CONTEXT.md` on day one. Every skill reads it for tech-stack
decisions, naming conventions, and the architecture rules. Keep it the single
source of truth — update it when an ADR changes a decision.

## File-Aware Prompting

Feed each skill real context, not a fresh prompt:

- Product → paste the idea + audience; output PRD to `docs/prd.md`.
- Architecture → paste `docs/prd.md`; output `docs/architecture.md` + ADRs.
- UX → paste PRD + architecture presentation contracts; output `docs/ux-spec.md`.
- Development → run `scaffold` CLI, then paste the architecture plan and the
  relevant `docs/ux-spec.md` section; implement only the target feature.
- Review → paste the diff + `PROJECT_CONTEXT.md`; output a review report.
- QA → paste acceptance criteria + feature code; output tests + CI.
- Build → paste architecture plan; output / update Gradle + CI.
- Release → run `audit` CLI; output AAB + store listing.
- Maintenance → paste release report; output regression/migration plan.

## The Review Loop (enforce quality)

```
Dev implements feature  →  Review reports issues
        ↑                        |
        |         fix critical/major (re-review until clean)
        |                        ↓
        └──────────── QA writes & runs tests
```

Rule: **no feature "done" until tests are generated and pass, and Review has
approved (no open critical/major).** Only then merge and proceed to Build.

## Orchestration Options

- **Manual:** you invoke the next skill yourself at each handoff.
- **Subagents:** spawn `delegate_task` per feature (Dev/Review/QA) in parallel,
  each loaded with the relevant skill + the shared context doc.
- **Cron:** schedule a nightly regression/audit job via the `cronjob` tool.

## Definition of Done (whole app)

- [ ] PRD + architecture + UX spec in `docs/`
- [ ] Every feature reviewed (no critical/major open) and tested
- [ ] `./gradlew lint detekt ktlintCheck testDebugUnitTest` green
- [ ] Release AAB signed, store listing + data safety complete
- [ ] Staged rollout monitored (crash-free ≥ 99.5%)
- [ ] Regression + migration plan in place for next iteration
