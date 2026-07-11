# End-to-End Best Practices Reference

Shared reference for the Android and Debian Development Suites.
Covers architecture, engineering, development, product, UX, process, quality, and operations.
Every role skill should align with the relevant sections below.

---

## 1. Architecture & Engineering

### 1.1 System Design

- **Modularity first.** Decompose into small, loosely coupled services or
  components. Each module has one reason to change.
- **Clear contracts.** Define explicit APIs and interfaces between every
  component. Version them. Never let implementation details leak across
  boundaries.
- **Layered architecture.** Separate presentation, domain, data, and
  infrastructure. Inner layers define abstractions; outer layers implement them.
  Dependency rule: dependencies point inward.
- **Pattern selection.** Use the right pattern for the problem, not the pattern
  you know best:
  - **Clean / Hexagonal Architecture** — when domain complexity is high and you
    need to swap infrastructure (DB, queue, API) independently.
  - **CQRS** — when read and write workloads differ significantly in shape,
    scale, or performance needs.
  - **Event-driven** — when multiple services react to the same state changes
    and coupling via direct calls becomes expensive.
  - **MVVM / MVI** — for UI-heavy apps (Android Compose, Qt, React). Keep UI
    state a pure function of data.
- **Scalability from day one.** Design for horizontal scaling where possible.
  Stateless services scale; stateful ones need sharding. Document the scaling
  axis for every component.
- **Backward compatibility.** APIs change; clients don't. Version your
  endpoints, your database schemas, and your serialized formats. Deprecate
  before you remove.
- **Observability built in, not bolted on.** Every component emits structured
  logs, metrics, and traces. You cannot debug what you cannot see. (See §5.1.)

### 1.2 Reliability & Performance

- **Defensive programming.** Validate inputs at every boundary. Assume external
  data is malicious until proven clean. Fail fast on internal invariants.
- **Error handling is a feature.** Distinguish recoverable from unrecoverable.
  Recoverable: retry with backoff, fall back, degrade gracefully. Unrecoverable:
  fail loudly, alert, and leave a clear trace.
- **Timeouts on every external call.** No unbounded waits. Set connect, read,
  and total timeouts. Default: 30s connect, 60s read, 120s total — tune per
  endpoint.
- **Retry with exponential backoff + jitter.** Retry on transient failures
  (network, 503, deadlock). Never retry on semantic failures (400, 404, 409).
  Cap retries (3–5). Add jitter to avoid thundering herd.
- **Circuit breaker.** After N consecutive failures, stop calling the downstream
  for a cooldown period. Return a cached or fallback response. Prevents cascade
  failures and gives downstream time to recover.
- **Bulkhead.** Isolate resources per component or tenant. One slow client
  should not starve everyone else. Use separate thread pools, connection pools,
  or rate-limit queues.
- **Graceful degradation.** When a dependency is down, serve what you can.
  Stale cache > error page. Core features > auxiliary features.
- **Idempotency.** Design write operations to be safely retried. Use
  idempotency keys for payment/order/state-mutation endpoints. `POST` with
  `Idempotency-Key` header.
- **Rate limiting.** Protect your services from abuse and accidents. Apply at
  the edge (API gateway) and at the service level. Return `429` with
  `Retry-After`.
- **Performance budgets.** Define latency and throughput targets per endpoint.
  Profile critical paths. Optimize only where data says you need to.
- **Caching with purpose.** Cache to reduce latency or load, not both.
  Document the invalidation strategy before you implement the cache. TTL,
  write-through, write-behind, cache-aside — pick one and stick with it.
  Never cache without an invalidation path.

### 1.3 Security

- **Least privilege.** Services, users, and API keys get the minimum access
  needed. Rotate credentials regularly. Revoke what isn't used.
- **Secrets vault.** Store secrets in a dedicated secret manager (Bitwarden
  Secrets Manager, HashiCorp Vault, AWS Secrets Manager, or environment-specific
  equivalents). Never in code, never in version control, never in config files,
  never in logs.
- **Secure defaults.** HTTPS everywhere (HSTS). Secure cookie flags (HttpOnly,
  Secure, SameSite=Lax). Strong TLS configuration (TLS 1.2+, modern cipher
  suites). Disable unused ports, services, and endpoints.
