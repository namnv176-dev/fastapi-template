# FastAPI Template: GEMINI.md

This document provides essential context, architectural principles, and operational guidelines for AI interactions within this project.

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

## Project Structure & Architecture

The project follows a modular structure where features are encapsulated within `src/modules/`.

- `src/main.py`: Application entry point.
- `src/api_router.py`: Centralized router for all API modules.
- `src/core/`: Infrastructure and cross-cutting concerns (config, security, logging, health).
- `src/db/`: Database configuration and SQLAlchemy models.
- `src/modules/`: Business logic divided into domain modules (e.g., `auth`, `user`).
  - `*/api/v1/`: API endpoints (routers).
  - `*/services/`: Business logic layer (handles transactions).
  - `*/schemas/`: Pydantic models for domain-specific data.
- `src/repositories/`: Data Access Layer (DAL).
- `src/dependencies/`: Reusable FastAPI dependencies (auth, database).
- `src/middleware/`: Custom FastAPI middlewares.
- `src/worker/`: Background job definitions and settings.

## Development Conventions

### 1. Database Operations (Repository Pattern)
- **Repositories (`src/repositories/`)**: Inherit from `BaseRepository`. They handle data fetching and `db.add()`, but **NEVER** perform `db.commit()` or `db.rollback()`.
- **Services (`src/modules/*/services/`)**: Orchestrate business logic and manage database transactions (`commit`/`rollback`).

### 2. Async First
- All database and I/O operations must be `async`. Use `await` for repository calls and service methods.

### 3. Type Safety
- Use Pydantic models for all request bodies and response schemas.
- Ensure strict typing with Mypy throughout the codebase.

### 4. Modular Design
- Keep domain logic within its respective module under `src/modules/`. Avoid tight coupling between modules where possible.

## Key Commands

### Local Development
- **Run Application**: `uv run uvicorn src.main:app --reload`
- **Docker Compose**: `docker-compose up` (Starts Postgres, Redis, and Web app)
- **Database Migrations**:
  - Create: `alembic revision --autogenerate -m "description"`
  - Upgrade: `alembic upgrade head`
  - Downgrade: `alembic downgrade -1`

### Testing & Quality
- **Run Tests**: `pytest`
- **Linting**: `ruff check . --fix`
- **Type Checking**: `mypy src`

## Operational Safety
- **Environment Variables**: Always use `src/core/config.py` to access environment variables. Never hardcode secrets.
- **Error Handling**: Use custom exceptions from `src/core/exceptions/` (e.g., `HTTPException`, `NotFoundException`).
- **Commits**: Do not stage or commit changes unless explicitly requested.

---
*Note: This file is a foundational mandate for AI interactions. Adhere to the patterns established here.*
