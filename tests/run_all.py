#!/usr/bin/env python3
"""
Android Development Suite — Verification Test Suite

Tests covering skill discovery, CLI scaffold/audit, blueprint integrity,
reference completeness, routing logic, and the new workflow/context artifacts.
Returns 0 on all pass, 1 on any failure.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SUITE_ROOT = Path(__file__).resolve().parent.parent
CLI = SUITE_ROOT / "scripts" / "android_suite_tool.py"
TEMPLATES = SUITE_ROOT / "templates" / "blueprints"
TEMPLATES_ROOT = SUITE_ROOT / "templates"
REFERENCES = SUITE_ROOT / "references"
SKILLS = SUITE_ROOT / "skills"
MARKETPLACE = SUITE_ROOT / "marketplace.json"
ORCHESTRATOR = SUITE_ROOT / "SKILL.md"

PYTHON = sys.executable or "python3"

# Skill names expected (9 role-based skills)
SKILL_NAMES = [
    "android-orchestrator-skill",
    "android-product-skill",
    "android-architecture-skill",
    "android-ux-skill",
    "android-development-skill",
    "android-review-skill",
    "android-qa-skill",
    "android-build-skill",
    "android-release-skill",
    "android-maintenance-skill",
]

# Global counters
passed = 0
failed = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check(condition, message):
    """Increment counters and print result for one assertion."""
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"    FAIL: {message}")


def check_in(needle, haystack, message):
    check(needle in haystack, message)


def run_cli(*args):
    """Run the CLI tool with given args; return (returncode, stdout, stderr)."""
    cmd = [PYTHON, str(CLI)] + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# Test 1: Skill Discovery
# ---------------------------------------------------------------------------

def test_skill_discovery():
    print("\n[Test 1] Skill Discovery")
    # marketplace.json exists and is valid
    check(MARKETPLACE.exists(), "marketplace.json exists")
    data = json.loads(MARKETPLACE.read_text())
    check("name" in data, "marketplace has name field")
    check(data["name"] == "android-development-suite", "marketplace name correct")
    check("skills" in data, "marketplace has skills array")
    check(len(data["skills"]) == 10, "marketplace declares 10 skills")
    for s in data["skills"]:
        check("name" in s, f"skill has name: {s.get('name', '?')}")
        check("path" in s, f"skill has path: {s.get('name', '?')}")
        check("role" in s, f"skill has role: {s.get('name', '?')}")
        check("triggers" in s, f"skill has triggers: {s.get('name', '?')}")
        check("inputs" in s, f"skill has inputs: {s.get('name', '?')}")
        check("outputs" in s, f"skill has outputs: {s.get('name', '?')}")
        check("dependencies" in s, f"skill has dependencies: {s.get('name', '?')}")

    # All 9 SKILL.md files exist
    for name in SKILL_NAMES:
        skill_file = SKILLS / name / "SKILL.md"
        check(skill_file.exists(), f"{name}/SKILL.md exists")
        if skill_file.exists():
            content = skill_file.read_text()
            check("---" in content, f"{name} has YAML frontmatter")
            check("name:" in content, f"{name} has name field")
            check("description:" in content, f"{name} has description field")
            check("version:" in content, f"{name} has version field")
            check("tags:" in content, f"{name} has tags field")


# ---------------------------------------------------------------------------
# Test 2: CLI Scaffold
# ---------------------------------------------------------------------------

def test_cli_scaffold():
    print("\n[Test 2] CLI Scaffold")
    tmpdir = tempfile.mkdtemp(prefix="android_suite_test_")
    try:
        rc, out, err = run_cli(
            "scaffold",
            "--package", "com.example.app",
            "--feature", "profile",
            "--base-dir", tmpdir,
            "--use-room", "--use-retrofit",
        )
        check(rc == 0, f"scaffold returns 0 (rc={rc}, err={err})")
        base = Path(tmpdir) / "com/example/app/profile"
        expected = [
            "domain/ProfileModel.kt",
            "domain/ProfileRepository.kt",
            "data/ProfileEntity.kt",
            "data/ProfileDao.kt",
            "data/ProfileApi.kt",
            "data/ProfileDto.kt",
            "data/ProfileRepositoryImpl.kt",
            "presentation/ProfileViewModel.kt",
            "presentation/ProfileScreen.kt",
            "presentation/ProfileUiState.kt",
            "presentation/components/ProfileCard.kt",
            "di/ProfileModule.kt",
            "navigation/ProfileNavigation.kt",
        ]
        for f in expected:
            check((base / f).exists(), f"scaffold generated {f}")
        vm = base / "presentation/ProfileViewModel.kt"
        if vm.exists():
            vm_content = vm.read_text()
            check("class ProfileViewModel" in vm_content, "ViewModel has class")
            check("HiltViewModel" in vm_content, "ViewModel has @HiltViewModel")
            check("Inject" in vm_content, "ViewModel has @Inject")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test 3: CLI Audit
# ---------------------------------------------------------------------------

def test_cli_audit():
    print("\n[Test 3] CLI Audit")
    tmpdir = tempfile.mkdtemp(prefix="android_audit_test_")
    try:
        project = Path(tmpdir) / "myapp"
        project.mkdir()

        gradle_content = """
