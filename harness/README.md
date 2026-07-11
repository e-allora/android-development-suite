# Harness — Modular Agentic Workflow Driver

This is the **process framework** for the Android Development Suite. It
turns the 9-stage pipeline from a sequence of role skills into a
**state machine** you can drive, restart, audit, and reuse on any
Android project.

## The four pieces

```
harness/
├── project.schema.json     # JSON schema for the state file
├── harness.py              # the driver (init/status/next/mark/verify/advance/import/doctor)
├── harness.sh              # shell wrapper
├── test_harness.py         # 36 driver tests
├── stage_runbooks/         # one contract per stage (0_init.md through 9_maintenance.md)
└── STAGE_RUNBOOK_TEMPLATE.md
```

State lives at `<project-root>/.harness/project.json` (one per project).

## The six commands you actually use

```bash
# Start a new project
harness init <name> "<brief>"

# Or pick up an existing one (scans for known artifacts)
harness init <name> "<brief>" --force
harness import

# See where you are
harness status

# See what to do next (prints the role, the runbook, and the gate)
harness next

# Mark progress
harness mark <stage> in_progress
harness mark <stage> done

# Verify the gate (artifact existence + content + optional commands)
harness verify <stage>
harness verify <stage> --run       # also runs the stage's verification commands

# Move on
harness advance
harness advance --force            # override gate failures (not recommended)

# Diagnose
harness doctor

# Optional shell wrapper
./harness/harness.sh <cmd>
```

## The state schema (one paragraph)

Per-stage: `pending | in_progress | awaiting_review | blocked | done | skipped`.
Plus `owner`, `started_at`, `completed_at`, `attempts`, `output[]`
(absolute paths to produced artifacts), and `verification` (commands
run with exit codes + limitations).

Project-level: `name`, `brief`, `root`, `tech_stack` (from
PROJECT_CONTEXT.md), `current_stage` (the pointer the driver reads),
`gate_blockers[]` (why we can't advance), `artifacts{}`, `decisions[]`
(the ADRs).

Full schema: `harness/project.schema.json`.

## How a role subagent uses it

When a role subagent is spawned, it runs:

1. `harness status` — see the current stage
2. `harness next` — get the role + runbook + gate
3. Read `harness/stage_runbooks/<stage>.md` — the contract
4. Produce the output
5. Run the verification commands
6. `harness mark <stage> done --note "..."` and `harness advance`

The subagent never has to ask "what's next" — the harness tells it.

## Reusing the harness on a new project

The driver is generic enough to wire to any 9-stage pipeline. To
adapt for iOS, web, or Linux desktop:

1. Copy `harness/`
2. Update `STAGE_LABEL`, `STAGE_ROLE`, `STAGE_GATE`, `STAGE_VERIFY_CMDS`
   in `harness.py` to the new stages
3. Rewrite the 9 runbooks in `stage_runbooks/` for the new platform
4. Update the schema's stage names in `project.schema.json`

## Tests

```bash
python3 harness/test_harness.py
# Expected: 36 passed, 0 failed
```

These test the driver itself (init/status/mark/verify/advance/doctor/
import/next). They do not test the role skills (those have their own
tests in `tests/run_all.py`).

## Honest limitations

- **`harness import` does not run live verification.** It only checks
  that the expected artifacts exist. The `limitations` field on each
  imported stage records this. Run the stage's verification commands
  manually before trusting the import.
- **The gate is content-aware but not quality-aware.** It checks that
  `docs/prd.md` exists with 50+ lines and the required sections, but
  it does not read the PRD and tell you if it's *good*. That's what
  the role skills and human review are for.
- **The verification commands are hard-coded** for stages 4, 6, 7
  (development, qa, build). Other stages' verifications are
  documented in the runbook but not auto-run by the driver.

See `references/harness.md` for the human-facing explanation.
