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

**Evaluation consolidation.** Per-component evals from TASK-003 and TASK-005 already exist; add the missing draft-quality eval and roll everything into one `eval/RESULTS.md`:
- Grounding rate (cited claims / total claims) on 5 drafts.
- Retrieval precision@5 on the 10-query eval set.
- Edit-loop effectiveness — edit-distance between baseline draft and operator-edited draft, before vs. after the loop has seen the same edits twice.

**Code quality pass.** No new features; only:
- Module-level docstrings on every file under `app/`.
- Type hints on every public function.
- Error handling at module boundaries — no bare `except`, no swallowed tracebacks.
- A single `app/logging.py` configures structured logging used across the pipeline.
- `ruff` clean, `mypy` clean on `app/` (configuration committed; not on tests).

**Submission readiness.**
- README walked through on a fresh clone — every command in the setup section works.
- `tsensei` and `abubakarsiddik31` invited as collaborators on the repo.
- Draft submission email saved at `SUBMISSION_EMAIL.md` for the user to copy into Gmail (recipient `talha@ideabuilders.studio`, contains repo link + short intro slot).

## Acceptance criteria

- [ ] `eval/RESULTS.md` committed with all three metrics, methodology, and short narratives on failures.
- [ ] `ruff check app/` exits 0.
- [ ] `mypy app/` exits 0 (or with a pinned, explained ignore list ≤ 5 lines).
- [ ] Every file under `app/` has a module docstring describing what it does and what it depends on.
- [ ] Fresh-clone walkthrough: clone the repo on a clean machine, follow only the README, run `streamlit run app/dashboard.py`, see the sample corpus, generate a draft — works end-to-end.
- [ ] Both collaborators show as Pending or Accepted on the repo's collaborator settings page.
- [ ] `SUBMISSION_EMAIL.md` committed with the body filled in.

## Definition of Done

- [ ] `eval/RESULTS.md` merged.
- [ ] Lint + typecheck CI badges (or local commands documented in README) green.
- [ ] README setup section verified against a clean clone (Windows + macOS at minimum).
- [ ] Collaborator invites sent.
- [ ] `SUBMISSION_EMAIL.md` ready to copy-send.

## Technical notes

- Draft-quality eval doesn't need a benchmark dataset — five operator-graded drafts is enough. Grading rubric goes in `eval/draft_quality_rubric.md` and is referenced from `RESULTS.md`.
- Don't refactor in this task. If the quality pass surfaces a real bug, file it as a follow-up card; the sprint's job is to ship.
- The submission email body should be short (≤ 150 words): who you are, what you built, repo link, one sentence on the most interesting tradeoff.
- Run the fresh-clone walkthrough yourself before marking this Done — it's the single most common reason take-home submissions get downgraded.
