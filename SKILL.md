---
name: android-development-suite
description: >-
  A comprehensive Android development skill suite providing intent-based routing
  to ten specialized skills: an Orchestrator Driver plus nine role-based skills
  (Product Manager, Software Architect, UX Designer, Android Developer, Code
  Reviewer, QA Engineer, Build Engineer, Release Engineer, Maintenance Engineer).
  Includes a CLI tool for scaffolding MVVM Compose features and auditing
  projects, a shared PROJECT_CONTEXT template, an end-to-end workflow runbook,
  blueprint templates, and engineering reference documentation.
version: 2.1.0
tags:
  - android
  - kotlin
  - compose
  - mvvm
  - hilt
  - room
  - retrofit
  - ci-cd
  - release
  - qa
  - review
  - ux
  - architecture
  - product
  - maintenance
  - play-store
  - workflow
  - orchestrator
  - pipeline
---

# Android Development Suite

## Overview

The Android Development Suite is an integrated collection of skills, templates,
references, and tooling that covers the **entire Android development lifecycle**
— from product requirements through architecture, UX, implementation, code
review, testing, build, Play Store release, and post-release maintenance. The
suite uses **intent-based routing** to direct incoming requests to the most
appropriate specialized skill based on trigger keywords in the user's message.

The whole thing is designed to run as one **agentic workflow**: an
**Orchestrator Driver** (`android-orchestrator-skill`) can run all nine role
skills from a single brief, with a shared `PROJECT_CONTEXT.md` as the single
source of truth. Each role skill produces a concrete artifact and hands it to
the next (see `references/workflow-runbook.md`).

## The Pipeline (+ Orchestrator Driver)

```
0. Orchestrate  android-orchestrator-skill  drives stages 1–9 end-to-end; you are the gatekeeper
1. Product       android-product-skill       PRD, user stories, ACs, backlog, roadmap
2. Architecture  android-architecture-skill  module tree, DI graph, data layer, contracts, ADRs
3. UX            android-ux-skill            screen catalog, nav graph, theming, a11y spec
4. Development   android-development-skill   feature code (scaffold CLI + blueprints)
5. Review        android-review-skill        review report (critical/major gate)
6. QA            android-qa-skill            test plan, unit/UI/integration, CI, coverage gate
7. Build         android-build-skill         Gradle, flavors, signing, R8, CI pipeline
8. Release       android-release-skill       audit, AAB, store listing, staged rollout
9. Maintenance   android-maintenance-skill   regression, migration, flags, observability
```

## ⚠️ Pitfalls — Do NOT Skip

- **ALWAYS load `android-orchestrator-skill` first** for any work on a project
  using this suite. The VoxBook pilot session proved that ad-hoc coding without
  loading the orchestrator wastes turns, misses the proven stage artifacts
  (PRD, ADRs, UX spec, review report, test plan), and produces code that works
  but has no pipeline documentation. Load the skill, route via intent keywords.
- **Each project MUST have `PROJECT_CONTEXT.md`** at the repo root. Without it,
  subagents spawned by `delegate_task` have no shared source of truth about tech
  stack, architecture decisions, or naming conventions. The orchestrator's
  Stage 0 creates it; verify it exists before delegating.

Stages 2 and 3 can start in parallel after Product (both only need the PRD).
Development can fan out per feature. After Development, the loop
**Review → Dev(fix) → QA** repeats until green. No feature merges until Review
approves (no open critical/major) and tests pass. To run the whole thing from
one brief, invoke `android-orchestrator-skill`.

## Architecture — Seven Layers

| # | Layer | Purpose | Artifact(s) |
|---|-------|---------|-------------|
| 1 | **Orchestration** | Intent-based routing to specialized skills + orchestrator driver | `SKILL.md` (this file) |
| 2 | **Roles** | Ten role-based skills with workflows and templates | `skills/android-*-skill/SKILL.md` |
| 3 | **Tooling** | CLI for scaffolding features and auditing projects | `scripts/android_suite_tool.py` |
| 4 | **Blueprints** | Copy-and-adapt Gradle / Kotlin / XML templates | `templates/blueprints/` |
| 5 | **References** | Deep engineering reference documentation | `references/*.md` |
| 6 | **Manifest** | Declares all components for discovery and install | `marketplace.json` |
| 7 | **Verification** | Automated test suite validating suite integrity | `tests/run_all.py` |

