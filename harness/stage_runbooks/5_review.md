# Stage 5 — Review

## Goal
A `docs/review-report.md` that documents what was checked, what passed,
what failed, and what the dev must fix. The gate: no open critical or
major issues.

## Inputs
- The diff (`git diff main...HEAD` or the feature branch diff).
- `PROJECT_CONTEXT.md`, `docs/architecture.md`, `docs/ux-spec.md`.
- The Stage 4 verification report.

## Clarifications to ask
None. The reviewer asks nothing of the user; the reviewer reports to
the gatekeeper (the orchestrator). The dev answers the reviewer's
findings, not the user.

## Output
- `<root>/docs/review-report.md`:
  - Summary (one paragraph: overall quality, risk level, recommendation)
  - Critical issues (block merge; if any, status = blocked)
  - Major issues (block merge; if any, status = blocked)
  - Minor issues (don't block; track as follow-ups)
  - Nitpicks (style only)
  - Architecture conformance (does the code match the architecture?)
  - UX conformance (does the UI match the UX spec?)
  - Test coverage (did dev add tests for the new logic?)
  - Security (any obvious issues — hardcoded secrets, insecure
    networking, missing input validation?)
  - Performance (any obvious hot paths — blocking I/O on main thread,
    large lists without keys, etc.)

## Verification
- `docs/review-report.md` exists, ≥ 50 lines.
- Each issue has: severity, file:line, problem, suggested fix.
- "Critical: 0, Major: 0" is the gate.

## Done report format
```
[Stage 5 — Review] done.
Artifact: <root>/docs/review-report.md
Verified by: wc -l docs/review-report.md && grep -c "^### " docs/review-report.md
Critical: <N>
Major:    <N>
Minor:    <N>
Architecture conformance: OK / issues
UX conformance: OK / issues
Recommendation: ACCEPT / REWORK
Next: 6_qa (if ACCEPT) or back to 4_development (if REWORK)
```

## Next stage
- If ACCEPT and 0 critical/major: Stage 6 — QA.
- If REWORK: back to Stage 4 (Development). The orchestrator advances
  only after the rework is re-reviewed.
