# Stage Runbook Template

Each stage has one runbook at `harness/stage_runbooks/<stage>.md`. The
format is fixed so the agent (or you) can use it as a checklist without
re-reading the role's full SKILL.md.

## Sections (in this order)

1. **Goal** — one sentence: what this stage produces in user-facing terms.
2. **Inputs** — what the stage needs from the prior stage(s) and the
   project state. Files that must exist.
3. **Clarifications to ask** — questions whose answers would change the
   output. Listed in priority order. "None" if the brief is unambiguous.
4. **Output** — exact files to produce, with absolute paths (or
   `<root>/docs/...`).
5. **Verification** — commands to run, with their expected outcome. If
   the command cannot run, say so in Limitations.
6. **Done report format** — what the agent must say when reporting back.
   Mirrors the agent-conduct contract.
7. **Next stage** — what stage advances after this one is verified.

The stage runbook is the *contract* for the stage. The role SKILL.md is
the *playbook* (more depth, more options, more examples). The harness
points you at both.
