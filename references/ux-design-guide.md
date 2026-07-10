# UX Design Guide (Android / Jetpack Compose)

Companion to `android-ux-skill`. Use this to flesh out screens, navigation,
theming, motion, and accessibility before any code is written.

## Screen States

Every screen has at least these states. The `UiState` sealed interface in the
architecture plan should mirror them 1:1.

- **Loading** — skeleton/shimmer; no interactive controls.
- **Empty** — zero-data illustration + primary CTA.
- **Partial** — cached/partial data with a retry banner (don't block the user).
- **Error** — message + retry; never a blank screen.
- **Success** — the happy path.
- **Offline** — explicit banner when connectivity is lost mid-session.

## Navigation Patterns

- Single-activity + `NavHost`. One graph per feature module
  (`featureGraph(navController)`), nested into the app graph.
- Start destination: `home`, or `login` if auth-gated.
- Pass arguments as `NavArguments`; never via global mutable state.
- Deep links declared in the nav graph (`deepLinks = listOf(navDeepLink(...))`).
- Use `NavType` for type-safe args (Compose Navigation 2.8+ `NavType.Mapable`).
- Conditional flows (auth gate, paywall) live in a top-level `NavHost` wrapper.

## Navigation Components

- Primary destinations (≤5): `NavigationBar` (bottom).
- 5–7 destinations or wide screens: `NavigationRail` / `NavigationDrawer`.
- Sub-destinations: stack pushes. Modals: `ModalBottomSheet`.

## Theming System (Material3)

- Roles, not raw colors: `primary/secondary/tertiary`, `surface` variants,
  `error`, `outline`.
- `dynamicColor` ON by default; provide a manual fallback palette.
- Typography: M3 baseline scale (`displaySmall`…`labelSmall`).
- Shape: M3 corner sizes (small 8 / medium 12 / large 16 / full 999).
- Dark theme: follow system; in-app override stored in `DataStore`.

## Motion

- Default M3 easing; durations 200–400ms.
- `sharedAxisX/Y` for forward/back; `fade` for overlay; `scale` for dialogs.
- Respect `reducedMotion` — disable non-essential animation when the OS
  "Remove animations" setting is on.

## Accessibility (WCAG 2.1 AA)

- Minimum 48×48 dp touch targets.
- Contrast: 4.5:1 body text, 3:1 large text & UI components.
- Every `Image`/`Icon` gets a `contentDescription` (or `null` if decorative).
- Merge semantics for custom composite components.
- Expose errors via `semantics { error() }` / `LiveRegionMode`.
- Logical focus order; announce pagination in `HorizontalPager`.
- All strings from `resources` (no hardcoded text) for localization.

## Anti-Patterns

- Designing only the happy path (no empty/error/offline).
- Hardcoded colors instead of theme roles.
- Navigation via singletons/globals instead of the `NavController`.
- Forgetting TalkBack labels until QA.
- Animating everything (motion sickness / perf cost).
