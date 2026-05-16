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

## Coverage matrix — brief → task

Each rubric item maps to at least one task; this is the audit reviewers see before approving the sprint.

| Brief / Rubric item | Points (rubric) | Covered by |
|---------------------|----------------:|------------|
| Document Processing — OCR, messy inputs, structured outputs | 25 | TASK-001, TASK-002 |
| Retrieval & Grounding — relevance, inspectable evidence | 25 | TASK-003, TASK-004 (citation validator) |
| Draft Quality — clarity, structure, source consistency | 10 | TASK-004 |
| Improvement from Edits — capture, learn, apply | 25 | TASK-005 |
| Code Quality & System Design | 10 | All tasks (DoD); final pass in TASK-007 |
| Documentation & Clarity | 5 | All tasks (DoD); polish in TASK-007 |
| Sample inputs / outputs (required deliverable) | — | TASK-001, TASK-002, TASK-004, TASK-005 |
| Evaluation approach & results (required deliverable) | — | TASK-003, TASK-005, consolidated in TASK-007 |
| Admin UI to assist the operator (in-scope addition) | — | TASK-006 |
| Submission ceremony (collaborator invites, email) | — | TASK-007 |

No rubric item is uncovered.

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
