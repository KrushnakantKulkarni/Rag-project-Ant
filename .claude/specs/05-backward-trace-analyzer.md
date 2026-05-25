# 📋 Phase Spec: 05 · Backward Trace Analyzer

This spec details the backward root-cause analysis logic, telemetry walk-backs, and the five-tier failure taxonomy.

---

## 🎯 1. Overview & Goal

The goal of this phase is to implement the backward walk-back analysis engine. When a pipeline run fails or is flagged with low confidence, this module traces execution backwards from the final step to identify the root cause step and categorize it.

---

## 🔗 2. Depends On
* `04-confidence-scoring.md`

---

## 📂 3. File & Module Map

* `analysis/analyzer.py` ➔ Core backward trace analyzer engine.
* `analysis/taxonomy.py` ➔ Defines the strict failure categories and evidence parsers.
* `analysis/evidence.py` ➔ Constructs the diagnostic report with evidence chains.

---

## 📝 4. Interface Contracts

### Root-Cause Diagnostics Contract
```python
from pydantic import BaseModel
from typing import Optional

class AnomalyEvidence(BaseModel):
    step_name: str
    attribute_flagged: str          # confidence_score, error, or data_divergence
    observed_value: str
    justification: str

class DiagnosticsReport(BaseModel):
    trace_id: str
    root_cause_step: str           # intake, extraction, classification, summarization
    failure_category: str          # EXTRACTION_HALLUCINATION, MISCLASSIFICATION, PROPAGATION_ERROR, PROMPT_FAILURE, CONTEXT_LOSS
    confidence_at_failure: int
    evidence_chain: list[AnomalyEvidence]
    suggested_remediation: str
```

---

## ⚙️ 5. Rules for Implementation

* **Reverse Walk Sequence**: Walk execution logs in reverse chronological order:
  `Summarization` ➔ `Classification` ➔ `Extraction` ➔ `Intake`.
* **Heuristics for Diagnostics**:
  * An execution error trace ➔ Category is `PROPAGATION_ERROR` or `PROMPT_FAILURE` depending on stack contents.
  * A confidence score ≤ 2 ➔ Category matches `EXTRACTION_HALLUCINATION` or `MISCLASSIFICATION` depending on step type.
  * Long text truncations detected ➔ Category matches `CONTEXT_LOSS`.
* **Zero Free-Text Labels**: The failure category field must be strictly assigned to one of the five canonical classifications. No arbitrary text labels allowed.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Reverse walk validation**: Executing the analyzer logs a backward search path, traversing from final steps back to initial stages.
- [ ] **Taxonomy classification validation**: Confirm that simulated extraction hallucinations are correctly classified as `EXTRACTION_HALLUCINATION` by the heuristics.
- [ ] **Evidence chain coverage**: Every diagnostics report includes a structured evidence list showing the values that triggered the diagnosis.
- [ ] **Offline Analyzer Testing**: Diagnostic suite executes offline and resolves correct root causes across mocked failures in 8 test documents.