- **Input validation.** Validate at every trust boundary: API parameters,
  user input, file uploads, environment variables, database values. Whitelist
  what's allowed; reject everything else.
- **Output encoding.** Encode output for its context: HTML entities for HTML,
  parameterized queries for SQL, shell escaping for command execution. Prevents
  XSS, injection, and command injection.
- **Dependency management.** Pin dependencies with hash verification
  (`requirements.txt` with hashes, `package-lock.json`, Gradle lockfiles).
  Automate vulnerability scanning (SCA tools: Dependabot, Snyk, OWASP
  Dependency-Check, `pip-audit`, `npm audit`). Review every dependency before
  adding it — you ship their bugs and their vulnerabilities.
- **SBOM.** Generate a Software Bill of Materials for every release. Know
  exactly what you ship. Tools: `syft`, `cyclonedx-gradle-plugin`,
  `pip-audit --sbom`.
- **Threat modeling.** For features touching auth, payments, PII, or external
  APIs: sketch the data flow, list the trust boundaries, enumerate threats
  (STRIDE), and document mitigations. Do this during architecture, not after
  the breach.
- **Authentication & authorization.** Use standard protocols (OAuth 2.0, OIDC,
  WebAuthn). Never roll your own crypto or auth. Validate tokens on every
  request. Short-lived access tokens + refresh token rotation.
- **Mobile/desktop specifics.** Encrypt local storage (Android Keystore,
  `libsecret` on Linux). Validate deep links / custom URL schemes. Obfuscate
  sensitive code paths (ProGuard/R8 for Android). Don't trust the client —
  validate on the server.

---

## 2. Software Development

### 2.1 Code Quality

- **Write for humans first.** Code is read 10× more than written. Optimize for
  comprehension. Clever code is bug-prone code.
- **Consistent style.** Use automated formatters (ktlint/detekt, Black/isort,
  gofmt, Prettier). Style debates cost time; automation ends them. Enforce in CI.
- **Small, focused units.** Functions: ~20 lines max. Classes: one
  responsibility. Modules: one purpose. If you need "and" to describe what
  something does, split it.
- **Meaningful names.** Variables, functions, classes, modules — name them for
  what they do, not how they do it. `userRepository.fetchById(id)` not
  `db.getUserRow(col=id)`. Avoid single-letter names except in loop indices and
  very short lambdas.
- **DRY with judgment.** Don't Repeat Yourself — but don't over-abstract either.
  Two identical blocks: extract. Three similar blocks with different shapes:
  pause — wrong abstraction is costlier than duplication. The rule isn't "no
  duplication"; it's "every piece of knowledge has one canonical representation."
- **Immutability by default.** Prefer `val` over `var` (Kotlin), `const` over
  `let` (JS/TS), `final` fields (Java), frozen dataclasses (Python). Mutable
  state is the root of most concurrency bugs.
- **Composition over inheritance.** Favor interfaces and delegation over deep
  class hierarchies. Inheritance locks you into a taxonomy; composition lets you
  mix behaviors freely.
- **No dead code.** If it's not called, delete it. Version control remembers.
  Dead code confuses readers and bloats builds.
- **Comments explain why, not what.** Code says what. Comments say why the code
  does something surprising, why a workaround exists, or why a simpler approach
  was rejected. Link to the issue/ADR.
- **Error messages are for humans.** "Connection refused" is useless. "Failed to
  reach payment service at payments.internal:8443 after 3 retries (last error:
  ECONNREFUSED)" is actionable.

### 2.2 Testing

- **Tests are a safety net, not a checkbox.** The goal is confidence to refactor,
  not a coverage percentage. 100% coverage of trivial getters is noise. 80%
  coverage that exercises every branch of core logic is gold.
- **Test pyramid, not ice-cream cone.** Base: many fast unit tests. Middle:
  fewer integration tests for cross-component behavior. Top: very few end-to-end
  tests for critical user journeys. Invert this and your CI takes hours.
- **Unit tests.** Test one thing. Isolate with mocks/fakes for external deps.
  Test the happy path, every error path, every edge case (null, empty, max
  size, boundary values). Test that failures propagate correctly.
