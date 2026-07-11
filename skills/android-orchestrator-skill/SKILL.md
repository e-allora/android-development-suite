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

---

## Best Practices Alignment

This orchestrator aligns with all 5 sections of the user's stated best-practices
cheatsheet — captured in
[Appendix C of the Best Practices Reference](references/best-practices.md#appendix-c-user-stated-best-practices-minimum-bar-cheatsheet).
As gatekeeper across the full pipeline, every section is in scope: architecture,
development, product/UX, collaboration, and operations.

### §1 Architecture & Engineering (always-on gate)
- **Modularity, layered architecture, clear contracts** — the suite enforces
  this via per-stage role skills with explicit input/output contracts
  (`PRD → architecture → UX → code → review → QA → build → release`).
- **Scalability, observability from day one** — verify every stage artifact
  names the relevant §1.2 (resilience) and §5.1 (observability) hooks it
  introduces; the Stage 7 build and Stage 8 release are the primary
  enforcement points.
- **Security (least privilege, secrets vault, SCA)** — no stage may commit
  a `local.properties` key, hardcoded token, or `signingConfigs` block with
  committed keystore. Verify with `gitleaks` and `gradle signingReport` in
  CI before declaring "done."

### §2 Software Development
- **CI/CD on every change, deterministic builds** — Stage 7 (Build) must
  produce a GitHub Actions workflow that runs build + lint + test + security
  on every PR; pinning JDK, AGP, Gradle, and lockfile hashes.
- **Small increments, working tree always green** — never advance a stage
  with failing CI; the orchestrator holds the gate. Use stacked PRs for
  large features.

### §3 Product & UX
- **User goals, not features** — Stage 1 (Product) must produce a PRD that
  states problem + user + success metric before any solution. Reject PRDs
  that lead with "we will build X."
- **Accessibility, design system, real-user validation** — Stage 3 (UX) must
  deliver a Material 3 token set + screen catalog + a11y checklist; Stage 6
  (QA) must include an automated a11y scan (Accessibility Scanner or
  `lint` accessibility rules).

### §4 Collaboration & Process
- **Clear requirements, RFCs for non-trivial changes** — every cross-stage
  handoff carries an ADR. `docs/adr/` must list the major decisions
  (state mgmt, DI framework, networking, persistence) with status.
- **Tickets with AC and DoD** — every stage produces a backlog with AC. The
  orchestrator's status report must show acceptance criteria being met
  before advancing.
- **Constructive review** — Stage 5 (Review) output is feedback to the
  developer, not a verdict. Require critical/major = 0; treat minors as
  follow-ups.

### §5 Quality, Monitoring & Operations
- **Observability (logs, metrics, traces), SLOs** — Stage 9 (Maintenance)
  must set up Crashlytics + a metrics SDK (or self-hosted Prometheus/Grafana
  if the app is privacy-sensitive) before the first production rollout.
- **Blue-green / canary / feature flags, rollback tested** — Stage 8
  (Release) must use Play Console staged rollout; Stage 7 (Build) must
  wire feature flags via a config service or local feature-flag library.
- **Blameless postmortems, incidents → guardrails** — Stage 9 produces a
  runbook for any user-facing alert. Incidents become automated tests or
  CI gates, not heroics.

Every role's `SKILL.md` (this orchestrator + the 9 specialists) inlines the
exact minimum-bar bullets relevant to its stage. The full cheatsheet is
reproduced in
[Appendix C](references/best-practices.md#appendix-c-user-stated-best-practices-minimum-bar-cheatsheet);
the deep reference is the rest of `references/best-practices.md`.

**How to apply during pipeline runs:**
1. Before spawning Stage N, restate the user-stated bullets that apply (in
   the subagent `context` payload, after the role's full `SKILL.md`).
2. In the stage's status report, name which bullets the deliverable
   satisfies.
3. If a deliverable skips a required bullet without justification, block
   the gate.
