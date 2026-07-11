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


---

## Best Practices Alignment

This role aligns with the following sections of the shared
[Best Practices Reference](references/best-practices.md).

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