- **Integration tests.** Test real interactions: database queries return real
  data, API calls hit a test server, message queues deliver messages. Use test
  containers or embedded substitutes (Room in-memory, MockWebServer, WireMock).
- **End-to-end tests.** Cover the top 3–5 user journeys. These are expensive and
  brittle — keep them few and focused. Run them on every merge to main, not
  every commit.
- **Test failure cases first.** Happy path is the easy part. What happens when
  the network fails mid-request? When the DB returns corrupt data? When the user
  submits a 10MB name field? Test these before you ship.
- **Security tests.** Fuzz inputs (AFL, libFuzzer, Jazzer). Test auth bypass,
  privilege escalation, and injection vectors. Run SAST (static analysis) and
  DAST (dynamic analysis) in CI.
- **Flaky test management.** A flaky test is worse than no test — it trains
  teams to ignore failures. Quarantine flaky tests immediately. Fix or delete
  within the sprint. Never ship a test that fails non-deterministically.
- **Test data.** Never use production data in tests. Generate realistic fake
  data. Tests must be deterministic: same seed → same result. No tests that pass
  on Tuesday and fail on Wednesday.
- **Mutation testing.** Coverage tells you what ran; mutation testing tells you
  what was actually tested. Tools: PIT (Java/Kotlin), `mutmut` (Python),
  `stryker` (JS/TS). Run periodically, not per-commit.

### 2.3 Version Control & Branching

- **Pick a branching strategy and enforce it.**
  - **Trunk-based development** — short-lived feature branches (< 1 day), merge
    to main frequently, feature-flag incomplete work. Best for CI/CD velocity.
  - **GitHub Flow** — feature branches off main, PR + review + CI → merge.
    Good for open-source and team coordination.
  - **GitFlow** — separate `develop`, `release`, and `hotfix` branches. Use only
    when you have scheduled releases and multiple versions in production.
  - **Don't mix them.** Pick one per repo and stick with it.
- **Branches are short-lived.** A branch open longer than 2 days is a risk.
  Rebase on main daily to avoid merge hell. If work is too big for a short
  branch, break it into smaller features behind a flag.
