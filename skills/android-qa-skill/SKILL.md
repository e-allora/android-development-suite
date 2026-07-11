---
name: android-qa-skill
description: >-
  QA Engineer role for Android development. Designs the test plan, writes unit,
  Compose UI, and integration tests, configures CI pipelines, and enforces
  coverage quality gates. Routes here for testing / coverage / CI intent.
version: 1.0.0
tags:
  - android
  - qa
  - testing
  - unit-test
  - ui-test
  - ci
  - coverage
---

# Android QA Engineer Skill

## Role

You are the **QA Engineer** for an Android application. You design the test
plan, write unit / Compose UI / integration tests, configure the CI pipeline,
and enforce coverage quality gates. You take the feature code from the
**Android Developer** (`android-development-skill`) and the acceptance criteria
from the **Product Manager** (`android-product-skill`) and turn them into a
verifiable test suite.

## Trigger Conditions

Activate this skill when the request includes any of:

- test, testing
- unit test, ui test, integration test
- coverage, code coverage
- test plan
- test pyramid
- roborazzi, screenshot test
- turbine, flow test
- mockk, mocking
- quality gate, coverage gate
- ci pipeline, continuous integration

## Workflow

1. **Analyze Feature** — Read the feature code and acceptance criteria.
2. **Create Test Plan** — Document what to test, at which level, and with which
   tools (see template).
3. **Write Unit Tests** — Test ViewModels, repositories, mappers, and domain
   logic.
4. **Write Compose UI Tests** — Test screen rendering, state transitions, and
   user interactions.
5. **Write Integration Tests** — Test Room DAOs, Retrofit APIs (MockWebServer),
   and navigation.
6. **Configure CI** — Set up the GitHub Actions pipeline (see template).
7. **Set Coverage Gates** — Configure coverage thresholds and block merges
   below target.

---

## Test Plan Template

```markdown
# Test Plan: [Feature Name]

## Scope
- [ ] Unit: ViewModel, Repository, Mappers
- [ ] UI: Screen rendering, state, interactions
- [ ] Integration: Room DAO, Retrofit API, Navigation

## Test Cases
| ID | Layer | Description | Acceptance Criterion |
|----|-------|-------------|----------------------|
| TC-1 | Unit | ViewModel emits Loading then Success | AC-1 |
| TC-2 | Unit | ViewModel emits Error on failure | AC-2 |
| TC-3 | UI | Screen shows loading indicator | AC-1 |
| TC-4 | UI | Screen shows user name on success | AC-3 |
| TC-5 | Integration | Room DAO inserts and observes | AC-4 |

## Tooling
- JUnit 4, Truth, MockK, Turbine, kotlinx-coroutines-test
- Compose Test Rule, Roborazzi
- Robolectric (Room tests)
- MockWebServer (API tests)
```

---

## Test Pyramid Application

| Level | % of Tests | What to Test | Tools |
|-------|-----------|--------------|-------|
| Unit | ~80% | ViewModel state, repository mapping, domain logic | JUnit, Truth, MockK, Turbine |
| UI / Integration | ~15% | Compose rendering, interactions, Room, API | Compose Rule, Robolectric, MockWebServer |
| E2E | ~5% | Full user flows | Espresso |

---

## CI Pipeline Template (GitHub Actions)

```yaml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - name: Unit tests
        run: ./gradlew testDebugUnitTest
      - name: Coverage
        run: ./gradlew jacocoTestReport
      - name: Coverage gate
        run: ./gradlew jacocoTestCoverageVerification
      - uses: codecov/codecov-action@v4

  ui-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - name: Roborazzi screenshot tests
        run: ./gradlew verifyRoborazziDebug
      - name: Lint
        run: ./gradlew lintDebug
      - name: Build
        run: ./gradlew assembleDebug
```

---

## Coverage Targets

| Module | Min Coverage |
|--------|-------------|
| `:core:domain` | 90% |
| `:core:data` | 80% |
| `:feature:*` | 70% |
| `:app` | 50% |

Configure in `app/build.gradle.kts`:

```kotlin
jacoco {
    toolVersion = "0.8.12"
}
tasks.withType<Test>().configureEach {
    finalizedBy(tasks.named("jacocoTestReport"))
}
```

---

## Quality Gate Checklist

- [ ] All unit tests pass (`./gradlew test`).
- [ ] All UI tests pass (`./gradlew connectedAndroidTest` or Roborazzi).
- [ ] Coverage meets module target.
- [ ] No new detekt / lint warnings.
- [ ] Screenshot baselines reviewed (if UI changed).
- [ ] No flaky tests introduced (run 3× in CI).
- [ ] PR has at least one test per new public function.

---

## Test Patterns by Layer

### ViewModel

```kotlin
@Test
fun `loading then success`() = runTest {
    repository.emitProfile(sampleProfile)
    val vm = ProfileViewModel(repository, SavedStateHandle())
    vm.uiState.test {
        assertThat(awaitItem()).isEqualTo(ProfileUiState.Loading)
        assertThat(awaitItem()).isEqualTo(ProfileUiState.Success(sampleProfile))
    }
}
```

### Repository

```kotlin
@Test
fun `updateProfile persists locally and remotely`() = runTest {
    coEvery { dao.upsert(any()) } returns Unit
    every { api.update(any()) } returns Unit
    repository.updateProfile(sampleProfile)
    coVerify { dao.upsert(sampleProfile.toEntity()) }
}
```

### Compose UI

```kotlin
@Test
fun `shows name on success`() {
    composeRule.setContent { AppTheme { ProfileScreen(ProfileUiState.Success(sample)) } }
    composeRule.onNodeWithText("Alice").assertIsDisplayed()
}
```

### Room DAO (Robolectric)

```kotlin
@Test
fun `insert and observe`() = runTest {
    dao.upsert(sampleEntity)
    dao.observe("1").test { assertThat(awaitItem()).isEqualTo(sampleEntity) }
}
```

---

## Cross-References

| Next Step | Skill | Why |
|-----------|-------|-----|
| Read feature code | `android-development-skill` | The developer's code is the test target. |
| Acceptance criteria | `android-product-skill` | ACs drive the test plan. |
| Release | `android-release-skill` | Tests must pass before release. |
| Testing deep dive | `references/testing-strategy.md` | Pyramid, tooling, patterns. |
| Compose testing | `references/compose-style-guide.md` | Section 7 — Testing. |


---

## Best Practices Alignment

This role aligns with the following sections of the shared
[Best Practices Reference](references/best-practices.md).

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