## Intent-Based Routing

When a request arrives, scan it for the trigger keywords below and route to the
matching skill. The first matching row wins; if multiple skills are relevant,
route to the skill that owns the *primary* intent and mention the others.

| Intent | Trigger Keywords | Route To Skill |
|--------|------------------|----------------|
| **Orchestration** | orchestrate, run the pipeline, full workflow, end-to-end, agentic workflow, drive the process, build from scratch | `android-orchestrator-skill` |
| **Product** | requirements, prd, user story, acceptance criteria, backlog, roadmap, feature request, stakeholder, mvp, definition of done, definition of ready | `android-product-skill` |
| **Architecture** | architecture, adr, module structure, layer, dependency injection, hilt graph, data layer design, presentation contracts, system design, tech debt | `android-architecture-skill` |
| **UX** | ux, ui/ux, screen, navigation graph, wireframe, mockup, flow, screen states, theming, typography, color, motion, accessibility, design system | `android-ux-skill` |
| **Development** | implement, scaffold, feature, compose screen, viewmodel, repository, room, retrofit, navigation, domain model, ui state, build the feature | `android-development-skill` |
| **Review** | review, code review, static analysis, lint, detekt, ktlint, architecture conformance, lifecycle, coroutine, error handling, security, secret | `android-review-skill` |
| **QA / Testing** | test, unit test, ui test, integration test, coverage, test plan, test pyramid, roborazzi, turbine, mockk, quality gate, ci pipeline | `android-qa-skill` |
| **Build** | build.gradle, gradle, flavor, build variant, versioning, version code, signing config, keystore, ci, cd, proguard, r8, minify, bundle, aab | `android-build-skill` |
| **Release** | release, play store, play store listing, store listing, privacy policy, r8, proguard, minify, signing, aab, app bundle, rollout, version bump, release notes, audit, crash reporting | `android-release-skill` |
| **Maintenance** | maintenance, regression, db migration, room migration, feature flag, feature toggle, crashlytics, analytics, observability, deprecation, post-release | `android-maintenance-skill` |

### Routing Rules

1. **Keyword match.** If the user's message contains one or more trigger keywords, route to the skill whose row matches.
2. **Multiple matches.** If keywords from multiple skills appear, route to the skill with the most keyword hits and note the secondary skill(s) in the response.
3. **Ambiguous.** If intent is unclear, ask the user to clarify which role should handle the request.
4. **Cross-skill.** If a skill's workflow references another skill (see *Skill Dependency Graph*), mention the cross-reference so the user can continue.
5. **Fallback.** If no keywords match, default to `android-development-skill` for general Android development questions.

## CLI Usage

The suite ships a Python CLI at `scripts/android_suite_tool.py`. Make it
executable and run it from anywhere.

```bash
# Scaffold a new MVVM Compose feature
python3 scripts/android_suite_tool.py scaffold \
  --package com.example.app \
  --feature profile \
  --base-dir ./app/src/main/java \
  --use-room --use-retrofit

# Audit a project for R8 and permission issues
python3 scripts/android_suite_tool.py audit \
  --project-dir ./my-android-app \
  --check-r8 --check-permissions

# List suite contents
python3 scripts/android_suite_tool.py list --type all
```

### Scaffold generates

| Layer | File |
|-------|------|
| Domain | `<feature>/domain/<Feature>Model.kt`, `<feature>/domain/<Feature>Repository.kt` |
| Data (Room) | `<feature>/data/<Feature>Entity.kt`, `<feature>/data/<Feature>Dao.kt` |
| Data (Retrofit) | `<feature>/data/<Feature>Api.kt`, `<feature>/data/<Feature>Dto.kt` |
| Presentation | `<feature>/presentation/<Feature>ViewModel.kt`, `<feature>/presentation/<Feature>Screen.kt`, `<feature>/presentation/<Feature>UiState.kt`, `<feature>/presentation/components/<Feature>Card.kt` |
| DI | `<feature>/di/<Feature>Module.kt` |
| Navigation | `<feature>/navigation/<Feature>Navigation.kt` |

## Blueprint Templates

