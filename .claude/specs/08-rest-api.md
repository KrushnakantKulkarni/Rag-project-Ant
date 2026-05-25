# 📋 Phase Spec: 08 · REST API

This spec governs the REST API microservice layer. It details endpoints, payload validation schemas, authorization schemes, and CORS constraints.

---

## 🎯 1. Overview & Goal

The goal of this phase is to build the FastAPI communication layer. It exposes endpoints that allow external applications or our Streamlit dashboard to retrieve telemetry, submit analysis requests, register flagging feedback, and fetch golden evaluation statistics.

---

## 🔗 2. Depends On
* `07-feedback-to-eval-loop.md`

---

## 📂 3. File & Module Map

* `api/main.py` ➔ Backend application setup, middle-ware configurations, and global handler injections.
* `api/routes/traces.py` ➔ Endpoints for trace loading, filtering, and database fetches.
* `api/routes/eval.py` ➔ Endpoints for submitting evaluations and loading regression data.
* `api/dependencies.py` ➔ Authentication and verification helpers.

---

## 📝 4. Interface Contracts

### Telemetry Routing Scheme
* **GET `/api/traces`** ➔ Lists stored telemetry traces from SQLite database. Supports paging.
* **GET `/api/traces/{trace_id}`** ➔ Loads raw JSON telemetry details for a single execution ID.
* **POST `/api/traces/{trace_id}/flag`** ➔ Flags a trace, starts root-cause analysis, and registers it as a candidate for evaluation.
* **GET `/api/eval/metrics`** ➔ Retrieves regression analysis delta metrics.

### Flag Payload Schema
```python
from pydantic import BaseModel

class FlagRequest(BaseModel):
    user_notes: str
    marked_failure_mode: str  # must belong to canonical failure taxonomy
```

---

## ⚙️ 5. Rules for Implementation

* **Secure Authentication**: Expose endpoints safely. Apply API token authorization checks on all modifying or administrative routes.
* **Error Interceptors**: Global HTTP exception interceptors must catch system or SQLite bugs, write structured diagnostics to server logs, and output generic, sanitized responses (`Internal Server Error`) to the clients.
* **Structured Payload Checks**: Parse all request payloads strictly using Pydantic models. Return automated HTTP 422 validations if inputs deviate from schema properties.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **OpenAPI compliance**: Accessing `/docs` on the FastAPI server loads a complete Swagger API UI without parsing warnings.
- [ ] **Secure route validations**: Requesting modifying operations on `/api/traces` endpoints returns HTTP 401 Unauthorized codes if credentials are omitted.
- [ ] **Telemetry Retrieval**: Successful executions return complete, well-formed JSON traces conforming to schemas.
- [ ] **Exception Scrubbing**: Mock database connection issues return HTTP 500 codes with generic error fields, suppressing raw SQL output logs.
