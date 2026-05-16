# Legal AI Assessment — Document Understanding, Grounded Drafting & Improvement-from-Edits

Internal workflow for Pearson Specter Litt that ingests messy legal-style documents, pulls usable information out of them, and turns that information into grounded draft outputs an operator can edit. The system learns from those edits and improves subsequent drafts. An admin dashboard wraps the pipeline so the operator never needs to drop to a terminal.

## What this repo is

This repository is the **planning and tracking artifact** for the take-home assessment. It contains:

- `README.md` — this file (project overview, deliverables, how to read the plan)
- `REQUIREMENTS.md` — verbatim assessment brief, the source-of-truth doc
- `PLAN.md` — architecture, approach, scope decisions, tradeoffs
- `tasks/` — Scrum sprint task cards, one per deliverable slice

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
  [5] Draft           ── Claude API, inline citations [DOC#:chunk]
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
| [TASK-001 Document Ingestion](tasks/TASK-001-document-ingestion.md) | 5 | To Do |
| [TASK-002 Structured Extraction](tasks/TASK-002-structured-extraction.md) | 3 | To Do |
| [TASK-003 Retrieval Layer](tasks/TASK-003-retrieval-layer.md) | 5 | To Do |
| [TASK-004 Draft Generation](tasks/TASK-004-draft-generation.md) | 3 | To Do |
| [TASK-005 Edit-Learning Loop](tasks/TASK-005-edit-learning-loop.md) | 5 | To Do |
| [TASK-006 Admin Dashboard](tasks/TASK-006-admin-dashboard.md) | 5 | To Do |
| [TASK-007 Evaluation, Quality & Submission](tasks/TASK-007-evaluation-quality-submission.md) | 3 | To Do |
| **Sprint total** | **29** | |

No single task exceeds 5 story points — anything heavier must be split before it enters the sprint.

For the brief→task coverage audit, see [`tasks/README.md` § Coverage matrix](tasks/README.md#coverage-matrix--brief--task).

## Deliverables (per assessment brief)

Required:
- source code
- README with setup and run instructions
- short architecture overview (`PLAN.md`)
- assumptions and tradeoffs writeup (`PLAN.md` § Tradeoffs)
- sample inputs and outputs (`samples/`, `outputs/` — added during sprint)
- evaluation approach and results (`eval/` — added during sprint)

In-scope additions:
- Admin dashboard (TASK-006)

Not committed in this sprint: API endpoints, Docker.

## Submission

- Public repo on GitHub
- Collaborators invited: `tsensei`, `abubakarsiddik31`
- Email to `talha@ideabuilders.studio` with repo link

## Getting started

Setup and run instructions are added to this README as TASK-001 lands and finalised in TASK-007. Until then, see `PLAN.md` for the intended runtime topology and `tasks/` for the work plan.
