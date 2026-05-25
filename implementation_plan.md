# 📋 Phase Spec: 02 · Four-Step Pipeline Implementation Plan

This implementation plan establishes the stateless step modules and execution runner for Phase 02.

## 📂 Proposed File Scaffolding

Here is the exact list of files to be created for the analysis pipeline, their relative paths, and a one-line description of their purpose:

| File Path | Purpose |
| :--- | :--- |
| **`pipeline/intake.py`** | Reads raw incident files, extracts name, and performs character count validation. |
| **`pipeline/extraction.py`** | Processes intake text using OpenAI to extract structured entities, timestamps, and error codes. |
| **`pipeline/classification.py`** | Groups incident logs into failure category and severity taxonomies with justifications. |
| **`pipeline/summarization.py`** | Synthesizes details into executive summaries and lists actionable remediation steps. |
| **`pipeline/runner.py`** | Integrates and orchestrates the four sequential steps into a stateless end-to-end execution. |

## ⚙️ Rules for Implementation
- **Decoupled State**: All steps must be pure, stateless functions receiving typed inputs and returning typed outputs.
- **Pydantic Validation**: Instantiate and validate input and output models at the boundary of every step.
- **Structured Prompts**: Prompts must use clear contextual division (XML tags or specific parameters) to isolate system instructions and inputs.
- **No Swallowing**: Do not declare functions with `**kwargs` or generic `dict` arguments.

## ✅ Definition of Done (DoD)
- **Interface Schema Isolation**: Standalone step modules exist under `pipeline/` with explicit input/output models.
- **Contract Chaining**: Outputs of upstream stages map fully to input models of downstream stages.
- **Offline Mock Tests**: Unit tests run cleanly and verify each step using mocked OpenAI API client calls.
- **E2E execution block**: `pipeline/runner.py` executes end-to-end and aggregates mock telemetry and outputs.

---

*This plan is currently at the gate. **No source code changes will be made until explicit user approval is received.***
