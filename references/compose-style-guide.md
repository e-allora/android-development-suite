# Jetpack Compose Style Guide

> **Reference** — Android Development Suite
> Coding standards and best practices for Jetpack Compose UI development.

---

## 1. Composable Function Rules

### Naming

- Composable functions use **PascalCase** and describe the UI element, not the
  action: `ProfileHeader`, `UserAvatar`, `SubmitButton`.
- Non-composable helper functions use camelCase.
- Composable functions that return a value (not `Unit`) should be named to
  describe the value: `rememberCurrentUser()`.

### Structure

```kotlin
@Composable
fun ProfileHeader(
    user: User,
    modifier: Modifier = Modifier,
) {
    // 1. State reads
    // 2. Side-effect launching (LaunchedEffect, etc.)
    // 3. Composition of child composables
}
```

Rules:

1. **Parameters first.** Data flows in through parameters.
2. **`Modifier` parameter.** Every public composable that renders UI must accept
   a `modifier: Modifier = Modifier` parameter as the **second** parameter
   (after required data).
3. **No implicit state.** Do not read `ViewModel` or global state directly
   inside a leaf composable — hoist it.
4. **Single responsibility.** One composable = one UI concern.

### Stability

Compose recomposes when inputs change. A composable is **stable** if its inputs
are stable types (primitives, `String`, or classes marked `@Immutable` /
`@Stable`).

- Prefer `data class` with `val` properties — they are stable by default.
- Use `@Immutable` for classes Compose cannot infer stability for (e.g., `List`
  wrappers).
- Avoid `List<Unit>`-returning lambdas; pass specific callbacks.

```kotlin
@Immutable
data class UserProfile(
    val id: String,
    val name: String,
    val avatarUrl: String,
)
```

---

## 2. State Management

### State Hoisting

Stateless composables are easier to test and reuse. **Hoist** state to the
caller:

| Pattern | Instead of | Use |
|---------|-----------|-----|
| `value` + `onValueChange` | `remember { mutableStateOf() }` inside | Pass state down, events up |

```kotlin
// Stateless — hoisted
@Composable
fun NameField(
    name: String,
    onNameChange: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    TextField(value = name, onValueChange = onNameChange, modifier = modifier)
}
```

### Collecting State

Always use `collectAsStateWithLifecycle()` (from
`androidx.lifecycle:lifecycle-runtime-compose`) — it stops collecting when the
lifecycle drops below `STARTED`.

```kotlin
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // ...
}
```

> ❌ Do **not** use `collectAsState()` in screens tied to a `ViewModel` — it
> does not respect lifecycle.

### Derived State

Use `remember { derivedStateOf { } }` when a value depends on other states but
should only update when the *result* changes:

```kotlin
val showSubmit by remember {
    derivedStateOf { name.isNotBlank() && email.isNotBlank() }
}
```

---

## 3. Performance

### Recomposition

- **Avoid recomputing expensive operations** during composition. Use
  `remember`.
- **Do not read state you don't use.** Reading `ViewModel` properties at the
  top of a large composable forces the whole tree to recompose.
- **Use `key()`** in `LazyColumn` / `LazyRow` items when list items have stable
  identities.

### Lazy Lists

```kotlin
LazyColumn {
    items(items = list, key = { it.id }) { item ->
        ProfileRow(item)
    }
}
```

- Always provide a `key` for `items()` when the list has stable IDs.
- Do **not** create new lambda instances in every item — hoist them with
  `remember`.

### Modifiers

- Chain modifiers in order: layout → appearance → interaction.
- Reuse modifiers with `remember` when they are expensive (e.g.,
  `drawBehind`).

---

## 4. Side Effects

| Effect | When to use | Cancels on |
|--------|-------------|------------|
| `LaunchedEffect(key)` | One-shot work keyed on input | Key change or leave composition |
| `rememberCoroutineScope()` | Long-lived scope tied to composition | Leave composition |
| `DisposableEffect` | Cleanup required (listeners, observers) | Leave composition / key change |
| `SideEffect` | Publish Compose state to non-Compose systems | Every recomposition |
| `produceState` | Convert non-Compose state into Compose state | Leave composition |
| `derivedStateOf` | Compute derived value | Inputs change |
| `rememberUpdatedState` | Capture latest value in long-lived effects | — |

### Rules

