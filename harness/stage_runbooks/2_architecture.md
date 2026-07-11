# Stage 2 — Architecture

## Goal
A `docs/architecture.md` that pins down the module tree, DI graph, data
layer, presentation contracts, and the ADRs that justify the choices.

## Inputs
- `docs/prd.md` (Stage 1 done).
- `PROJECT_CONTEXT.md` (tech stack decisions).

## Clarifications to ask
Only if the PRD leaves architectural choices open.

1. **State management** — MVI (single source of truth, immutable state)
   or MVVM with mutable state held in ViewModel? Default: MVI for any
   app with non-trivial flows; MVVM for simple CRUD.
2. **DI module split** — one per feature, or one giant `AppModule`?
   Default: one per feature.
3. **Persistence boundary** — single Room database for everything, or
   per-feature? Default: single DB, one DAO per feature.
4. **Networking** — one Retrofit instance, or per-feature service
   interfaces? Default: one instance, per-feature interfaces.
5. **Concurrency** — Coroutines + Flow throughout, or RxJava? Default:
   Coroutines + Flow.

## Output
- `<root>/docs/architecture.md`:
  - Module tree (text tree, or `gradle projects` output)
  - DI graph (Hilt modules per feature)
  - Data layer (DB schema, network, repositories)
  - Presentation contracts (one section per screen, in the language of
    the UX spec's screen catalog)
  - Cross-cutting concerns (logging, error handling, navigation)
- `<root>/docs/adr/ADR-001-<slug>.md` and onwards — one per non-trivial
  decision.

## Verification
- `docs/architecture.md` exists, ≥ 100 lines.
- `docs/adr/` contains at least 2 ADRs (tech stack + state management
  at minimum).
- All non-trivial decisions in the architecture are backed by an ADR
  (decision is "in ADR or in code, not floating in chat").

## Done report format
```
[Stage 2 — Architecture] done.
Artifact: <root>/docs/architecture.md
Verified by: wc -l docs/architecture.md && ls docs/adr/ | wc -l
ADRs: <N>
Modules: <N>
Limitations: <anything not yet pinned, e.g. "networking library for v2
  not decided, deferred to feature work">
Next: 3_ux (can run in parallel with Stage 2 if it hasn't started yet)
```

## Next stage
Stage 3 — UX. Same inputs (PRD + project context). Can run in parallel
with Stage 2.
