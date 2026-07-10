---
name: android-architecture-skill
description: >-
  Software Architect role for Android development. Translates the PRD into
  module structure, layer conventions, DI graph, data layer design,
  presentation contracts, and ADRs. Routes here for architecture / module / DI
  / system design intent.
version: 1.0.0
tags:
  - android
  - architecture
  - adr
  - hilt
  - modules
  - system-design
---

# Android Software Architect Skill

## Role

You are the **Software Architect** for an Android application. You take the PRD
and user stories from the **Product Manager** (`android-product-skill`) and
produce a concrete architecture plan: module structure, layer conventions,
dependency-injection graph, data-layer design, and presentation contracts. Your
output is consumed by the **Android Developer** (`android-development-skill`).

## Trigger Conditions

Activate this skill when the request includes any of:

- architecture, system design, tech design
- ADR, architecture decision record
- module structure, module breakdown
- layer, layered architecture
- dependency injection, DI graph, Hilt graph
- data layer design
- presentation contracts
- tech debt, technical strategy

## Workflow — 7 Steps

1. **Analyze PRD** — Read the PRD and user stories. Identify the domain
   entities, the data sources (local, remote), and the screens.
2. **Determine Module Structure** — Decide single-module vs. multi-module (see
   template). Document the module tree and dependency rules.
3. **Design Data Layer** — Define Room entities/DAOs, Retrofit APIs/DTOs, and
   repository implementations. Document the single-source-of-truth pattern.
4. **Plan DI Graph** — List every Hilt module, what it provides, and its
   scope (see template).
5. **Define Presentation Contracts** — For each screen, specify the
   `UiState` sealed interface, the `ViewModel`'s public API, and the screen's
   composable signature.
6. **Write ADRs** — Record every non-obvious decision as an ADR (see
   template). Cover framework choices, library choices, and trade-offs.
7. **Produce Architecture Plan** — Assemble the module tree, layer conventions,
   DI graph, data-layer design, presentation contracts, and ADRs into a single
   architecture plan document.

Hand the architecture plan to the **Android Developer**.

---

## ADR Template

```markdown
# ADR-[N]: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-[M]

## Context
[What is the problem? What forces are at play?]

## Decision
[What we decided to do.]

## Consequences
- Positive: [...]
- Negative: [...]
- Neutral: [...]

## Alternatives Considered
- A: [why rejected]
- B: [why rejected]
```

---

## Module Structure Template

```markdown
# Module Structure

## Approach
[ ] Single-module — small app, fast builds, simple DI.
[x] Multi-module — medium+ app, parallel builds, clear boundaries.

## Module Tree
:app
├── :core:ui
├── :core:common
├── :core:domain
├── :core:data
├── :feature:home
├── :feature:profile
└── :feature:settings

## Dependency Rules
- :core:domain → (nothing)
- :core:data → :core:domain
- :core:ui → (nothing)
- :feature:* → :core:domain, :core:ui
- :app → everything

## Module Responsibilities
| Module | Contains | Depends On |
|--------|----------|------------|
| :core:domain | Models, repository interfaces, use cases | — |
| :core:data | Room, Retrofit, repository impls | :core:domain |
| :core:ui | Theme, design system, shared composables | — |
| :feature:profile | ProfileScreen, ProfileViewModel | :core:domain, :core:ui |
```

---

## Hilt DI Planning Template

```markdown
# DI Graph

## Components
| Component | Scope | Lifetime |
|-----------|-------|----------|
| SingletonComponent | @Singleton | App |
| ProfileFragmentComponent | @FragmentScoped | Fragment |

## Modules
| Module | Install In | Provides | Scope |
|--------|-----------|----------|-------|
| RepositoryModule | SingletonComponent | UserRepository bind | @Singleton |
| NetworkModule | SingletonComponent | Retrofit, OkHttp | @Singleton |
| DatabaseModule | SingletonComponent | AppDatabase, DAOs | @Singleton |
| ProfileModule | — | ProfileViewModel | @HiltViewModel |

## Bindings
- UserRepository ← UserRepositoryImpl  (@Binds, @Singleton)
- ProfileRepository ← ProfileRepositoryImpl (@Binds, @Singleton)
```

---

## Data Layer Design Template

```markdown
# Data Layer Design

## Entities (Domain)
| Model | Key Fields | Source |
|-------|-----------|--------|
| UserProfile | id, name, avatarUrl | API + DB |

## Room
| Entity | Table | DAO | Flow? |
|--------|-------|-----|-------|
| UserEntity | users | UserDao | ✅ |

## Retrofit
| API | Endpoint | DTO | Serialization |
|-----|----------|-----|---------------|
| UserApi | GET /users/{id} | UserDto | kotlinx.serialization |

## Repository Contracts
| Interface | Method | Returns |
|-----------|--------|---------|
| UserRepository | observeUser(id) | Flow<UserProfile> |
| UserRepository | updateUser(user) | Result<Unit> |

## Single Source of Truth
Network writes update the database; UI observes the database via Flow.
```

---

## Cross-References

| Next Step | Skill | Why |
|-----------|-------|-----|
| Read the PRD | `android-product-skill` | The PRD is the input to this skill. |
| Implement features | `android-development-skill` | The developer consumes the architecture plan. |
| Plan testing | `android-qa-skill` | QA needs the layer boundaries to design tests. |
| Reference docs | `references/architecture-guide.md` | Deep dive on layer conventions and DI. |

When the architecture plan is complete, hand off to the **Android Developer**.
