# Sprint Tasks

Scrum sprint backlog for the Legal AI assessment. One task card per deliverable slice. **No task exceeds 5 story points** — anything heavier gets split before it enters the sprint.

## Story-point scale (Fibonacci)

| Points | Meaning |
|------:|---------|
| 1 | Trivial — ~1 hour of focused work, no unknowns. |
| 2 | Small — half-day, well-understood. |
| 3 | Medium — one focused day, minor unknowns. |
| 5 | Large — two days, several unknowns or coordination cost. Cap. |
| 8+ | Too big — split it. |

## Backlog

| ID | Title | Points | Status | Owner |
|----|-------|-------:|--------|-------|
| TASK-001 | [Document Ingestion](TASK-001-document-ingestion.md) | 5 | To Do | — |
| TASK-002 | [Structured Extraction](TASK-002-structured-extraction.md) | 3 | To Do | — |
| TASK-003 | [Retrieval Layer](TASK-003-retrieval-layer.md) | 5 | To Do | — |
| TASK-004 | [Draft Generation](TASK-004-draft-generation.md) | 3 | To Do | — |
| TASK-005 | [Edit-Learning Loop](TASK-005-edit-learning-loop.md) | 5 | To Do | — |
| TASK-006 | [Admin Dashboard](TASK-006-admin-dashboard.md) | 5 | To Do | — |
| TASK-007 | [Evaluation, Quality & Submission](TASK-007-evaluation-quality-submission.md) | 3 | To Do | — |
| | **Total** | **29** | | |

## Coverage matrix — brief → task / doc

Every rubric item and every required deliverable maps to at least one task or committed doc.

### Rubric items

| Rubric item | Points | Covered by |
|-------------|-------:|------------|
| Document Processing | 25 | TASK-001 (ingest + TrOCR handwriting route), TASK-002 (normalize + structured extraction) |
| Retrieval & Grounding | 25 | TASK-003 (confidence-aware ranking, stale-chunk eviction, hygiene), TASK-004 (citation validator) |
| Draft Quality | 10 | TASK-004 |
| Improvement from Edits | 25 | TASK-005 (schema-versioned pattern store, frequency-gated promotion) |
| Code Quality & System Design | 10 | All tasks' DoD; final pass in TASK-007 (lint, typecheck, structured logging, scalability documented in ARCHITECTURE.md) |
| Documentation & Clarity | 5 | All tasks' DoD; reviewer-experience polish in TASK-007 |

### Required submission deliverables (per `REQUIREMENTS.md`)

| Deliverable | Where it lives |
|-------------|----------------|
| Source code | `app/` — produced by TASK-001 → TASK-006 |
| README with setup & run instructions | [`../README.md`](../README.md) — finalised in TASK-007 |
| Short architecture overview | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) ✓ committed |
| Assumptions & tradeoffs writeup | [`../ASSUMPTIONS.md`](../ASSUMPTIONS.md) ✓ committed |
| Sample inputs & outputs | [`../samples/`](../samples/) inventory ✓ committed; files land in TASK-001/002/004/005 |
| Evaluation approach | [`../eval/README.md`](../eval/README.md) ✓ committed |
| Evaluation results | `../eval/RESULTS.md` — lands in TASK-007 |

### Optional deliverables

| Deliverable | Status |
|-------------|--------|
| API endpoints | Out of scope (PLAN deliberately omits — see ASSUMPTIONS) |
| Simple UI | **In scope as Admin Dashboard** — TASK-006 |
| Tests | Minimum set in TASK-007 DoD |
| Docker | Out of scope |

### Submission ceremony

| Item | Where |
|------|-------|
| GitHub repo (public) | `https://github.com/sufian07/legal-ai-assessment` ✓ live |
| Invite `tsensei`, `abubakarsiddik31` | TASK-007 |
| Email `talha@ideabuilders.studio` | [`../SUBMISSION_EMAIL.md`](../SUBMISSION_EMAIL.md) ✓ drafted |

No rubric item is uncovered. No required deliverable is missing.

## Card format

Each task card has:

- **Story points** (Fibonacci, ≤5)
- **Sprint** — which sprint it belongs to
- **Status** — To Do / In Progress / In Review / Done
- **User story** — "As a … I want … so that …"
- **Description** — what's being built
- **Acceptance criteria** — observable, testable
- **Definition of Done** — code merged, docs updated, sample input/output committed, etc.
- **Dependencies** — upstream tasks
- **Technical notes** — implementation hints, not prescriptions

## Working agreement

- A task moves to **In Review** only when acceptance criteria are demonstrable on a fresh clone.
- A task moves to **Done** only when the DoD checklist is complete.
- If a task grows past 5 points mid-sprint, it gets split — don't quietly carry a 5-point card that's secretly an 8.
