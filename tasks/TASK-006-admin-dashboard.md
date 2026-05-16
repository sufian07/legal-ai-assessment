# TASK-006 — Admin Dashboard

| Field | Value |
|-------|-------|
| **Story points** | 5 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005 |

## User story

> As an operator, I want a single web dashboard where I can browse ingested documents, inspect retrieval, generate drafts, edit them inline, and watch the system learn from my edits — so that I can drive the whole pipeline without juggling CLI commands.

## Description

A Streamlit-based admin dashboard that wraps every stage of the pipeline. The dashboard is the operator's primary surface; the CLIs from earlier tasks remain available for headless use.

Five views, accessible from a left sidebar:

1. **Documents** — table of ingested docs with per-page extraction confidence; expandable rows show the manifest and the extracted `fields.json`.
2. **Retrieval Playground** — text input → top-k chunks with score, doc, page, and highlighted excerpt. Lets the reviewer sanity-check grounding without running a draft.
3. **Draft Workspace** — pick a corpus, click "Generate Draft", get the markdown back with inline citations. Edit in a Monaco-style markdown editor. "Save edits" triggers the learning loop and shows which patterns were extracted.
4. **Learned Patterns** — table of rules in `learned_patterns.json` with type, frequency, confidence, before/after examples. Each row has a "Forget" button that calls the same logic as `app.edits forget`.
5. **Stats** — three small charts: grounding rate per draft, retrieval P@5 over time, edit-distance reduction (v1 vs v2) across sessions. Pulls from `eval/` artifacts.

Styling: custom dark theme (not stock Streamlit), legible typography, no orange error banners — all errors caught and rendered as inline warnings.

## Acceptance criteria

- [ ] `streamlit run app/dashboard.py` boots the app on first try with no missing-dependency errors.
- [ ] All five views are reachable from the sidebar and render without exceptions on the sample corpus.
- [ ] Generating a draft from the dashboard produces the same output as `python -m app.draft` (same prompts, same model, same result for identical input).
- [ ] Editing a draft in the workspace and clicking "Save edits" produces a diff that appears in TASK-005's learning store; the **Learned Patterns** view refreshes to show the new patterns within one page reload.
- [ ] "Forget" on a pattern row removes it from `learned_patterns.json`.
- [ ] Custom theme is applied via `.streamlit/config.toml` — no default Streamlit blue.
- [ ] Every long-running action (ingest, embed, generate, learn) shows a spinner and never freezes the UI.

## Definition of Done

- [ ] Code merged in `app/dashboard.py` (entrypoint) and `app/dashboard_views/` (one module per view).
- [ ] `.streamlit/config.toml` committed with the custom theme.
- [ ] `requirements.txt` includes `streamlit`, `plotly`, and the markdown editor component.
- [ ] README has a "Run the dashboard" section with screenshots committed under `docs/screenshots/`.
- [ ] Smoke test: scripted launch + screenshot via `playwright` lives under `tests/test_dashboard_smoke.py` (skipped in CI but documented in the test file).

## Technical notes

- Don't re-implement business logic in the dashboard — every view calls the same functions as the CLIs (`ingest()`, `retrieve()`, `draft()`, `capture_edits()`, `load_patterns()`). The dashboard is a presentation layer, not a parallel pipeline.
- Use `st.session_state` for cross-view state (selected corpus, current draft); never re-run heavy work on every Streamlit rerender. Cache embedding loads with `@st.cache_resource`.
- For the markdown editor, prefer `streamlit-ace` (lightweight) over heavier Monaco wrappers — the dashboard already shoulders enough dependencies.
- The Stats view reads from disk artifacts written by TASK-007's eval scripts — keep the read path tolerant of missing files (empty chart, "run evaluation first" hint), not crashes.
- Keep the dashboard runnable without an Anthropic API key — fall back to displaying previously generated drafts when generation is unavailable. The brief says reviewers may not run end-to-end.
