# 📋 Phase Spec: 04 · Confidence Scoring Implementation Plan

This implementation plan establishes the co-generated self-confidence scoring metrics, resilient Pydantic schema fallbacks, and warning alert thresholds for Phase 04.

## 📂 Proposed File Scaffolding & Modifications

Here is the exact list of files that will be created and modified for this phase, their relative paths, and a one-line description of their purpose:

| File Path | Action | Purpose |
| :--- | :--- | :--- |
| **`utils/thresholds.py`** | **[NEW]** | Implements the core threshold criteria checking, flagging warning logs when confidence score ≤ 2. |
| **`pipeline/extraction.py`** | **[MODIFY]** | Updates extraction prompt, response schema, and output model to co-generate self-confidence scores. |
| **`pipeline/classification.py`** | **[MODIFY]** | Updates classification prompt, response schema, and output model to co-generate self-confidence scores. |
| **`pipeline/summarization.py`** | **[MODIFY]** | Updates summarization prompt, response schema, and output model to co-generate self-confidence scores. |

## ⚙️ Rules for Implementation
- **Co-generation Principle**: Absolutely no separate scoring LLM calls. Prompts must require the model to return both the primary results and the confidence score together in one API request.
- **Strict Integer Type**: Confidence scores must be processed and saved as strict integers strictly in the range of 1 to 5.
- **Justification Logging**: Prompts must instruct the LLM to output a textual sentence explaining the assigned score, cataloged inside telemetry.
- **Pydantic Parsing Resilience**: Enforce fallback validation via `@field_validator` converting invalid text (e.g. `"High"`, `"90%"`) to standard defaults (`3`).

## ✅ Definition of Done (DoD)
- **Co-generation Verification**: Spans confirm confidence and justification are fetched inside the primary step execution.
- **Score Range Enforcement**: Verify that confidence integers are strictly formatted and assert that they fall in the `1–5` range.
- **Threshold Alert Validation**: Ensure a warning is logged when step self-scores are low (score ≤ 2).
- **Pydantic Parsing Resilience**: Test validators with wrong string formats and verify they map automatically to the standard default value (`3`).

---

*This plan is currently at the gate. **No source code changes will be made until explicit user approval is received.***
