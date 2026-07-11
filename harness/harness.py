#!/usr/bin/env python3
"""
harness.py — the Android Development Suite workflow harness.

WHAT THIS IS
- A driver that reads `project.json` (the state schema) and tells you
  what to do next: which stage you're on, what its gate is, what the
  role should produce, and how to verify it's done.
- A status reporter — `harness.py status` shows where every stage is.
- A stage advancer — `harness.py advance` moves the pointer to the
  next stage after you've verified the current one.

WHAT THIS IS NOT
- Not the agent itself. The agent (this LLM session, or a subagent it
  spawns) is what actually does the work. The harness is the checklist
  and the bookkeeping.
- Not a replacement for the role skills. Each role's SKILL.md still
  describes what that role produces. The harness knows which role is
  on at any moment and points you at its SKILL.md.

USAGE
    harness.py init    <name> <brief>   # bootstrap a new project
    harness.py status                   # show where every stage is
    harness.py next                     # print what the current role should do
    harness.py mark <stage> <status>    # update a stage's status
    harness.py verify <stage>           # check the stage's gate (artifacts + verification)
    harness.py advance                  # move to the next stage if gate is clear
    harness.py doctor                   # diagnose issues with state

All commands operate on `<project_root>/.harness/project.json`. The
project root is either the current directory or the path passed with
`--root <path>`.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Avoid utcnow() deprecation noise on Python 3.12+
def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SUITE_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = Path(__file__).resolve().parent / "project.schema.json"

STAGE_ORDER = [
    "0_init", "1_product", "2_architecture", "3_ux", "4_development",
    "5_review", "6_qa", "7_build", "8_release", "9_maintenance",
]

STAGE_LABEL = {
    "0_init":         "Stage 0 — Init (Project Context)",
    "1_product":      "Stage 1 — Product (PRD, stories, ACs, backlog)",
    "2_architecture": "Stage 2 — Architecture (module tree, DI, data layer, ADRs)",
    "3_ux":           "Stage 3 — UX (screen catalog, nav, theming, a11y)",
    "4_development":  "Stage 4 — Development (feature code, scaffold CLI)",
    "5_review":       "Stage 5 — Review (review report, critical/major gate)",
    "6_qa":           "Stage 6 — QA (tests, coverage, CI)",
    "7_build":        "Stage 7 — Build (Gradle, flavors, signing, R8, CI pipeline)",
    "8_release":      "Stage 8 — Release (audit, AAB, store listing, staged rollout)",
    "9_maintenance":  "Stage 9 — Maintenance (regression, migrations, flags, observability)",
}

STAGE_ROLE = {
    "0_init":         "android-orchestrator-skill",
    "1_product":      "android-product-skill",
    "2_architecture": "android-architecture-skill",
    "3_ux":           "android-ux-skill",
    "4_development":  "android-development-skill",
    "5_review":       "android-review-skill",
    "6_qa":           "android-qa-skill",
    "7_build":        "android-build-skill",
    "8_release":      "android-release-skill",
    "9_maintenance":  "android-maintenance-skill",
}

# Gate check: for each stage, what artifacts are required to mark it done.
# A requirement is either:
#   "<path>"               -> file must exist (or dir if trailing /)
#   ("<path>", min_lines)  -> file must exist AND have at least min_lines non-empty lines
#   ("<path>", min_lines, ["required", "section", "headers"])  -> file must exist + have min lines + contain all listed markdown headers (without the leading #)
STAGE_GATE = {
    "0_init":         [("PROJECT_CONTEXT.md", 20, ["Tech Stack", "Architecture Rules", "Conventions", "Open Decisions"])],
    "1_product":      [("docs/prd.md", 50, ["Problem", "User", "Success", "Backlog", "Out of scope"])],
    "2_architecture": [("docs/architecture.md", 50, ["Module", "DI", "Data"]), "docs/adr/"],
    "3_ux":           [("docs/ux-spec.md", 50, ["Screen", "Navigation", "Accessibility"])],
    "4_development":  ["app/src/main/AndroidManifest.xml"],   # smoke: app builds
    "5_review":       [("docs/review-report.md", 30, ["Critical", "Major", "Minor"])],
    "6_qa":           ["app/src/test/"],                       # smoke: tests exist
    "7_build":        [".github/workflows/"],
    "8_release":      [("docs/release-report.md", 30, ["Version", "Rollout", "Data safety"])],
    "9_maintenance":  [("docs/maintenance-plan.md", 50, ["Monitoring", "Regression", "Migration", "On-call"])],
}

# Required verification commands for each stage (must exit 0 for "done").
STAGE_VERIFY_CMDS = {
    "4_development": [
        {"cmd": "./gradlew :app:assembleDebug", "label": "build debug APK"},
    ],
    "6_qa": [
        {"cmd": "./gradlew :app:testDebugUnitTest", "label": "run unit tests"},
    ],
    "7_build": [
        {"cmd": "./gradlew :app:assembleRelease", "label": "build release AAB"},
    ],
}


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def project_root(args) -> Path:
    if args.root:
        return Path(args.root).resolve()
    return Path.cwd()


def state_path(root: Path) -> Path:
    return root / ".harness" / "project.json"


def load_state(root: Path) -> dict[str, Any]:
    p = state_path(root)
    if not p.exists():
        sys.exit(f"No project state at {p}. Run `harness.py init` first.")
    return json.loads(p.read_text())


def save_state(root: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = _now_iso()
    p = state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, sort_keys=False) + "\n")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args) -> int:
    name = args.name
    brief = args.brief
    root = project_root(args)
    if state_path(root).exists() and not args.force:
        sys.exit(f"State already exists at {state_path(root)}. Use --force to overwrite.")
    state = {
        "name": name,
        "brief": brief,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "root": str(root),
        "pipeline": {
            stage: {"status": "pending", "attempts": 0, "output": [], "verification": {"commands": [], "limitations": []}}
            for stage in STAGE_ORDER
        },
        "current_stage": "0_init",
        "gate_blockers": [],
        "artifacts": {},
        "decisions": [],
    }
    save_state(root, state)
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
    # Copy PROJECT_CONTEXT template if it exists in the suite
    tmpl = SUITE_ROOT / "templates" / "PROJECT_CONTEXT.md"
    if tmpl.exists():
        (root / "PROJECT_CONTEXT.md").write_text(tmpl.read_text())
        print(f"Created {root / 'PROJECT_CONTEXT.md'} from template")
    print(f"Project '{name}' initialized at {root}")
    print(f"Current stage: 0_init. Next: run `harness.py next` to see what to do.")
    return 0


def cmd_status(args) -> int:
    root = project_root(args)
    state = load_state(root)
    print(f"Project: {state['name']}  ({state.get('root', root)})")
    print(f"Brief:   {state.get('brief', '(none)')}")
    print(f"Updated: {state.get('updated_at', '(unknown)')}")
    print()
    print(f"{'Stage':<14} {'Status':<18} {'Attempts':<9} {'Role':<32} Artifact count")
    print(f"{'-'*14} {'-'*18} {'-'*9} {'-'*32} {'-'*13}")
    for stage in STAGE_ORDER:
        s = state["pipeline"][stage]
        marker = " ->" if state["current_stage"] == stage else "   "
        print(f"{marker} {stage:<11} {s['status']:<18} {s.get('attempts', 0):<9} {STAGE_ROLE[stage]:<32} {len(s.get('output', []))}")
    if state.get("gate_blockers"):
        print()
        print("Gate blockers:")
        for b in state["gate_blockers"]:
            print(f"  - {b}")
    if state["current_stage"] == "done":
        print()
        print("Pipeline complete.")
    return 0


def check_requirement(req, root: Path) -> list[str]:
    """Return a list of blocker strings (empty if requirement is met)."""
    if isinstance(req, str):
        # Simple existence check
        p = (root / req) if not req.startswith("/") else Path(req)
        ok = p.exists() if not req.endswith("/") else p.is_dir()
        return [] if ok else [f"missing artifact: {req}"]
    # Tuple form
    path, *rest = req
    p = (root / path) if not path.startswith("/") else Path(path)
    blockers = []
    if not p.exists():
        return [f"missing artifact: {path}"]
    if rest:
        min_lines = rest[0] if len(rest) >= 1 else 0
        text = p.read_text()
        nonempty = [ln for ln in text.splitlines() if ln.strip()]
        if len(nonempty) < min_lines:
            blockers.append(f"{path}: only {len(nonempty)} non-empty lines (need {min_lines})")
        if len(rest) >= 2:
            for header in rest[1]:
                # Accept the header as a markdown section ("## Header" or "# Header")
                if f"## {header}" not in text and f"# {header}" not in text and header not in text:
                    blockers.append(f"{path}: missing section '{header}'")
    return blockers


def cmd_next(args) -> int:
    root = project_root(args)
    state = load_state(root)
    cur = state["current_stage"]
    if cur == "done":
        print("Pipeline is complete. Nothing to do.")
        return 0
    role_skill = STAGE_ROLE[cur]
    label = STAGE_LABEL[cur]
    print(f"Current: {label}")
    print(f"Role:    {role_skill}")
    print(f"Status:  {state['pipeline'][cur]['status']}")
    print()
    print("What to do:")
    print(f"  1. Load skill:  skill_view name='{role_skill}'")
    print(f"  2. Read the stage's contract: harness/stage_runbooks/{cur}.md")
    print(f"  3. Produce the artifacts listed in the runbook (see 'Output' section).")
    print(f"  4. Run the verification commands listed in the runbook.")
    print(f"  5. Mark complete: harness.py mark {cur} done  (and add verification evidence)")
    print(f"  6. Advance:       harness.py advance")
    print()
    print("Gate (what MUST be true to mark this stage done):")
    for req in STAGE_GATE.get(cur, []):
        path_display = req[0] if isinstance(req, tuple) else req
        blockers = check_requirement(req, root)
        mark = "OK " if not blockers else "MISS"
        print(f"  [{mark}] {path_display}")
        for b in blockers:
            print(f"          -> {b}")
    return 0


def cmd_mark(args) -> int:
    root = project_root(args)
    state = load_state(root)
    stage = args.stage
    if stage not in STAGE_ORDER:
        sys.exit(f"Unknown stage '{stage}'. Valid: {', '.join(STAGE_ORDER)}")
    status = args.status
    valid = ["pending", "in_progress", "awaiting_review", "blocked", "done", "skipped"]
    if status not in valid:
        sys.exit(f"Invalid status '{status}'. Valid: {', '.join(valid)}")
    s = state["pipeline"][stage]
    s["status"] = status
    if status == "in_progress" and not s.get("started_at"):
        s["started_at"] = _now_iso()
        s["attempts"] = s.get("attempts", 0) + 1
    if status == "done":
        s["completed_at"] = _now_iso()
    if args.note:
        s.setdefault("notes", []).append({"at": _now_iso(), "text": args.note})
    save_state(root, state)
    print(f"Stage {stage} -> {status}")
    return 0


def cmd_verify(args) -> int:
    root = project_root(args)
    state = load_state(root)
    stage = args.stage
    if stage not in STAGE_ORDER:
        sys.exit(f"Unknown stage '{stage}'.")
    blockers = []
    for req in STAGE_GATE.get(stage, []):
        blockers.extend(check_requirement(req, root))
    if args.run:
        for vc in STAGE_VERIFY_CMDS.get(stage, []):
            cmd = vc["cmd"]
            label = vc.get("label", cmd)
            print(f"  running: {cmd}  ({label})")
            try:
                r = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True, timeout=600)
                ev = {"cmd": cmd, "exit": r.returncode, "summary": r.stdout[-200:] if r.stdout else ""}
                state["pipeline"][stage].setdefault("verification", {}).setdefault("commands", []).append(ev)
                if r.returncode != 0:
                    blockers.append(f"command failed (exit {r.returncode}): {cmd}")
            except subprocess.TimeoutExpired:
                blockers.append(f"command timed out: {cmd}")
    state["gate_blockers"] = blockers if blockers else []
    save_state(root, state)
    if blockers:
        print(f"Stage {stage} GATE NOT CLEAR:")
        for b in blockers:
            print(f"  - {b}")
        return 1
    print(f"Stage {stage} gate is clear.")
    return 0


def cmd_advance(args) -> int:
    root = project_root(args)
    state = load_state(root)
    cur = state["current_stage"]
    if cur == "done":
        print("Pipeline already complete.")
        return 0
    blockers = []
    for req in STAGE_GATE.get(cur, []):
        blockers.extend(check_requirement(req, root))
    if blockers and not args.force:
        print(f"Cannot advance from {cur}:")
        for b in blockers:
            print(f"  - {b}")
        print(f"Use --force to override (not recommended).")
        return 1
    next_stage = None
    for s in STAGE_ORDER:
        if STAGE_ORDER.index(s) > STAGE_ORDER.index(cur):
            if state["pipeline"][s]["status"] in ("pending", "in_progress", "blocked"):
                next_stage = s
                break
    if next_stage is None:
        state["current_stage"] = "done"
        save_state(root, state)
        print("Pipeline complete. All stages done.")
        return 0
    state["current_stage"] = next_stage
    save_state(root, state)
    print(f"Advanced: {cur} -> {next_stage}")
    print(f"Next: run `harness.py next` to see what to do.")
    return 0


def cmd_doctor(args) -> int:
    root = project_root(args)
    if not state_path(root).exists():
        print(f"FAIL: no state file at {state_path(root)}")
        return 1
    state = load_state(root)
    issues = []
    for stage in STAGE_ORDER:
        s = state["pipeline"][stage]
        if s["status"] == "done":
            for out in s.get("output", []):
                p = Path(out)
                if not p.exists():
                    issues.append(f"stage {stage} marked done but output missing: {out}")
        if s["status"] in ("in_progress", "awaiting_review") and s.get("started_at"):
            started = datetime.datetime.fromisoformat(s["started_at"].rstrip("Z")).replace(tzinfo=datetime.timezone.utc)
            age = datetime.datetime.now(datetime.timezone.utc) - started
            if age.days > 7:
                issues.append(f"stage {stage} {s['status']} for {age.days} days (stale)")
    if issues:
        print("Doctor found issues:")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("No issues found.")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def cmd_import(args) -> int:
    """Back-fill state for an existing project by scanning for known artifacts.

    Looks for PROJECT_CONTEXT.md, docs/prd.md, docs/architecture.md, docs/adr/,
    docs/ux-spec.md, app/src/main/AndroidManifest.xml, docs/review-report.md,
    app/src/test/, .github/workflows/, docs/release-report.md, docs/maintenance-plan.md.
    Marks each stage as 'done' if its required artifacts are all present.
    """
    root = project_root(args)
    if not state_path(root).exists():
        print(f"No state at {state_path(root)}. Run `harness.py init` first.")
        return 1
    state = load_state(root)
    # Build a per-stage check that doesn't require the user to know the
    # exact gate tuples — we just check existence + min lines for the
    # primary artifact.
    primary_artifact = {
        "0_init":         "PROJECT_CONTEXT.md",
        "1_product":      "docs/prd.md",
        "2_architecture": "docs/architecture.md",
        "3_ux":           "docs/ux-spec.md",
        "4_development":  "app/src/main/AndroidManifest.xml",
        "5_review":       "docs/review-report.md",
        "6_qa":           "app/src/test/",
        "7_build":        ".github/workflows/",
        "8_release":      "docs/release-report.md",
        "9_maintenance":  "docs/maintenance-plan.md",
    }
    extra_artifacts = {
        "2_architecture": ["docs/adr/"],
    }
    now = _now_iso()
    for stage, primary in primary_artifact.items():
        p = root / primary
        exists = p.exists() if not primary.endswith("/") else p.is_dir()
        if not exists:
            continue
        all_extras = all((root / ea).exists() for ea in extra_artifacts.get(stage, []))
        if not all_extras:
            continue
        s = state["pipeline"][stage]
        s["status"] = "done"
        s["completed_at"] = now
        s.setdefault("output", []).append(primary)
        s.setdefault("verification", {}).setdefault("limitations", []).append(
            "imported from existing project by harness.py import — no live verification run"
        )
        print(f"  {stage}: marked done (found {primary})")
    # Advance current_stage to the first pending stage (or done)
    cur = state["current_stage"]
    next_stage = None
    for s in STAGE_ORDER:
        if state["pipeline"][s]["status"] not in ("done", "skipped"):
            next_stage = s
            break
    if next_stage is None:
        state["current_stage"] = "done"
    else:
        state["current_stage"] = next_stage
    save_state(root, state)
    print(f"Current stage is now: {state['current_stage']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Android Development Suite workflow harness")
    p.add_argument("--root", help="Project root (default: cwd)", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="Bootstrap a new project")
    sp.add_argument("name")
    sp.add_argument("brief", help="One-paragraph project brief")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("status", help="Show stage statuses")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("next", help="Show what the current stage requires")
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("mark", help="Set a stage's status")
    sp.add_argument("stage")
    sp.add_argument("status")
    sp.add_argument("--note", help="Optional note to attach to the status change")
    sp.set_defaults(func=cmd_mark)

    sp = sub.add_parser("verify", help="Check a stage's gate (artifacts + optional commands)")
    sp.add_argument("stage")
    sp.add_argument("--run", action="store_true", help="Run the stage's verification commands")
    sp.set_defaults(func=cmd_verify)

    sp = sub.add_parser("advance", help="Move to the next stage if gate is clear")
    sp.add_argument("--force", action="store_true", help="Override gate failures")
    sp.set_defaults(func=cmd_advance)

    sp = sub.add_parser("doctor", help="Diagnose state file issues")
    sp.set_defaults(func=cmd_doctor)

    sp = sub.add_parser("import", help="Back-fill state from existing project artifacts")
    sp.set_defaults(func=cmd_import)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
