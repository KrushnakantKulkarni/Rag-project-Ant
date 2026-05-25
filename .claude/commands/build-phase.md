---
description: Scaffolds a build phase branch and loads its technical spec into active context, entering Plan Mode.
argument-hint: "<phase-number> <slug>"
allowed-tools:
  - run_command
  - view_file
  - write_to_file
---

# 🛠️ Command: `/build-phase`

This command initiates a new engineering build phase by scaffolding a dedicated feature branch, importing the phase contract specifications, and setting up the planner sequence.

## 📋 Pre-flight Checks
1. Ensure the workspace git status is clean (`git status --porcelain` is empty).
2. Validate that `<phase-number>` matches a double-digit sequence (01 to 09).
3. Confirm that the spec file `.claude/specs/<phase-number>-*.md` exists in the codebase.

## 🚀 Execution Steps

1. **Parse Arguments**:
   - Extract `phase-number` (e.g., `03`) and `slug` (e.g., `tracing-layer`).
   - Find the exact spec file path matching: `.claude/specs/<phase-number>-*.md`.

2. **Branch Scaffolding**:
   - Create and checkout a clean git branch: `git checkout -b feature/<phase-number>-<slug>`.

3. **Context Loading**:
   - Read the corresponding spec file using `view_file`.
   - Read `skills/pipeline-architecture/SKILL.md` into memory.

4. **Plan Mode Activation**:
   - Create or update the `implementation_plan.md` artifact outlining specific files to edit and verification assertions.
   - Set `RequestFeedback` to `true` in metadata and pause for user approval.

## 🛑 Failure Handling
- If git status is dirty: Prompt user to commit/stash before proceeding.
- If spec file is not found: Show list of available spec files under `.claude/specs/` and abort branch creation.
