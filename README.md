# FastAPI Template

A production-ready FastAPI boilerplate with async PostgreSQL, Redis, JWT authentication, and integrated LLM (AI) capabilities.

---

## Tech Stack

| Category | Technology |
|---|---|
| **Framework** | FastAPI (Standard) |
| **Server** | Uvicorn + UVLoop + HTTPTools |
| **Database** | PostgreSQL (async: asyncpg / sync: psycopg2) |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Cache & Queue** | Redis |
| **AI / LLM** | LangChain, LangChain-Community, LangChain-Google-GenAI, LangChain-Anthropic |
| **Tokenization** | Tiktoken |
| **Auth** | JWT (python-jose + bcrypt) |
| **Task Queue** | ARQ |
| **Validation** | Pydantic v2 |
| **Logging** | Structlog |
| **Code Quality** | Ruff, MyPy, Pre-commit |
| **Testing** | pytest, pytest-asyncio |
| **Container** | Docker, Docker Compose |
| **LLM Providers** | OpenAI (GPT-4o), Google Gemini, Anthropic (Claude) |

---

## Features

### Authentication & Security
- JWT-based authentication (Access Token + Refresh Token)
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Secure configuration management via environment variables (Pydantic Settings)

### Database
- Async database driver (asyncpg) for high performance
- SQLAlchemy 2.0 with async support
- Alembic for schema migrations
- Support for both async and sync database connections

### LLM Integration
- Unified LLM handler via LangChain
- Multi-provider support: **OpenAI, Google Gemini, Anthropic Claude**
- Streaming response support
- Structured output (Pydantic schema)
- Input/Output guardrails validation
- Token counting (tiktoken)
- Conversation history management

### Caching & Background Tasks
- Redis caching layer
- Redis-based task queue (ARQ) for background jobs
- Client-side cache headers

### Observability
- Structured JSON logging with structlog
- Request ID, path, method, client host, and status code in logs
- Health check endpoint

### Developer Experience
- Hot reload in local environment
- Pre-commit hooks (format, lint, type-check)
- Ruff linter + MyPy type checker
- Docker & Docker Compose ready
- Environment-based configuration (local / staging / production)

---

## Project Structure

```
src/
├── main.py                    # Application entry point
├── api_router.py              # Route aggregation
├── core/                      # Core utilities
│   ├── config.py              # Settings & configuration
│   ├── security.py            # JWT & password utils
│   ├── logger.py              # Structured logging
│   ├── setup.py               # FastAPI app factory
│   └── exceptions/            # Custom exceptions
├── db/                        # Database layer
│   ├── session.py             # Async/sync sessions
│   └── models/                # SQLAlchemy models
├── dependencies/              # FastAPI dependencies
├── middleware/                # Custom middleware
├── modules/                   # Feature modules
│   ├── user/                  # Auth, users
│   ├── health/                # Health check
│   └── post/                  # Posts & comments
├── repositories/              # Data access layer
├── infrastructure/            # External services
│   ├── llm/                   # LLM handler, factory, guardrails
│   └── pydantic/              # Shared Pydantic schemas
└── scripts/                   # Utility scripts
    └── create_first_superuser.py
```

---

## Quick Start

### 1. Clone & Install

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database, Redis, and LLM API keys
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start the Server

```bash
# Development (with hot reload)
uvicorn src.main:app --reload

# Production
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 5. Run Tests

```bash
pytest
```

---

## API Endpoints (v1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/logout` | User logout |
| GET | `/api/v1/users` | List users |
| GET | `/api/v1/users/{id}` | Get user by ID |
| POST | `/api/v1/posts` | Create a post |
| GET | `/api/v1/posts` | List posts |
| POST | `/api/v1/comments` | Create a comment |
| GET | `/api/v1/health` | Health check |

---

## LLM Configuration

Set the provider and model in `.env`:

```env
LLM_PROVIDER=openai        # openai | gemini | anthropic
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
# or
GEMINI_API_KEY=...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

### Using the LLM Handler

```python
from src.infrastructure.llm import llm_handler

# Streaming chat
async for chunk in await llm_handler.chat(
    message_content="Hello!",
    history=[],
    system_prompt="You are a helpful assistant.",
    streaming=True,
):
    print(chunk)

# Structured output
result = await llm_handler.chat(
    message_content="Extract the name and email.",
    history=[],
    structured_output=SomePydanticSchema,
)
```

---

## Docker

```bash
# Build and run
docker compose up --build

# Run only the app
docker compose up app

# Run only dependencies (DB, Redis)
docker compose up db redis
```

---

## Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy src/

# Run pre-commit on all files
pre-commit run --all-files
```

---

## License

See [LICENSE](LICENSE).
