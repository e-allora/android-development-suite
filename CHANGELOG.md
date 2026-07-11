# Changelog

All notable changes to the Android Development Suite are documented here.
The format is loosely [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Appendix C: User-Stated Best Practices (Minimum Bar Cheatsheet)** in
  `references/best-practices.md`. The user's canonical 5-section best-practices
  list (Architecture & Engineering, Software Development, Product & UX,
  Collaboration & Process, Quality/Monitoring/Operations) is captured
  verbatim with deep-reference cross-links and a per-role activation
  cheatsheet. Every bullet is already covered in the main reference; the
  appendix exists so the minimum-bar language stays visible and diffable.
- **Best Practices Alignment section in the orchestrator** (`android-orchestrator-skill`).
  Previously the orchestrator was the only skill without a best-practices
  section. It now embeds all 5 user-stated sections (since the orchestrator
  is the gatekeeper across the full pipeline) with explicit per-stage
  enforcement guidance.
- **User-Stated Best Practices cross-link** in every specialist role
  (`android-product-skill`, `android-architecture-skill`, `android-ux-skill`,
  `android-development-skill`, `android-review-skill`, `android-qa-skill`,
  `android-build-skill`, `android-release-skill`, `android-maintenance-skill`).
  Each role's `SKILL.md` now points to Appendix C and lists which of the 5
  sections apply to its stage.

### Changed
- `README.md` "Best Practices" section updated to mention Appendix C and
  the increased line count (586 -> 728).
- `references/best-practices.md` is now 728 lines (up from 586). No content
  was removed; Appendix C is purely additive.

## [1.0.0] - 2026-07-10

### Added
- Initial 10-skill agentic pipeline (orchestrator + 9 role skills).
- `references/best-practices.md` — shared 586-line reference covering
  architecture, development, product/UX, collaboration, quality/operations,
  and platform-specific guidance (Android + Debian).
- Best-practices embedding wired into all 9 role skills (commit `9ff39dd`).
- "Best Practices" section in `README.md`.
- Integrity-checkpoint policy for Stage 4 (tests required, DI modules
  required, build must pass) — commit `3f9038b`.

[Unreleased]: https://github.com/e-allora/android-development-suite/compare/main...HEAD
[1.0.0]: https://github.com/e-allora/android-development-suite/releases/tag/v1.0.0
