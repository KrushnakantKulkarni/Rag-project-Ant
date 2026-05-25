---
description: Spawns parallel specialist reviewer subagents (Pipeline, Trace, Security) to review current phase changes.
argument-hint: "<phase-spec-slug>"
allowed-tools:
  - run_command
  - view_file
---

# 🛠️ Command: `/code-review-phase`

This command runs parallel checks across modified code. It spawns the Pipeline Reviewer, Tracing Reviewer, and Security Reviewer in parallel, aggregates their findings, filters duplicate reports, and provides an actionable review summary.

## 📋 Pre-flight Checks
1. Validate that the `<phase-spec-slug>` matches the current active git branch spec.
2. Confirm there are modified or uncommitted changes on the active branch (`git diff` has content).
3. Validate that all subagent specs are loaded under `.claude/agents/`.

## 🚀 Execution Steps

1. **Extract Git Changes**:
   - Capture current codebase differences: `git diff HEAD`.

2. **Spawn Specialist Reviewers**:
   - Spawns the following three subagents simultaneously, providing them with the active git diff and the target phase spec:
     - **forensics-pipeline-reviewer**
     - **forensics-trace-reviewer**
     - **forensics-security-reviewer**

3. **Merge and De-duplicate**:
   - Aggregate findings from the three agents.
   - De-duplicate overlapping findings (e.g., when a tracing bug is also flagged as a security data leak).
   - Order findings strictly by Severity: `Critical` ➔ `High` ➔ `Medium` ➔ `Low`.

4. **Calculate Build Verdict**:
   - Set verdict to `CHANGES REQUESTED` if any `Critical` or `High` findings are present.
   - Set verdict to `APPROVED` if only `Medium` or `Low` warnings remain.

5. **Report and Confirm**:
   - Present the unified markdown review report to the user.
   - Ask the user: "Do you want me to automatically implement the recommended fixes for these findings?" and wait for explicit confirmation.

## 🛑 Failure Handling
- If git diff is empty: Stop and report: "No changes detected on the active phase branch. Commit or edit files before running review."
- If any subagent fails to complete: Process findings from the surviving agents, mark the verdict as incomplete, and output warning telemetry.
