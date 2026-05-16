# Architecture

Concise architecture overview. Assumptions and tradeoffs live in [ASSUMPTIONS.md](ASSUMPTIONS.md). Sprint plan in [`tasks/`](tasks/).

## System diagram

```
  raw docs (PDF / image / scan / handwritten)
        │
        ▼
  [1] Ingest          ── pdfplumber │ pytesseract │ TrOCR
        │                            (per-page confidence emitted)
        ▼
  [2] Extract         ── regex pre-pass → format normalize → LLM (Claude, T=0)
        │                            (schema-constrained, provenance per field)
        ▼
  [3] Chunk + Embed   ── sentence-boundary, 500-token windows, 80-token overlap
        │                            (stable IDs: doc_id:p{page}:c{ordinal})
        ▼
  [4] Retrieve        ── MiniLM-L6-v2 → Chroma, confidence-aware ranking
        │                            (low-conf chunks downweighted 0.7×)
        ▼
  [5] Draft           ── section-by-section, Claude T=0, inline [doc_id:chunk_id]
        │                            (post-gen citation validator → rewrite or hedge)
        ▼
  [6] Operator edits  ── unified diff captured
        │
        ▼
  [7] Learn           ── LLM classifies hunks → patterns store (schema-versioned)
        │                            (frequency-gated promotion: low/medium/high)
        │
        └─── rules + few-shot examples + skeleton seed → next draft

  All seven stages surfaced in the Admin Dashboard (Streamlit, 5 views).
```

## Components

### 1. Ingest (`app/ingest.py`)
- `pdfplumber` for text-bearing PDFs.
- `pdf2image + pytesseract` for image-based PDFs (printed text).
- `microsoft/trocr-base-handwritten` (HuggingFace) for handwriting.
- `PIL` for standalone images.
- Emits per document: extracted text (with page markers) + manifest JSON (`per_page_confidence`, `ocr_engine`, `warnings`).

### 2. Structured Extraction (`app/extract.py`)
- Regex pre-pass for dates, currency, case numbers — cheap, no hallucination surface.
- Format normalization: collapse whitespace, unify date strings, normalize bullets.
- LLM (Claude, temperature 0) field pull, schema-constrained via `app/schemas.py:DocumentFields` (Pydantic).
- Provenance map: every non-empty field tagged with source page(s).

### 3. Chunking & Embeddings (`app/chunking.py` + `app/retrieval.py`)
- Sentence-boundary splits via `nltk.sent_tokenize`.
- 500-token windows, 80-token overlap.
- Chunk IDs deterministic: `{doc_id}:p{page}:c{ordinal}` — citations stay human-debuggable.
- Embedding: `sentence-transformers/all-MiniLM-L6-v2` on CPU.
- Store: ChromaDB persistent collection at `./.chroma/`.

### 4. Retrieval (`app/retrieval.py`)
- `retrieve(query, k=8) → list[Chunk]`.
- Confidence-aware: chunks inheriting low-confidence page metadata downweighted by configurable penalty (default 0.7×).
- Stale chunk eviction: re-indexing a doc removes Chroma entries whose `chunk_id` is no longer present in the new chunk set.
- Inspection CLI: `python -m app.retrieval inspect "<query>"` for offline grounding debug.

### 5. Draft Generation (`app/draft.py`)
- Section-by-section drafting: each section issues its own retrieval query.
- Inline citations in format `[doc_id:chunk_id]`. **Single citation format across the codebase.**
- Post-generation citation validator (`app/citations.py`): unresolved IDs trigger one rewrite attempt, then a hard hedge ("source unclear").
- Empty retrieval → section says "No supporting evidence found in the provided documents" rather than fabricating.
- Final **Evidence** section lists every cited chunk with `doc_id`, page, snippet — this is what makes grounding inspectable.

### 6. Edit Capture (`app/edits.py`)
- Operator saves edited markdown alongside baseline → unified diff stored under `edits/`.
- Trivial-whitespace hunks filtered out before classification.

### 7. Pattern Learning (`app/learning.py`)
- LLM classifies each hunk: `terminology | structure | tone | citation_style | content_emphasis | omission`.
- Store: `learned_patterns.json` with `schema_version`, keyed on `{type, rule}`.
- Frequency-gated confidence promotion: ≥1 = `low`, ≥2 = `medium`, ≥3 = `high`.
- Application on next draft:
  - **High-confidence** → explicit rules at top of system prompt.
  - **Medium-confidence** → 2–3 before/after few-shot pairs.
  - **Structural** → output skeleton seed.

### Dashboard (`app/dashboard.py` + `app/dashboard_views/`)
- Streamlit + custom dark theme via `.streamlit/config.toml`.
- Five views: Documents, Retrieval Playground, Draft Workspace, Learned Patterns, Stats.
- Presentation only — every action calls the same functions as the CLIs.
- Stats view surfaces grounding %, retrieval P@5, edit-distance reduction trend, **per-run token cost and latency**.
- Runs without an Anthropic API key against committed `processed/` and `outputs/` artifacts (review mode).

## Determinism

- All LLM calls run at `temperature=0` (ingest, extract, draft, classify).
- Embedding model pinned by version in `requirements.txt`.
- Chunk IDs deterministic from `doc_id + page + ordinal`.
- Same input + same prompts + same pattern store → byte-identical output across runs.

## Scaling

- **Vector store** — ChromaDB is fine for < 100k chunks. Beyond that, swap to Qdrant or pgvector behind the same `retrieve()` interface.
- **Ingestion** — synchronous in v1. For high-volume intake, run ingestion behind an async queue (Redis/RQ); the stage already writes manifests so resume-on-failure is trivial.
- **Embeddings** — MiniLM CPU embeds ~150 chunks/s on a laptop. For > 10k docs, run a batch embedder service so the API path stays warm.
- **Multi-tenancy** — `doc_id` namespacing isolates tenants in Chroma; `learned_patterns.json` is per-tenant. No code change needed to add a second tenant; just a directory split.

## Privacy

Documents and embeddings stay on disk in the working directory. No telemetry. LLM calls go only to the configured provider (Anthropic by default). Nothing is forwarded elsewhere.

## File layout (planned)

```
app/
  ingest.py            TASK-001
  extract.py           TASK-002
  schemas.py           shared Pydantic models
  chunking.py          TASK-003
  retrieval.py         TASK-003
  draft.py             TASK-004
  citations.py         TASK-004
  edits.py             TASK-005 (capture)
  learning.py          TASK-005 (store + apply)
  dashboard.py         TASK-006 (entrypoint)
  dashboard_views/     TASK-006 (one module per view)
  prompts/             markdown templates per LLM call
  config.py            tunable thresholds
  logging.py           structured logging shared across pipeline
samples/
  raw/                 source inputs
  processed/           pre-computed outputs (committed for review mode)
eval/
  README.md            approach
  queries.json         held-out retrieval queries
  draft_quality_rubric.md
  RESULTS.md           measured numbers (TASK-007)
outputs/               generated drafts
edits/                 captured diffs
.chroma/               vector store (gitignored)
tests/                 unit tests
.streamlit/config.toml custom theme
tasks/                 sprint task cards
```
