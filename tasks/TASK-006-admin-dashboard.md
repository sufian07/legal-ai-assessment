# TASK-006 — Admin Dashboard

| Field | Value |
|-------|-------|
| **Story points** | 5 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-000, TASK-001, TASK-002, TASK-003, TASK-004, TASK-005 |

## User story

> As an operator, I want a single web dashboard where I can browse ingested documents, inspect retrieval, generate drafts, edit them inline, and watch the system learn from my edits — so that I can drive the whole pipeline without juggling CLI commands.

## Description

A Streamlit-based admin dashboard that wraps every stage of the pipeline. The dashboard is the operator's primary surface; the CLIs from earlier tasks remain available for headless use.

Five views, accessible from a left sidebar:

1. **Documents** — table of ingested docs with per-page extraction confidence; expandable rows show the manifest and the extracted `fields.json`.
2. **Retrieval Playground** — text input → top-k chunks with score, doc, page, and highlighted excerpt. Lets the reviewer sanity-check grounding without running a draft.
3. **Draft Workspace** — pick a corpus, click "Generate Draft", get the markdown back with inline citations. Edit in a Monaco-style markdown editor. "Save edits" triggers the learning loop and shows which patterns were extracted.
4. **Learned Patterns** — table of rules in `learned_patterns.json` with type, frequency, confidence, before/after examples. Each row has a "Forget" button that calls the same logic as `app.edits forget`.
5. **Stats** — small charts: grounding rate per draft, retrieval P@5 over time, edit-distance reduction (v1 vs v2) across sessions, **per-run token cost and end-to-end latency**. Pulls from `eval/` artifacts plus a lightweight `app/usage_log.jsonl` written by every pipeline call.

## Visual design

A genuinely polished dashboard, not stock Streamlit. Every bullet below is testable.

- **Color palette** — dark navy base (`#0B1220`), accent blue (`#3B82F6`), warning amber (`#F59E0B`), success green (`#10B981`), text on a Slate gray scale. Defined once in `.streamlit/config.toml` and `app/dashboard_theme.py` so charts and custom components share it.
- **Typography** — Inter for UI, JetBrains Mono for code, citations, and chunk IDs. Loaded via Google Fonts.
- **Layout** — persistent left sidebar with active-view highlight, breadcrumb in the main content area, sticky action bar in Draft Workspace (Generate / Save Edits / Clear).
- **Charts** — Plotly throughout, themed to the palette via `app/dashboard_theme.py:PLOTLY_TEMPLATE`. Zero stock Plotly defaults.
- **Documents view** — tile/card layout (via `streamlit-extras` `card` or hand-rolled HTML), not a stock dataframe. Each card surfaces: doc name, ingest engine, confidence sparkline, click-to-expand manifest.
- **Draft Workspace** — three-pane layout. Left: markdown editor (`streamlit-ace`). Middle: live citation-resolved preview. Right: **Source** panel that highlights the cited chunk when an inline `[doc_id:chunk_id]` is clicked in the preview.
- **Empty states** — every view renders a friendly empty state when there's no data, with a one-line next action ("Drop a PDF in `samples/raw/` and run `python -m app.ingest`").
- **Loading states** — `st.empty()` skeletons during ingest, embed, generate, learn. The UI never freezes.
- **Toast notifications** — `streamlit-extras` toasts for Save, Learn, Forget events. No alert dialogs.
- **Branding** — Pearson Specter Litt text-based logo placeholder in the sidebar header (we don't have rights to firm assets). Favicon set.
- **Error UX** — no orange Streamlit error banners. Every exception caught and rendered as an `st.error` card with cause + suggested fix.

## Acceptance criteria

- [ ] `streamlit run app/dashboard.py` boots the app on first try with no missing-dependency errors.
- [ ] All five views are reachable from the sidebar and render without exceptions on the sample corpus.
- [ ] Generating a draft from the dashboard produces the same output as `python -m app.draft` (same prompts, same model, same result for identical input).
- [ ] Editing a draft in the workspace and clicking "Save edits" produces a diff that appears in TASK-005's learning store; the **Learned Patterns** view refreshes to show the new patterns within one page reload.
- [ ] "Forget" on a pattern row removes it from `learned_patterns.json`.
- [ ] Custom theme is applied via `.streamlit/config.toml` AND `app/dashboard_theme.py` — palette hex codes match the Visual Design spec; no default Streamlit blue anywhere.
- [ ] Plotly chart theme matches the palette via `PLOTLY_TEMPLATE` — no stock Plotly defaults.
- [ ] Documents view uses a tile/card layout, not a stock dataframe.
- [ ] Draft Workspace renders the three-pane layout (editor | preview | source). Clicking an inline citation in the preview highlights the source chunk in the right panel.
- [ ] Empty states render in all five views when there's no data, each with a one-line next-action hint.
- [ ] Five screenshots committed under `docs/screenshots/` (one per view) and linked from the README.
- [ ] Every long-running action (ingest, embed, generate, learn) shows a spinner and never freezes the UI.

## Definition of Done

- [ ] Code merged in `app/dashboard.py` (entrypoint) and `app/dashboard_views/` (one module per view).
- [ ] `.streamlit/config.toml` committed with the custom theme.
- [ ] `requirements.txt` includes `streamlit`, `streamlit-extras`, `streamlit-ace`, `plotly`, and the markdown preview library.
- [ ] `app/dashboard_theme.py` defines the shared color palette + Plotly template, imported by every view module.
- [ ] Five screenshots committed: `docs/screenshots/documents.png`, `retrieval.png`, `draft.png`, `patterns.png`, `stats.png`.
- [ ] README has a "Run the dashboard" section with screenshots committed under `docs/screenshots/`.
- [ ] Smoke test: scripted launch + screenshot via `playwright` lives under `tests/test_dashboard_smoke.py` (skipped in CI but documented in the test file).

## Technical notes

- Don't re-implement business logic in the dashboard — every view calls the same functions as the CLIs (`ingest()`, `retrieve()`, `draft()`, `capture_edits()`, `load_patterns()`). The dashboard is a presentation layer, not a parallel pipeline.
- Use `st.session_state` for cross-view state (selected corpus, current draft); never re-run heavy work on every Streamlit rerender. Cache embedding loads with `@st.cache_resource`.
- For the markdown editor, prefer `streamlit-ace` (lightweight) over heavier Monaco wrappers — the dashboard already shoulders enough dependencies.
- The Stats view reads from disk artifacts written by TASK-007's eval scripts — keep the read path tolerant of missing files (empty chart, "run evaluation first" hint), not crashes.
- Keep the dashboard runnable without an Anthropic API key — fall back to displaying previously generated drafts when generation is unavailable. The brief says reviewers may not run end-to-end.
