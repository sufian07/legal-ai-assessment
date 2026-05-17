# Legal AI Assessment — Document Understanding, Grounded Drafting & Improvement-from-Edits

Internal workflow for Pearson Specter Litt that ingests messy legal-style documents, pulls usable information out of them, and turns that information into grounded draft outputs an operator can edit. The system learns from those edits and improves subsequent drafts. An admin dashboard wraps the pipeline so the operator never needs to drop to a terminal.

## What this repo is

This repository is the **planning and tracking artifact** for the take-home assessment. It contains:

- [`README.md`](README.md) — this file (project overview, deliverables)
- [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) — **start here if you only have 60 seconds**
- [`REQUIREMENTS.md`](REQUIREMENTS.md) — verbatim assessment brief, the source-of-truth doc
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — concise architecture overview (required deliverable)
- [`ASSUMPTIONS.md`](ASSUMPTIONS.md) — assumptions, tradeoffs, risks (required deliverable)
- [`SUBMISSION_EMAIL.md`](SUBMISSION_EMAIL.md) — pre-drafted email body for `talha@ideabuilders.studio`
- [`tasks/`](tasks/) — Scrum sprint task cards, one per deliverable slice
- [`samples/`](samples/) — synthetic input documents + pre-computed processed outputs (review mode)
- [`eval/`](eval/) — evaluation methodology and (post-sprint) measured results

Code is added incrementally as each task in `tasks/` moves to **Done**.

## Chosen draft output

**Case Fact Summary** — a first-pass internal memo extracting parties, dates, facts, and outstanding issues from the source documents. Broad enough to apply across notice, title-review, and contract-style inputs; narrow enough to evaluate grounding rigorously.

## High-level pipeline

```
  raw docs (PDF / image / scan)
        │
        ▼
  [1] Ingest          ── pdfplumber + pytesseract fallback
        │
        ▼
  [2] Extract         ── structured fields (parties, dates, claims)
        │
        ▼
  [3] Chunk + Embed   ── sentence-transformers → Chroma
        │
        ▼
  [4] Retrieve        ── top-k passages with citation IDs
        │
        ▼
  [5] Draft           ── Claude API, inline citations [doc_id:chunk_id]
        │
        ▼
  [6] Operator edits  ── diff captured, patterns extracted
        │
        ▼
  [7] Learn           ── patterns stored, fed back as rules + few-shot

  All seven stages are surfaced in the Admin Dashboard (Streamlit).
```

Steps 1–5 produce the baseline draft. Steps 6–7 close the improvement loop. The dashboard (TASK-006) is the operator's UI over the whole pipeline.

## Sprint at a glance

| Task | Points | Status |
|------|-------:|--------|
| [TASK-000 Project Setup & Scaffolding](tasks/TASK-000-project-setup.md) | 3 | **Done** |
| [TASK-001 Document Ingestion](tasks/TASK-001-document-ingestion.md) | 5 | **Done** |
| [TASK-002 Structured Extraction](tasks/TASK-002-structured-extraction.md) | 3 | To Do |
| [TASK-003 Retrieval Layer](tasks/TASK-003-retrieval-layer.md) | 5 | To Do |
| [TASK-004 Draft Generation](tasks/TASK-004-draft-generation.md) | 3 | To Do |
| [TASK-005 Edit-Learning Loop](tasks/TASK-005-edit-learning-loop.md) | 5 | To Do |
| [TASK-006 Admin Dashboard](tasks/TASK-006-admin-dashboard.md) | 5 | To Do |
| [TASK-007 Evaluation, Quality & Submission](tasks/TASK-007-evaluation-quality-submission.md) | 3 | To Do |
| **Sprint total** | **32** | |

No single task exceeds 5 story points — anything heavier must be split before it enters the sprint.

For the brief→task coverage audit, see [`tasks/README.md` § Coverage matrix](tasks/README.md#coverage-matrix--brief--task--doc).

## Deliverables (per assessment brief)

Required:
- source code — `app/` (produced by TASK-001 → TASK-006)
- README with setup and run instructions — this file, finalised in TASK-007
- short architecture overview — [`ARCHITECTURE.md`](ARCHITECTURE.md)
- assumptions and tradeoffs writeup — [`ASSUMPTIONS.md`](ASSUMPTIONS.md)
- sample inputs and outputs — [`samples/`](samples/) (inventory committed; files land in TASK-001/002/004/005)
- evaluation approach and results — [`eval/README.md`](eval/README.md) (approach committed; `eval/RESULTS.md` lands in TASK-007)

In-scope additions:
- Admin dashboard (TASK-006)

Not committed in this sprint: API endpoints, Docker.

## Submission

- Public repo on GitHub
- Collaborators invited: `tsensei`, `abubakarsiddik31`
- Email to `talha@ideabuilders.studio` with repo link

## Setup

### Prerequisites

- Python 3.11+
- *(For OCR on scanned PDFs)* **Tesseract OCR** — [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki) · macOS: `brew install tesseract`
- *(For scanned PDFs)* **Poppler** — Windows: [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases), add `bin/` to PATH · macOS: `brew install poppler`
- *(For handwriting)* **TrOCR weights** download automatically on first ingest (~330 MB, cached under `.models/`).

### Install

```bash
git clone https://github.com/sufian07/legal-ai-assessment
cd legal-ai-assessment
make install
cp .env.example .env   # fill in ANTHROPIC_API_KEY (optional — see review mode below)
```

**Windows without `make`** — Git Bash or GNU Make on PATH is the easy path. If you don't have either, run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
copy .env.example .env
```

### Verify

```bash
make lint        # ruff check app/
make typecheck   # mypy app/
make test        # pytest
```

### Run

```bash
make dashboard   # launches Streamlit on http://localhost:8501
```

Or via CLI:

```bash
python -m app.ingest samples/raw/
python -m app.extract samples/processed/
python -m app.retrieval index samples/processed/
python -m app.draft default --out outputs/draft_v1.md
```

### Review mode — no API key required

The repo ships pre-computed `samples/processed/` and `outputs/` artifacts. The dashboard renders them without calling any LLM. See [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) for the no-key walkthrough.
