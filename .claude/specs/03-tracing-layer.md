# 📋 Phase Spec: 03 · Tracing Layer

This spec covers telemetry and tracing layers, standardizing execution monitoring, decorator span extraction, and SQLite database storage.

---

## 🎯 1. Overview & Goal

The goal of this phase is to build the observability backbone. By implementing an `@instrument` decorator and a centralized `Trace` schema, we ensure that every step’s execution telemetry (latency, token costs, raw LLM payloads) is cleanly recorded, saved as an structured JSON file, and cataloged inside our SQLite index database.

---

## 🔗 2. Depends On
* `02-four-step-pipeline.md`

---

## 📂 3. File & Module Map

* `tracing/span.py` ➔ Span schema models.
* `tracing/trace.py` ➔ Trace container models holding collection lists of Spans.
* `tracing/instrumentation.py` ➔ Context-manager timers and `@instrument` decorators.
* `tracing/storage.py` ➔ JSON file writing and SQLite insertion modules.

---

## 📝 4. Interface Contracts

### Span Definition
```python
from typing import Optional
from pydantic import BaseModel

class Span(BaseModel):
    span_id: str
    trace_id: str
    step_name: str
    status: str                    # SUCCESS, FAILED
    serialized_input: str          # JSON formatted input models
    serialized_output: Optional[str] # JSON formatted outputs, None on error
    raw_llm_prompt: Optional[str] = None
    raw_llm_response: Optional[str] = None
    token_count: int = 0
    latency_ms: float
    confidence_score: Optional[int] = None # range 1-5
    error: Optional[str] = None    # traceback details on failure
```

### Trace Definition
```python
class Trace(BaseModel):
    trace_id: str
    document_name: str
    status: str
    spans: list[Span]
    overall_latency_ms: float
    overall_token_count: int
```

### Instrumentation Decorator
```python
def instrument(step_name: str):
    """
    Decorator to intercept pipeline execution, capture input/output metadata,
    record latency metrics and token tallies, and append Spans to active context.
    """
    ...
```

---

## ⚙️ 5. Rules for Implementation

* **Accurate Latencies**: Measure execution using high-resolution monotonic clocks (`time.perf_counter_ns()`).
* **Exception Capture**: The `@instrument` decorator must catch all exceptions, write the full traceback into the Span's `error` attribute, change status to `FAILED`, and then re-raise the exception to allow safe pipeline abort actions.
* **Atomic DB Commits**: Database operations indexing the trace metadata and individual spans must be executed in a single SQLite transaction context to avoid partial indexing bugs.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Telemetry schema validation**: Spans and Traces validate successfully using strict Pydantic schemas.
- [ ] **Decorator timing validation**: Timing metrics captured by `@instrument` report actual processing latencies within a ±5ms margin.
- [ ] **Atomic storage validation**: Executing mock failing pipelines writes standard failed telemetry files to `traces/` and correctly records the failed status inside `traces.db` without crashing the app.
- [ ] **Offline Telemetry Tests**: Standard unit tests run cleanly on decorator timers using mock sleep durations.