android {
    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
"""
        (project / "app.build.gradle.kts").write_text(gradle_content)

        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:name=".App" />
</manifest>
"""
        (project / "AndroidManifest.xml").write_text(manifest_content)

        rc, out, err = run_cli("audit", "--project-dir", str(project), "--check-r8", "--check-permissions")
        combined = (out + err).lower()

        check(rc == 1, f"audit returns 1 for issues (rc={rc})")
        check("issues" in combined, "audit reports issues section")
        check("minifyenabled" in combined, "audit mentions minifyEnabled")
        check("internet" in combined, "audit output contains 'internet' permission name")
        check("camera" in combined, "audit output contains 'camera' permission name")

        clean_project = Path(tmpdir) / "cleanapp"
        clean_project.mkdir()
        clean_gradle = """
android {
    buildTypes {
        release {
            isMinifyEnabled = true
        }
    }
}
"""
        (clean_project / "app.build.gradle.kts").write_text(clean_gradle)
        clean_manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:name=".App" />
</manifest>
"""
        (clean_project / "AndroidManifest.xml").write_text(clean_manifest)

        rc2, out2, err2 = run_cli("audit", "--project-dir", str(clean_project), "--check-r8", "--check-permissions")
        check(rc2 == 0, f"audit returns 0 for clean project (rc={rc2})")
        check("passed" in (out2 + err2).lower(), "clean project shows passed section")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test 4: Blueprint Integrity
# ---------------------------------------------------------------------------

def test_blueprint_integrity():
    print("\n[Test 4] Blueprint Integrity")
    templates = [
        "libs.versions.toml",
        "build.gradle.kts",
        "app.build.gradle.kts",
        "AndroidManifest.xml",
        "Application.kt",
        "MainActivity.kt",
        "Theme.kt",
    ]
    for name in templates:
        f = TEMPLATES / name
        check(f.exists(), f"blueprint {name} exists")

    # Shared PROJECT_CONTEXT template
    pc = TEMPLATES_ROOT / "PROJECT_CONTEXT.md"
    check(pc.exists(), "templates/PROJECT_CONTEXT.md exists")
    if pc.exists():
        pc_content = pc.read_text()
        check("PROJECT_CONTEXT" in pc_content, "PROJECT_CONTEXT template has header")
        check("Tech Stack" in pc_content, "PROJECT_CONTEXT has Tech Stack section")
        check("Architecture Rules" in pc_content, "PROJECT_CONTEXT has Architecture Rules")

    toml = TEMPLATES / "libs.versions.toml"
    if toml.exists():
        toml_content = toml.read_text()
        check("[versions]" in toml_content, "TOML has [versions]")
        check("[libraries]" in toml_content, "TOML has [libraries]")
        check("[plugins]" in toml_content, "TOML has [plugins]")
        check("8.7.3" in toml_content, "TOML has AGP 8.7.3")
        check("2.0.21" in toml_content, "TOML has Kotlin 2.0.21")
        check("2024.12.01" in toml_content, "TOML has Compose BOM")
        check("2.52" in toml_content, "TOML has Hilt 2.52")
        check("2.6.1" in toml_content, "TOML has Room 2.6.1")
        check("2.11.0" in toml_content, "TOML has Retrofit 2.11.0")

    root_gradle = TEMPLATES / "build.gradle.kts"
    if root_gradle.exists():
        rg = root_gradle.read_text()
        check("plugins {" in rg, "root gradle has plugins block")
        check("apply false" in rg, "root gradle has apply false")
        check("android.application" in rg or "android-application" in rg, "root gradle has android-application plugin")
        check("kotlin.android" in rg or "kotlin-android" in rg, "root gradle has kotlin-android plugin")
        check("kotlin.compose" in rg or "kotlin-compose" in rg, "root gradle has kotlin-compose plugin")
        check("kotlin.serialization" in rg or "kotlin-serialization" in rg, "root gradle has kotlin-serialization plugin")
        check("ksp" in rg, "root gradle has ksp plugin")
        check("hilt" in rg, "root gradle has hilt plugin")
        check("room" in rg, "root gradle has room plugin")

    app_gradle = TEMPLATES / "app.build.gradle.kts"
    if app_gradle.exists():
        ag = app_gradle.read_text()
        check("compileSdk = 35" in ag, "app gradle has compileSdk 35")
        check("minSdk = 26" in ag, "app gradle has minSdk 26")
        check("targetSdk = 35" in ag, "app gradle has targetSdk 35")
        check("minifyEnabled" in ag or "isMinifyEnabled" in ag, "app gradle has minifyEnabled/isMinifyEnabled")
        check("isMinifyEnabled = true" in ag or "minifyEnabled true" in ag, "app gradle release has minify enabled")
        check("isShrinkResources = true" in ag, "app gradle has shrinkResources")
        check("VERSION_17" in ag or "17" in ag, "app gradle has Java 17")
        check("compose = true" in ag, "app gradle has compose enabled")

    manifest = TEMPLATES / "AndroidManifest.xml"
    if manifest.exists():
        mc = manifest.read_text()
        check("xmlns:android" in mc, "manifest has xmlns:android")
        check("xmlns:tools" in mc, "manifest has xmlns:tools")
        check("INTERNET" in mc, "manifest has INTERNET permission")
        check('android:name=".App"' in mc, "manifest has .App application name")
        check("MainActivity" in mc, "manifest has MainActivity")
        check("LAUNCHER" in mc, "manifest has LAUNCHER category")
        try:
            ET.fromstring(mc)
            check(True, "manifest is valid XML")
        except ET.ParseError as e:
            check(False, f"manifest is valid XML: {e}")

    app_kt = TEMPLATES / "Application.kt"
    if app_kt.exists():
        check("package com.example.app" in app_kt.read_text(), "Application.kt has package")

    main_kt = TEMPLATES / "MainActivity.kt"
    if main_kt.exists():
        mk = main_kt.read_text()
        check("package com.example.app" in mk, "MainActivity.kt has package")
        check("AndroidEntryPoint" in mk, "MainActivity.kt has @AndroidEntryPoint")

    theme_kt = TEMPLATES / "Theme.kt"
    if theme_kt.exists():
        tk = theme_kt.read_text()
        check("package com.example.app.ui.theme" in tk, "Theme.kt has ui.theme package")
        check("AppTheme" in tk, "Theme.kt has AppTheme composable")
        check("lightColorScheme" in tk, "Theme.kt has light color scheme")
        check("darkColorScheme" in tk, "Theme.kt has dark color scheme")


# ---------------------------------------------------------------------------
# Test 5: Reference Completeness
# ---------------------------------------------------------------------------

def test_reference_completeness():
    print("\n[Test 5] Reference Completeness")
    refs = {
        "compose-style-guide.md": [
            "Composable Function Rules",
            "State Management",
            "Performance",
            "Side Effects",
            "Theming",
            "Navigation",
            "Testing",
            "Accessibility",
            "Anti-Patterns",
        ],
        "release-checklist.md": [
            "Version",
            "R8",
            "Permissions",
            "App Bundle",
            "Signing",
            "Store Listing",
            "Data Safety",
            "Testing",
            "Crash",
            "Rollout",
            "Post-Release",
        ],
        "architecture-guide.md": [
            "High-Level Architecture",
            "Module Structure",
            "Domain Layer",
            "Data Layer",
            "Presentation Layer",
            "Dependency Injection",
            "Error Handling",
            "Testing Boundaries",
        ],
        "testing-strategy.md": [
            "Test Pyramid",
            "Tooling",
            "Unit Testing",
            "Compose UI",
            "Test Doubles",
            "Coroutines",
            "Room Testing",
            "CI",
            "Roborazzi",
            "Anti-Patterns",
        ],
        "ux-design-guide.md": [
            "Screen States",
            "Navigation",
            "Theming",
            "Accessibility",
            "Anti-Patterns",
        ],
        "review-checklist.md": [
            "Architecture Conformity",
            "Lifecycle",
            "Security",
            "Severity",
        ],
        "build-packaging-guide.md": [
            "Build Types",
            "Product Flavors",
            "Signing",
            "R8",
        ],
        "maintenance-guide.md": [
            "Regression",
            "Migration",
            "Feature Flags",
            "Observability",
        ],
        "workflow-runbook.md": [
            "Pipeline",
            "Review Loop",
            "Orchestration",
        ],
    }
    for fname, sections in refs.items():
        f = REFERENCES / fname
        check(f.exists(), f"reference {fname} exists")
        if f.exists():
            content = f.read_text()
            for section in sections:
                check(section in content, f"{fname} covers '{section}'")


# ---------------------------------------------------------------------------
# Test 6: Routing Logic
# ---------------------------------------------------------------------------

def test_routing_logic():
    print("\n[Test 6] Routing Logic")
    check(ORCHESTRATOR.exists(), "orchestrator SKILL.md exists")
    if not ORCHESTRATOR.exists():
        return
    content = ORCHESTRATOR.read_text().lower()

    # References all 9 skills
    for name in SKILL_NAMES:
        check(name in content, f"orchestrator references {name}")

    # Routing keywords (one representative per intent)
    routing_keywords = [
        "orchestrate", "pipeline",
        "requirements", "prd",
        "architecture", "adr",
        "ux", "screen",
        "scaffold", "compose", "viewmodel", "repository",
        "review", "detekt", "coroutine",
        "test", "coverage",
        "gradle", "flavor",
        "release", "r8", "signing", "aab", "rollout",
        "maintenance", "regression",
    ]
    for kw in routing_keywords:
        check(kw in content, f"orchestrator has routing keyword '{kw}'")

    check("routing" in content, "orchestrator has routing section")
    check("trigger" in content, "orchestrator mentions triggers")
    check("cli" in content, "orchestrator references CLI")

    check("layer" in content, "orchestrator mentions layers")
    check("dependency" in content, "orchestrator mentions dependency graph")

    check("libs.versions.toml" in content, "orchestrator lists libs.versions.toml")
    check("androidmanifest.xml" in content, "orchestrator lists AndroidManifest.xml")
    check("project_context" in content, "orchestrator references PROJECT_CONTEXT")
    check("workflow-runbook" in content, "orchestrator references workflow-runbook")

    check("compose-style-guide" in content, "orchestrator lists compose-style-guide")
    check("release-checklist" in content, "orchestrator lists release-checklist")
    check("architecture-guide" in content, "orchestrator lists architecture-guide")
    check("testing-strategy" in content, "orchestrator lists testing-strategy")
    check("ux-design-guide" in content, "orchestrator lists ux-design-guide")
    check("review-checklist" in content, "orchestrator lists review-checklist")
    check("build-packaging-guide" in content, "orchestrator lists build-packaging-guide")
    check("maintenance-guide" in content, "orchestrator lists maintenance-guide")

    check("install" in content, "orchestrator has installation instructions")
    check("verify" in content or "test" in content, "orchestrator has verification instructions")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global passed, failed
    print("=" * 60)
    print("Android Development Suite — Verification Tests")
    print("=" * 60)

    tests = [
        test_skill_discovery,
        test_cli_scaffold,
        test_cli_audit,
        test_blueprint_integrity,
        test_reference_completeness,
        test_routing_logic,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            failed += 1
            print(f"    ERROR in {test.__name__}: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Total assertions: {passed + failed}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
