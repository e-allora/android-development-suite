# Stage 0 — Init

## Goal
Create `PROJECT_CONTEXT.md` at the project root — the single source of
truth for tech stack, architecture rules, and naming conventions that
every later stage reads.

## Inputs
- The user's brief (one paragraph, in `project.json -> brief`).
- The project root path (in `project.json -> root`).
- `harness init <name> <brief>` has been run; `project.json` exists.

## Clarifications to ask
Only the load-bearing ones. Default everything else to the suite's
defaults (Kotlin 2.0+, Compose, Hilt, Room, Retrofit, minSdk 26,
compileSdk 35, AGP 8.7+).

1. **Target audience** — who is this for? (one sentence)
2. **MVP scope** — what's in v0.1? What's explicitly NOT in v0.1?
3. **Hard constraints** — offline-first? tablet? Wear? accessibility floor?
4. **Backend / data** — does this need a server, or is it all local?
5. **Branding** — name, package (`com.example.appname`), and any visual
   identity to respect.

Max 5 questions. If the user says "use defaults," accept it and proceed.

### Output
- `<root>/PROJECT_CONTEXT.md` — filled in from the suite template at
  `templates/PROJECT_CONTEXT.md`. The template's required sections
  (must be present for the gate to clear): **Tech Stack**, **Architecture
  Rules**, **Conventions**, **Open Decisions**.

## Verification
- `PROJECT_CONTEXT.md` exists, ≥ 20 non-empty lines.
- `PROJECT_CONTEXT.md` contains the required sections: **Tech Stack**,
  **Architecture Rules**, **Conventions**, **Open Decisions**.
- `git init` has been run at the project root; first commit is the
  template + state.

## Done report format
```
[Stage 0 — Init] done.
Artifact: <root>/PROJECT_CONTEXT.md
Verified by: ls <root>/PROJECT_CONTEXT.md && wc -l (>= 30 lines)
Decisions:
  - language: Kotlin
  - min_sdk: 26
  - ui: Jetpack Compose
  - di: Hilt
  - db: Room
  - network: Retrofit
Limitations: <anything the user didn't specify>
Next: 1_product (run `harness.py advance` to move on)
```

## Next stage
Stage 1 — Product. Role: `android-product-skill`. Runbook:
`harness/stage_runbooks/1_product.md`.
