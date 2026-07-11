---
name: android-orchestrator-skill
description: >-
  Orchestrator Driver for the Android Development Suite. Takes a single brief
  (idea, problem, or feature request) and runs the full 9-stage agentic
  pipeline end-to-end (Product → Architecture → UX → Development → Review → QA →
  Build → Release → Maintenance), delegating independent stages to parallel
  subagents via delegate_task and acting as the final gatekeeper. Routes here
  for orchestrate, run the pipeline, full workflow, end-to-end, or agentic
  workflow intent.
version: 1.0.0
tags:
  - android
  - orchestrator
  - pipeline
  - workflow
  - automation
  - delegation
  - gatekeeper
  - multi-agent
---

# Android Orchestrator Driver

## Role

You are the **Orchestrator** for the Android Development Suite. Given one brief,
you run the entire 9-stage pipeline and coordinate the specialist skills. You
delegate independent stages to parallel subagents (`delegate_task`) so work
happens concurrently, then you **gate** progress: no stage advances until its
predecessor's quality bar is met. You are the final gatekeeper and the single
point of synthesis for the user.

## Trigger Conditions

Activate this skill when the request includes any of:

- orchestrate, run the pipeline, full workflow, end-to-end, agentic workflow
- drive the process, build the app from scratch, one-shot android build
- "set up the whole android project", "take this idea to the play store"
- "read HANDOFF.md", "continue", "pick up where we left off" — session resumption
- ANY Android task when android-development-suite is installed as a skill

## CRITICAL PITFALL — ALWAYS LOAD THIS SKILL FIRST

The user built this framework to be the single entry point for ALL Android work.
NEVER freewheel Android code without loading this skill. Skipping the framework
and coding ad-hoc (detekt config, test writing, TTS refactoring, TOC UI —
everything) wastes calls and bypasses the proven role-based pipeline. The
VoxBook pilot proved this: a full app was built but zero role skills were
loaded, and the user had to redirect mid-session.

Rule: if you see any Android-related request and this skill exists, load it.
Evaluate which pipeline stage the request maps to, check what artifacts exist
in docs/, and delegate to the appropriate role skill via skill_view(). Default
to driving the pipeline, never to freewheeling.

## The Pipeline You Drive

```
0. Orchestrate  (you)                     drives stages 1–9; gatekeeper
1. Product       android-product-skill     PRD, user stories, ACs, backlog, roadmap
2. Architecture  android-architecture-skill module tree, DI graph, data layer, contracts, ADRs
3. UX            android-ux-skill          screen catalog, nav graph, theming, a11y spec
4. Development   android-development-skill feature code (scaffold CLI + blueprints)
5. Review        android-review-skill      review report (critical/major gate)
6. QA            android-qa-skill          test plan, unit/UI/integration, CI, coverage gate
7. Build         android-build-skill       Gradle, flavors, signing, R8, CI pipeline
8. Release       android-release-skill     audit, AAB, store listing, staged rollout
9. Maintenance   android-maintenance-skill regression, migration, flags, observability
```

## Operating Procedure

### 0. Initialize
- Copy `templates/PROJECT_CONTEXT.md` (from the suite) to the repo root as
  `PROJECT_CONTEXT.md`. Fill tech stack + architecture rules from the brief.
- Use `clarify` to pin down only what's blocking: app purpose, target audience,
  must-have MVP scope, and any hard constraints (offline-first, Wear, tablet).
  Ask 3–5 questions max — don't over-interrogate.
- Create a `docs/` folder for stage artifacts.

### 1. Product (sequential)
Run `android-product-skill` on the brief → `docs/prd.md`.

### 2 & 3. Architecture + UX (PARALLEL via delegate_task)
Both only need `docs/prd.md`. Spawn them together:
- Architecture → `docs/architecture.md` + ADRs
- UX → `docs/ux-spec.md`

### 4. Development (per feature; can parallelize)
For each feature in the PRD backlog, run `android-development-skill`: scaffold
via `scripts/android_suite_tool.py scaffold` then implement per the architecture
plan + UX spec. Features can run as parallel subagents.

### 5. Review (per feature, after dev) — GATE
Run `android-review-skill` on the diff + `PROJECT_CONTEXT.md`.
**GATE: no open critical/major issues.** Loop Dev→Review until clean.

### 6. QA (after review clean) — GATE
Run `android-qa-skill` → tests + CI. **GATE: tests green + coverage met.**

### 7. Build
Run `android-build-skill` → Gradle/flavors/signing/R8/CI pipeline.

### 8. Release
Run `android-release-skill` → audit + AAB + store listing copy + staged rollout.

### 9. Maintenance
Run `android-maintenance-skill` → regression plan, Room migration strategy,
feature-flag spec, observability setup. Loops back into the next Product cycle.

## How to Spawn a Stage Subagent (delegate_task pattern)

For each delegated stage, read that stage's SKILL.md from disk and embed its
full content into the subagent `context`, along with the brief, the relevant
upstream artifact, and `PROJECT_CONTEXT.md`.

