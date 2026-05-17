.PHONY: help install lint typecheck test dashboard ingest extract draft clean

PY := python
VENV := .venv
ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV)/Scripts
else
	VENV_BIN := $(VENV)/bin
endif

help:
	@echo "Targets:"
	@echo "  install     Create venv and install runtime + dev dependencies"
	@echo "  lint        Run ruff check on app/"
	@echo "  typecheck   Run mypy on app/"
	@echo "  test        Run pytest"
	@echo "  dashboard   Launch the Streamlit admin dashboard"
	@echo "  ingest      Process files in samples/raw/   (override: DIR=path)"
	@echo "  extract     Run structured extraction       (override: FILE=path)"
	@echo "  draft       Generate a Case Fact Summary    (override: CORPUS=name)"
	@echo "  clean       Remove caches and generated artifacts"

install:
	$(PY) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt
	$(VENV_BIN)/pip install -r requirements-dev.txt
	$(VENV_BIN)/pip install -e .
	@echo "Setup complete. Next: cp .env.example .env, fill in ANTHROPIC_API_KEY, then 'make dashboard'."

lint:
	$(VENV_BIN)/ruff check app/

typecheck:
	$(VENV_BIN)/mypy app/

test:
	$(VENV_BIN)/pytest

dashboard:
	$(VENV_BIN)/streamlit run app/dashboard.py

ingest:
	$(VENV_BIN)/python -m app.ingest $(or $(DIR),samples/raw/)

extract:
	$(VENV_BIN)/python -m app.extract $(or $(FILE),samples/processed/)

draft:
	$(VENV_BIN)/python -m app.draft $(or $(CORPUS),default) --out outputs/draft_v1.md

clean:
	rm -rf $(VENV) __pycache__ */__pycache__ */**/__pycache__ \
		.chroma .mypy_cache .ruff_cache .pytest_cache build dist *.egg-info
