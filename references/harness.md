# Harness — How to Drive the Pipeline as a Reusable Process

The harness is the **state machine** and **driver** for the Android
Development Suite. It turns the 9-stage pipeline from prose into a
runnable, restartable, auditable process.

> If the role skills are the *team*, the harness is the *project
> manager + ticket board + gate checkpoint*. The role skills describe
> what each role does; the harness tracks what each role has done
> and what they still owe.

## The Four Pieces

```
harness/
├── project.schema.json     # what project.json must look like
├── harness.py              # the driver (init / status / next / mark / verify / advance / doctor)
├── stage_runbooks/         # one contract per stage (0_init.md through 9_maintenance.md)
└── STAGE_RUNBOOK_TEMPLATE.md
```

The state file lives at `<project-root>/.harness/project.json`. Each
project you start with the harness has its own state file.

## The Workflow

```
1. Start a new project:
     python3 harness/harness.py init my-app "A reader app for long-form text with TTS"

2. See where you are:
     python3 harness/harness.py status
     python3 harness/harness.py next

3. Do the stage (the role skill tells you HOW):
     skill_view name='android-product-skill'
     read harness/stage_runbooks/1_product.md   # the contract for THIS stage

4. Mark progress as you go:
     python3 harness/harness.py mark 1_product in_progress
     ... produce the artifacts ...
     python3 harness/harness.py mark 1_product awaiting_review

5. Verify the gate:
     python3 harness/harness.py verify 1_product
     python3 harness/harness.py verify 1_product --run   # also runs the stage's commands

6. Advance to the next stage:
     python3 harness/harness.py advance

7. If a stage is blocked, the harness shows why (gate_blockers).
```

## The State Schema (one paragraph)

`project.json` is the single source of truth. It tracks:

- **Project identity** — name, brief, root path, tech stack
- **Per-stage status** — `pending | in_progress | awaiting_review | blocked | done | skipped`
  (plus owner, started/completed timestamps, attempts, output paths,
  and verification evidence)
- **Current pointer** — which stage the harness should run next
- **Gate blockers** — what the current stage is missing
- **Artifacts map** — file path -> last-updated
- **Decisions** — the ADR list (id, title, status, path)

See `project.schema.json` for the full machine-readable schema.

## How a Subagent Uses the Harness

When a role subagent is spawned (by the orchestrator, or by you
manually), the harness tells it:

1. **What stage it's on** — `harness.py status`
2. **What the contract is** — `harness/stage_runbooks/<stage>.md`
3. **What the gate is** — `harness.py verify <stage>` (lists missing
   artifacts)
4. **How to report back** — the runbook's "Done report format" section,
   which mirrors the agent-conduct contract

The subagent never invents what the next step is. The harness tells it.

## Reusing the Harness on a New Project

The harness is **platform-agnostic** in the sense that the *driver* is
generic — any 9-stage pipeline could plug into it. Today it's wired to
the Android pipeline. To reuse it for a different platform (iOS, web,
Linux desktop), copy the harness dir, replace the stage labels and
the role-skill mapping in `harness.py`, and rewrite the 9 runbooks
with platform-specific inputs/outputs/verifications.

## What the Harness Does NOT Do

- **It does not run the agent.** The LLM is still the thing that
  produces output. The harness is bookkeeping.
- **It does not replace the role skills.** The role SKILL.md is the
  *playbook* (depth, options, examples). The runbook is the
  *contract* (inputs, outputs, verification). The harness points you
  at both.
- **It does not push code, build APKs, or upload to Play Console.**
  Those happen when the agent runs the verification commands. The
  harness records what was run and what passed.

## When Things Go Wrong

| Symptom | What to do |
|---------|------------|
| `harness.py status` says stage X is `in_progress` for >7 days | Run `harness.py doctor` to see stale stages. Either complete it or `mark X pending` to restart. |
| `harness.py advance` says "missing artifact" but the file exists | The path in `STAGE_GATE` is relative to project root. If the file moved, either move it back or `mark X done --note "..."` to document why. |
| You want to skip a stage (e.g. no QA in a prototype) | `harness.py mark X skipped --note "prototype, no QA"`. Then `harness.py advance` to move on. |
| The schema changes (new stage, new status enum) | Edit `project.schema.json`, update `STAGE_ORDER` / `STAGE_GATE` / `STAGE_ROLE` in `harness.py`, rewrite the affected runbook. Existing `project.json` files will need migration. |

## Cross-references

- Agent behavior contract: [`agent-conduct.md`](agent-conduct.md)
- Best-practices cheatsheet: [`coding-best-practices.md`](coding-best-practices.md)
- Best-practices deep reference: [`best-practices.md`](best-practices.md)
- The orchestrator (loads this harness on session start):
  [`../skills/android-orchestrator-skill/SKILL.md`](../skills/android-orchestrator-skill/SKILL.md)
