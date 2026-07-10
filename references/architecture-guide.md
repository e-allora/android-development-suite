# Architecture Guide

> **Reference** — Android Development Suite
> Architecture conventions for modern Android apps using MVVM + Compose + Hilt.

---

## 1. High-Level Architecture

The app follows a **layered architecture** with unidirectional data flow.

```
┌──────────────────────────────────────────────┐
│              Presentation Layer              │
│   Compose UI · ViewModel · UiState           │
└───────────────────┬──────────────────────────┘
                    │ State / Events
┌───────────────────┴──────────────────────────┐
│                Domain Layer                  │
│   Models · Repository Interfaces · Use Cases │
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────┴──────────────────────────┐
│                 Data Layer                    │
│   Repository Impl · Room DAO · Retrofit API  │
└──────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Owns | Does NOT |
|-------|------|----------|
| **Presentation** | UI rendering, state management, user intent | Know where data comes from |
| **Domain** | Business rules, repository interfaces, models | Android framework imports |
| **Data** | Data sources (DB, network), repository impls | UI logic |

**Dependency rule:** Presentation → Domain ← Data. Domain has no dependencies on
either side.

---

## 2. Module Structure

### Single-Module (Small Apps)

```
app/
├── src/main/java/com/example/app/
│   ├── App.kt
│   ├── MainActivity.kt
│   ├── data/
│   │   ├── local/        # Room entities, DAOs
│   │   ├── remote/       # Retrofit APIs, DTOs
│   │   └── repository/   # Repository implementations
│   ├── domain/
│   │   ├── model/         # Domain models
│   │   └── repository/    # Repository interfaces
│   ├── di/               # Hilt modules
│   ├── ui/
│   │   ├── theme/
│   │   ├── navigation/
│   │   └── feature/
│   │       └── profile/
│   │           ├── ProfileScreen.kt
│   │           ├── ProfileViewModel.kt
│   │           └── ProfileUiState.kt
│   └── util/
└── src/test/
```

### Multi-Module (Medium+ Apps)

```
:app          — Application, MainActivity, navigation host, DI root
:core:ui      — Theme, design system, shared composables
:core:common  — Utilities, base classes
:core:data    — Repository implementations, Room, Retrofit
:core:domain  — Models, repository interfaces, use cases
:feature:profile
:feature:settings
:feature:home
```

Rules:

- `:core:domain` depends on **nothing** (pure Kotlin).
- `:core:data` depends on `:core:domain`.
- `:feature:*` depend on `:core:domain` and `:core:ui`.
- `:app` depends on everything and wires the DI graph.

---

## 3. Domain Layer Conventions

### Models

Plain Kotlin data classes — no Android imports.

```kotlin
data class UserProfile(
    val id: String,
    val displayName: String,
    val avatarUrl: String,
    val bio: String,
)
```

### Repository Interfaces

Define contracts in the domain layer; implementations live in the data layer.

```kotlin
interface UserRepository {
    fun observeUser(id: String): Flow<UserProfile>
    suspend fun updateUser(user: UserProfile): Result<Unit>
}
```

- Use `Flow` for observable data.
- Use `Result<T>` for one-shot operations that can fail.
- Repository interfaces should be framework-agnostic.

### Use Cases (optional)

For complex business logic, wrap it in a `UseCase`:

```kotlin
class RefreshUserProfile @Inject constructor(
    private val repository: UserRepository,
) {
    suspend operator fun invoke(id: String): Result<UserProfile> =
        repository.refreshUser(id)
}
```

- One use case = one responsibility.
- Use `operator fun invoke()` so the call site reads as a function.
- Use cases are `@Inject constructor` — Hilt provides them.

---

## 4. Data Layer Conventions

### Repository Implementation

```kotlin
class UserRepositoryImpl @Inject constructor(
    private val dao: UserDao,
    private val api: UserApi,
) : UserRepository {

    override fun observeUser(id: String): Flow<UserProfile> =
        dao.observeUser(id).map { it.toDomain() }

    override suspend fun updateUser(user: UserProfile): Result<Unit> =
        runCatching {
            api.updateUser(user.toDto())
            dao.upsertUser(user.toEntity())
        }
}
```

- Repository is the **single source of truth**: network writes update the
  database, and UI observes the database via `Flow`.
- Map between layers (`Entity → Domain`, `Dto → Domain`).

### Room

- `@Entity` classes live in `data/local/`.
- `@Dao` interfaces return `Flow` for observable queries.
- Schema export enabled for migration testing:
  `room { schemaDirectory("$projectDir/schemas") }`.

### Retrofit

- API interfaces in `data/remote/`.
- Use `kotlinx.serialization` (not Gson) — annotate DTOs with `@Serializable`.
- Add an OkHttp `HttpLoggingInterceptor` in debug builds.

---

## 5. Presentation Layer Conventions

### ViewModel

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val uiState: StateFlow<ProfileUiState> = userRepository
        .observeUser(userId)
        .map { ProfileUiState.Success(it) }
        .catch { emit(ProfileUiState.Error(it.message ?: "Unknown")) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), ProfileUiState.Loading)
}
```

