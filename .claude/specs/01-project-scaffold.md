# 📋 Phase Spec: 01 · Project Scaffold

This spec establishes the project layout, local virtual environment setup, SQLite index database initialization, Docker setup, and centralized dependency declarations.

---

## 🎯 1. Overview & Goal

The goal of this phase is to scaffold the base workspace directory, establish package structures, verify configuration setups, initialize `traces.db` with appropriate schema fields, and containerize the environment.

---

## 🔗 2. Depends On
* *None* (First Phase)

---

## 📂 3. File & Module Map

```text
📁 e:\ai-projects\Rag-project-Ant/
├── 📁 pipeline/                      # Pure step function modules
│   └── __init__.py
├── 📁 tracing/                       # Decorators, schemas, and db interface
│   └── __init__.py
├── 📁 analysis/                      # Backward analyzer logic
│   └── __init__.py
├── 📁 eval/                          # Evaluation and regression datasets
│   └── __init__.py
├── 📁 api/                           # FastAPI server app
│   └── __init__.py
├── 📁 ui/                            # Streamlit dashboard
│   └── __init__.py
├── 📁 utils/                         # Global logger and configurations
│   ├── __init__.py
│   ├── logger.py
│   └── settings.py
├── .env.example                      # Environment variables template
├── Dockerfile                        # Multi-stage image build file
├── docker-compose.yml                # Telemetry and local stack compose
├── requirements.txt                  # Direct dependency declarations
└── schema.sql                        # SQLite database init script
```

---

## 📝 4. Interface Contracts

### `utils/settings.py`
A centralized `pydantic-settings` model managing credentials and system attributes:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    DATABASE_PATH: str = "traces.db"
    TRACE_ARCHIVE_DIR: str = "traces/"
    API_KEY_SECRET: str
    
    class Config:
        env_file = ".env"
```

### `schema.sql`
SQLite database schema initialization script:
```sql
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    document_name TEXT NOT NULL,
    status TEXT NOT NULL,          -- SUCCESS or FAILED
    error_message TEXT,
    overall_latency_ms REAL,
    overall_token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence_score INTEGER,      -- 1 to 5, NULL for non-LLM steps
    latency_ms REAL,
    token_count INTEGER,
    error TEXT,
    FOREIGN KEY(trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
);
```

---

## ⚙️ 5. Rules for Implementation

* **Dependency Isolation**: All core libraries (FastAPI, Streamlit, Pydantic, SQLite3, OpenAI) must be explicitly listed in `requirements.txt`.
* **Database Actions**: Use standard, lightweight context-managed SQLite queries (`sqlite3` standard library). No heavy ORMs like SQLAlchemy.
* **Environment Integrity**: Ensure `.env.example` lists all needed variables without exposing actual secrets.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Folder Structure**: All directories specified in the map exist.
- [ ] **Configuration Loading**: Executing `utils/settings.py` successfully loads variables from `.env` or defaults.
- [ ] **Database Scaffolding**: Executing Python's SQLite connect against `schema.sql` successfully compiles tables without syntax warnings.
- [ ] **Docker Compliance**: Command `docker build -t failure-forensics:latest .` executes and compiles the scaffold container cleanly.
