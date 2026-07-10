# Skill Suite Install Pitfalls

Lessons learned from building and installing the Android Development Suite.

## 1. Symlink Loops in install.sh

**The problem:** When a skill suite lives inside `~/.hermes/skills/` and an install script symlinks the suite to itself (`ln -s "$SUITE_ROOT" "$HERMES_SKILLS_DIR/$ORCHESTRATOR_NAME"` where both paths resolve to the same directory), it creates a symlink loop. If the script does `rm -rf "$TARGET"` before symlinking, it destroys the real directory and all files.

**The fix:** Always detect the in-place case before symlinking:

```bash
if [[ "$SUITE_ROOT" -ef "$HERMES_SKILLS_DIR/$ORCHESTRATOR_NAME" ]]; then
    log "Suite already in-place, skipping self-symlink"
else
    # Safe to symlink — source and destination are different directories
    ln -s "$SUITE_ROOT" "$HERMES_SKILLS_DIR/$ORCHESTRATOR_NAME"
fi
```

Never `rm -rf` a path before checking if it's the same directory as the source. The `-ef` test checks if two paths resolve to the same inode (handles symlinks, bind mounts, and canonical paths).

## 2. Individual Skill Symlinks

When a suite has sub-skills (e.g., `skills/android-product-skill/`), each sub-skill needs its own symlink into `~/.hermes/skills/` so Hermes can discover it independently. The orchestrator SKILL.md should mention all sub-skills, but each sub-skill also needs to be individually discoverable.

```bash
for skill in "${SKILLS[@]}"; do
    SOURCE="$SUITE_ROOT/skills/$skill"
    DEST="$HERMES_SKILLS_DIR/$skill"
    if [[ -f "$SOURCE/SKILL.md" ]]; then
        ln -s "$SOURCE" "$DEST"
    fi
done
```

## 3. Recovery from Lost Files

If a symlink loop does destroy a skill directory, the files can be recovered if:
- A subagent was dispatched to recreate them (save the delegation context)
- A git repo exists (e.g., `git checkout` to restore)
- The content was printed in the conversation (scroll up and re-save)

Always verify file existence after running install.sh: `ls -la ~/.hermes/skills/<suite-name>/SKILL.md`.
