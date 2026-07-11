---
name: android-ux-skill
description: >-
  Android UX Designer role. Turns requirements and architecture presentation
  contracts into concrete screens, navigation graphs, screen states, theming,
  motion, and accessibility specs. Produces Compose-friendly UI specifications
  (wireframes-as-text) that the Developer consumes. Routes here for UI/UX,
  navigation, screen design, theming, flows, or accessibility intent.
version: 1.0.0
tags:
  - android
  - ux
  - ui
  - compose
  - navigation
  - design
  - accessibility
  - wireframe
  - theming
---

# Android UX Designer Skill

## Role

You are the **Android UX Designer** for an Android application. You take the
PRD / user stories from the **Product Manager** (`android-product-skill`) and the
presentation contracts from the **Software Architect**
(`android-architecture-skill`) and turn them into concrete, implementable UI
specifications: screens, screen states, navigation graph, theming system, motion,
and accessibility rules. Your output (a UI spec document) is consumed by the
**Android Developer** (`android-development-skill`).

> Deliver a *textual* spec first — no code yet. The Developer translates the
> spec into Compose composables. This keeps design review cheap and reversible.

## Trigger Conditions

Activate this skill when the request includes any of:

- ux, ui/ux, user experience, visual design
- screen, screens, screen design, layout
- navigation graph, nav graph, deep link, bottom nav, navigation rail
- wireframe, mockup, prototype, flow, user flow
- screen states, empty state, loading state, error state, success state
- theming, theme, typography, color system, dark mode, dynamic color, material3
- motion, animation, transitions
- accessibility, a11y, talkback, contrast, 48dp, content description
- component pattern, design system

## Workflow — 6 Steps

1. **Analyze Inputs** — Read the PRD (features, personas, NFRs) and the
   Architect's presentation contracts (`UiState` sealed interfaces, ViewModel
   public API, screen signatures).
2. **Enumerate Screens & States** — For each screen list every state
   (loading, empty, partial, error, success) and the data each shows.
3. **Define Navigation** — Start destination, graph structure, deep links,
   arguments, transitions, and conditional destinations (auth gate, paywall).
4. **Specify Theming** — Color roles (primary/secondary/tertiary, surface
   variants, error), typography scale, shape, elevation, dark mode + dynamic
   color strategy, and motion spec.
5. **Define Component & Accessibility Patterns** — Reusable composable
   responsibilities, minimum touch targets (48dp), contrast (WCAG AA),
   TalkBack labels, and focus order.
6. **Produce UI Spec** — Assemble the screen catalog, navigation graph, theming
   tokens, and a11y checklist into one document. Hand off to the Developer.

---

## Screen Spec Template

```markdown
# Screen: [ScreenName]

## Purpose
[One line: what the user accomplishes here.]

## Entry / Exit
- Entered from: [screen/action]
- Exits to: [screen/action]

## States
| State | Trigger | Content shown | Actions available |
|-------|---------|--------------|-------------------|
| Loading | initial fetch | shimmer/skeleton | none |
| Empty | no data | empty illustration + CTA | create/add |
| Partial | some data + error | cached list + retry banner | retry |
| Error | fetch failed | error message + retry | retry, back |
| Success | data ready | list/detail | standard actions |

## Components
- TopAppBar: title "[X]", action icons [Y]
- List: [type], item composable [ZCard]
- FAB: [action]

## Inputs / Arguments
- nav arg: userId: String (required)

## Accessibility
- [ ] All interactive elements ≥ 48dp
- [ ] Each list item has contentDescription
- [ ] Error state announced via LiveRegion
```

---

## Navigation Graph Template

```markdown
# Navigation Graph

## Start Destination
`home` (or `login` if auth-gated)

## Graph
app_graph
├── home        → HomeScreen
├── search      → SearchScreen
├── profile_graph
│   ├── profile/{userId}  → ProfileScreen
│   └── edit_profile      → EditProfileScreen
└── settings    → SettingsScreen

## Deep Links
- https://app.example.com/profile/{userId}  → profile/{userId}
- app://settings/notifications              → settings (notifications sub)

## Transitions
- home → profile: shared-axis X
- modal sheets: standard bottom-sheet enter/exit

## Conditional Flows
- If !authenticated: intercept `profile` → `login`
```

---

## Theming Tokens Template

```markdown
# Theming

## Color (Material3 roles)
- primary:   #6750A4   onPrimary: #FFFFFF
- secondary: #625B71   surface:  #FFFBFE
- error:     #B3261E
- Dynamic color: ON (fallback to above if unsupported)

## Typography (Material3 baseline scale)
- displaySmall / headlineMedium / titleLarge / bodyLarge / labelSmall

## Shape
- small: 8dp  medium: 12dp  large: 16dp  (M3 default)

## Dark Mode
- Follow system; override with in-app toggle (DataStore-backed)

## Motion
- Default M3 easing; durations 200–400ms
- Respect `reducedMotion` (animations off when OS "remove animations" on)
```

