# Stage 4 — Development

## Goal
Runnable feature code that builds clean, passes lint, and has at least
the smoke test the role requires. The agent runs the build at the end
and shows the exit code.

## Inputs
- `docs/prd.md`, `docs/architecture.md`, `docs/ux-spec.md`,
  `PROJECT_CONTEXT.md` — all four must exist.
- For each feature: the relevant user story from the PRD, the
  relevant screen from the UX spec, the relevant module from the
  architecture.

## Clarifications to ask
Only on load-bearing ambiguity. The architecture stage should have
answered most of these.

1. **Feature slice order** — implement all screens' data layer first,
   or one full vertical slice first (data + UI for screen A, then
   screen B)? Default: vertical slice for v0.1.
2. **Mock data** — fake repository, or real (network) calls against a
   stub? Default: fake repository returning canned data for v0.1.
3. **Test scope** — every public function, or one test per ViewModel
   per state? Default: one test per ViewModel state + one per repo
   method.

## Output
- Code under `<root>/app/src/main/...` matching the module tree in
  the architecture.
- Tests under `<root>/app/src/test/...` — unit tests only at this
  stage; UI/integration tests come in Stage 6 (QA).
- A diff that compiles and passes `./gradlew :app:assembleDebug`.

## Verification
- `./gradlew :app:assembleDebug` exits 0.
- `./gradlew :app:lintDebug` produces no errors (warnings OK, log them).
- `./gradlew :app:testDebugUnitTest` exits 0 (any new tests must pass).
- Every new ViewModel has at least one unit test.

## Done report format
```
[Stage 4 — Development] done.
Artifact: <root>/app/src/main/
Verified by:
  - ./gradlew :app:assembleDebug -> exit 0
  - ./gradlew :app:lintDebug -> exit 0 (warnings: <N>)
  - ./gradlew :app:testDebugUnitTest -> exit 0 (X passed, Y skipped)
Files added: <N>
Files modified: <N>
Lines: +<added> -<removed>
Limitations:
  - UI tests deferred to Stage 6 (QA)
  - Real network calls not wired; fake repo returns canned data
  - No a11y audit yet; deferred to Stage 6
Open issues: <N>
Next: 5_review
```

## Next stage
Stage 5 — Review. The reviewer independently checks the diff against
the architecture, the UX spec, and the agent-conduct contract. If
critical/major issues are found, the loop fires: 4_development
(attempts++) -> 5_review again.
