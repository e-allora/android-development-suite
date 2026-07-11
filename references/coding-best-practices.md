# Coding & Engineering Best Practices

A standalone, comprehensive best-practices reference for Android (and
adjacent) software development. This document is **additive** — it does
not modify, replace, or delete any existing suite files. Use it as a
quick-load reference you can pull into any project, role, or review.

> **Status:** New file. Lives next to the existing
> `references/best-practices.md`, which covers the same ground with more
> depth and platform-specific guidance (Android, Debian/Linux). The two
> docs complement each other: this one is the **minimum-bar cheatsheet
> (5 sections, ~30 bullets)**, the other is the **deep reference
> (5 sections, ~150 bullets + appendices)**.
>
> **Agent behavior contract:** Every role in this suite runs under
> [`agent-conduct.md`](agent-conduct.md) — the operating rules for
> "done means verified," honest limitations, asking when unclear,
> testing by default, and accountability. The cheatsheet below states
> *what* the work should look like; the conduct contract states *how*
> the agent must report and verify it. Load both together.

---

## Table of Contents

1. [Architecture & Engineering Best Practices](#1-architecture--engineering-best-practices)
   1.1 System Design · 1.2 Reliability & Performance · 1.3 Security
2. [Software Development Best Practices](#2-software-development-best-practices)
   2.1 Code Quality · 2.2 Testing · 2.3 Version Control & Branching ·
   2.4 Tooling & Automation
3. [Product & UX Design Best Practices](#3-product--ux-design-best-practices)
   3.1 User-Centered Design · 3.2 Interaction & Visual Design ·
   3.3 Accessibility · 3.4 Validation & Iteration
4. [Collaboration & Process Best Practices](#4-collaboration--process-best-practices)
   4.1 Requirements & Documentation · 4.2 Planning & Delivery ·
   4.3 Code & Design Reviews
5. [Quality, Monitoring & Operations](#5-quality-monitoring--operations)
   5.1 Observability · 5.2 Deployment & Rollout · 5.3 Post-Incident Learning

---

## 1. Architecture & Engineering Best Practices

### 1.1 System Design

- Design for **modularity**: decompose into small, loosely coupled services
  or components.
- Favor **clear contracts** (APIs, interfaces) between components.
- Use **layered architecture** (presentation, domain, data, infrastructure).
- Plan for **scalability** (horizontal where possible) and **observability**
  (logs, metrics, traces) from day one.
- Prefer **standard patterns** where applicable: CQRS, event-driven,
  hexagonal/clean architecture.

### 1.2 Reliability & Performance

- Apply **defensive programming**: validate inputs, handle errors, timeouts,
  retries, circuit breakers.
- Design for **failure**: graceful degradation, fallbacks, bulkheads.
- Use **performance budgets** and profiling for critical paths.
- Cache where appropriate, but with clear **invalidation strategies**.

### 1.3 Security

- Follow **least privilege** for services, users, and data access.
- Store secrets in a **secure vault**, never in code or version control.
- Use **secure defaults**: HTTPS everywhere, secure cookies, strong TLS
  configs.
- Implement **input validation** and **output encoding** to avoid injections
  and XSS.
- Keep dependencies updated; use **SCA tools** (Software Composition
  Analysis) and automated vuln scanning.

---

## 2. Software Development Best Practices

### 2.1 Code Quality

- Write **clear, readable code**; optimize for comprehension, not cleverness.
- Follow a consistent **style guide** and automated formatting (Prettier,
  Black, gofmt, ktlint/detekt, etc.).
- Keep functions and classes **small and focused** (single responsibility).
- Use **meaningful names** for variables, functions, modules.
- Avoid duplication; use **DRY** carefully without over-abstracting.

### 2.2 Testing

- Maintain a strong **unit test** base for core logic.
- Add **integration tests** for cross-service behavior and external
  dependencies.
- Use **end-to-end tests** for key user flows.
- Aim for coverage that **protects behavior**, not just a % metric.
- Test failure cases, edge cases, and security-relevant logic.

### 2.3 Version Control & Branching

- Use **Git** with a clear branching strategy (GitHub Flow, GitFlow,
  Trunk-based).
- Keep branches **small and short-lived**; rebase or merge frequently.
- Write **descriptive commit messages** explaining the "why" as well as
  the "what."
- Protect main branches; use **PR reviews, CI checks, and status
  requirements**.

### 2.4 Tooling & Automation

- Implement **CI/CD**: automated build, test, lint, security checks on
  every change.
- Use **infrastructure as code** (Terraform, CloudFormation, Pulumi) for
  environments.
- **Automate repetitive tasks** (scripts, pipelines) to reduce human error.
- Keep build artifacts **reproducible**; ensure **deterministic builds**
  where possible.

---

## 3. Product & UX Design Best Practices

### 3.1 User-Centered Design

- Start from **user goals, pain points, and context**, not from features.
- Use **research**: interviews, surveys, analytics, and usability tests.
- Define **personas** and main **use cases / user journeys** before
  detailing screens.

### 3.2 Interaction & Visual Design

- Keep interfaces **simple, consistent, and predictable**.
- Use a **design system** (tokens, components, patterns) for consistency.
- Maintain clear **hierarchy and affordance**: users should know what's
  clickable and what's important.
- Ensure **responsiveness** and accessibility across devices.

### 3.3 Accessibility

- Follow **WCAG guidelines**: color contrast, keyboard navigation, screen
  reader support.
- Provide **alt text, labels, and semantic markup** (HTML for web,
  `contentDescription` for Android, ARIA roles for native).
- Don't rely solely on color to communicate meaning; use icons, text,
  and patterns.

### 3.4 Validation & Iteration

- Prototype early (**low-fidelity first**) and **test with real users**.
- Measure: **task success, time on task, funnel conversion, error
  rates, and NPS / CSAT**.
- Iterate based on **data + qualitative feedback**, not opinions alone.

---

## 4. Collaboration & Process Best Practices

### 4.1 Requirements & Documentation

- Write **clear requirements**: problem, scope, constraints, success
  metrics.
- Use **RFCs / design docs** for non-trivial changes; capture tradeoffs
  and alternatives.
- Keep documentation **close to the code** and up to date (README, ADRs,
  inline docs).

### 4.2 Planning & Delivery

- Break work into **small, testable increments**; deliver value
  continuously.
- Use **tickets** with clear **acceptance criteria** and **definition of
  done**.
- **Timebox** exploration / spikes; document learnings and decisions.

### 4.3 Code & Design Reviews

- Review for **correctness, clarity, consistency, and risk**.
- Be **constructive and specific**, focusing on the work, not the person.
- For designs, review against **user goals, constraints, and system
  standards**.

---

## 5. Quality, Monitoring & Operations

### 5.1 Observability

- Instrument critical flows with **structured logs, metrics, and traces**.
- Define **SLIs / SLOs** (latency, error rate, availability) for important
  services.
- Use **dashboards and alerts** tuned to reduce noise but catch real
  issues.

### 5.2 Deployment & Rollout

- Favor **blue-green, canary, or feature flags** over big-bang releases.
- Ensure **rollback** is fast and tested.
- Maintain **release notes** and communicate changes to stakeholders.

### 5.3 Post-Incident Learning

- Run **blameless postmortems**; focus on systems, not individuals.
- Capture **root causes, contributing factors, and concrete actions**.
- Turn incidents into **long-term improvements** (tests, automation,
  guardrails).

---

## Cross-Reference

- **Agent conduct contract** (operating rules — "done means verified,"
  honest limitations, ask when unclear, test by default,
  accountability): [`agent-conduct.md`](agent-conduct.md)
- Deep reference (more depth, Android + Debian specifics, appendices):
  [`best-practices.md`](best-practices.md)
- Per-role activation: see the `## Best Practices Alignment` section in
  each role's `SKILL.md` (orchestrator + 9 role skills).
