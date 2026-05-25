# 📋 Phase Spec: 04 · Confidence Scoring

This spec details LLM self-scoring requirements, confidence telemetry schema integrations, and validation thresholds.

---

## 🎯 1. Overview & Goal

The goal of this phase is to instrument LLM steps to perform self-evaluation, rating their output accuracy on a 1-5 integer scale. Integrating confidence evaluation inside main prompts prevents expensive redundant API transactions.

---

## 🔗 2. Depends On
* `03-tracing-layer.md`

---

## 📂 3. File & Module Map

* `pipeline/extraction.py` ➔ Updated prompts and schemas return a self-score confidence.
* `pipeline/classification.py` ➔ Prompts return classification confidence scores.
* `pipeline/summarization.py` ➔ Prompts return executive summary confidence scores.
* `utils/thresholds.py` ➔ Implements scoring metrics and flags warnings if confidence ≤ 2.

---

## 📝 4. Interface Contracts

### Structured LLM Payload Shape
LLM-backed steps must request structured JSON format outputs. For example, step outputs must match:
```json
{
  "content": {
    "facts": [...],
    "category": "Network",
    "executive_summary": "..."
  },
  "confidence": {
    "score": 4,
    "justification": "Detailed entity list and timestamps successfully parsed from clean log files."
  }
}
```

---

## ⚙️ 5. Rules for Implementation

* **Co-generation Principle**: Absolute rule—never make a separate LLM call to score an execution step. Prompt structure must require the model to return both the primary results and the confidence score together in one API request.
* **Strict Integer Type**: The confidence score must be parsed and stored as a strict integer scale from 1 (unreliable/ambiguous input) to 5 (complete fact check and structure mapping).
* **Self-justification**: Prompt templates must instruct the LLM to output a short textual sentence justifying the assigned score, helping humans evaluate low scores.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Co-generation verification**: Step telemetry traces confirm confidence metrics are received within the primary LLM call.
- [ ] **Score range enforcement**: Assert that confidence integers strictly match values between 1 and 5.
- [ ] **Threshold alert validation**: Spans are correctly flagged inside `traces.db` and the UI with status warning states when self-scores fall below a threshold value (score ≤ 2).
- [ ] **Pydantic parsing resilience**: Ensure invalid confidence text (e.g., `"High"` or `"90%"`) is automatically translated to standard defaults (e.g., `3`) by Pydantic parsers instead of raising uncaught exceptions.