- **Commit messages matter.** Structure: `<type>: <subject>` (50 chars max for
  subject). Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`,
  `perf`, `security`. Body explains why, not what. Link to issue/ticket.
  ```
  fix: prevent duplicate user registration on concurrent signup

  The email-uniqueness check and INSERT were not in a transaction,
  allowing a race condition. Wrapped both in a serializable transaction.
  Added an integration test reproducing the race.

  Fixes #1427
  ```
- **Protect main.** Require PR reviews, CI passing, and status checks before
  merge. No direct pushes. Signed commits encouraged but not required for all
  teams.
- **Atomic commits.** Each commit is one logical change. It compiles. It passes
  tests. It can be reverted cleanly. Never commit WIP ("fix stuff", "wip",
  "tmp") — squash before merging.
- **Semantic versioning.** `MAJOR.MINOR.PATCH`. Bump MAJOR for breaking changes,
  MINOR for backward-compatible features, PATCH for backward-compatible fixes.
  Tag every release. Automate version bumping in CI.
- **Changelog.** Maintain a human-readable CHANGELOG.md. Every user-facing
  change gets an entry. Link to the PR/issue. Keep it current — update in the
  same PR that makes the change.

### 2.4 Tooling & Automation

- **CI/CD is not optional.** Every push triggers: build → lint → test →
  security scan. Every merge to main triggers: build → test → package →
  deploy to staging. Deploy to production is a manual gate (or fully automated
  with canary analysis).
- **Infrastructure as Code.** Terraform, Pulumi, CloudFormation, or Ansible.
  Configuration in version control, not in a wiki or a person's head.
  Environments are reproducible. Drift is detected and corrected automatically.
- **Deterministic builds.** Same commit + same flags = identical artifact.
  Pin toolchain versions (JDK, NDK, Python, Node). Use lockfiles
  (`gradle.lockfile`, `package-lock.json`, `poetry.lock`). No `latest` tags.
  No network access during build (vendored or cached deps only).
- **Automate the boring stuff.** Linting, formatting, dead-code detection,
  dependency updates, changelog generation, release notes — script it once,
  never do it manually again.
- **Secret rotation in CI.** CI tokens and deploy keys auto-rotate. Never share
  credentials between environments. Use OIDC where possible (GitHub Actions →
  cloud provider) instead of long-lived secrets.
- **Artifact signing.** Sign every release artifact (APK, AAB, .deb, .jar,
  container image). Verify signatures before deployment. Store signing keys in
  hardware security modules or secure enclaves — never in CI config.
- **Pre-commit hooks.** Catch obvious issues before they reach CI: formatting,
  lint, trailing whitespace, merge conflict markers, large files. Keep hooks
  fast (< 5 seconds). Tools: `pre-commit` (general), `husky` + `lint-staged`
  (JS), `ktlintFormat` + `detekt` for staged files (Android).

---

## 3. Product & UX Design

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

## 4. Collaboration & Process

### 4.1 Requirements & Documentation

- **Requirements answer five questions.** Who is this for? What problem does it
  solve? What are the constraints? What does success look like? What is
  explicitly out of scope? If you can't answer all five, the requirement is
  incomplete.
- **RFCs for non-trivial changes.** Any change touching multiple components,
  introducing a new pattern, or with significant trade-offs gets a design doc.
  Template: problem statement, proposed solution, alternatives considered,
  trade-offs, migration plan, security/privacy implications, rollout plan.
  RFCs are for discussion, not approval — the best idea wins.
- **ADRs record decisions.** Architecture Decision Records capture the context,
  the decision, and the consequences. They prevent "why did we do it this way?"
  two years later. Every ADR has a status: proposed, accepted, deprecated,
  superseded.
- **Documentation lives with the code.** README at the repo root (what, why,
  how to build, how to run). ADRs in `docs/adr/`. API docs auto-generated from
  code. Inline comments for "why," not "what." Wiki for long-form guides and
  runbooks. Every doc has a last-updated date and an owner.
- **Living documentation.** Docs that aren't updated rot. Make doc updates part
  of the PR checklist. Better a one-paragraph README that's current than a wiki
  that's 2 years stale.

### 4.2 Planning & Delivery

- **Work in small, shippable increments.** Break features into slices that each
  deliver user value independently. A slice that "sets up the database but does
  nothing" is a task, not an increment. A slice that "lets users view their
  profile (read-only)" is an increment.
- **Every ticket has acceptance criteria and a definition of done.** AC: "given
  X, when Y, then Z" format. DoD: code reviewed, tested, documented, deployed
  to staging, feature-flagged if behind a flag.
- **Estimate for alignment, not precision.** Story points or T-shirt sizes are
  for capacity planning, not performance evaluation. They will be wrong.
  Re-estimate as you learn. Timebox spikes: "spend 2 days exploring option A,
  then decide."
- **Continuous delivery over big-bang releases.** Ship to production as soon as
  a feature is ready (behind a flag if incomplete). Small, frequent releases
  reduce risk — if something breaks, the diff is tiny.
- **Dependency management across teams.** If team A blocks team B, surface it
  immediately. Visualize dependencies on the board. Break dependencies by
  defining interfaces early and building against mocks.
- **Retrospectives.** Every sprint or milestone: what worked, what didn't, what
  we'll change. Actions, not complaints. Owned, tracked, and reviewed next
  retro.

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

## 5. Quality, Monitoring & Operations

### 5.1 Observability

- **Three pillars.** Logs (discrete events), metrics (aggregate numbers over
  time), traces (end-to-end request flows). All three or you're flying blind.
- **Structured logging.** JSON or key=value format. Every log line has:
  timestamp, level, service name, trace ID, and message. No free-text logs —
  you can't query "something went wrong."
- **Metrics that matter.** RED method for services: Rate (requests/sec), Errors
  (failure rate), Duration (latency p50/p95/p99). USE method for resources:
  Utilization, Saturation, Errors. Business metrics: signups, purchases,
  feature adoption. Don't collect metrics you won't alert on.
- **Distributed tracing.** Every incoming request gets a trace ID. Propagate
  it across service calls. Tools: OpenTelemetry, Jaeger, Zipkin. Without
  traces, debugging a slow request across 5 services is guesswork.
- **SLIs and SLOs.** Service Level Indicators measure what users care about
  (latency, error rate, availability). Service Level Objectives are the targets
  (99.9% availability, p95 latency < 200ms). SLOs are NOT internal targets —
  they're user-facing promises. Set them, measure them, alert on burn rate.
- **Dashboards with purpose.** One dashboard per service showing the "golden
  signals" (latency, traffic, errors, saturation). One business dashboard for
  stakeholders. No dashboard with 50 charts that nobody looks at. Alerts fire
  from SLO burn rate, not from dashboard thresholds.
- **Alert fatigue prevention.** Every alert must require human action. If the
  alert fires and the correct response is "acknowledge and ignore," delete the
  alert. Alert on symptoms (SLO burn rate, error rate spike), not causes (CPU
  > 80%). Page for user-facing impact; ticket for everything else.
- **Log aggregation.** Centralize logs from all services. Tools: Loki,
  Elasticsearch, CloudWatch. Retention: 30 days hot, 90 days cold. Logs that
  aren't searchable don't exist.

### 5.2 Deployment & Rollout

- **No big-bang releases.** Every deployment strategy should support fast,
  tested rollback:
  - **Blue-green:** two identical environments. Deploy to inactive, switch
    traffic. Rollback: switch back. Cost: double infrastructure.
  - **Canary:** deploy to a small % of users/traffic. Monitor for N minutes.
    If clean, ramp to 100%. If not, roll back the canary — most users never
    saw the bad version.
  - **Feature flags:** deploy code dark. Enable for internal users, then beta,
    then 5% → 50% → 100%. Rollback = disable flag (seconds, no redeploy).
    Clean up flags after full rollout — stale flags are tech debt.
- **Rollback is tested and fast.** Rehearse rollbacks in staging. The rollback
  procedure is documented, automated, and takes under 5 minutes. The person
  on-call at 3 AM can execute it without thinking.
- **Database migrations are backward-compatible.** Phase 1: add columns/tables
  (code ignores them). Phase 2: deploy code that writes to both old and new
  schema. Phase 3: migrate existing data. Phase 4: deploy code that reads only
  new schema. Phase 5: drop old columns. Never deploy a migration that breaks
  the currently-running version.
- **Release notes.** Every release gets human-readable notes: new features,
  bug fixes, breaking changes, known issues, upgrade instructions. Not a git
  log dump. Write for the user, not for yourself.
- **Stakeholder communication.** Product, support, marketing, and sales know
  what's shipping, when, and what changes for users. A surprise release is a
  support nightmare. Communication happens before the deploy, not after.

### 5.3 Post-Incident Learning

- **Blameless postmortems.** The goal is to prevent recurrence, not assign
  fault. "The engineer made a mistake" is never the root cause — why was the
  mistake possible? What system allowed it? Focus on the system, not the
  individual.
- **Postmortem template.**
  1. Summary (what happened, impact, duration)
  2. Timeline (detection → response → resolution, with timestamps)
  3. Root cause analysis (5 Whys or equivalent)
  4. Contributing factors (what made it worse or harder to fix)
  5. What went well (detection speed, communication, teamwork)
  6. Action items (concrete, owned, with due dates)
  7. Lessons learned (what we'd do differently)
- **Action items are tracked to completion.** Every postmortem produces tickets.
  Tickets are prioritized, assigned, and reviewed at the next incident review.
  An action item that's 6 months old with no progress is a lie — close it or
  escalate it.
- **Incident commander role.** During an incident, one person coordinates.
  Everyone else executes. The commander is not the person fixing the problem —
  they're managing communication, timeline, and handoffs. Rotate the role so
  everyone builds the skill.
- **Runbook over heroics.** Every alert worth paging on has a runbook: what it
  means, how to diagnose, step-by-step mitigation, escalation path. If the
  runbook doesn't exist, write it during the postmortem. Next time, the
  on-call engineer follows the runbook instead of waking the team.
- **Turn incidents into guardrails.** Every incident should produce at least one
  automated prevention: a test, a validation check, a deployment gate, a
  monitoring alert. If a human can cause it, a machine can prevent it.

---

## 6. Platform-Specific Considerations

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

### 6.2 Debian / Linux Desktop

- **Packaging discipline.** Follow Debian Policy. Dependencies declared
  correctly (Depends, Recommends, Suggests). Files in FHS-compliant locations
  (binaries in `/usr/bin`, libs in `/usr/lib/<pkg>`, config in `/etc/<pkg>`,
  data in `/usr/share/<pkg>`).
- **Lintian clean.** Zero errors. Zero warnings (with overrides for false
  positives, documented). Lintian is the gatekeeper — it catches 90% of
  packaging bugs before users do.
- **Desktop integration.** `.desktop` file with proper categories, icon, and
  MIME types. Respect `XDG_*` environment variables. Use `libsecret` or
  `secret-tool` for credential storage, never plaintext.
- **Accessibility via AT-SPI.** Expose widget roles, names, and states.
  Test with Orca screen reader. Keyboard navigation is mandatory — many Linux
  users are keyboard-driven.
- **Backward compatibility.** Target the oldest supported distribution in your
  user base (e.g., Debian stable, Ubuntu LTS). Don't force users to upgrade
  their OS to run your app. Static linking or vendored libraries when necessary,
  but prefer shared system libs.

---

## Appendix A: Quick-Audit Checklist

Before any release or major merge, run this:

```
[ ] All external calls have timeouts, retries, and circuit breakers
[ ] Secrets are in a vault, not in code/config/logs
[ ] Dependencies are pinned with hashes; vuln scan is clean
[ ] Input validated at every trust boundary; output encoded
[ ] Tests cover happy path, error paths, and edge cases
[ ] No flaky tests; CI is green
[ ] Branch is up to date with main; commits are atomic
[ ] PR reviewed; no open critical or major issues
[ ] Observability: logs are structured, metrics emitted, traces propagated
[ ] SLOs defined and monitored for critical paths
[ ] Rollback plan documented and tested
[ ] Release notes written; stakeholders notified
[ ] Postmortem action items from last incident are closed
[ ] Accessibility: keyboard-navigable, screen-reader tested, color contrast OK
```

---

## Appendix B: Role-to-Section Mapping

| Role | Primary Sections | Secondary |
|------|-----------------|-----------|
| Product Manager | §3.1, §3.4, §4.1, §4.2 | §4.3 |
| Software Architect | §1.1, §1.2, §1.3, §5.1 | §4.1, §6 |
| UX Designer | §3.1, §3.2, §3.3, §3.4 | §4.3, §6 |
| Developer | §2.1, §2.2, §2.3, §2.4 | §1.2, §1.3 |
| Code Reviewer | §2.1, §2.3, §4.3 | §1.2, §1.3, §2.2 |
| QA Engineer | §2.2, §2.4 | §5.1 |
| Build Engineer | §2.4, §6 | §1.3, §5.2 |
| Release Engineer | §5.2, §6 | §2.3, §5.1 |
| Maintenance Engineer | §5.1, §5.3 | §1.2, §2.2, §4.1 |


---

## Appendix C: User-Stated Best Practices (Minimum Bar Cheatsheet)

The user's canonical 5-section best-practices list, captured verbatim. Every
bullet here is **already covered with more depth** in the main reference (see
the per-section cross-references inline). This appendix exists so the
minimum-bar language stays visible, can be diffed against the deep reference,
and loads inline in every role skill (see role `SKILL.md` "Best Practices
Alignment" sections).

When auditing a stage's output, every section below must show evidence
**somewhere** in the deliverable. "Section X" references below point to the
deep guidance in the main body of this document.

### 1. Architecture & Engineering Best Practices

#### 1.1 System Design
- Design for modularity: decompose into small, loosely coupled services or components. -> §1.1 *Modularity first*
- Favor clear contracts (APIs, interfaces) between components. -> §1.1 *Clear contracts*
- Use layered architecture (presentation, domain, data, infrastructure). -> §1.1 *Layered architecture*
- Plan for scalability (horizontal where possible) and observability (logs, metrics, traces) from day one. -> §1.1 *Scalability*, *Observability built in*
- Prefer standard patterns where applicable: CQRS, event-driven, hexagonal/clean architecture. -> §1.1 *Pattern selection*

#### 1.2 Reliability & Performance
- Apply defensive programming: validate inputs, handle errors, timeouts, retries, circuit breakers. -> §1.2 *Defensive programming*, *Timeouts*, *Retry*, *Circuit breaker*
- Design for failure: graceful degradation, fallbacks, bulkheads. -> §1.2 *Graceful degradation*, *Bulkhead*
- Use performance budgets and profiling for critical paths. -> §1.2 *Performance budgets*
- Cache where appropriate, but with clear invalidation strategies. -> §1.2 *Caching with purpose*

#### 1.3 Security
- Follow least privilege for services, users, and data access. -> §1.3 *Least privilege*
- Store secrets in a secure vault, never in code or version control. -> §1.3 *Secrets vault*
- Use secure defaults: HTTPS everywhere, secure cookies, strong TLS configs. -> §1.3 *Secure defaults*
- Implement input validation and output encoding to avoid injections and XSS. -> §1.3 *Input validation*, *Output encoding*
- Keep dependencies updated; use SCA tools (Software Composition Analysis) and automated vuln scanning. -> §1.3 *Dependency management*

### 2. Software Development Best Practices

#### 2.1 Code Quality
- Write clear, readable code; optimize for comprehension, not cleverness. -> §2.1 *Write for humans first*
- Follow a consistent style guide and automated formatting (Prettier, Black, gofmt, etc.). -> §2.1 *Consistent style*
- Keep functions and classes small and focused (single responsibility). -> §2.1 *Small, focused units*
- Use meaningful names for variables, functions, modules. -> §2.1 *Meaningful names*
- Avoid duplication; use DRY carefully without over-abstracting. -> §2.1 *DRY with judgment*

#### 2.2 Testing
- Maintain a strong unit test base for core logic. -> §2.2 *Unit tests*
- Add integration tests for cross-service behavior and external dependencies. -> §2.2 *Integration tests*
- Use end-to-end tests for key user flows. -> §2.2 *End-to-end tests*
- Aim for coverage that protects behavior, not just a % metric. -> §2.2 *Tests are a safety net, not a checkbox*
- Test failure cases, edge cases, and security-relevant logic. -> §2.2 *Test failure cases first*, *Security tests*

#### 2.3 Version Control & Branching
- Use Git with clear branching strategy (GitHub Flow, GitFlow, Trunk-based). -> §2.3 *Pick a branching strategy*
- Keep branches small and short-lived; rebase or merge frequently. -> §2.3 *Branches are short-lived*
- Write descriptive commit messages explaining the "why" as well as the "what". -> §2.3 *Commit messages matter*
- Protect main branches; use PR reviews, CI checks, and status requirements. -> §2.3 *Protect main*

#### 2.4 Tooling & Automation
- Implement CI/CD: automated build, test, lint, security checks on every change. -> §2.4 *CI/CD is not optional*
- Use infrastructure as code (Terraform, CloudFormation, Pulumi) for environments. -> §2.4 *Infrastructure as Code*
- Automate repetitive tasks (scripts, pipelines) to reduce human error. -> §2.4 *Automate the boring stuff*
- Keep build artifacts reproducible; ensure deterministic builds where possible. -> §2.4 *Deterministic builds*

### 3. Product & UX Design Best Practices

#### 3.1 User-Centered Design
- Start from user goals, pain points, and context, not from features. -> §3.1 *Start from user goals, not features*
- Use research: interviews, surveys, analytics, and usability tests. -> §3.1 *Research before design*
- Define personas and main use cases/user journeys before detailing screens. -> §3.1 *Personas are decision tools*, *User journeys*

#### 3.2 Interaction & Visual Design
- Keep interfaces simple, consistent, and predictable. -> §3.2 *Simplicity is hard work*, *Consistency*
- Use a design system (tokens, components, patterns) for consistency. -> §3.2 *Consistency reduces cognitive load*
- Maintain clear hierarchy and affordance: users should know what's clickable and what's important. -> §3.2 *Clear hierarchy*, *Affordance*
- Ensure responsiveness and accessibility across devices. -> §3.2 *Responsive design*, §3.3

#### 3.3 Accessibility
- Follow WCAG guidelines: color contrast, keyboard navigation, screen reader support. -> §3.3 *WCAG 2.2 AA minimum*
- Provide alt text, labels, and semantic HTML for web. -> §3.3 *Alt text and labels*
- Don't rely solely on color to communicate meaning; use icons, text, and patterns. -> §3.3 *Color contrast*

#### 3.4 Validation & Iteration
- Prototype early (low-fidelity first) and test with real users. -> §3.4 *Prototype before you build*, *Test with real users*
- Measure: task success, time on task, funnel conversion, error rates, and NPS/CSAT. -> §3.4 *Measure what matters*
- Iterate based on data + qualitative feedback, not opinions alone. -> §3.4 *Iterate on evidence*

### 4. Collaboration & Process Best Practices

#### 4.1 Requirements & Documentation
- Write clear requirements: problem, scope, constraints, success metrics. -> §4.1 *Requirements answer five questions*
- Use RFCs/design docs for non-trivial changes; capture tradeoffs and alternatives. -> §4.1 *RFCs for non-trivial changes*
- Keep documentation close to the code and up to date (README, ADRs, inline docs). -> §4.1 *Documentation lives with the code*, *Living documentation*

#### 4.2 Planning & Delivery
- Break work into small, testable increments; deliver value continuously. -> §4.2 *Work in small, shippable increments*
- Use tickets with clear acceptance criteria and definition of done. -> §4.2 *Every ticket has acceptance criteria and a definition of done*
- Timebox exploration/spikes; document learnings and decisions. -> §4.2 *Estimate for alignment*, *Retrospectives*

#### 4.3 Code & Design Reviews
- Review for correctness, clarity, consistency, and risk. -> §4.3 *Review for four things*
- Be constructive and specific, focusing on the work, not the person. -> §4.3 *Constructive and specific*
- For designs, review against user goals, constraints, and system standards. -> §4.3 *Design reviews are not code reviews*

### 5. Quality, Monitoring & Operations

#### 5.1 Observability
- Instrument critical flows with structured logs, metrics, and traces. -> §5.1 *Three pillars*, *Structured logging*
- Define SLIs/SLOs (latency, error rate, availability) for important services. -> §5.1 *SLIs and SLOs*
- Use dashboards and alerts tuned to reduce noise but catch real issues. -> §5.1 *Dashboards with purpose*, *Alert fatigue prevention*

#### 5.2 Deployment & Rollout
- Favor blue-green, canary, or feature flags over big-bang releases. -> §5.2 *No big-bang releases*
- Ensure rollback is fast and tested. -> §5.2 *Rollback is tested and fast*
- Maintain release notes and communicate changes to stakeholders. -> §5.2 *Release notes*, *Stakeholder communication*

#### 5.3 Post-Incident Learning
- Run blameless postmortems; focus on systems, not individuals. -> §5.3 *Blameless postmortems*
- Capture root causes, contributing factors, and concrete actions. -> §5.3 *Postmortem template*, *Action items are tracked*
- Turn incidents into long-term improvements (tests, automation, guardrails). -> §5.3 *Turn incidents into guardrails*

### Per-Role Activation Cheatsheet

The minimum-bar bullets above are split across the 10 role skills. When a role
loads, it gets its relevant user-stated bullets inline via the
"User-Stated Best Practices" subsection in that role's `SKILL.md`:

| Role | User-Stated Subsections Embedded |
|------|----------------------------------|
| Orchestrator | All 5 sections (gatekeeper across the pipeline) |
| Product Manager | §3.1, §3.4, §4.1, §4.2 |
| Software Architect | §1.1, §1.2, §1.3, §4.1 |
| UX Designer | §3.1, §3.2, §3.3, §3.4 |
| Developer | §2.1, §2.2, §2.3, §2.4, §1.2, §1.3 |
| Code Reviewer | §2.1, §2.3, §4.3, §2.2 |
| QA Engineer | §2.2, §2.4, §5.1 |
| Build Engineer | §2.4, §1.3, §5.2 |
| Release Engineer | §5.2, §5.1, §2.3 |
| Maintenance Engineer | §5.1, §5.3, §1.2, §2.2, §4.1 |
