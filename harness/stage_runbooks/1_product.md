# Stage 1 — Product

## Goal
A `docs/prd.md` that states the problem, the user, the success metric,
the MVP scope, and the backlog. This is the document every later stage
reads as its "what are we building" anchor.

## Inputs
- `PROJECT_CONTEXT.md` (must exist — Stage 0 done).
- The user's brief (`project.json -> brief`).
- Target audience + MVP scope (from the Stage 0 clarifications).

## Clarifications to ask
Only if the brief is genuinely ambiguous. Default the rest.

1. **Success metric** — how will we know v1 worked? (one number, e.g.
   "30% of opens lead to a shared link within 7 days of install")
2. **Top 3 user journeys** — what are the 3 things the user must be
   able to do in v0.1? (list)
3. **Out of scope for v0.1** — what are we explicitly NOT building?
4. **Anti-goals** — what's the user pain we're *not* trying to solve?

## Output
- `<root>/docs/prd.md` containing:
  - Problem statement
  - User (persona + context)
  - Success metric
  - MVP scope (in / out)
  - Top 3 user journeys
  - Anti-goals
  - Backlog (user stories in "As a <user>, I want <action>, so that
    <outcome>" format, with acceptance criteria)
  - Open questions
- `<root>/docs/backlog.md` (optional; can be appended to PRD instead)

## Verification
- File exists, ≥ 80 lines.
- Each user story has at least one acceptance criterion.
- "Out of scope" is filled in (not empty).

## Done report format
```
[Stage 1 — Product] done.
Artifact: <root>/docs/prd.md
Verified by: wc -l docs/prd.md && grep "Out of scope" docs/prd.md
Stories: <N>
ACs: <N>
Open questions: <list, or "none">
Limitations: <anything assumed>
Next: 2_architecture and 3_ux (can run in parallel)
```

## Next stage
Stage 2 — Architecture AND Stage 3 — UX can run in parallel after
Product. Both only need the PRD.
