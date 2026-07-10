# Orchestrator Run Pattern

Concrete recipe for driving the Android Development Suite pipeline from one brief.
Companion to the orchestrator SKILL.md.

## Parallel fan-out (the key move)

Dependency check before sequencing:

- Stage 1 (Product) → must finish first (produces the PRD).
- Stage 2 (Architecture) and Stage 3 (UX) depend ONLY on the PRD → run them
  **concurrently** in a single `delegate_task(tasks=[...])` call.
- Stage 4 (Development) can fan out per feature as parallel subagents.
- Stage 5 (Review) and Stage 6 (QA) are sequential **gates**, not parallel.

This is the biggest leverage point: two expensive specialist passes happen at
once instead of back-to-back.

## Subagent context payload

For each delegated stage, embed into the subagent `context` field:

1. The full text of that stage's `SKILL.md` (read from
   `~/.hermes/skills/android-development-suite/skills/<stage>/SKILL.md`).
2. The relevant upstream artifact (e.g. PRD for Architecture + UX).
3. `PROJECT_CONTEXT.md` (the shared source of truth).
4. A concrete output instruction with an absolute file path
   (write to `docs/<artifact>.md`).

Keep each subagent's goal single-purpose and self-contained — it has no memory
of the parent conversation, so over-specify rather than assume.

## Worked example — VoxBook TTS Reader

Brief: "basic TTS app for epub/pdf/md files."

- Stage 0: wrote `PROJECT_CONTEXT.md` (app: VoxBook; single-module v1 per
  ADR-1; on-device TTS per ADR-2; PdfRenderer/epublib/commonmark parsers).
- Stage 1: wrote `docs/prd.md` (PRD + 6 user stories + MoSCoW backlog).
- Stage 2 + 3: ONE `delegate_task` with two tasks → `docs/architecture.md` + ADRs
  and `docs/ux-spec.md`, produced in parallel.
- Stages 4–9: Development (scaffold CLI per architecture plan), Review gate
  (critical/major = 0), QA gate (tests green + coverage met), Build, Release,
  Maintenance.

The orchestrator reports one status line per stage and a final one-page summary
of the artifact map.

## Gatekeeping (non-negotiable)

- Never advance past **Review** until critical/major = 0.
- Never advance past **QA** until tests pass and coverage meets the module
  targets in `PROJECT_CONTEXT.md`.
- Synthesize each stage's deliverable; do not dump raw subagent output to the
  user.
