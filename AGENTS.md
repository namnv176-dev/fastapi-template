# FastAPI Template: AGENTS.md

This document serves as the absolute mandate for AI interactions, architectural principles, and operational guidelines for this project.

## Project Overview
**FastAPI Template** is a modern, production-ready backend boilerplate designed with Clean Architecture and Modular Monolith principles. It leverages high-performance Python tools for asynchronous API development.

### Core Technology Stack
- **Framework**: FastAPI (Asynchronous, Type-safe)
- **Validation/Settings**: Pydantic v2
- **Database**: PostgreSQL (via `asyncpg` and SQLAlchemy 2.0 Async)
- **Migrations**: Alembic
- **Caching**: Redis
- **Task Queue**: `arq` (Redis-based background workers)
- **Dependency Management**: `uv` (Astral's fast Python package manager)
- **Linting & Formatting**: Ruff, Mypy
- **Containerization**: Docker & Docker Compose

## Core Architectural Principle: Modular Monolith
The project is organized into self-contained domain modules under `src/modules/`. Each module encapsulates its API, business logic (Services), and domain-specific schemas. Cross-module logic access MUST be handled through an `access.py` file to maintain structural integrity.

## Project Structure
- `src/main.py`: Entry point.
- `src/api_router.py`: Central router.
- `src/core/`: Cross-cutting concerns (config, security, logging, exceptions).
- `src/db/`: Database models and session management.
- `src/modules/`: Business domain modules (e.g., `user`, `post`).
    - `*/api/v1/`: Endpoints.
    - `*/services.py`: Business logic layer (orchestrates transactions).
    - `*/access.py`: Public interface for other modules to access this module's logic.
    - `*/schemas.py`: Pydantic models.
- `src/repositories/`: Data Access Layer (DAL).
- `src/dependencies/`: Reusable FastAPI dependencies.

---

## Coding Rules

### 1. Function Standards
- **Max length:** 30 lines.
- **Responsibility:** Single responsibility only.
- **Nesting:** Max 2-3 levels deep.
- **Pattern:** Use **early returns** to reduce complexity.

### 2. Naming Conventions
- **Functions:** `verb_noun` (e.g., `get_user`, `create_post`).
- **Variables:** Nouns (e.g., `user_list`, `post_data`).
- **Booleans:** Prefix with `is_` or `has_` (e.g., `is_active`, `has_permission`).

### 3. Type Safety & Validation
- **Type Hints:** Mandatory for all parameters and return types.
- **Validation:** Always validate input using Pydantic models.
- **Immutability:** Use `dataclass(frozen=True)` for internal data structures when possible.

### 4. Logic & Data Separation
- **No Business Logic in API:** Views/API layers only handle request parsing and calling services.
- **Repository Pattern:** Services cannot use direct ORM calls (like `select(Post)`). All data access must pass through `src/repositories/`.
- **Transaction Orchestration:** Services manage `db.commit()` and `db.rollback()`. Repositories perform `db.add()`, `db.delete()`, and `db.flush()`, but **NEVER** commit.
- **Cross-Module Access:** Modules must NEVER call each other's Services or Repositories directly. They must use the target module's `access.py` as a public API proxy.

### 5. Error Handling & Logging
- **Exceptions:** Use custom exceptions from `src/core/exceptions/`.
- **Critical Logic:** Never return `None` for critical operations where data is expected; raise an exception instead.
- **Structured Logging:** Use `logger.info("msg", extra={})` for all key events.

### 6. Code Quality
- **PEP 8:** Strict adherence required.
- **Built-in Functions:** Prefer Python built-ins and list comprehensions for readability.
- **DRY:** Extract reusable logic into helper functions or utilities.
- **Constants:** No magic numbers. Use `CAPITAL_SNAKE_CASE` constants in `src/core/constants.py` or within modules.
- **No Side Effects:** Functions should return values and avoid hidden state mutations.

### 7. File & Import Standards
- **File Size:** Max 300-500 lines per file.
- **Import Order:**
    1. Standard Library
    2. Third-party packages
    3. Local modules

### 8. Async First
- **Async I/O:** Use `async/await` for all database, Redis, and I/O operations.
- **Consistency:** Ensure repository methods called by services are properly awaited.

---

## Operational Guidelines for AI
1. **Pre-completion Verification:** Before confirming the task is complete, the Agent MUST run the following command to ensure code quality:
   ```bash
   uv run ruff check . --fix && uv run mypy src
   ```
2. **Context Awareness:** Always review `AGENTS.md` at the start of a session.
3. **Safety:** Never commit/push unless explicitly asked.

## Key Operational Commands
- **Run**: `uv run uvicorn src.main:app --reload`
- **Migrations**: `alembic revision --autogenerate -m "desc"` -> `alembic upgrade head`
- **Quality**: `pytest`, `ruff check . --fix`, `mypy src`

---
*Failure to adhere to these rules is unacceptable. Adherence ensures a stable, testable, and maintainable codebase.*
