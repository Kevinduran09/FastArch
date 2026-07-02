.PHONY: help setup setup-dev clean run test lint format check-python

PYTHON := $(shell command -v python3.14 || command -v python3.12 || command -v python3.11 || command -v python3.10 || echo python3)
VENV := .venv
BIN := $(VENV)/bin
PYTHON_VENV := $(BIN)/python
PIP := $(PYTHON_VENV) -m pip

help:
	@echo "FastArch Development Commands"
	@echo "=============================="
	@echo "make setup          → Create venv and install dependencies"
	@echo "make setup-dev      → setup + dev dependencies (tests, formatting)"
	@echo "make run            → Start FastAPI server on localhost:8000"
	@echo "make test           → Run pytest"
	@echo "make test-watch     → Run tests in watch mode"
	@echo "make lint           → Run code quality checks"
	@echo "make format         → Auto-format code"
	@echo "make clean          → Remove venv and cache files"
	@echo ""
	@echo "Using Python: $(PYTHON)"

check-python:
	@if [ "$(PYTHON)" = "python3" ]; then \
		echo "⚠️  Warning: Using system python3, might be < 3.10"; \
		echo "Consider: brew install python@3.14"; \
	fi

setup: check-python
	@echo "🔧 Creating virtual environment with $(PYTHON)..."
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PIP) install uvicorn[standard]
	@echo "✅ Setup complete! Run 'make run' to start the server"

setup-dev: setup
	@echo "🔧 Installing dev dependencies..."
	$(PIP) install -e ".[test]"
	$(PIP) install black ruff
	@echo "✅ Dev setup complete!"

run:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first"; \
		exit 1; \
	fi
	@echo "🚀 Starting FastAPI server on http://localhost:8000"
	$(PYTHON_VENV) -m uvicorn examples.fastapi_backend.app:app --reload --port 8000

test:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup-dev' first"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -m pytest -v

test-watch:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup-dev' first"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -m pytest -v --tb=short -x

lint:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup-dev' first"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -m ruff check fastarch tests examples
	$(PYTHON_VENV) -m ruff format --check fastarch tests examples

format:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup-dev' first"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -m ruff format fastarch tests examples
	$(PYTHON_VENV) -m ruff check --fix fastarch tests examples

clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned up"
