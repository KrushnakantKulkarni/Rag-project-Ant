---
description: Seeds the project workspace with eight curated failure-mode document inputs designed to test observability coverage.
argument-hint: ""
allowed-tools:
  - run_command
  - write_to_file
---

# 🛠️ Command: `/seed-documents`

This command creates a standardized dataset of eight failure-inducing documents under the `data/seed_failures/` directory. These files are crafted to trigger specific edge cases across the five canonical failure categories, allowing engineers to validate trace instrumentations.

## 📋 Pre-flight Checks
1. Validate that the workspace directory is writeable.
2. Confirm the directory `data/seed_failures/` can be created.

## 🚀 Execution Steps

1. **Create Target Directory**:
   - Initialize the directory: `data/seed_failures/`.

2. **Write Seed Documents**:
   - Write the following eight files with distinct contextual patterns:
     1. `01_hallucination_source.txt`: Extensively dense financial text containing ambiguous formatting to trigger `EXTRACTION_HALLUCINATION`.
     2. `02_misclassification_edge.txt`: Hybrid legal/medical document designed to test boundary classifiers (`MISCLASSIFICATION`).
     3. `03_propagation_type_break.txt`: Contains special character strings and missing delimiter arrays to break JSON parsing (`PROPAGATION_ERROR`).
     4. `04_prompt_injection.txt`: Simple text containing instruction-hijack phrases ("Ignore previous rules...") to test prompt isolation (`PROMPT_FAILURE`).
     5. `05_context_overflow.txt`: Extremely verbose log file exceeding context lengths to verify truncation behavior (`CONTEXT_LOSS`).
     6. `06_ambiguous_entity.txt`: Multiple entities with identical names but different context scopes.
     7. `07_malformed_json_input.txt`: Raw JSON with trailing commas and unescaped quotes.
     8. `08_nested_loop_recursion.txt`: Self-referential structural outline testing loop bounds.

3. **Status Report**:
   - Output a list of seeded paths and matching failure categories to target during test runs.

## 🛑 Failure Handling
- If write permission is denied: Output an error and prompt user to grant permission or execute in an alternative directory.