| File | Description |
|------|-------------|
| `templates/blueprints/libs.versions.toml` | Gradle version catalog (AGP, Kotlin, Compose BOM, Hilt, Room, Retrofit, OkHttp, Coroutines, Coil, Navigation, Lifecycle, testing) |
| `templates/blueprints/build.gradle.kts` | Root build script with plugin aliases (`apply false`) |
| `templates/blueprints/app.build.gradle.kts` | App-module build script (compileSdk 35, minSdk 26, R8 enabled, Compose, Hilt, Room, Retrofit) |
| `templates/blueprints/AndroidManifest.xml` | Manifest with INTERNET permission, `.App` application, MainActivity launcher |
| `templates/blueprints/Application.kt` | `@HiltAndroidApp` Application class |
| `templates/blueprints/MainActivity.kt` | Single-activity entry with splash screen, edge-to-edge, Compose |
| `templates/blueprints/Theme.kt` | Material3 theme with dynamic color support |

## Reference Documentation

| File | Description |
|------|-------------|
| `references/compose-style-guide.md` | Jetpack Compose coding standards: composable rules, state, performance, side effects, theming, navigation, testing, a11y, anti-patterns |
| `references/release-checklist.md` | Pre-release checklist: versioning, R8/ProGuard, permissions, AAB, signing, store listing, data safety, testing, crashes, rollout, verification |
| `references/architecture-guide.md` | Architecture guide: layers, module structure, domain/data/presentation conventions, DI, error handling, testing boundaries |
| `references/testing-strategy.md` | Testing strategy: pyramid, tooling, unit/UI/integration tests, doubles, coroutines, Room, CI, Roborazzi, anti-patterns |
| `references/testing-android-dependencies.md` | How to make Android framework dependencies testable on JVM without emulator (TtsEngine DI pattern, fake implementations, Hilt wiring) |
| `references/ux-design-guide.md` | UX guide: screen states, navigation patterns, theming tokens, motion, accessibility, anti-patterns |
| `references/review-checklist.md` | Code review rubric: architecture conformance, Kotlin idioms, lifecycle, coroutines, error handling, security, Compose perf, Detekt/Ktlint |
| `references/build-packaging-guide.md` | Build guide: Gradle/AGP, build types, flavors, versioning, signing, R8 rules, CI pipeline, quality gates |
| `references/maintenance-guide.md` | Maintenance guide: regression strategy, Room migrations, feature flags, observability, deprecation, post-mortem |
| `references/workflow-runbook.md` | End-to-end runbook: 9-stage pipeline, shared PROJECT_CONTEXT, file-aware prompts, review loop, orchestration options |

## Shared Project Context

Copy `templates/PROJECT_CONTEXT.md` to your repo root as `PROJECT_CONTEXT.md`
on day one. Every skill reads it for tech-stack decisions, naming conventions,
and the architecture rules. Keep it the single source of truth; update it when
an ADR changes a decision. See `references/workflow-runbook.md` for how the
skills hand off artifacts to one another.

## Skill Dependency Graph

```
android-orchestrator-skill
  │  (drives the full pipeline from a single brief; delegates stages 1–9)
  ▼
android-product-skill
  │  (PRD, user stories, acceptance criteria)
  ├───────────────────────────┐
  ▼                           ▼
android-architecture-skill   android-ux-skill
  │  (architecture plan,      │  (UI spec: screens, nav,
  │   ADRs, module structure) │   theming, a11y)
  └─────────────┬─────────────┘
                ▼
android-development-skill
  │  (implements features per architecture plan + UX spec)
  ▼
android-review-skill
  │  (review report; gate on critical/major)
  ▼
android-qa-skill
  │  (test plan, unit/UI/integration tests, CI, coverage)
  ▼
android-build-skill
  │  (Gradle, flavors, signing, R8, CI pipeline)
  ▼
android-release-skill
  │  (audit, AAB, store listing, staged rollout)
  ▼
android-maintenance-skill
     (regression, migration, flags, observability → loops back to Product)
```

Each skill's `SKILL.md` cross-references the next so a workflow can hand off
context cleanly.

## Installation

```bash
cd ~/.hermes/skills/android-development-suite
chmod +x install.sh
./install.sh
```

The installer symlinks all ten individual skills into `~/.hermes/skills/`
(skipping self if the suite already lives there), makes the CLI executable, and
runs `list --type all` to verify. Run it again after adding skills to refresh
the symlinks.

## Verification

Run the test suite to confirm the installation is complete:

```bash
python3 tests/run_all.py
```

Expected: **all tests and assertions passing**. Returns `0` on success and `1`
on any failure.
