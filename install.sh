#!/usr/bin/env bash
#
# install.sh — Android Development Suite installer
#
# Symlinks the five individual skills into ~/.hermes/skills/, makes the CLI
# executable, and runs `list --type all` to verify.
#

set -euo pipefail

SUITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_SKILLS_DIR="${HOME}/.hermes/skills"
SUITE_NAME="android-development-suite"

echo "=========================================="
echo " Android Development Suite — Installer"
echo "=========================================="
echo ""
echo "Suite directory: ${SUITE_DIR}"
echo "Hermes skills:    ${HERMES_SKILLS_DIR}"
echo ""

# ---------------------------------------------------------------------------
# 1. Detect if the suite is already inside ~/.hermes/skills/ (skip self-symlink)
# ---------------------------------------------------------------------------
REAL_SUITE="$(cd "${SUITE_DIR}" && pwd -P)"
REAL_HERMES="$(cd "${HERMES_SKILLS_DIR}" 2>/dev/null && pwd -P || true)"

if [[ "${REAL_SUITE}" == "${REAL_HERMES}/${SUITE_NAME}" ]]; then
    echo "ℹ️  Suite is already installed at ${HERMES_SKILLS_DIR}/${SUITE_NAME}"
    echo "   Skipping self-symlink."
else
    echo "Symlinking suite into ${HERMES_SKILLS_DIR}/ ..."
    mkdir -p "${HERMES_SKILLS_DIR}"
    TARGET="${HERMES_SKILLS_DIR}/${SUITE_NAME}"

    if [[ -L "${TARGET}" ]]; then
        echo "   Removing existing symlink at ${TARGET}"
        rm -f "${TARGET}"
    elif [[ -d "${TARGET}" ]]; then
        echo "   Directory already exists at ${TARGET} (not a symlink) — leaving as-is"
    else
        ln -s "${SUITE_DIR}" "${TARGET}"
        echo "   Created symlink: ${TARGET} → ${SUITE_DIR}"
    fi
fi
echo ""

# ---------------------------------------------------------------------------
# 2. Symlink individual skills into ~/.hermes/skills/
# ---------------------------------------------------------------------------
echo "Symlinking individual skills..."
SKILLS_SRC="${SUITE_DIR}/skills"
if [[ -d "${SKILLS_SRC}" ]]; then
    for skill_dir in "${SKILLS_SRC}"/*/; do
        skill_name="$(basename "${skill_dir}")"
        target="${HERMES_SKILLS_DIR}/${skill_name}"

        # Skip if the skill already exists as a real directory or symlink
        if [[ -e "${target}" || -L "${target}" ]]; then
            echo "   ${skill_name}: already present — skipping"
            continue
        fi

        ln -s "${skill_dir}" "${target}"
        echo "   ${skill_name}: linked"
    done
fi
echo ""

# ---------------------------------------------------------------------------
# 3. Make the CLI executable
# ---------------------------------------------------------------------------
echo "Making CLI executable..."
CLI="${SUITE_DIR}/scripts/android_suite_tool.py"
if [[ -f "${CLI}" ]]; then
    chmod +x "${CLI}"
    echo "   ${CLI} — executable"
else
    echo "   ⚠️  CLI not found at ${CLI}"
fi
echo ""

# ---------------------------------------------------------------------------
# 4. Verify by running `list --type all`
# ---------------------------------------------------------------------------
echo "Verifying installation..."
if command -v python3 &>/dev/null; then
    if python3 "${CLI}" list --type all; then
        echo ""
        echo "✅ Installation verified successfully!"
    else
        echo ""
        echo "⚠️  Verification command returned non-zero — check output above"
    fi
else
    echo "⚠️  python3 not found — cannot run verification"
fi
echo ""
echo "=========================================="
echo " Installation complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  cd ${HERMES_SKILLS_DIR}/${SUITE_NAME}"
echo "  python3 tests/run_all.py    # verify suite integrity"
