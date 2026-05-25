# Implementation Plan - Phase 03: Tracing Layer

This plan details the design, files, interfaces, and testing strategies for implementing the observability, decorators, database transaction storage, and JSON logging layers in Phase 03.

## Proposed Changes

### Component: Observability & Telemetry

We establish the tracing engine under the `tracing/` directory boundary, and adapt the runner to support telemetry:

#### [NEW] [span.py](file:///e:/ai-projects/Rag-project-Ant/tracing/span.py)
Declares the strict `Span` Pydantic model storing latency, confidence (range 1-5), input/output payloads, token tallies, raw LLM context, and traceback error reports.

#### [NEW] [trace.py](file:///e:/ai-projects/Rag-project-Ant/tracing/trace.py)
Declares the `Trace` container Pydantic model aggregating all child Spans and calculating aggregate stats (overall token count, overall latency).

#### [NEW] [instrumentation.py](file:///e:/ai-projects/Rag-project-Ant/tracing/instrumentation.py)
Implements context-managed high-resolution performance timers and the `@instrument` step decorator. It maintains an active tracing context list of child spans, automatically logs elapsed processing time in microseconds, and captures exceptions.

#### [NEW] [storage.py](file:///e:/ai-projects/Rag-project-Ant/tracing/storage.py)
Implements file-system serialization writing trace files as JSON inside `traces/`, and transaction-managed SQLite database inserts to catalog traces and spans into `traces.db` atomic blocks.

#### [MODIFY] [runner.py](file:///e:/ai-projects/Rag-project-Ant/pipeline/runner.py)
Updates `execute_pipeline` to initialize a global/local trace context before running steps. It catches any internal execution errors, compiles the consolidated `Trace` model, and commits the records atomically using `storage.py`.

---

## Interface Contracts (Observability schemas)

### 1. `Span` Model
```python
class Span(BaseModel):
    span_id: str
    trace_id: str
    step_name: str
    status: str                         # SUCCESS, FAILED
    serialized_input: str               # JSON string of input model
    serialized_output: Optional[str]    # JSON string of output model, None on error
    raw_llm_prompt: Optional[str] = None
    raw_llm_response: Optional[str] = None
    token_count: int = 0
    latency_ms: float
    confidence_score: Optional[int] = None # range 1-5
    error: Optional[str] = None         # traceback error log
```

### 2. `Trace` Model
```python
class Trace(BaseModel):
    trace_id: str
    document_name: str
    status: str
    spans: list[Span]
    overall_latency_ms: float
    overall_token_count: int
```

---

## Verification Plan

### Automated Tests
- Run unit tests verifying `Span` and `Trace` schema validation.
- Timing validation: Execute tests running mocked steps with known sleep durations (e.g. `time.sleep(0.05)`) and assert recorded `latency_ms` falls within ±5ms bounds.
- Atomic storage validation: Execute E2E runner tests with forced exceptions at step 3, verifying that a `FAILED` trace JSON is saved and the SQLite database tables contain exactly 1 failed trace row and cascading failed span indexes.

### Manual Verification
- Execute the pipeline E2E, inspect generated JSON files inside `traces/` and query `traces.db` tables manually to confirm entry integrity.
