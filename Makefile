# ============================================================
# FastAPI Template — Makefile
# ============================================================
# Requirements:
#   - uv          (pip install uv)
#   - docker      (for docker-compose commands)
#   - make        (pre-installed on macOS/Linux)
# ============================================================

# ---------- Variables ----------
PYTHON      := python
UV          := uv
PYTEST      := pytest
ALEMBIC     := alembic
COMPOSE     := docker compose
SERVICE_WEB := web
SERVICE_DB  := db
SERVICE_REDIS := redis
ENV_FILE    := .env

# Check if .env exists, fallback to .env.example
ifeq ($(wildcard $(ENV_FILE)),)
	ENV_PARAM    := --env-file .env.example
else
	ENV_PARAM    := --env-file $(ENV_FILE)
endif


# ============================================================
# 🐍 Local Development (native, no Docker)
# ============================================================

## Install dependencies with uv
.PHONY: install
install:
	$(UV) sync --all-packages

## Install dev dependencies
.PHONY: install-dev
install-dev:
	$(UV) sync --all-packages --dev

## Run the FastAPI server locally (hot reload)
.PHONY: run
run:
	$(UV) run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

## Run with gunicorn (production-like)
.PHONY: run-prod
run-prod:
	$(UV) run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

## Run the FastAPI server with custom port
.PHONY: run-port
run-port:
	$(UV) run uvicorn src.main:app --reload --host 0.0.0.0 --port $(PORT)

## Run tests
.PHONY: test
test:
	$(UV) run $(PYTEST) ./tests -v

## Run tests with coverage
.PHONY: test-cov
test-cov:
	$(UV) run $(PYTEST) ./tests -v --cov=src --cov-report=html

## Run tests matching a pattern
.PHONY: test-watch
test-watch:
	$(UV) run $(PYTEST) ./tests -v -k "$(PATTERN)"


# ============================================================
# 🗄️ Database Migrations (Alembic + uv)
# ============================================================

## Create a new migration revision
.PHONY: migration-create
migration-create:
	$(UV) run alembic revision --autogenerate -m "$(NAME)"

## Create an empty migration revision
.PHONY: migration-create-empty
migration-create-empty:
	$(UV) run alembic revision -m "$(NAME)"

## Run all pending migrations
.PHONY: migration-upgrade
migration-upgrade:
	$(UV) run alembic upgrade head

## Downgrade one migration step
.PHONY: migration-downgrade
migration-downgrade:
	$(UV) run alembic downgrade -1

## Downgrade to a specific revision
.PHONY: migration-downgrade-to
migration-downgrade-to:
	$(UV) run alembic downgrade "$(REV)"

## Show current migration revision
.PHONY: migration-current
migration-current:
	$(UV) run alembic current

## Show migration history
.PHONY: migration-history
migration-history:
	$(UV) run alembic history --verbose

## Show pending migrations
.PHONY: migration-check
migration-check:
	$(UV) run alembic check


# ============================================================
# 🐳 Docker Compose — Dependencies Only (DB + Redis)
# ============================================================

## Start DB and Redis containers only
.PHONY: deps-up
deps-up:
	$(COMPOSE) up -d $(SERVICE_DB) $(SERVICE_REDIS)

## Stop DB and Redis containers
.PHONY: deps-down
deps-down:
	$(COMPOSE) stop $(SERVICE_DB) $(SERVICE_REDIS)

## Restart DB and Redis containers
.PHONY: deps-restart
deps-restart:
	$(COMPOSE) restart $(SERVICE_DB) $(SERVICE_REDIS)

## Remove DB and Redis containers and volumes
.PHONY: deps-clean
deps-clean:
	$(COMPOSE) down -v $(SERVICE_DB) $(SERVICE_REDIS)

## View logs of DB container
.PHONY: logs-db
logs-db:
	$(COMPOSE) logs -f $(SERVICE_DB)

## View logs of Redis container
.PHONY: logs-redis
logs-redis:
	$(COMPOSE) logs -f $(SERVICE_REDIS)


# ============================================================
# 🐳 Docker Compose — Web (FastAPI) Only
# ============================================================

## Build the web Docker image
.PHONY: web-build
web-build:
	$(COMPOSE) build $(SERVICE_WEB)

## Run FastAPI via Docker (depends on DB + Redis)
.PHONY: web-up
web-up: deps-up
	$(COMPOSE) up -d $(SERVICE_WEB)

## Run FastAPI via Docker with hot reload (bind mount)
.PHONY: web-up-reload
web-up-reload: deps-up
	$(COMPOSE) up $(SERVICE_WEB)

## Stop the web container
.PHONY: web-down
web-down:
	$(COMPOSE) stop $(SERVICE_WEB)

## Restart the web container
.PHONY: web-restart
web-restart:
	$(COMPOSE) restart $(SERVICE_WEB)

## Remove the web container
.PHONY: web-remove
web-remove:
	$(COMPOSE) rm -f $(SERVICE_WEB)

## View logs of the web container
.PHONY: logs-web
logs-web:
	$(COMPOSE) logs -f $(SERVICE_WEB)

