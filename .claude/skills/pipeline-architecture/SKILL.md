# 🧠 Domain-Specific Skill: Pipeline Architecture & Tracing Standards

This skill governs the system design principles, package boundaries, function interfaces, telemetry capture rules, and failure taxonomy definitions for the **Failure Forensics Tool**.

---

## 📐 1. Module & Package Boundaries

To maintain high modularity and clean division of concerns, code must be placed strictly according to these boundaries:
* `pipeline/` ➔ Contains only step logic. Each module represents a single, stateless stage.
* `tracing/` ➔ Contains the telemetry engine, span context models, decorator instrumentation, and storage integrations.
* `analysis/` ➔ Implements backward trace walk-backs, root-cause heuristics, and diagnostics.
* `eval/` ➔ Manages baseline tracking, evaluation datasets, and regression testing rigs.
* `api/` ➔ Contains the FastAPI routing layers, access control checks, and request models.
* `ui/` ➔ Houses the Streamlit front-end dashboards, styling sheets, and visualization widgets.

---

## 📝 2. Pure Step Function Contracts

Every pipeline step must present a uniform, predictable interface. Hard constraints:
* **Signature**: Each step must be declared with explicit inputs and outputs:
  ```python
  def run_step(input_data: StepInputModel) -> StepOutputModel:
  ```
* **No Swallowing**: Never declare functions with `**kwargs` or generic `dict` arguments.
* **No Raw Outputs**: Returning unvalidated primitives like strings or dictionaries is strictly forbidden.
* **Statelessness**: Steps must not write or read from internal module state or instance attributes. They are mathematical transformations of input models.

---

## ⚡ 3. Telemetry Span Capture Rules

* **Decoration**: Every step function must be wrapped using the `@instrument` decorator from `tracing.instrumentation`.
* **Latency Timers**: Execution times must be measured using monotonic microsecond-accuracy counters.
* **Confidence Scoring**: Confidence scores must be represented as integers strictly in the range of `1–5` (with 5 being absolute certainty).
* **LLM Co-generation**: The confidence score must be returned in the same LLM payload as the step's primary textual output (e.g., using structured JSON tool outputs). Triggering a secondary LLM call to score a step's output is strictly prohibited.

---

## 🔍 4. The Canonical Failure Taxonomy

The backward trace analyzer must categorize failures into exactly one of these five classes:
1. `EXTRACTION_HALLUCINATION` ➔ The extraction step generated facts, dates, or values not supported by the input intake model.
2. `MISCLASSIFICATION` ➔ The classification step assigned wrong taxonomy labels, failing boundary assertions.
3. `PROPAGATION_ERROR` ➔ A downstream step raised validation or execution errors because a prior step generated structural anomalies.
4. `PROMPT_FAILURE` ➔ The LLM failed to adhere to system instructions or output specifications due to structure changes.
5. `CONTEXT_LOSS` ➔ Text truncation or context constraints resulted in vital information being excluded from summarizations.

---

## 🚫 5. Forbidden Patterns

* **No LangChain**: Do not use LangChain, LlamaIndex, or other agent frameworks in `pipeline/` or `tracing/` core code. Use direct LLM calls or client wrappers.
* **No `print()`**: All diagnostic console messages must go through the structured logger (`utils/logger.py`).
* **No Hardcoded Models**: Reading or hardcoding strings like `"gpt-4o"` or `"claude-3-5-sonnet"` is forbidden. Always read from `settings.LLM_MODEL`.
