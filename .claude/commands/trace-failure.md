---
description: Initiates a backward root-cause analysis on a flagged or failed pipeline execution trace.
argument-hint: "<trace-id>"
allowed-tools:
  - run_command
  - view_file
---

# 🛠️ Command: `/trace-failure`

This command performs backward root-cause walk-backs on a designated telemetry execution trace. It reads the raw JSON telemetry logs, analyzes pipeline step transformations from end to start, and identifies the exact step introducing the degradation.

## 📋 Pre-flight Checks
1. Validate that the `<trace-id>` is provided.
2. Confirm the raw trace file `traces/<trace-id>.json` exists.
3. Check that the SQLite trace index is readable to fetch metadata if required.

## 🚀 Execution Steps

1. **Load Telemetry**:
   - Read and parse the target JSON trace file from `traces/<trace-id>.json`.

2. **Walk Back Pipeline Spans**:
   - Analyze step telemetry in reverse chronological order:
     `Summarization` ➔ `Classification` ➔ `Extraction` ➔ `Intake`.
   - Inspect confidence scores and identify the first node where `confidence_score` ≤ 2 or where `error` is present.

3. **Diagnose and Classify**:
   - Trace inputs and outputs between the failing step and its predecessor to spot propagation regressions.
   - Classify the failure mode into exactly one of the five taxonomy categories:
     - `EXTRACTION_HALLUCINATION` (Extracted data contains unsupported facts)
     - `MISCLASSIFICATION` (Document mislabeled or assigned wrong taxonomy labels)
     - `PROPAGATION_ERROR` (Downstream steps failed because of downstream type parsing/bad upstream payload)
     - `PROMPT_FAILURE` (LLM instructions were ignored or broke under structural layout shifts)
     - `CONTEXT_LOSS` (Long documents truncated or lost core details in early step operations)

4. **Deliver Forensic Report**:
   - Output a detailed Markdown Diagnostic Report with:
     - Identified failing node.
     - Divergence analysis (Inputs vs. Output vs. Expected).
     - Concrete remediation steps (API updates, prompt edits).

## 🛑 Failure Handling
- If trace file is missing: Search for trace metadata in SQLite `traces.db` to check if a different ID format was passed, and report available IDs.
- If analysis fails to isolate root cause: Set failure category to `PROMPT_FAILURE` as a fallback and dump raw spans for human review.