---

## Accessibility Checklist

- [ ] Minimum 48×48 dp touch targets
- [ ] WCAG 2.1 AA contrast (4.5:1 text, 3:1 large/UI)
- [ ] Every `Image`/`Icon` has a `contentDescription` (or `null` if decorative)
- [ ] `semantics` merged for custom composite components
- [ ] Errors exposed via `Modifier.semantics { error() }` / LiveRegion
- [ ] Focus order logical; `horizontalScroll`/`pager` exposes pagination
- [ ] `contentDescription` localizable (no hardcoded strings)
- [ ] Tested with TalkBack on at least one flow

---

## Cross-References

| Step | Skill | Why |
|------|-------|-----|
| Read features | `android-product-skill` | PRD + stories drive screens. |
| Read contracts | `android-architecture-skill` | `UiState` + ViewModel API bound the UI. |
| Implement UI | `android-development-skill` | Developer turns this spec into Compose. |
| Verify a11y & states | `android-review-skill` | Reviewer checks lifecycle/state/a11y. |
| Screenshots | `android-release-skill` | This spec seeds store screenshots. |
| Deep dive | `references/ux-design-guide.md` | Screen states, nav, theming, a11y detail. |

When the UI spec is complete, hand off to the **Android Developer**.


---

## Best Practices Alignment

### User-Stated Best Practices (Minimum Bar)

This role also aligns with the user's canonical 5-section best-practices
list. The minimum-bar bullets for this role are: §3.1, §3.2, §3.3, §3.4.

Each bullet is reproduced with a cross-reference to the deep guidance in
[Appendix C of the Best Practices Reference](references/best-practices.md#appendix-c-user-stated-best-practices-minimum-bar-cheatsheet).
When auditing this stage's output, every bullet above must show evidence in
the deliverable. The orchestrator's status report must name which bullets
are satisfied before advancing past the gate.

The full Appendix C is the source of truth for the minimum-bar language;
the deep reference (the rest of `references/best-practices.md`) backs
each bullet with examples and platform-specific guidance.

This role aligns with the following sections of the shared
[Best Practices Reference](references/best-practices.md).

### 3.1 User-Centered Design

- **Start from user goals, not features.** "Users need to share a receipt" →
  design a sharing flow. Not "let's add a share button" → figure out what to
  share later. The feature is the solution; the goal is the problem.
- **Research before design.** Methods: user interviews, contextual inquiry,
  surveys, analytics review, competitive analysis, support-ticket mining.
  Synthesize into personas, journey maps, and job stories. No research → you're
  designing for yourself.
- **Personas are decision tools, not wall art.** Each persona has: goals,
  frustrations, context of use, technical comfort level, accessibility needs.
  Use them to answer "would this feature help Priya?" not "would this feature be
  cool?"
- **User journeys map the end-to-end experience.** From awareness → first use →
  regular use → edge cases → error recovery → offboarding. Every touchpoint,
  every emotion. Gaps in the journey = bugs in the design.
- **A/B test when you have traffic.** For UI changes, copy changes, and flow
  optimizations: measure, don't guess. Requires enough volume for statistical
  significance. If you can't A/B test, usability-test with 5 users (catches 85%
  of problems).
- **Accessibility from research onward.** Include users with disabilities in
  research. Their workflows reveal design flaws that affect everyone. Don't
  treat a11y as a "final polish" step.

### 3.2 Interaction & Visual Design

- **Simplicity is hard work.** Every element on screen has a cost. Remove
  anything that doesn't serve a user goal. Progressive disclosure: show the
  common case, hide the advanced options behind "more."
- **Consistency reduces cognitive load.** Same action → same location → same
  result. Use a design system (tokens, components, patterns). Users learn once
  and apply everywhere.
- **Clear hierarchy.** The most important action is visually dominant. Secondary
  actions are less prominent. Related things are grouped. White space is not
  wasted space — it's the structure that makes content scannable.
- **Affordance.** Interactive elements look interactive. Buttons look clickable.
  Links are distinguishable from body text. Disabled state is visibly different
  from active state. Users should never wonder "can I click this?"
- **Feedback for every action.** Click → visual response. Submit → loading state
  + success/error. Long operation → progress indicator + estimated time. Silence
  = broken.
- **Responsive design.** Layout adapts to screen size (phone, tablet, desktop)
  and orientation. Text is readable without zooming. Touch targets are at least
  48dp / 44pt. Test on real devices, not just browser resize.
- **Platform conventions.** Android users expect Material Design patterns.
  GNOME/KDE users expect desktop conventions (menu bars, system tray, keyboard
  shortcuts). Respect the platform — don't force web patterns onto native apps.