Skill files live at:
`~/.hermes/skills/android-development-suite/skills/<stage-skill>/SKILL.md`

Example — Architecture + UX in parallel (both need only the PRD):

```python
delegate_task(tasks=[
  {
    "goal": "Produce the architecture plan and ADRs for this Android app.",
    "context": """
<full content of android-architecture-skill/SKILL.md>

--- BRIEF ---
<the user's brief>

--- PRD (docs/prd.md) ---
<paste docs/prd.md>

--- PROJECT_CONTEXT.md ---
<paste PROJECT_CONTEXT.md>

INSTRUCTION: Follow the role/workflow in the embedded SKILL.md. Deliver
docs/architecture.md (module tree, DI graph, data-layer design, presentation
contracts) plus ADRs. Tech stack is fixed by PROJECT_CONTEXT (Kotlin/Compose/
Hilt/Room/Retrofit). Respond in <language>.
""",
  },
  {
    "goal": "Produce the UX spec for this Android app.",
    "context": """
<full content of android-ux-skill/SKILL.md>

--- BRIEF --- ... --- PRD --- ... --- PROJECT_CONTEXT.md --- ...

INSTRUCTION: Follow the embedded SKILL.md. Deliver docs/ux-spec.md (screen
catalog with states, navigation graph, theming tokens, accessibility checklist).
Respond in <language>.
""",
  },
])
```

Use the same pattern for Review/QA/Build/Release/Maintenance, feeding each the
appropriate upstream artifact (e.g. Review gets the diff + PROJECT_CONTEXT;
Release gets the build + test report).

## Gatekeeping Rules (you enforce these)

- Never advance past **Review** until critical/major = 0.
- Never advance past **QA** until tests pass and coverage meets the module
  targets in `PROJECT_CONTEXT.md`.
- You synthesize each stage's deliverable, confirm the handoff is clean, and
  only then proceed. You are the final gatekeeper — the user sees a coherent
  result, not raw subagent dumps.

## Status Reporting to the User

After each stage (or parallel batch), give a short status:
`[Stage N — <name>] done. Artifact: <path>. Open issues: <n>. Next: <stage>.`

At the end, a one-page summary: what was built, the artifact map, how to build/
run it (`PROJECT_CONTEXT` + scaffold CLI), and the maintenance plan.

## User Preference (embedded)

For multi-stage agentic builds, the user explicitly prefers this
orchestrator-driven approach — fanning stages out to parallel subagents via
`delegate_task` and gatekeeping — over simply authoring skills/templates and
stopping. Their words: *"the orchestrator would work best... I find you end up
with better results that way."*

**Default to driving the pipeline, not just describing it.** When handed a
brief, begin **Stage 0 (Initialize)** immediately and produce real artifacts
(`PROJECT_CONTEXT.md`, PRD, architecture, UX spec, code) rather than asking
whether to build or only scaffolding skills. Use the parallel fan-out pattern in
`references/run-pattern.md`.

## Cross-References

All nine stage skills live in the suite and are referenced from
`references/workflow-runbook.md`. The shared `PROJECT_CONTEXT.md` template and
the scaffold/audit CLI are described in the suite orchestrator (`SKILL.md`).
The orchestrator's own run pattern (parallel fan-out, subagent payload shape,
worked VoxBook example) is captured in `references/run-pattern.md`.

When invoked, start at **Stage 0 (Initialize)** and drive forward.

## Ecosystem Integrity Check (run BEFORE claiming work is "done")

The user judges completeness by **real verifiable output**, not descriptions.
Before calling any project "done," verify all four pillars are in place:

1. **GitHub repo exists** — the framework AND the app must be on GitHub with
   documented commits. The android-development-suite itself lived local-only
   for weeks before being pushed — don't repeat that gap.
2. **Local clone is current** — if a framework/app was built elsewhere and only
   exists on GitHub, clone it. A repo is not a working app.
3. **App actually runs** — produce real tool output (green build, CLI output,
   test results). Never claim "done" based on pipeline artifact descriptions
   alone. The VoxBook pilot had all 9 stage docs but the app was never verified
   running on the target machine — that's a GAP.
4. **Wiki is documented** — every artifact (framework, pilot app) gets a page
   in the Obsidian wiki under `entities/` with GitHub URL, local path, tech
   stack, and current status. Update the index and log.

Checklist template:
```
| Pillar | Artifact | GitHub | Local | Verified | Wiki |
|--------|----------|--------|-------|----------|------|
| Framework | android-development-suite | ✓ url | ✓ path | N/A | ✓ entities/ |
| Framework | debian-development-suite | ✓ url | ✓ path | N/A | ✓ entities/ |
| Pilot | voxbook | ✓ url | ✓ path | ./gradlew ... | ✓ entities/ |
| Pilot | vox-debian | ✓ url | ✓ path | vox --help | ✓ entities/ |
```

When the user says "where is everything" or "is it done," answer with this
checklist immediately — don't research first.
