---
description: Executes the 4-step pipeline on a target folder of documents, capturing telemetry spans, and writing trace outputs.
argument-hint: "<document-directory>"
allowed-tools:
  - run_command
  - list_dir
---

# 🛠️ Command: `/run-pipeline`

This command runs the four pipeline stages (Intake, Extraction, Classification, Summarization) in sequence across a directory of document inputs, instrumenting trace logs and updating `traces.db`.

## 📋 Pre-flight Checks
1. Validate that the `<document-directory>` path exists and is readable.
2. Confirm the pipeline runner modules are importable: `import pipeline.runner`.
3. Check if the SQLite schema is initialized (`traces.db` exists).

## 🚀 Execution Steps

1. **Scan Documents**:
   - List files in the target directory, sorting by name to preserve order.
   - Ignore non-text files or temporary system artifacts.

2. **Invoke Runner**:
   - Execute the processing script, directing inputs through:
     ```bash
     python -m pipeline.runner --input-dir <document-directory> --trace-out traces/ --db traces.db
     ```
   
3. **Capture Telemetry Spans**:
   - For each processed document, verify that `@instrument` successfully captures structural outputs, latencies, and token counts.

4. **Verify Telemetry Writes**:
   - Confirm new JSON files are successfully written under `traces/` and atomic logs are committed in the `traces.db` table.

## 🛑 Failure Handling
- If target directory is empty: Return a warning and exit early.
- If pipeline execution raises exception: Write failed trace JSON detailing the error inside the failing step span, index the error trace in SQLite, and report the stack trace to the console.