- Expose `StateFlow<UiState>` — never `MutableStateFlow`.
- Use `stateIn` with `SharingStarted.WhileSubscribed(5_000)`.
- Read navigation arguments from `SavedStateHandle`.

### Screen

```kotlin
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // Render based on uiState
}
```

### State

Use a sealed interface for UI state:

```kotlin
sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Error(val message: String) : ProfileUiState
    data class Success(val profile: UserProfile) : ProfileUiState
}
```

- One state class per screen.
- Include everything the UI needs (loading, error, data).
- User actions (like "retry") go on the `ViewModel`, not the state.

---

## 6. Dependency Injection

### Hilt Modules

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .build()
}
```

- `@Binds` for interface-to-implementation bindings (abstract, faster).
- `@Provides` for objects you construct.
- Group modules by concern: `RepositoryModule`, `NetworkModule`, `DatabaseModule`.

### Scoping

| Scope | Lifetime | Use For |
|-------|----------|---------|
| `@Singleton` (SingletonComponent) | App lifetime | Database, Retrofit, repositories |
| `@ActivityRetainedScoped` | Activity (survives config change) | Heavy per-screen objects |
| `@ViewModelScoped` | ViewModel lifetime | Per-screen data |
| `@Composable` (no scope) | Recomposition | UI |

---

## 7. Error Handling

### Strategy

1. **Fail fast at the source** — network/DB errors propagate as exceptions.
2. **Wrap in `Result<T>`** at the repository boundary.
3. **Map to `UiState.Error`** in the ViewModel with a user-facing message.
4. **Never swallow** — log to crash reporting, surface to UI.

### Retry

Use a `RetryPolicy` for transient network failures:

```kotlin
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
) : UserRepository {
    override suspend fun refreshUser(id: String): Result<UserProfile> =
        runCatching {
            retry(times = 3) { attempt ->
                api.getUser(id)
            }
        }
}
```

- Retry only idempotent operations.
- Use exponential backoff for network retries.

---

## 8. Testing Boundaries

| Layer | Test Type | Tools | What to Test |
|-------|-----------|-------|--------------|
| Domain (models, use cases) | Unit | JUnit, Truth | Business logic, mapping functions |
| Data (repository impl) | Unit | JUnit, MockK, Turbine | Mapping, error handling, retry |
| Room DAO | Instrumented | Robolectric, Room testing | Queries, migrations |
| Retrofit API | Unit | MockWebServer | Request/response parsing |
| ViewModel | Unit | JUnit, Turbine, MainDispatcherRule | State transitions, intents |
| Compose UI | UI | Compose TestRule, Roborazzi | Rendering, interactions, a11y |
| Navigation | UI | Compose TestRule | Route correctness, deep links |
| E2E | Instrumented | Espresso | Full user flows |

Rules:

- Domain layer tests are pure JVM — no Android dependencies.
- ViewModel tests use `MainDispatcherRule` to control coroutines.
- Repository tests fake the DAO/API — don't use real Room or network.
- Compose UI tests assert on visible content and interactions, not
  implementation details.
