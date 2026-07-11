# Stage 6 — QA

## Goal
Tests that exercise every public surface of the new code, an integration
test for the highest-risk boundary, and a CI config that runs them on
every push.

## Inputs
- The feature code (Stage 4 done, Stage 5 accepted).
- The review report (knows what to test extra).
- `docs/prd.md` (acceptance criteria become test cases).

## Clarifications to ask
1. **Coverage floor** — 70% (default), 80% (strict), 90% (overkill for
   most apps). Default: 80% for new code, no gate on legacy.
2. **Flaky-test policy** — quarantine on first flake (default), or
   fix immediately? Default: quarantine, fix in the same sprint.
3. **E2E scope** — top 3 user journeys only, or every screen happy
   path? Default: top 3 journeys.

## Output
- `<root>/app/src/test/...` — additional unit tests for any code that
  lacked them after Stage 4.
- `<root>/app/src/androidTest/...` — one UI test per top user journey.
- `<root>/.github/workflows/ci.yml` (or update existing) — runs unit
  + lint + detekt + UI test on every PR.

## Verification
- `./gradlew :app:testDebugUnitTest` exits 0, all tests pass.
- `./gradlew :app:lintDebug detekt` exit 0 (no new warnings introduced
  by this stage).
- Coverage report exists; new code is at or above the floor.
- CI workflow file parses (yamllint or GitHub Actions schema check).

## Done report format
```
[Stage 6 — QA] done.
Artifact: <root>/app/src/test/, <root>/app/src/androidTest/, .github/workflows/ci.yml
Verified by:
  - ./gradlew :app:testDebugUnitTest -> exit 0 (X passed)
  - ./gradlew :app:lintDebug detekt -> exit 0
  - coverage report: <file> (new code coverage: <Y%>)
Tests added: <N>
UI tests:    <N>
CI workflows: <N>
Limitations:
  - Real-device testing not done in this environment
  - No accessibility scanner run yet (deferred to Stage 8 if added)
Open issues: <N>
Next: 7_build
```

## Next stage
Stage 7 — Build. Role wires the signing config, R8/ProGuard rules, and
the CI pipeline that produces a release AAB.
