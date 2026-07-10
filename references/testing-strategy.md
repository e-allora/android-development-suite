# Testing Strategy

> **Reference** — Android Development Suite
> Comprehensive testing strategy covering unit, UI, integration, and screenshot
> tests for Android apps.

---

## 1. Test Pyramid

```
                 /\
                /  \
               / E2E\          ~5%
              /------\
             /  UI   \         ~15%
            /---------\
           /  Unit    \       ~80%
          /____________\
```

| Level | % of Tests | Speed | Confidence |
|-------|-----------|-------|-----------|
| Unit | ~80% | Fast (<1s each) | Low (logic only) |
| UI / Integration | ~15% | Medium (seconds) | Medium |
| E2E | ~5% | Slow (minutes) | High |

Invest most in unit tests — they are fast and catch regressions early.

---

## 2. Tooling Stack

| Tool | Purpose |
|------|---------|
| **JUnit 4** | Test runner, assertions |
| **Truth** | Fluent assertions (`assertThat(x).isEqualTo(y)`) |
| **MockK** | Mocking / verification |
| **Turbine** | `Flow` testing |
| **kotlinx-coroutines-test** | Coroutine test control |
| **Robolectric** | On-JVM Android framework |
| **Roborazzi** | Screenshot tests (JVM via Robolectric) |
| **Espresso** | Instrumented UI tests |
| **Compose Test Rule** | Compose UI tests |
| **MockWebServer** | Retrofit API tests |
| **Room Testing** | Migration + DAO tests |

---

## 3. Unit Testing Conventions

### ViewModel Tests

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {

    @get:Rule val mainDispatcherRule = MainDispatcherRule()
    private val repository = FakeUserRepository()

    @Test
    fun `loads user on init`() = runTest {
        repository.emitUser(sampleUser)
        val viewModel = ProfileViewModel(repository, SavedStateHandle(mapOf("userId" to "123")))
        viewModel.uiState.test {
            assertThat(awaitItem()).isInstanceOf(ProfileUiState.Loading::class.java)
            val success = awaitItem()
            assertThat(success).isInstanceOf(ProfileUiState.Success::class.java)
            assertThat((success as ProfileUiState.Success).profile).isEqualTo(sampleUser)
        }
    }
}
```

### Repository Tests

```kotlin
class UserRepositoryImplTest {

    private val dao = mockk<UserDao>()
    private val api = mockk<UserApi>()
    private val repository = UserRepositoryImpl(dao, api)

    @Test
    fun `updateUser persists locally and remotely`() = runTest {
        every { api.updateUser(any()) } returns Unit
        coEvery { dao.upsertUser(any()) } returns Unit

        repository.updateUser(sampleUser)

        coVerify { dao.upsertUser(sampleUser.toEntity()) }
        verify { api.updateUser(sampleUser.toDto()) }
    }
}
```

### Domain Model Tests

```kotlin
@Test
fun `toEntity maps all fields`() {
    val model = UserProfile("1", "Alice", "url", "bio")
    val entity = model.toEntity()
    assertThat(entity.id).isEqualTo("1")
    assertThat(entity.name).isEqualTo("Alice")
}
```

---

## 4. Compose UI Testing

### Screen Tests

```kotlin
class ProfileScreenTest {

    @get:Rule val composeRule = createComposeRule()

    @Test
    fun `shows loading state`() {
        composeRule.setContent {
            AppTheme { ProfileScreen(uiState = ProfileUiState.Loading) }
        }
        composeRule.onNodeWithText("Loading...").assertIsDisplayed()
    }

    @Test
    fun `shows user name when loaded`() {
        composeRule.setContent {
            AppTheme { ProfileScreen(uiState = ProfileUiState.Success(sampleUser)) }
        }
        composeRule.onNodeWithText("Alice").assertIsDisplayed()
    }
}
```

### Test Tags Convention

- Use `Modifier.testTag("profile-avatar")` for elements without stable text.
- Tag names follow `<feature>-<element>`: `profile-avatar`, `profile-bio`.
- Define tag constants in a `TestTags` object.

```kotlin
object ProfileTags {
    const val Avatar = "profile-avatar"
    const val EditButton = "profile-edit"
}

