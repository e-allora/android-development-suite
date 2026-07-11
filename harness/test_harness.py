#!/usr/bin/env python3
"""
Harness driver tests — verify init/status/next/mark/verify/advance/doctor
behave correctly on a real temp directory.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
HARNESS = SUITE_ROOT / "harness" / "harness.py"

passed = 0
failed = 0


def run(cmd, cwd=None, expect_exit=0):
    r = subprocess.run(
        [sys.executable, str(HARNESS)] + cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True, text=True,
    )
    ok = r.returncode == expect_exit
    return ok, r.returncode, r.stdout, r.stderr


def check(cond, label):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {label}")
    else:
        failed += 1
        print(f"  FAIL {label}")


def test_init_and_status():
    print("\n[init + status]")
    with tempfile.TemporaryDirectory() as tmp:
        ok, _, out, _ = run(["init", "demo", "A demo app"], cwd=tmp)
        check(ok, "init exits 0")
        state_file = Path(tmp) / ".harness" / "project.json"
        check(state_file.exists(), "state file created")
        s = json.loads(state_file.read_text())
        check(s["name"] == "demo", "name stored")
        check(s["brief"] == "A demo app", "brief stored")
        check(s["current_stage"] == "0_init", "current_stage = 0_init")
        check(s["pipeline"]["0_init"]["status"] == "pending", "stage 0 pending")
        # PROJECT_CONTEXT.md should have been copied
        check((Path(tmp) / "PROJECT_CONTEXT.md").exists(), "PROJECT_CONTEXT.md copied from template")
        # status command
        ok, _, out, _ = run(["status"], cwd=tmp)
        check(ok and "Stage" in out, "status prints stages")


def test_mark_and_advance():
    print("\n[mark + advance]")
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", "demo2", "x"], cwd=tmp)
        # The init command already copied the full PROJECT_CONTEXT template.
        # Stage 0 gate requires >= 20 lines AND 5 sections. The template
        # meets both, so the gate should be clear without any edits.
        pc = Path(tmp) / "PROJECT_CONTEXT.md"
        check(pc.read_text().count("\n") >= 20, "template is long enough for the gate")
        ok, _, _, _ = run(["mark", "0_init", "done", "--note", "first"], cwd=tmp)
        check(ok, "mark 0_init done")
        ok, _, out, _ = run(["advance"], cwd=tmp)
        check(ok, "advance clears gate")
        check("Advanced" in out, "advance prints 'Advanced'")
        s = json.loads((Path(tmp) / ".harness" / "project.json").read_text())
        check(s["current_stage"] == "1_product", "advanced to 1_product")


def test_advance_blocked_by_missing_artifact():
    print("\n[advance blocks on missing artifact or content]")
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", "demo3", "x"], cwd=tmp)
        # Replace the template with a stub that's missing the required sections
        pc = Path(tmp) / "PROJECT_CONTEXT.md"
        pc.write_text("# Stub\n\nNothing here.\n")
        ok, exit_code, out, _ = run(["advance"], cwd=tmp)
        check(exit_code == 1, "advance refused (exit 1) when sections are missing")
        check("missing" in out or "lines" in out or "section" in out, "advance reports gate failure")


def test_verify_with_run():
    print("\n[verify checks gate against content + runs commands]")
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", "demo4", "x"], cwd=tmp)
        # The full template was copied at init. Verify clears.
        ok, _, out, _ = run(["verify", "0_init"], cwd=tmp)
        check(ok, "verify 0_init clears when template is present")
        # Now strip it
        (Path(tmp) / "PROJECT_CONTEXT.md").unlink()
        ok, exit_code, out, _ = run(["verify", "0_init"], cwd=tmp)
        check(exit_code == 1, "verify 0_init fails (exit 1) after artifact deleted")
        check("missing" in out, "verify reports missing artifact")


def test_doctor():
    print("\n[doctor]")
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", "demo5", "x"], cwd=tmp)
        ok, _, out, _ = run(["doctor"], cwd=tmp)
        check(ok, "doctor passes on fresh state")


def test_next_prints_role():
    print("\n[next prints role + runbook]")
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", "demo6", "x"], cwd=tmp)
        ok, _, out, _ = run(["next"], cwd=tmp)
        check(ok, "next exits 0")
        check("android-orchestrator-skill" in out, "next names the role")
        check("0_init.md" in out or "stage_runbooks/0_init" in out, "next points at runbook")


def test_schema_valid():
    print("\n[schema file is valid JSON]")
    schema = json.loads((SUITE_ROOT / "harness" / "project.schema.json").read_text())
    check("$schema" in schema, "schema has $schema")
    check("properties" in schema, "schema has properties")
    check("pipeline" in schema["properties"], "schema defines pipeline")
    check(all(stage in schema["properties"]["pipeline"]["properties"] for stage in [
        "0_init", "1_product", "2_architecture", "3_ux", "4_development",
        "5_review", "6_qa", "7_build", "8_release", "9_maintenance"
    ]), "schema defines all 10 stages")


def test_all_runbooks_present():
    print("\n[all 10 stage runbooks present]")
    rbs = SUITE_ROOT / "harness" / "stage_runbooks"
    for stage in [
        "0_init", "1_product", "2_architecture", "3_ux", "4_development",
        "5_review", "6_qa", "7_build", "8_release", "9_maintenance"
    ]:
        check((rbs / f"{stage}.md").exists(), f"runbook {stage}.md exists")


def test_import_backfills_state():
    print("\n[import back-fills state from existing artifacts]")
    with tempfile.TemporaryDirectory() as tmp:
        # Set up a fake project with artifacts for stages 0, 1, 2
        run(["init", "import-demo", "x"], cwd=tmp)
        (Path(tmp) / "docs").mkdir(exist_ok=True)
        (Path(tmp) / "docs" / "adr").mkdir(exist_ok=True)
        # PRD with the required sections
        prd = Path(tmp) / "docs" / "prd.md"
        prd.write_text(
            "# PRD\n\n## Problem\nBig problem.\n" + ("filler\n" * 50) +
            "\n## User\nA user.\n## Success\nWin.\n## Backlog\n- Story\n## Out of scope\nNothing.\n"
        )
        (Path(tmp) / "docs" / "architecture.md").write_text(
            "# Arch\n\n## Module\nx\n" + ("y\n" * 50) + "\n## DI\nhilt\n## Data\nroom\n"
        )
        # Run import
        ok, _, out, _ = run(["import"], cwd=tmp)
        check(ok, "import exits 0")
        s = json.loads((Path(tmp) / ".harness" / "project.json").read_text())
        check(s["pipeline"]["0_init"]["status"] == "done", "0_init marked done after import")
        check(s["pipeline"]["1_product"]["status"] == "done", "1_product marked done after import")
        check(s["pipeline"]["2_architecture"]["status"] == "done", "2_architecture marked done after import")
        # 3_ux has no docs/ux-spec.md, should still be pending
        check(s["pipeline"]["3_ux"]["status"] == "pending", "3_ux remains pending (no ux-spec.md)")
        # current_stage should be 3_ux (first pending after done ones)
        check(s["current_stage"] == "3_ux", "current_stage points to first pending")


def main():
    test_schema_valid()
    test_all_runbooks_present()
    test_init_and_status()
    test_mark_and_advance()
    test_advance_blocked_by_missing_artifact()
    test_verify_with_run()
    test_doctor()
    test_next_prints_role()
    test_import_backfills_state()
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
