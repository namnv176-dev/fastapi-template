# 🚀 Enterprise AI-Ready Modular Monolith Architecture (FastAPI)

This document defines the unified architectural standard for a scalable, maintainable, and AI-compatible backend, combining **Modular Monolith** principles with **Strict Transaction Management** and **Cross-Module Access Layers**.

---

## 1. High-Level Project Structure

```text
.
├── alembic/                # [External] Database migrations
├── app/
│   ├── core/               # Global Config, Security, Constants
│   ├── db/                 # Shared Data Infrastructure
│   │   ├── models/         # Centralized SQLAlchemy Models (Single Source of Truth)
│   │   └── session.py      # Engine and SessionLocal factory
│   ├── repositories/       # Shared Data Access Layer (BaseRepo, UserRepo, etc.)
│   ├── infrastructure/     # External Adapters (Qdrant, Redis, LLM Clients)
│   ├── dependencies/       # Centralized DI (Auth, DB Session, Clients)
│   ├── middleware/         # Observability (Logging, Tracing, Monitoring)
│   ├── modules/            # PLUG-AND-PLAY FEATURE DOMAINS
│   │   ├── research/       # Example Module: AI Research
│   │   │   ├── api/        # HTTP Handlers
│   │   │   ├── services/   # Business Logic & Transaction Control
│   │   │   ├── schemas/    # Pydantic Models (Validation)
│   │   │   ├── access.py   # [CRITICAL] Controlled Interface for other modules
│   │   │   └── tasks.py    # Async Workers (Taskiq/Celery)
│   │   └── notification/   # Example Module: Notification
│   └── main.py             # App Entry & Module Registration
├── docker/                 # Multi-stage Dockerfiles (K8s Ready)
└── pyproject.toml          # Dependency Management (Uv/Poetry)
```

---

## 2. Layer Definitions & Responsibilities

### 🔹 API Layer (`modules/*/api/`)
- **Role:** Handle HTTP requests/responses.
- **Rules:** Validate data using Pydantic; Call Service layer **only**. Never touch Repositories.

### 🔹 Service Layer (`modules/*/services/`)
- **Role:** The "Brain". Orchestrates business logic and **owns Transactions**.
- **Rules:** Must handle `db.commit()` and `db.rollback()`. Orchestrates Repositories and Infrastructure clients.

### 🔹 Access Layer (`modules/*/access.py`)
- **Role:** The "Safe Gateway" for cross-module communication.
- **Rules:** If Module A needs data from Module B, it **must** call `ModuleB.access`. Service A is forbidden from importing Service B.

### 🔹 Repository Layer (`app/repositories/`)
- **Role:** Pure Database Operations.
- **Rules:** Receives `db` session from Service. **Never** commit or rollback. Stay "dumb" regarding business logic.

### 🔹 Infrastructure Layer (`app/infrastructure/`)
- **Role:** External Service Adapters (LLMs, Vector DBs).
- **Rules:** Return standardized objects (Pydantic) to keep the core logic independent of third-party API changes.

---

## 3. Strict Development Rules (The "Laws")

### ⚖️ Transaction Integrity
Transactions are managed **ONLY** in the Service layer.
```python
# Correct Implementation in Service
def process_ai_task(self, db: Session, data: Schema):
    try:
        self.repo.update_status(db, data.id, "processing")
        self.ai_infra.call_llm(data.prompt)
        db.commit() # Single point of truth
    except Exception:
        db.rollback()
        raise
```

### 🤝 Cross-Module Interaction
- **NO** circular imports.
- **NO** direct repository calls to other modules.
- **YES** call `access.py` functions which act as internal APIs.

### 📊 Monitoring & Observability (K8s)
- Use `structlog` for JSON logging.
- Every log entry must include `request_id` and `module_name`.
- Health checks must verify connections to DB, Redis, and Vector DB (Qdrant).

---

## 4. AI-Agent Compatibility (SOP)
To enable AI Agents (Cursor, Claude) to code efficiently without breaking the architecture:
1. **Context injection:** Provide the `app/repositories/base.py` and a module template.
2. **Interface-First:** Require the Agent to define the `Schema` and `Access` function before writing the Service.
3. **Validation:** Use `mypy` and `ruff` in CI/CD to catch architectural violations (like illegal imports).

---

## 5. Deployment (Docker & K8s)
- **Multi-stage build:** Keep production images small and secure.
- **Environment Parity:** Use Pydantic Settings to ensure `.env` keys are validated on startup.
- **Worker/Web Isolation:** Use the same image but different CMDs for the API server and the AI Background Worker.
