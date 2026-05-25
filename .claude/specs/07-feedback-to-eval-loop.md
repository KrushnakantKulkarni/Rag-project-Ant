# 📋 Phase Spec: 07 · Feedback-to-Eval Loop

This spec defines the regression testing harness, feedback loop mechanics, golden dataset schema, and analytics reporting.

---

## 🎯 1. Overview & Goal

The goal of this phase is to turn telemetry failures into continuous improvement datasets. When users flag an execution, this workflow automatically extracts the failed payload, saves it inside our golden evaluation dataset (`eval/eval_dataset.json`), and integrates it into the automated regression testing suite.

---

## 🔗 2. Depends On
* `06-trace-explorer-ui.md`

---

## 📂 3. File & Module Map

* `eval/dataset.py` ➔ Appends and manages items in `eval/eval_dataset.json`.
* `eval/regression.py` ➔ Runs pipelines over golden datasets to compute accuracy delta scores.
* `eval/harness.py` ➔ Automated pytest extension integrating golden evaluation cases.

---

## 📝 4. Interface Contracts

### Golden Case Definition
```python
from pydantic import BaseModel
from typing import Optional

class GoldenCase(BaseModel):
    case_id: str
    original_trace_id: str
    document_name: str
    raw_input: str
    expected_category: str
    expected_summary: str
    known_failure_mode: str        # e.g., EXTRACTION_HALLUCINATION
    added_at: str
```

### Regression Summary
```python
class RegressionReport(BaseModel):
    total_cases_run: int
    passed_cases: int
    failed_cases: int
    accuracy_percentage: float
    category_accuracies: dict[str, float]
    regression_warning: bool       # True if accuracy dropped vs. baseline
```

---

## ⚙️ 5. Rules for Implementation

* **Immutable Baselines**: Ensure that historical evaluation performance baselines cannot be programmatically deleted or overwritten during routine runs.
* **Auto-Scrubbing**: Scrub raw traces of credentials or secrets before appending them to the public golden dataset files under `eval/eval_dataset.json`.
* **Accuracy assertions**: Pytest integration suites must check performance scores against the recorded baseline and fail the build if accuracy falls below the established target thresholds.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Golden entry generation**: Flagging a trace correctly formats and appends the new test case to `eval/eval_dataset.json`.
- [ ] **Regression analysis pass**: Executing `regression.py` computes total accuracy metrics, comparing results with the baseline.
- [ ] **Build blocking validation**: Intentionally introducing a pipeline bug triggers build failures on the regression tests due to performance degradation.
- [ ] **Dataset safety test**: Safety hooks block destructive operations (`DROP`, `DELETE`) targeting the golden JSON file.
