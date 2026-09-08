.PHONY: help venv format lint test run up up-dev down migrate coverage

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

venv: ## Create the uv-managed virtual environment and install deps
	uv venv .venv
	uv pip install -e ".[dev]" --python .venv/bin/python

format: ## Format code with ruff
	uv run --python .venv/bin/python ruff format app/ tests/
	uv run --python .venv/bin/python ruff check --fix app/ tests/

lint: ## Lint + type check
	uv run --python .venv/bin/python ruff check app/ tests/
	uv run --python .venv/bin/python ruff format --check app/ tests/
	uv run --python .venv/bin/python pyright app/

test: ## Run unit tests
	uv run --python .venv/bin/python pytest tests/ -v --tb=short

coverage: ## Run tests with coverage report
	uv run --python .venv/bin/python pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

run: ## Start the app locally (hot reload)
	uv run --python .venv/bin/python uvicorn app.main:app --reload --port 8000

up: ## Start production-like Docker stack
	docker-compose up --build -d

up-dev: ## Start dev Docker stack (volume mount + reload)
	docker-compose -f docker-compose.dev.yml up --build -d

down: ## Stop Docker stack
	docker-compose down

migrate: ## Run Alembic migrations
	.venv/bin/alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="add X")
	.venv/bin/alembic revision --autogenerate -m "$(msg)"