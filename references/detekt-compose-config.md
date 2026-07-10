# Detekt Configuration for Compose/MVVM Projects

Pitfalls discovered during VoxBook Stage 5 gate setup. Save yourself the trial-and-error.

## config.excludes does NOT disable rules

`config.excludes` only silences config *validation* warnings, not rule execution. To disable a rule you MUST set `active: false` in its section:

```yaml
# WRONG — rule still runs:
config:
  excludes: 'style/MagicNumber,style/WildcardImport'

# CORRECT:
style:
  MagicNumber:
    active: false
  WildcardImport:
    active: false
```

## Rules to deactivate for Compose projects (with rationale)

| Rule | Reason |
|------|--------|
| `style/WildcardImport` | `androidx.compose.*` wildcards are idiomatic Compose |
| `style/MagicNumber` | Theme color literals (0xFF...) in AppTheme.kt |
| `naming/FunctionNaming` | Composables are PascalCase, not camelCase |
| `naming/MatchingDeclarationName` | Multi-declaration files common (Routes + AppNavHost) |
| `empty-blocks/EmptyFunctionBlock` | `onError {}` in UtteranceProgressListener required by API |
| `exceptions/TooGenericExceptionCaught` | Repository boundary catch-all is intentional |
| `complexity/ReturnCount` | Parser early-returns are legitimate |
| `complexity/LoopWithTooManyJumpStatements` | Parser loop with break/continue is idiomatic |

## buildUponDefaultConfig merges ON TOP of defaults

Set `buildUponDefaultConfig = true` so you only need to override what changes. Otherwise you must redeclare every rule.

## Verify rule names against the actual jar

Don't guess rule names. Extract default config from the cached jar:
```bash
jar xf ~/.gradle/caches/.../detekt-core-<version>.jar default-detekt-config.yml
```
Then verify your rule sections exist. Stale rule names (e.g. `Filename` doesn't exist in 1.23.8) cause config validation errors.

## Control the gate: maxIssues: 0

```yaml
build:
  maxIssues: 0
```
This fails the build on ANY finding — the strictest gate.

## Version pins (known good for Kotlin 2.0.21 / AGP 8.7.3)
- detekt: 1.23.8
- ktlint plugin: 14.2.0 (CLI artifact: 1.8.0)
