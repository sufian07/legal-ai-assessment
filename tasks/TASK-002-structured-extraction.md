# TASK-002 — Structured Extraction

| Field | Value |
|-------|-------|
| **Story points** | 3 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-001 |

## User story

> As a drafting system, I want each ingested document tagged with structured fields (parties, dates, document type, monetary amounts, claims, obligations, outstanding items), so that the draft generator can fill those slots without re-reading raw text.

## Description

Take the cleaned text from TASK-001 and emit a structured `fields.json` per document.

Three-step approach:

1. **Format normalize** — collapse whitespace, unify date strings to ISO-where-confident, normalize bullet markers (`•`, `-`, `*` → all `-`), strip repeated page headers/footers. Pure-Python, deterministic. Directly addresses the brief's "inconsistently formatted files" input regime.
2. **Deterministic field pre-pass** — regex / `dateutil` pulls of obvious patterns (ISO + common date formats, currency, case numbers, postal addresses) on the normalized text. Cheap, no LLM cost, no hallucination surface.
3. **LLM pass** — Claude (temperature 0) prompted with the normalized text and the pre-pass results, asked to produce the full schema. Schema-constrained output (Pydantic + retry-on-validation-fail).

Pre-pass results are passed in so the LLM can correct them, not duplicate them. Determinism: every call in this stage runs at `temperature=0`.

## Acceptance criteria

- [ ] `python -m app.extract processed/<doc_id>.text.md` writes `processed/<doc_id>.fields.json` validated against `app/schemas.py:DocumentFields`.
- [ ] Every field in the schema is present, even if empty (`[]` or `null`).
- [ ] Output includes a `provenance` map: for each non-empty field, which page(s) it came from.
- [ ] When the LLM returns malformed JSON, the extractor retries up to 2× with corrective feedback before failing.
- [ ] Running on all 4 sample documents produces 4 valid `fields.json` files in under 60s total.

## Definition of Done

- [ ] Code merged in `app/extract.py` (LLM pass) and `app/normalize.py` (deterministic formatting normalization, reusable from other stages).
- [ ] `app/schemas.py:DocumentFields` defined as a Pydantic model and imported by both extract and downstream draft stages.
- [ ] A short prompt template lives in `app/prompts/extract.md` so it's editable without touching Python.
- [ ] Sample `fields.json` for each of the 4 raw samples committed under `samples/processed/`.
- [ ] README "What the system extracts" section lists the schema fields.

## Technical notes

- Keep the LLM prompt under ~2k tokens; truncate the text to the most field-dense pages if needed (long contracts shouldn't blow context every time).
- Use `response_model` with the Anthropic SDK if available, else parse + validate manually.
- The `provenance` map is what makes extracted output trustable downstream — don't skip it to save time.
