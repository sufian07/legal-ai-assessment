# TASK-000 — Project Setup & Scaffolding

| Field | Value |
|-------|-------|
| **Story points** | 3 |
| **Sprint** | Sprint 1 |
| **Status** | Done |
| **Owner** | — |
| **Depends on** | — |

## User story

> As a developer joining the project, I want `make install` to take me from a fresh clone to a working dev environment in five minutes, so I can start TASK-001 without yak-shaving.

## Description

Lay down the project scaffold every other task depends on. No business logic — just the bones. Without this card, every downstream task has to invent its own setup, and TASK-001's first day evaporates on tooling.

Deliverables:

- **`pyproject.toml`** — Python 3.11+ project, setuptools build backend, project metadata, classifiers.
- **`requirements.txt`** + **`requirements-dev.txt`** — runtime vs. dev deps (lint, typecheck, test). Pin versions.
- **`.env.example`** — every env var the system reads (`ANTHROPIC_API_KEY`, `OCR_CONFIDENCE_FLOOR`, `EMBEDDING_MODEL`, `LOG_LEVEL`, `ANTHROPIC_MODEL`, etc.), each with a one-line comment.
- **`app/__init__.py`** — package marker.
- **`app/config.py`** — `pydantic-settings`-based settings, auto-loads from `.env`, validates types. Single import surface for any tunable.
- **`app/logging.py`** — structured JSON logger via `app.logging.get_logger(__name__)`. Used across the pipeline.
- **`app/usage_log.py`** — append-only `usage_log.jsonl` writer (token counts, wall-clock per LLM call). Dashboard Stats view reads from it.
- **`.ruff.toml`** + **`mypy.ini`** — lint + typecheck configuration.
- **`.editorconfig`** — consistent indentation across editors.
- **`Makefile`** — `install`, `lint`, `typecheck`, `test`, `dashboard`, `ingest`, `extract`, `draft`, `clean`. Cross-platform via Git Bash on Windows; PowerShell users get the equivalent `python -m` commands inline in the README.
- **README setup section** — first draft: Python version, venv creation, install, env vars, Tesseract/Poppler/TrOCR install per OS. TASK-007 verifies it on a fresh clone.
- **`.gitignore` extension** — `.venv/`, `__pycache__/`, `.env`, `.chroma/`, `.models/`, transient artifacts.

## Acceptance criteria

- [ ] `make install` on a fresh clone creates a venv, installs runtime + dev deps, prints a one-line success message. Five steps or fewer end-to-end (including the `cp .env.example .env` step).
- [ ] `make lint` runs `ruff check app/` and exits 0 on the empty scaffold.
- [ ] `make typecheck` runs `mypy app/` and exits 0.
- [ ] `python -c "from app.config import settings; print(settings.log_level)"` prints the configured log level without raising.
- [ ] `python -c "from app.logging import get_logger; get_logger('test').info('hi')"` emits a single structured JSON log line on stderr.
- [ ] `python -c "from app.usage_log import record; record('test', tokens_in=10, tokens_out=5, latency_ms=42)"` appends one JSONL line to `usage_log.jsonl`.
- [ ] `.env.example` lists every env var the system will read; no env var is read in code that isn't documented here.

## Definition of Done

- [ ] All files committed under appropriate paths.
- [ ] README setup section walks fresh-clone-to-`make install` in five steps or fewer.
- [ ] `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `Makefile`, `.env.example`, `.ruff.toml`, `mypy.ini`, `.editorconfig` all committed.
- [ ] `app/__init__.py`, `app/config.py`, `app/logging.py`, `app/usage_log.py` exist with module docstrings.
- [ ] `make lint` and `make typecheck` both exit 0.

## Technical notes

- Use `pydantic-settings` for `app/config.py`. Auto-loads from `.env`, validates types, single source of truth for every tunable. Don't sprinkle `os.environ.get` across the codebase.
- Structured logs go to stderr by default; JSON format. Every module gets a named logger via `get_logger(__name__)` — no per-module `logging.basicConfig` calls.
- `Makefile` works on Windows via Git Bash. For native PowerShell, document the equivalent `python -m` commands inline in the README. Don't fight Windows.
- Don't pre-install TrOCR weights here — TASK-001 owns the first-run download with HuggingFace cache.
- The `usage_log.jsonl` writer must be threadsafe-by-process (append-only line writes); don't bother with cross-process locking — the dashboard reads it but doesn't write.
