# TASK-007 — Evaluation, Code Quality Pass & Submission

| Field | Value |
|-------|-------|
| **Story points** | 3 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006 |

## User story

> As a reviewer, I want consolidated evaluation results, a tidy codebase, and a working setup walkthrough — so that I can judge the system on its merits in under 30 minutes without chasing missing pieces.

## Description

The closing task. Three buckets:

**Evaluation consolidation.** Per-component evals from TASK-003 and TASK-005 already exist; add the missing draft-quality eval and roll everything into one `eval/RESULTS.md`, following the methodology in [`eval/README.md`](../eval/README.md):
- Grounding rate (cited claims / total claims) on 5 drafts — target ≥ 0.95.
- Retrieval precision@5 on the held-out 10-query eval set — target ≥ 0.70.
- Edit-loop effectiveness — normalized edit distance between v2 and a reference edited draft, vs the same distance for v1, over ≥ 3 doc/edit pairs.
- Draft quality rubric per [`eval/draft_quality_rubric.md`](../eval/draft_quality_rubric.md) — five drafts scored on clarity & structure, factual support, and usefulness by two independent graders. Target ≥ 3.5 / 5 average.

**Code quality pass.** No new features; only:
- Module-level docstrings on every file under `app/`.
- Type hints on every public function.
- Error handling at module boundaries — no bare `except`, no swallowed tracebacks.
- A single `app/logging.py` configures structured logging used across the pipeline.
- `ruff` clean, `mypy` clean on `app/` (configuration committed; not on tests).

**Submission readiness.**
- **Review-mode artifacts committed**: `samples/processed/`, `outputs/draft_v1.md`, `outputs/draft_v1_edited.md`, `outputs/draft_v2.md`, and `app/learned_patterns.json` ship in the repo so a reviewer without an Anthropic API key (or without Tesseract/Poppler installed) can still inspect the full demo end-to-end via the dashboard.
- README walked through on a fresh clone — every command in the setup section works.
- `tsensei` and `abubakarsiddik31` invited as collaborators on the repo.
- Draft submission email at [`SUBMISSION_EMAIL.md`](../SUBMISSION_EMAIL.md) for the user to copy into Gmail (recipient `talha@ideabuilders.studio`, contains repo link + short intro slot).

## Acceptance criteria

- [ ] `eval/RESULTS.md` committed with numbers for all four metric axes (grounding, retrieval P@5, edit-loop, draft-quality rubric) plus short narratives on failures.
- [ ] `ruff check app/` exits 0.
- [ ] `mypy app/` exits 0 (or with a pinned, explained ignore list ≤ 5 lines).
- [ ] Every file under `app/` has a module docstring describing what it does and what it depends on.
- [ ] Fresh-clone walkthrough: clone the repo on a clean machine, follow only the README, run `streamlit run app/dashboard.py`, see the sample corpus, generate a draft — works end-to-end.
- [ ] Both collaborators show as Pending or Accepted on the repo's collaborator settings page.
- [ ] `SUBMISSION_EMAIL.md` committed with the body filled in.

## Definition of Done

- [ ] `eval/RESULTS.md` merged with numbers for all four metric axes.
- [ ] Minimum test coverage in `tests/`: `test_schemas.py` (DocumentFields round-trip), `test_citations.py` (valid / missing / malformed citation ID), `test_chunking.py` (boundary cases — short doc, overlap correctness), `test_pattern_dedup.py` (frequency increments instead of duplicating). All four green.
- [ ] Lint + typecheck CI badges (or local commands documented in README) green.
- [ ] README setup section verified against a clean clone (Windows + macOS at minimum).
- [ ] Review-mode artifacts committed and verified working on a fresh clone with no `ANTHROPIC_API_KEY` set.
- [ ] Collaborator invites sent to `tsensei` and `abubakarsiddik31`.
- [ ] `SUBMISSION_EMAIL.md` ready to copy-send.

## Technical notes

- Draft-quality eval doesn't need a benchmark dataset — five operator-graded drafts is enough. Grading rubric goes in `eval/draft_quality_rubric.md` and is referenced from `RESULTS.md`.
- Don't refactor in this task. If the quality pass surfaces a real bug, file it as a follow-up card; the sprint's job is to ship.
- The submission email body should be short (≤ 150 words): who you are, what you built, repo link, one sentence on the most interesting tradeoff.
- Run the fresh-clone walkthrough yourself before marking this Done — it's the single most common reason take-home submissions get downgraded.
