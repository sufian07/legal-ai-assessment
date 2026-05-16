# PLAN — Architecture, Approach, Tradeoffs

## Goal

Ingest messy legal-style documents → extract usable text + structured fields → retrieve grounded evidence → produce a Case Fact Summary draft with inline citations → capture operator edits → learn reusable patterns → apply them on the next draft.

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Ingest     │───▶│   Extract    │───▶│  Chunk+Embed │───▶│   Retrieve   │
│ pdfplumber + │    │ LLM-assisted │    │ MiniLM-L6-v2 │    │  top-k from  │
│  pytesseract │    │  field pull  │    │  → Chroma    │    │   Chroma     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                    │
                                                                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Learn      │◀───│ Edit Capture │◀───│   Operator   │◀───│    Draft     │
│ pattern JSON │    │  diff + LLM  │    │   edits .md  │    │  Claude API  │
│ + few-shot   │    │   classify   │    │              │    │ + citations  │
└──────┬───────┘    └──────────────┘    └──────────────┘    └──────▲───────┘
       │                                                            │
       └───── rules + examples injected next draft ─────────────────┘
```

## Component decisions

### Ingest
- **pdfplumber** for text-bearing PDFs (no external binary required).
- **pytesseract + pdf2image** for scanned / image-based PDFs (Tesseract binary is the only OS-level dependency).
- **PIL** for standalone images.
- Pages where extraction confidence is low get flagged in a per-document manifest so downstream stages can weight them appropriately.

### Structured extraction
- LLM-assisted (Claude) field pull driven by a JSON schema: `parties`, `dates`, `monetary_amounts`, `document_type`, `claims`, `obligations`, `outstanding_items`.
- Regex pre-pass for obvious patterns (dates, currency, case numbers) reduces hallucination risk before the LLM step.
- Output stored as `processed/<doc_id>.json` alongside the extracted text.

### Retrieval & grounding
- Chunking: ~500-token windows with 80-token overlap, on sentence boundaries. Each chunk carries `{doc_id, page, chunk_id, char_offset}` so citations are traceable to the source.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` — CPU-friendly, no GPU required (operator hardware has a 2 GB MX550, so anything heavier is off-table).
- Store: ChromaDB persistent collection on disk.
- Retrieve top-k (k=8 default) for any drafting task; passed to the LLM with explicit citation IDs.

### Draft generation
- Claude Sonnet 4.6 via `anthropic` SDK.
- System prompt enforces: every factual claim must reference a `[DOC#:chunk_id]` citation; if a question cannot be answered from retrieved evidence, the draft must say so explicitly rather than fabricate.
- Output is a markdown memo with a final "Evidence" section listing each citation and its source snippet — this is what makes grounding inspectable.

### Improvement from edits
This is the loop, not a diff viewer.

1. **Capture**: operator saves edited markdown alongside the baseline → unified diff computed.
2. **Pattern extraction**: diff sent to Claude with a classifier prompt. Patterns are labeled `terminology | structure | tone | citation_style | content_emphasis | omission`.
3. **Storage**: `learned_patterns.json` keyed by pattern type. Each entry has `{rule, before_example, after_example, frequency, confidence}`. Repeated patterns increment `frequency` and graduate from `low → medium → high` confidence.
4. **Application**: on the next draft,
   - **high-confidence** patterns become explicit rules in the system prompt,
   - **medium-confidence** patterns are injected as 2-3 before/after few-shot pairs,
   - **structural** patterns (e.g. operator consistently adds a "Key Dates" section) seed the output skeleton.

The loop is what the rubric is really testing — 25 points sit here.

## Scope decisions

In:
- One draft type (Case Fact Summary).
- 4–6 mock messy documents covering: clean PDF, scanned PDF, image, handwritten-with-illegible-spans.
- CLI-driven workflow **plus** an admin dashboard (Streamlit) wrapping every stage — see TASK-006.
- Evaluation: grounding (claims with valid citations / total claims), retrieval relevance (manual rubric on 10 queries), edit-loop effectiveness (edit-distance reduction between draft v1 and v2 on the same doc after learning).

Out:
- API endpoints, Docker (optional per brief; not committed in this sprint).
- Multi-draft-type support — adding more is a follow-up sprint once the loop is proven.
- Fine-tuning — the edit loop runs at the prompting layer for cost and iteration speed.

### Dashboard

Streamlit hosts five views on top of the pipeline: Documents, Retrieval Playground, Draft Workspace, Learned Patterns, Stats. The dashboard is a presentation layer over the same functions the CLIs use — no duplicated business logic. Custom dark theme via `.streamlit/config.toml`. Details in TASK-006.

## Tradeoffs

- **MiniLM over larger embeddings** — gives up some retrieval quality but stays runnable on a 2 GB GPU and on CI. For legal docs the bigger wins are chunking strategy and metadata-aware retrieval, not embedding dimensionality.
- **Prompting-layer learning over fine-tuning** — patterns adapt within a single session and need no training infra. Cost: ceiling on how deep "style" can be learned. Acceptable for the time horizon.
- **Tesseract over a hosted OCR API** — runs offline, no per-page cost, but lower quality on degraded scans. Documented in `samples/README.md` per-file confidence notes.
- **LLM-assisted extraction over pure regex/NER** — better recall on messy inputs, but adds latency and a hallucination surface. Mitigated by regex pre-pass + schema-constrained output.
- **No re-ranker in v1** — top-k from MiniLM is good enough for the eval set. A cross-encoder re-ranker is a cheap upgrade if precision@k disappoints in eval.

## Risks

- **Tesseract install friction** on reviewer machines. Mitigation: ship pre-processed `.txt` alongside raw PDFs so the pipeline is demonstrable end-to-end without OCR binaries.
- **Edit-loop overfitting** to one operator's idiosyncrasies. Mitigation: cap pattern frequency contribution per session; require ≥2 occurrences before graduation to `medium` confidence.
- **Citation drift** — model citing chunk IDs that don't exist. Mitigation: post-generation validator that checks every `[DOC#:chunk_id]` resolves to a real chunk; unresolved citations get stripped and the model is re-prompted.

## Definition of done for the sprint

- All 5 tasks in `tasks/` are Done.
- End-to-end run on a fresh checkout produces a baseline draft, an edited draft, and a v2 draft that visibly reflects the learned pattern.
- `README.md` setup section is accurate against a clean clone.
- Eval results are committed under `eval/`.
