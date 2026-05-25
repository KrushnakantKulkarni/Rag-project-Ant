---
description: Performs final test verifications, computes evaluation benchmarks, generates conventional commits, and merges the phase to main.
argument-hint: "<phase-spec-slug>"
allowed-tools:
  - run_command
  - view_file
---

# 🛠️ Command: `/ship-phase`

This command acts as the final delivery gate for a build phase. It ensures all unit and integration tests pass, checks for regressions against the golden dataset, creates a conventional git commit, merges the changes, and cleans up the feature branch.

## 📋 Pre-flight Checks
1. Verify that the workspace is currently on a branch matching `feature/<phase-spec-slug>`.
2. Ensure there are no uncommitted or modified files.
3. Validate that the golden evaluation dataset `eval/eval_dataset.json` exists.

## 🚀 Execution Steps

1. **Run Full Verification Suite**:
   - Spawn **forensics-test-runner** to execute:
     - All unit tests under `tests/`
     - Telemetry schema checks
     - Backward analyzer diagnostic tests
   - Verify that all tests pass 100% and there are zero regressions.

2. **Generate Telemetry Metrics Report**:
   - Compile evaluation pass-rates and compare them with stored baselines.
   - Stop and abort the ship process if diagnostic accuracy drops or regression warnings are raised.

3. **Conventional Git Commit**:
   - Formulate a clean, standardized conventional commit message:
     `feat(<phase-slug>): implement <phase-name> specifications and instrumentation`
   - Run `git add -A && git commit -m "<message>"`.

4. **Merge and Integration**:
   - Checkout the main branch: `git checkout main`.
   - Pull latest upstream modifications: `git pull origin main`.
   - Merge the feature branch: `git merge feature/<phase-spec-slug> --no-ff`.
   - Push updates: `git push origin main`.

5. **Branch Cleanup**:
   - Safely delete the local and remote feature branches:
     `git branch -d feature/<phase-spec-slug>`

## 🛑 Failure Handling
- If any test fails or regression is flagged: Immediately abort and print: "SHIP ABORTED: Tests failed or regression detected. Run pytest or check forensics-test-runner report."
- If merge conflict arises: Stop integration, alert the developer, and leave the workspace on the feature branch for manual resolution.
