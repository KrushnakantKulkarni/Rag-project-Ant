# 📋 Phase Spec: 02 · Four-Step Pipeline

This spec governs the core execution steps of the analysis pipeline. It enforces step isolation, strict Pydantic types, and stateless modularity.

---

## 🎯 1. Overview & Goal

The goal of this phase is to build the modular four-step text processing pipeline. It reads raw texts, extracts structured technical facts, maps documents to error categories, and compiles high-level executive summaries.

---

## 🔗 2. Depends On
* `01-project-scaffold.md`

---

## 📂 3. File & Module Map

* `pipeline/intake.py` ➔ Reads and validates raw input documents.
* `pipeline/extraction.py` ➔ Invokes structured LLM extraction of entities, timestamps, and error codes.
* `pipeline/classification.py` ➔ Classifies document failure events using LLM taxonomy.
* `pipeline/summarization.py` ➔ Generates a concise incident summary.
* `pipeline/runner.py` ➔ Controls step-by-step orchestrations.

---

## 📝 4. Interface Contracts

### Step 1: Intake
```python
from pydantic import BaseModel, Field

class IntakeInput(BaseModel):
    filepath: str
    raw_content: str

class IntakeOutput(BaseModel):
    document_name: str
    sanitized_text: str
    char_count: int
```

### Step 2: Extraction
```python
class ExtractionInput(BaseModel):
    document_name: str
    sanitized_text: str

class ExtractedFact(BaseModel):
    entity: str
    error_code: str
    timestamp: str
    description: str

class ExtractionOutput(BaseModel):
    document_name: str
    facts: list[ExtractedFact]
    raw_log_context: str
```

### Step 3: Classification
```python
class ClassificationInput(BaseModel):
    document_name: str
    facts: list[ExtractedFact]

class ClassificationOutput(BaseModel):
    document_name: str
    category: str  # Legal, Security, Network, Database, Application
    severity: str  # Critical, Major, Minor
    justification: str
```

### Step 4: Summarization
```python
class SummarizationInput(BaseModel):
    document_name: str
    category: str
    severity: str
    facts: list[ExtractedFact]

class SummarizationOutput(BaseModel):
    document_name: str
    executive_summary: str
    remediation_steps: str
```

---

## ⚙️ 5. Rules for Implementation

* **Decoupled State**: Step execution functions must be pure. No sharing data through disk caches or persistent buffers.
* **Pydantic Validation**: Instantiate and validate model objects at the boundary of every step. No raw lists or dicts allowed.
* **Structured Prompts**: Prompt templates inside extraction, classification, and summarization must isolate context cleanly using structured syntax (e.g., XML tags or formatted JSON parameters) to prevent prompt injection.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Interface Schema Isolation**: Each of the 4 steps has a standalone module file under `pipeline/` with explicit input/output classes.
- [ ] **Contract Chaining**: Verify that output structures map completely to input variables of subsequent steps.
- [ ] **Offline Execution Test**: Step unit tests run cleanly without network timeouts when mocking the OpenAI client interface.
- [ ] **E2E execution block**: `pipeline/runner.py` runs end-to-end with simulated outputs across the entire 4-stage pipeline.