1. **No side effects in the composition body.** Use an effect API.
2. **Key your effects.** `LaunchedEffect(Unit)` runs once — use it only for
   truly one-shot work; otherwise key on the data you depend on.
3. **Clean up.** If you register a listener in `DisposableEffect`, deregister in
   `onDispose`.

```kotlin
LaunchedEffect(userId) {
    viewModel.loadUser(userId)
}
```

---

## 5. Theming & Design System

### Material 3

Use `MaterialTheme` with `colorScheme`, `typography`, and `shapes`. Do **not**
hardcode colors or text styles in composables.

```kotlin
Text(
    text = title,
    color = MaterialTheme.colorScheme.onSurface,
    style = MaterialTheme.typography.titleLarge,
)
```

### Dark Mode

- Always support dark theme.
- Use semantic color tokens (`onSurface`, `surfaceVariant`, `primaryContainer`)
  — never assume a specific color.
- Test with `@Preview(name = "Dark", uiMode = UI_MODE_NIGHT_YES)`.

### Dimensions

- Define dimension resources in `dimens.xml` or a `Dimensions` object.
- Use `dp` for spacing, `sp` for text sizes.
- Prefer `Arrangement.spacedBy(dp)` over repeated `padding`.

---

## 6. Navigation

### NavHost

```kotlin
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController, startDestination = "home") {
        composable("home") { HomeScreen() }
        composable("profile/{userId}") { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            ProfileScreen(userId)
        }
    }
}
```

### Deep Links

```kotlin
composable(
    "profile/{userId}",
    deepLinks = listOf(navDeepLink { uriPattern = "myapp://profile/{userId}" }),
) { ... }
```

Rules:

- Route strings should be constants.
- Use typed `Safe Args`-style wrappers or `Serializable` route arguments.
- Keep navigation logic in `NavGraphBuilder` extensions, not screens.

---

## 7. Testing

### Previews

```kotlin
@Preview(showBackground = true, name = "Light")
@Preview(showBackground = true, uiMode = UI_MODE_NIGHT_YES, name = "Dark")
@Composable
private fun ProfileHeaderPreview() {
    AppTheme {
        ProfileHeader(user = sampleUser)
    }
}
```

- Every public composable should have at least one `@Preview`.
- Provide preview data in a `PreviewData` object, not hardcoded in the function.
- Preview multi-state variants: loading, error, empty, populated.

### UI Tests

```kotlin
@Test
fun profileHeader_displaysName() {
    composeRule.setContent {
        AppTheme { ProfileHeader(user = sampleUser) }
    }
    composeRule.onNodeWithText("Alice").assertIsDisplayed()
}
```

- Use `createComposeRule()` for pure Compose tests.
- Use `testTag` to find nodes that don't have stable text.
- Avoid sleeping; use `waitUntil`.

---

## 8. Accessibility

### Content Description

- Every `Icon`, `Image`, and `IconButton` must have a `contentDescription`
  (or `null` if purely decorative with adjacent text).
- Use string resources for localizable descriptions.

```kotlin
IconButton(onClick = onSave) {
    Icon(Icons.Default.Save, contentDescription = stringResource(R.string.save))
}
```

### Touch Targets

- Minimum **48dp** for interactive elements.
- Use `Modifier.size(48.dp)` or `Modifier.minimumInteractiveComponentSize()`.

### TalkBack

- Test with TalkBack enabled.
- Group related content with `Modifier.semantics(mergeDescendants = true)`.
- Use `LiveRegion` for dynamic announcements.

---

## 9. Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `collectAsState()` in screens | Doesn't respect lifecycle | Use `collectAsStateWithLifecycle()` |
| Mutable state in composables | Causes recomposition bugs | Hoist to `ViewModel` |
| Hardcoded colors | Breaks dark mode | Use `MaterialTheme.colorScheme` |
| `LaunchedEffect(Unit)` for data | Runs once, never refreshes | Key on the relevant input |
| New lambdas in `LazyColumn` items | Extra recomposition | Hoist lambdas with `remember` |
| Missing `key` in lazy lists | Unnecessary recomposition | `items(key = { it.id })` |
| State reads at top of large composable | Whole tree recomposes | Push reads to leaves |
| Side effects in composition body | Non-deterministic UI | Use `LaunchedEffect` / `SideEffect` |
| `Modifier` not a parameter | Cannot be repositioned | Always accept `modifier` |
| Nested `ScrollableColumn` | Layout conflicts | Use `LazyColumn` |