IconButton(onClick = {}, modifier = Modifier.testTag(ProfileTags.EditButton)) { ... }
```

---

## 5. Test Doubles

### Fakes vs Mocks

| | Fake | Mock |
|---|------|------|
| **What** | Working in-memory implementation | Recording proxy |
| **Tool** | Hand-written | MockK |
| **Use for** | Repository, data source | Verifying specific calls |
| **Refactor-safe?** | ✅ Yes | ❌ No (brittle) |

### FakeRepository Pattern

```kotlin
class FakeUserRepository : UserRepository {
    private val users = MutableStateFlow<Map<String, UserProfile>>(emptyMap())

    override fun observeUser(id: String): Flow<UserProfile> =
        users.map { it[id] ?: throw NoSuchElementException(id) }

    override suspend fun updateUser(user: UserProfile): Result<Unit> = runCatching {
        users.update { it + (user.id to user) }
    }

    // Test helper
    fun emitUser(user: UserProfile) {
        users.update { it + (user.id to user) }
    }
}
```

- Prefer fakes for repositories — they survive refactor better than mocks.
- Use mocks for leaf dependencies (API clients) where behaviour verification matters.

---

## 6. Coroutines Test Utilities

### MainDispatcherRule

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Turbine

```kotlin
viewModel.uiState.test {
    assertThat(awaitItem()).isEqualTo(Loading)
    assertThat(awaitItem()).isEqualTo(Success(data))
    cancelAndIgnoreRemainingEvents()
}
```

### runTest

```kotlin
@Test
fun `test`() = runTest {
    // Virtual time — delays skip instantly
    repository.fetch()
    advanceUntilIdle()
}
```

---

## 7. Room Testing

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
class UserDaoTest {

    private lateinit var database: AppDatabase
    private lateinit var dao: UserDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java,
        ).allowMainThreadQueries().build()
        dao = database.userDao()
    }

    @After
    fun teardown() = database.close()

    @Test
    fun `insert and observe`() = runTest {
        dao.upsertUser(sampleEntity)
        dao.observeUser("1").test {
            assertThat(awaitItem()).isEqualTo(sampleEntity)
        }
    }
}
```

- Always use `inMemoryDatabaseBuilder` for tests.
- Test migrations with `MigrationTestHelper` and exported schemas.

---

## 8. CI Integration

### GitHub Actions

```yaml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - uses: gradle/actions/setup-gradle@v3

      - name: Unit tests
        run: ./gradlew testDebugUnitTest

      - name: Coverage report
        run: ./gradlew jacocoTestReport

      - name: Upload coverage
        uses: codecov/codecov-action@v4

      - name: Lint
        run: ./gradlew lintDebug

      - name: Build
        run: ./gradlew assembleDebug
```

### Coverage Targets

| Module | Min Coverage |
|--------|-------------|
| `:core:domain` | 90% |
| `:core:data` | 80% |
| `:feature:*` | 70% |
| `:app` | 50% |

Block merges below the target using a coverage gate in CI.

---

## 9. Roborazzi Screenshot Tests

```kotlin
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w360dp-h640dp")
class ProfileScreenScreenshotTest {

    @get:Rule val roborazziRule = RoborazziRule(
        captureRoot = composeRule,
        options = RoborazziRule.Options(outputDirectoryPath = "src/test/screenshots"),
    )

    @Test
    @RoborazziConfig(outputDir = "src/test/screenshots")
    fun `profile screen light`() {
        composeRule.setContent {
            AppTheme { ProfileScreen(uiState = ProfileUiState.Success(sampleUser)) }
        }
        composeRule.waitForIdle()
        captureRoboImage()
    }
}
```

- Run: `./gradlew verifyRoborazziDebug` to compare against baselines.
- Update baselines: `./gradlew recordRoborazziDebug`.
- Commit baseline PNGs to the repo.

---

## 10. Testing Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Testing implementation details | Breaks on refactor | Test behaviour |
| `Thread.sleep()` in tests | Flaky, slow | Use `runTest` + `advanceUntilIdle` |
| Real network / DB in unit tests | Slow, flaky | Fake or mock |
| `Dispatchers.Main` without rule | Hangs | Use `MainDispatcherRule` |
| Mocking the class under test | Tests the mock | Mock only collaborators |
| One assertion per test only | Misses related bugs | Group related assertions |
| Testing private methods | Implementation detail | Test via public API |
| No test tags in dynamic UI | Can't find elements | Add `testTag` |
| Ignoring edge cases | Hides bugs | Test empty, error, boundary states |
| 100% coverage target | Encourages bad tests | Target meaningful coverage (70-90%) |
