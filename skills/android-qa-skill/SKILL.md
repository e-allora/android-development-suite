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