## Run a command inside the web container
.PHONY: web-exec
web-exec:
	$(COMPOSE) exec $(SERVICE_WEB) $(CMD)


# ============================================================
# 🐳 Docker Compose — Full Project (All Services)
# ============================================================

## Start all services (DB + Redis + Web)
.PHONY: up
up:
	$(COMPOSE) up -d

## Start all services with hot reload (show logs)
.PHONY: up-reload
up-reload:
	$(COMPOSE) up

## Start all services and rebuild images
.PHONY: up-build
up-build:
	$(COMPOSE) up --build -d

## Stop all services (preserve volumes)
.PHONY: down
down:
	$(COMPOSE) down

## Stop and remove all services + volumes + images
.PHONY: clean
clean:
	$(COMPOSE) down -v --rmi all

## Full reset: stop, remove volumes, rebuild, and start
.PHONY: reset
reset: clean up-build

## View logs of all services
.PHONY: logs
logs:
	$(COMPOSE) logs -f

## View logs of a specific service
.PHONY: logs-service
logs-service:
	$(COMPOSE) logs -f $(SERVICE)

## List all containers and their status
.PHONY: ps
ps:
	$(COMPOSE) ps

## Show resource usage of all containers
.PHONY: stats
stats:
	$(COMPOSE) stats

## Recreate all containers (preserving volumes)
.PHONY: recreate
recreate:
	$(COMPOSE) up -d --force-recreate


# ============================================================
# 🏗️ Database Utilities (inside Docker)
# ============================================================

## Run migrations inside Docker web container
.PHONY: docker-migration-upgrade
docker-migration-upgrade:
	$(COMPOSE) exec $(SERVICE_WEB) alembic upgrade head

## Create a migration inside Docker
.PHONY: docker-migration-create
docker-migration-create:
	$(COMPOSE) exec $(SERVICE_WEB) alembic revision --autogenerate -m "$(NAME)"

## Run tests inside Docker
.PHONY: docker-test
docker-test:
	$(COMPOSE) exec $(SERVICE_WEB) pytest ./tests -v

## Create first superuser inside Docker
.PHONY: docker-superuser
docker-superuser:
	$(COMPOSE) exec $(SERVICE_WEB) python -m src.scripts.create_first_superuser


# ============================================================
# 🛠️ Code Quality
# ============================================================

## Run ruff linter
.PHONY: lint
lint:
	$(UV) run ruff check .

## Auto-fix linting issues
.PHONY: lint-fix
lint-fix:
	$(UV) run ruff check . --fix

## Format code with ruff
.PHONY: format
format:
	$(UV) run ruff format .

## Run mypy type checker
.PHONY: typecheck
typecheck:
	$(UV) run mypy src/

## Run ruff, ruff format, and mypy
.PHONY: ci
ci: lint format typecheck


# ============================================================
# 📦 Utility Scripts
# ============================================================

## Create first superuser (local)
.PHONY: superuser
superuser:
	$(UV) run python -m src.scripts.create_first_superuser

## Drop all tables (DANGER: destroys data)
.PHONY: db-reset
db-reset:
	$(UV) run alembic downgrade base && $(UV) run alembic upgrade head


# ============================================================
# ℹ️ Help
# ============================================================

.PHONY: help
help:
	@echo ""
	@echo "FastAPI Template — Available Make Commands"
	@echo ""
	@echo "Local Development (native):"
	@echo "  make install           Install dependencies with uv"
	@echo "  make run              Run FastAPI server with hot reload"
	@echo "  make run-prod         Run with gunicorn"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make migration-create            NAME=\"your message\"   Create migration"
	@echo "  make migration-upgrade          Run pending migrations"
	@echo "  make migration-downgrade        Downgrade one step"
	@echo "  make migration-history         Show migration history"
	@echo ""
	@echo "Docker Dependencies (DB + Redis only):"
	@echo "  make deps-up            Start DB and Redis"
	@echo "  make deps-down          Stop DB and Redis"
	@echo "  make logs-db           View DB logs"
	@echo "  make logs-redis         View Redis logs"
	@echo ""
	@echo "Docker Web (FastAPI):"
	@echo "  make web-up             Start FastAPI via Docker"
	@echo "  make web-up-reload      Start with hot reload (bind mount)"
	@echo "  make logs-web          View web logs"
	@echo "  make web-exec CMD=...   Run command inside web container"
	@echo ""
	@echo "Docker Full Project:"
	@echo "  make up                 Start all services"
	@echo "  make up-reload          Start all (show live logs)"
	@echo "  make up-build           Rebuild and start all"
	@echo "  make down               Stop all services"
	@echo "  make clean              Stop and remove everything"
	@echo "  make reset              Full reset and restart"
	@echo "  make logs               View all logs"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               Run ruff linter"
	@echo "  make lint-fix           Auto-fix linting issues"
	@echo "  make format             Format code with ruff"
	@echo "  make typecheck          Run mypy type checker"
	@echo "  make ci                 Run lint + format + typecheck"
	@echo ""
	@echo "Examples:"
	@echo "  make migration-create NAME=\"add users table\""
	@echo "  make web-up-reload"
	@echo "  make up SERVICE=db logs"
	@echo ""
