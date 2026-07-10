# Android Development Suite

A comprehensive Android development skill suite providing intent-based routing to
specialized role skills for the full Android app lifecycle — from product requirements
through Play Store release and maintenance.

Built for [Hermes Agent](https://hermes-agent.nousresearch.com).

## Pipeline

```
Orchestrator → Product → Architecture → UX → Development → Review → QA → Build → Release → Maintenance
```

| Stage | Skill | Role | Artifacts |
|-------|-------|------|-----------|
| 0 | android-orchestrator-skill | Gatekeeper | PROJECT_CONTEXT.md, pipeline coordination |
| 1 | android-product-skill | Product Manager | PRD, user stories, acceptance criteria, backlog |
| 2 | android-architecture-skill | Software Architect | Module tree, DI graph, data layer, ADRs |
| 3 | android-ux-skill | UX Designer | Screen catalog, nav graph, theming, a11y |
| 4 | android-development-skill | Developer | Feature code (Kotlin/Compose/Hilt/Room) |
| 5 | android-review-skill | Code Reviewer | Review report (detekt, architecture conformance) |
| 6 | android-qa-skill | QA Engineer | Test plan, unit/UI tests, CI, coverage gate |
| 7 | android-build-skill | Build Engineer | Gradle, flavors, signing, R8, CI pipeline |
| 8 | android-release-skill | Release Engineer | AAB, store listing, staged rollout |
| 9 | android-maintenance-skill | Maintenance Engineer | Regression plan, migrations, feature flags |

## Quick Install

```bash
git clone https://github.com/e-allora/android-development-suite.git \
  ~/.hermes/skills/android-development-suite
cd ~/.hermes/skills/android-development-suite
./install.sh
```

## Usage

Load the orchestrator for any Android work:

```
hermes -s android-orchestrator-skill
```

Say "build me an app that does X" and the orchestrator drives the full pipeline.

Or target a specific stage by keyword:
- "write a PRD for..." → product-skill
- "review this code" → review-skill
- "set up CI" → build-skill

## Tech Stack (defaults)

- Kotlin 2.0+, Jetpack Compose BOM
- Hilt 2.51+ (DI), Room 2.6+ (persistence), Retrofit (networking)
- AGP 8.7+, Gradle 8.12+
- minSdk 26, compileSdk 35

## Proven

This framework drove the [VoxBook](https://github.com/e-allora/voxbook) pilot app
through all 9 stages end-to-end: 33 unit tests, 0 detekt findings, verified release
AAB, full documentation set.

## Structure

```
├── SKILL.md                    # Orchestrator entry point
├── marketplace.json            # Suite metadata (Her mes marketplace)
├── install.sh                  # Symlink installer
├── skills/                     # 10 role skills (orchestrator + 9 roles)
├── templates/                  # PROJECT_CONTEXT.md + Compose blueprints
├── references/                 # Engineering guides (one per role)
├── scripts/                    # android_suite_tool.py (scaffold + audit CLI)
└── tests/                      # Suite self-tests
```
