# Skill Authoring Notes — Chunked Write Technique

> Session-specific reference for creating or rewriting large SKILL.md files in this suite.

## Problem

When a single `write_file` (or `skill_manage(action='create'` / `action='edit'`) call
exceeds roughly 8K tokens of content, the tool stream can time out mid-delivery. The file
may not land on disk at all, or the target directory may be recreated empty, silently
discarding any prior content. The system then advises: "break the content into multiple
smaller tool calls."

This was encountered while creating `skills/android-development-skill/SKILL.md` (~870
lines, multiple Kotlin code templates). The initial single `write_file` call timed out
and the file was lost.

## Technique — Chunked Write

1. **Write the base** with `write_file` — frontmatter + the first 2-3 sections only
   (trigger conditions, workflow overview, first template). Keep it under ~8K tokens.
   This establishes the file on disk.

2. **Append remaining sections** with successive `patch` calls (mode='replace'). For
   each patch:
   - `old_string`: the last line or two of the previously written content — must be
     unique in the file so the patch targets the right spot.
   - `new_string`: that same last line + the next section's full content.
   - This effectively appends content to the end of the file.

3. **Keep each patch under ~8K tokens.** If a single section (e.g., a long Kotlin code
   template with comments) is very large, split it further — write the section header
   and opening, then patch in the rest.

4. **Verify after each step.** If a patch fails with "File not found", the base write
   didn't land — restart with `write_file`.

5. **End-of-session check:** read the final line count and tail of the file to confirm
   all sections landed and the frontmatter is intact.

## Why Patches Instead of Multiple write_file Calls

`write_file` overwrites the entire file. Calling it again would destroy the content from
the previous call. `patch` (mode='replace') does a targeted find-and-replace, so it can
append content by replacing the last unique line with itself + new content. This is the
correct primitive for incremental file growth.

## Applicability

- Creating any SKILL.md with multiple long code templates (>~8K tokens total)
- Rewriting a large existing skill with `skill_manage(action='edit')` — same stream
  limit applies to the `content` arg
- Writing any large file (references, templates) where the content exceeds the
  ~8K token streaming budget
