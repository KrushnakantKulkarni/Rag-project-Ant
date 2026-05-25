# 📋 Phase Spec: 03 · Tracing Layer Implementation Plan

This implementation plan establishes the observability decorators, telemetry span models, and transaction-managed SQLite/disk storage for Phase 03.

## 📂 Proposed File Scaffolding & Modifications

Here is the exact list of files that will be created and modified for this phase, their relative paths, and a one-line description of their purpose:

| File Path | Action | Purpose |
| :--- | :--- | :--- |
| **`tracing/span.py`** | **[NEW]** | Declares the Pydantic model for individual execution spans, storing latency, tokens, error logs, and confidence. |
| **`tracing/trace.py`** | **[NEW]** | Declares the Pydantic model for parent execution traces containing an aggregate of child Spans and metadata. |
| **`tracing/instrumentation.py`**| **[NEW]** | Implements the `@instrument` decorator and context managers using high-resolution monotonic timers. |
| **`tracing/storage.py`** | **[NEW]** | Implements transactional SQLite indexing and structured JSON serialization of trace telemetry files on disk. |
| **`pipeline/runner.py`** | **[MODIFY]** | Updates the E2E coordinator to run steps inside a tracing session and execute atomic telemetry storage. |

## ⚙️ Rules for Implementation
- **Accurate Latencies**: Capture execution time using python's nanosecond monotonic clocks (`time.perf_counter_ns()`).
- **Exception Capture**: The `@instrument` decorator must capture all exceptions, log the stack trace to the Span's `error` field, set status to `FAILED`, and re-raise.
- **Atomic DB Transactions**: Telemetry indexing in SQLite must be fully transaction-guaranteed (single commit block for trace + spans).
- **Concurrency Safety**: Use safe sqlite3 connections and directory creation handling.

## ✅ Definition of Done (DoD)
- **Telemetry Schema Validation**: Spans and Traces serialize and validate cleanly using strict Pydantic schemas.
- **Decorator Timing Validation**: High-resolution nanosecond timers record actual processing latencies within a ±5ms margin.
- **Atomic Storage Validation**: Failed E2E runs successfully produce failed trace JSONs and index "FAILED" states in SQLite without crashing.
- **Offline Telemetry Tests**: Automated unit tests execute successfully using mock timers and sleep assertions.

---

*This plan is currently at the gate. **No source code changes will be made until explicit user approval is received.***
