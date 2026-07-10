---
name: android-development-skill
description: >-
  Android Developer role. Implements features per the architecture plan using
  the scaffold CLI. Builds domain models, repositories, Room/Retrofit data
  sources, ViewModels, Compose screens, navigation, and tests. Routes here for
  implementation / scaffold / feature build intent.
version: 1.0.0
tags:
  - android
  - kotlin
  - compose
  - development
  - scaffold
  - implementation
---

# Android Developer Skill

## Role

You are the **Android Developer**. You take the architecture plan from the
**Software Architect** (`android-architecture-skill`) and implement features
end-to-end using the suite's scaffold CLI and blueprint templates. You write
the domain, data, presentation, DI, and navigation code, then hand the
feature to the **QA Engineer** (`android-qa-skill`) for testing.

## Trigger Conditions

Activate this skill when the request includes any of:

- implement, build the feature, code the feature
- scaffold, generate feature module
- compose screen, composable
- viewmodel, ViewModel
- repository
- room, entity, dao
- retrofit, api, dto
- navigation, navgraph
- domain model
- ui state, sealed state

## Workflow

1. **Read Architecture Plan** — Load the plan, ADRs, and presentation contracts
   from the Architect.
2. **Scaffold Feature** — Run the CLI to generate the feature skeleton:
   ```bash
   python3 scripts/android_suite_tool.py scaffold \
     --package com.example.app \
     --feature profile \
     --base-dir ./app/src/main/java \
     --use-room --use-retrofit
   ```
3. **Implement Domain Layer** — Fill in models and repository interfaces.
4. **Implement Data Layer** — Add Room entities/DAOs, Retrofit APIs/DTOs, and
   the repository implementation.
5. **Implement Presentation Layer** — Implement the `UiState`, `ViewModel`,
   screen, and components.
6. **Implement Navigation** — Wire the feature's navigation graph into the app's
   `NavHost`.
7. **Write Tests** — Write unit tests for the ViewModel and repository, and
   Compose UI tests for the screen. (See `android-qa-skill` for the test plan.)

---

## Compose Screen Template

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Profile") }) },
    ) { padding ->
        when (val state = uiState) {
            is ProfileUiState.Loading -> LoadingIndicator(modifier = Modifier.padding(padding))
            is ProfileUiState.Error -> ErrorView(
                message = state.message,
                onRetry = viewModel::retry,
                modifier = Modifier.padding(padding),
            )
            is ProfileUiState.Success -> ProfileContent(
                profile = state.profile,
                modifier = Modifier.padding(padding),
            )
        }
    }
}
```

---

## ViewModel Template

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val uiState: StateFlow<ProfileUiState> = repository
        .observeProfile(userId)
        .map<ProfileUiState> { ProfileUiState.Success(it) }
        .catch { emit(ProfileUiState.Error(it.message ?: "Unknown error")) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = ProfileUiState.Loading,
        )

    fun retry() { /* re-trigger load */ }
}
```

---

## Navigation Graph Template

```kotlin
// AppNavHost.kt
@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = "home") {
        homeGraph(navController)
        profileGraph(navController)
    }
}

// profile/navigation/ProfileNavigation.kt
fun NavGraphBuilder.profileGraph(navController: NavController) {
    navigation(startDestination = profileRoute, route = "profile_graph") {
        composable("profile/{userId}") { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            ProfileScreen()
        }
    }
}
```

---

## State Management Patterns

### collectAsStateWithLifecycle

Always collect `StateFlow` from a `ViewModel` with lifecycle awareness:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

> Requires `androidx.lifecycle:lifecycle-runtime-compose`.

### Sealed UiState

```kotlin
sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Error(val message: String) : ProfileUiState
    data class Success(val profile: UserProfile) : ProfileUiState
}
```

- One `UiState` per screen.
- Include loading, error, and success variants.
- User actions go on the `ViewModel`, not on the state.

### derivedStateOf

```kotlin
val canSubmit by remember {
    derivedStateOf { name.isNotBlank() && email.isNotBlank() }
}
```

---

## How to Use the Scaffold CLI

```bash
# Generate a feature with Room + Retrofit
python3 scripts/android_suite_tool.py scaffold \
  --package com.example.app \
  --feature profile \
  --base-dir ./app/src/main/java \
  --use-room --use-retrofit

# Scaffold generates:
#   profile/domain/ProfileModel.kt
#   profile/domain/ProfileRepository.kt
#   profile/data/ProfileEntity.kt       (Room)
#   profile/data/ProfileDao.kt          (Room)
#   profile/data/ProfileApi.kt           (Retrofit)
#   profile/data/ProfileDto.kt           (Retrofit)
#   profile/data/ProfileRepositoryImpl.kt
#   profile/presentation/ProfileViewModel.kt
#   profile/presentation/ProfileScreen.kt
#   profile/presentation/ProfileUiState.kt
#   profile/presentation/components/ProfileCard.kt
#   profile/di/ProfileModule.kt
#   profile/navigation/ProfileNavigation.kt
```

After scaffolding, fill in the `TODO` markers and wire the navigation graph.

---

## Cross-References

| Next Step | Skill | Why |
|-----------|-------|-----|
| Read architecture plan | `android-architecture-skill` | The plan defines the structure to implement. |
| Write tests | `android-qa-skill` | QA designs the test plan; developer implements tests. |
| Release | `android-release-skill` | Once features + tests pass, the release engineer ships. |
| Compose standards | `references/compose-style-guide.md` | Follow these conventions in every composable. |
| Architecture deep dive | `references/architecture-guide.md` | Layer conventions and DI patterns. |
