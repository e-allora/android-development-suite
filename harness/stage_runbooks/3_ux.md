# Stage 3 — UX

## Goal
A `docs/ux-spec.md` that captures every screen (states included), the
navigation graph, the design system tokens, and an accessibility
checklist.

## Inputs
- `docs/prd.md` (Stage 1 done).
- `PROJECT_CONTEXT.md` (tech stack — confirms Compose vs. Views).
- Optionally `docs/architecture.md` if Stage 2 already produced the
  presentation contracts.

## Clarifications to ask
Only if not covered by the PRD.

1. **Visual identity** — Material 3 defaults, or a custom palette /
   typography? If custom: brand colors hex, font names.
2. **Density** — compact (more on screen) vs. standard vs. expanded.
   Default: Material 3 default.
3. **Dark mode** — yes (follow system) / no (light only) / yes (toggle)?
   Default: follow system.
4. **Tablet layout** — phone-only, or responsive (single-pane on
   phone, two-pane on tablet)? Default: phone-only for v0.1.
5. **Motion** — any required animations (e.g. hero transitions between
   list and detail)? Default: Material 3 defaults only.

## Output
- `<root>/docs/ux-spec.md`:
  - Screen catalog (one section per screen; each screen lists every
    state: empty, loading, success, error, partial)
  - Navigation graph (text diagram, e.g. `Home -> Detail -> Settings`)
  - Design tokens (color, typography, spacing, shapes — as a table)
  - Component inventory (which Material 3 components per screen)
  - Accessibility checklist (touch target size, contrast, screen
    reader labels, keyboard nav)
  - Theming decisions (light/dark/auto, dynamic color yes/no)

## Verification
- `docs/ux-spec.md` exists, ≥ 80 lines.
- Every screen has a state table (no "TODO: add states").
- Accessibility checklist is filled in (not "TBD").

## Done report format
```
[Stage 3 — UX] done.
Artifact: <root>/docs/ux-spec.md
Verified by: wc -l docs/ux-spec.md && grep -c "^## " docs/ux-spec.md
Screens: <N>
States per screen: <min>-<max>
A11y items checked: <N>
Limitations: <anything deferred to v0.2>
Next: 4_development
```

## Next stage
Stage 4 — Development. Inputs: PRD + architecture + UX spec. This is
where the agent finally writes Kotlin.
