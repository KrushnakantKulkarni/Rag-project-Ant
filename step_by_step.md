# ⚡ Failure Forensics Co-Pilot: Step-by-Step Creation Guide

This guide walks you through the step-by-step creation of the **Failure Forensics Tool** project scaffold, processing pipeline, and tracing layer from top to bottom. It establishes the package directories, configuration models, SQLite index schemas, step functions, execution orchestrators, decorators, and telemetry logging modules.

---

## 📂 Step 1: Package Directories & Initialization Files (`__init__.py`)

We initialize the modular folder structure. Each folder acts as an isolated package boundary with its own dedicated responsibility, adhering to strict module separation rules.

### 1. `pipeline/__init__.py`
* **Path**: `pipeline/__init__.py`
* **Description**: Initializes the pure step function module boundary. This package houses the stateless processing steps (Intake, Extraction, Classification, Summarization) of the pipeline.

### 2. `tracing/__init__.py`
* **Path**: `tracing/__init__.py`
* **Description**: Initializes the telemetry package boundary. It will manage the database loggers, tracing context, and the `@instrument` decorator to seamlessly intercept pipeline metrics.

### 3. `analysis/__init__.py`
* **Path**: `analysis/__init__.py`
* **Description**: Initializes the backward trace analysis package. This package is dedicated to the root-cause diagnostics engine, which runs forensic walk-backs when executions fail or record low confidence.

### 4. `eval/__init__.py`
* **Path**: `eval/__init__.py`
* **Description**: Initializes the evaluation and regression testing package. It holds baseline datasets and validation frameworks to verify pipeline accuracy and detect regressions prior to deployment.

### 5. `api/__init__.py`
* **Path**: `api/__init__.py`
* **Description**: Initializes the FastAPI web API package. This boundary exposes REST endpoints for triggering pipeline runs, querying diagnostic traces, and running forensic analyses remotely.

### 6. `ui/__init__.py`
* **Path**: `ui/__init__.py`
* **Description**: Initializes the front-end Streamlit dashboard package. This package is responsible for the visual Trace Explorer, featuring color-coded flow charts and interactive payload side-by-side diff viewers.

### 7. `utils/__init__.py`
* **Path**: `utils/__init__.py`
* **Description**: Initializes the shared utility package. It holds common helper functions, system configurations, and cross-cutting capabilities used throughout the entire application.

---

## 🛠️ Step 2: Shared Utilities & Infrastructure Configuration

Next, we establish the global configurations and logging layers. These files provide structured console feedback and load credentials securely using typed Pydantic Settings.

### 8. `utils/logger.py`
* **Path**: `utils/logger.py`
* **Description**: Defines a standardized, structured global logger for the application. It ensures consistent log styling, eliminates forbidden `print()` statements, and provides color-coded diagnostics for easy troubleshooting.

### 9. `utils/settings.py`
* **Path**: `utils/settings.py`
* **Description**: Implements the centralized `BaseSettings` model using `pydantic-settings`. It parses system attributes and credentials (like API keys and database paths) directly from `.env` files with explicit schema validation.

---

## ⚙️ Step 3: Environment Templates & Database Schema Blueprint

We define the configuration variables template and the relational database schema required to persist pipeline telemetry.

### 10. `.env.example`
* **Path**: `.env.example`
* **Description**: A safe environment variables blueprint containing default values and empty placeholder secrets. It ensures that incoming co-pilots and developers know exactly which keys (OpenAI keys, API secrets) are required without exposing sensitive production values.

### 11. `schema.sql`
* **Path**: `schema.sql`
* **Description**: The core SQLite schema script. It initializes the `traces` index table (storing overall status, errors, and latency) and the child `spans` table (storing step-specific latencies, confidence metrics, and token usage) with cascade-on-delete constraints.

---

## 📦 Step 4: Containerization & Dependency Declarations

We specify all required libraries and declare the Docker environment configurations to package the workspace into a production-ready, isolated container.

### 12. `requirements.txt`
* **Path**: `requirements.txt`
* **Description**: Lists all core libraries and direct dependency declarations. It includes specific frameworks like `fastapi`, `streamlit`, `openai`, `pydantic-settings`, and `uvicorn`, guaranteeing dependency isolation.

### 13. `Dockerfile`
* **Path**: `Dockerfile`
* **Description**: A multi-stage Docker build file that compiles the scaffold container cleanly. It sets up the python virtual environment, installs the requirements, and packages both the FastAPI backend and Streamlit frontend.

### 14. `docker-compose.yml`
* **Path**: `docker-compose.yml`
* **Description**: The orchestration configuration for running local services. It sets up telemetry containers, maps database volumes safely, and lets you bring up the database, API server, and web UI with a single command.

---

## 🚀 Step 5: Pure Stateless Pipeline Steps (Phase 02)

Here we build the operational core of the processing pipeline. Each step is implemented in a separate, isolated module file with strict Pydantic inputs and outputs, preserving complete statelessness.

### 15. `pipeline/intake.py`
* **Path**: `pipeline/intake.py`
* **Description**: Reads incident source text files from disk, strips leading and trailing whitespaces, performs character count validation, and creates the validated `IntakeOutput` model. This is the entry point of the raw document processing stream.

### 16. `pipeline/extraction.py`
* **Path**: `pipeline/extraction.py`
* **Description**: Submits the sanitized intake text context to the OpenAI client using a highly structured prompt. It extracts precise facts, entities, timestamps, and error codes directly into Pydantic models.

### 17. `pipeline/classification.py`
* **Path**: `pipeline/classification.py`
* **Description**: Performs logical failure categorization (Network, Database, Application, Security, Legal) and assigns severity levels (Critical, Major, Minor). It parses the extracted facts list and enforces a rigorous justification block.

### 18. `pipeline/summarization.py`
* **Path**: `pipeline/summarization.py`
* **Description**: Processes the incident categories and facts to compile a clean, readable executive incident summary. It also maps failure states to actionable step-by-step remediation plans.

### 19. `pipeline/runner.py`
* **Path**: `pipeline/runner.py`
* **Description**: The centralized orchestrator that connects the four stateless stages in sequence. It chains output results from upstream steps into input schemas of downstream steps, and exposes a singular execution function returning consolidated results.

---

## 📊 Step 6: Observability Telemetry & Tracing Layer (Phase 03)

We implement the tracing ecosystem, providing high-resolution execution profiling, automatic exceptions catching decorators, and transactional relational database indexing.

### 20. `tracing/span.py`
* **Path**: `tracing/span.py`
* **Description**: Establishes the `Span` Pydantic model. This schema tracks granular data including errors, latencies, tokens, and raw prompt-response strings for each isolated execution stage.

### 21. `tracing/trace.py`
* **Path**: `tracing/trace.py`
* **Description**: Establishes the `Trace` Pydantic model. It acts as an execution context holder that aggregates the list of Spans, measures E2E latencies, and tallies total token costs.

### 22. `tracing/instrumentation.py`
* **Path**: `tracing/instrumentation.py`
* **Description**: Implements the context-managed timers and `@instrument` decorator. It captures processing speeds in microseconds, binds metadata, intercepts failures, and populates the global thread-safe span contexts.

### 23. `tracing/storage.py`
* **Path**: `tracing/storage.py`
* **Description**: Establishes local telemetry indexing. It serializes traces as individual JSON logs inside the `traces/` folder, and utilizes atomicity-guaranteed SQLite transactions to commit data safely to `traces.db`.