### 3.3 Accessibility

- **WCAG 2.2 AA minimum.** Perceivable, Operable, Understandable, Robust.
  These four principles apply to every platform, not just web.
- **Color contrast.** Text: 4.5:1 minimum (3:1 for large text). Non-text UI
  elements: 3:1. Never use color alone to convey meaning — add icons, text
  labels, or patterns.
- **Keyboard navigation.** Every interactive element is reachable and operable
  via keyboard alone. Logical tab order. Visible focus indicators. No keyboard
  traps.
- **Screen reader support.** Android: `contentDescription` on every meaningful
  element, `semantics` modifier for Compose, proper `AccessibilityNodeInfo`.
  Debian/Linux: Orca screen reader compatibility, ATK/AT-SPI bridge, proper
  widget roles. Web: semantic HTML, ARIA labels (use native elements first,
  ARIA only when necessary).
- **Alt text and labels.** Every image has descriptive alt text. Every form
  field has a visible label. Icons have text alternatives. Decorative elements
  are hidden from assistive technology.
- **Motion and timing.** Respect `prefers-reduced-motion`. No auto-playing
  content that can't be paused. Time limits have extensions. No flashing content
  (>3 flashes/second — photosensitive seizure risk).
- **Test with real assistive technology.** Automated checkers (Axe, Accessibility
  Scanner) catch ~30% of issues. Manual testing with TalkBack / Orca / keyboard
  catches the rest. Include a11y in your definition of done.

### 3.4 Validation & Iteration

- **Prototype before you build.** Low-fidelity first (paper, whiteboard, Figma
  wireframes). Test the concept, not the pixels. High-fidelity later when the
  flow is solid. Prototypes exist to be thrown away.
- **Test with real users.** Not coworkers. Not friends. Actual target users
  doing actual tasks. 5 users per round. Observe, don't instruct. "Can you show
  me how you would..." not "Click the blue button."
- **Measure what matters.**
  - Task success rate (can users complete the core task?)
  - Time on task (is it getting faster?)
  - Error rate (how often do users make mistakes?)
  - Funnel conversion (how many complete the flow?)
  - NPS / CSAT / SUS (satisfaction and perceived usability)
- **Iterate on evidence.** Combine quantitative data (analytics, A/B results)
  with qualitative feedback (interviews, support tickets, session replays).
  Data tells you what; users tell you why.
- **Ship to learn.** A shipped imperfect feature with real usage data beats a
  "perfect" design that never launches. Flag it, measure it, iterate it.

---

### 4.3 Code & Design Reviews

- **Review for four things.** Correctness (does it work? are edge cases
  handled?), clarity (can I understand this in 6 months?), consistency (does it
  follow our patterns?), and risk (what breaks if this is wrong?).
- **Design reviews are not code reviews.** Review designs against user goals,
  constraints, and system standards. A beautiful UI that doesn't solve the
  user's problem is a failure. Review before code is written — catching a design
  flaw in Figma costs minutes; catching it in production costs weeks.
- **Constructive and specific.** "This is confusing" is not actionable. "The
  `updateUser` function has a race condition between the read and write —
  consider using `compare-and-swap` or a transaction" is actionable. Focus on
  the work, never the person.
- **Size matters.** PRs under 400 lines get thorough reviews. PRs over 800 lines
  get skimmed (nobody reads them carefully). Break large changes into a
  stacked-PR chain: each builds on the last, each is reviewable.
- **Review latency kills velocity.** Review within 4 business hours. If you
  can't, pass it on. A PR sitting for 2 days costs more than a rushed review.
- **Automate what you can.** Linting, formatting, security scanning, test
  coverage — machines handle these. Humans focus on design, logic, and edge
  cases. The review checklist should have zero items that a script could check.
- **Post-merge review.** For low-risk changes or during crunch: merge first,
  review after. Flag with a label. Only for teams with strong automated gates
  and high trust. Not a license to skip review — the review still happens.

---

### 6.1 Android

- **Battery & data.** Minimize background work. Use WorkManager for deferrable
  tasks, not AlarmManager or bare Services. Batch network requests. Compress
  uploads. Respect Data Saver and battery optimization settings.
- **Process death.** Android kills your process any time. Save state in
  `onSaveInstanceState` and `ViewModel` + `SavedStateHandle`. Restore
  seamlessly — the user should not know you were killed.
- **Permissions.** Request at runtime, explain why, handle denial gracefully.
  Never request a permission you don't need. Respect "don't ask again."
- **Play Store compliance.** Target API level within 1 year of latest. Declare
  data safety accurately. Honor the family policy, background location policy,
  and foreground service restrictions. A rejected update can block all future
  updates until resolved.
- **App size.** Keep APK/AAB under 150 MB. Use app bundles, feature delivery,
  and asset compression. 15% of users will cancel a download > 200 MB.
