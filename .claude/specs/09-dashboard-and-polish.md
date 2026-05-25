# 📋 Phase Spec: 09 · Dashboard & Polish

This spec details Docker Compose multi-service configurations, global telemetry displays, end-to-end demo execution runs, and final validation plans.

---

## 🎯 1. Overview & Goal

The goal of this final phase is to coordinate the complete telemetry observability platform. By implementing multi-container orchestration with Docker Compose, integrating the FastAPI service with the Streamlit frontend, executing a full telemetry seed run, and formatting the diagnostic flows, we deliver a production-grade, portfolio-ready product.

---

## 🔗 2. Depends On
* `08-rest-api.md`

---

## 📂 3. File & Module Map

* `docker-compose.yml` ➔ Coordinates backend and frontend container services.
* `utils/logger.py` ➔ Streamlines diagnostic outputs.
* `README.md` ➔ Full documentation detailing application deployment steps, APIs, and diagnostic scenarios.

---

## 📝 4. Interface Contracts

### Docker Compose Services Layout
* **`api-service`**: Executes the FastAPI server via Uvicorn on port `8000`. Exposes backend endpoints.
* **`dashboard-ui`**: Runs the Streamlit dashboard on port `8501`. Connects to `api-service` utilizing environment configurations.

---

## ⚙️ 5. Rules for Implementation

* **Unified Configuration**: Both backend and frontend services must share configuration variables declared under a central `.env` template.
* **Resilient Startup**: Implement health check policies in `docker-compose.yml`. Ensure the `dashboard-ui` container pauses startup sequence until the `api-service` endpoint successfully responds to health probes.
* **Production Polish**: Compile clean documentation outlining step-by-step diagnostic workflows, failure taxonomy mappings, and commands configurations.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Multi-container orchestration**: Executing `docker compose up -d` successfully builds, boots, and coordinates both backend and frontend applications.
- [ ] **UI-API Integration**: The Streamlit trace dashboard fetches execution traces directly from the FastAPI server endpoints.
- [ ] **Seeded Failure Run**: Running `/run-pipeline` over documents seeded via `/seed-documents` populates the SQLite index and shows low confidence alerts.
- [ ] **Full diagnostic walk**: Demonstrable execution of a backward trace analysis walks step nodes, identifies root cause, and successfully appends the case to `eval/eval_dataset.json` via the frontend button.
- [ ] **Polished portfolio presentation**: Compiles a professional user handbook with system architecture flowcharts.
