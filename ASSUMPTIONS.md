# Assumptions & Tradeoffs

Companion to [ARCHITECTURE.md](ARCHITECTURE.md). This is the doc to read if you want to know *why* the system is shaped the way it is.

## Assumptions

- **Reviewers may not have an Anthropic API key.** The repo ships pre-computed `processed/` and `outputs/` artifacts so the demo is inspectable without running the pipeline (review mode). Setting `ANTHROPIC_API_KEY` enables full end-to-end runs.
- **Reviewers can install Tesseract and Poppler binaries** to exercise OCR paths if they want to re-ingest. README covers Windows + macOS install.
- **Sample documents are mock/synthetic** (per brief permission). Four samples cover the four input regimes: clean PDF, scanned PDF, image-based PDF, handwritten with partial illegibility.
- **Single operator per session.** Multi-operator concurrency is out-of-scope for this iteration; the `learned_patterns.json` store has no locking. Adding it is a small follow-up.
- **English documents.** Multilingual extraction is a follow-up.
- **"Case Fact Summary" overlaps with the brief's "first-pass internal memo" option.** Treated as the same target — a structured memo with parties, dates, facts, and outstanding issues, all cited.

## Scope decisions

**In:**

- One draft type (Case Fact Summary / first-pass memo).
- 4–6 sample documents covering all four input regimes.
- CLI + admin dashboard (Streamlit, 5 views).
- Evaluation across grounding rate, retrieval P@5, edit-loop effectiveness, draft-quality rubric. See [eval/README.md](eval/README.md).

**Out:**

- API endpoints — optional per brief, not committed.
- Docker — optional per brief, not committed.
- Multi-draft-type support — follow-up sprint once the loop is proven on one type.
- Fine-tuning — the improvement loop runs at the prompting layer for cost and iteration speed.
- Multi-tenant access control.

## Tradeoffs

| Decision | Cost | Benefit |
|---|---|---|
| **MiniLM-L6-v2** over larger embeddings | Some retrieval precision left on the table | Runs on a 2 GB GPU and on any CI laptop |
| **Prompting-layer learning** over fine-tuning | Ceiling on how deep "style" can be learned | Adapts within a session, no training infra, fast iteration |
| **Tesseract** over hosted OCR APIs | Lower quality on degraded scans | Offline, no per-page cost, no data egress |
| **TrOCR** for handwriting | Slower per page, ~330 MB model download | Real handwriting support without cloud |
| **LLM-assisted extraction** over pure regex/NER | Latency + hallucination surface | Recall on messy, inconsistently formatted inputs |
| **Section-by-section drafting** over one-shot | More LLM calls per draft | Focused retrieval per section, cleaner citations |
| **No re-ranker in v1** | Top-k precision ceiling | Simpler; cross-encoder (`bge-reranker-base`) is a cheap upgrade if P@5 eval underperforms |
| **Streamlit** over Next.js/React | Less polished than a custom frontend | Single-language stack, ships fast, fine for an internal tool |
| **Single citation format** `[doc_id:chunk_id]` | None of note | Validators stay simple; reviewer can grep |

## Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Tesseract/Poppler install friction on reviewer machines | High | Ship pre-processed text + manifest under `samples/processed/`. Pipeline is demonstrable without binaries. |
| Edit-loop overfits to one operator's idiosyncrasies | Medium | `frequency ≥ 2` required before any pattern affects the prompt; operator `forget` command for misclassifications. |
| Citation drift (model cites a chunk that doesn't exist) | Medium | Post-generation validator strips unresolved IDs and re-prompts once; hard hedge ("source unclear") otherwise. |
| TrOCR memory pressure on the 2 GB MX550 | Medium | Default to CPU inference; `--use-cpu` flag documented in README. |
| Reviewer with no API key can't run end-to-end | High | Pre-computed artifacts committed (review mode). Dashboard gracefully degrades to "show what we generated earlier" when no key is set. |
| `learned_patterns.json` schema drift mid-sprint | Low | `schema_version` field; migration shim drops incompatible entries with a warning rather than crashing. |
| Eval data contamination (queries leak into prompt tuning) | Medium | `queries.json` carries a `hygiene_rule` header; tuning happens against a separate scratch set. |
| Vector store grows unbounded across re-ingests | Medium | Re-indexing evicts chunks whose IDs no longer appear in the new chunk set for that `doc_id`. |

## Determinism

- All LLM calls run at `temperature=0`.
- Embedding model pinned by version in `requirements.txt`.
- Chunk IDs deterministic from `doc_id + page + ordinal`.
- Sample corpus is committed; results are reproducible byte-for-byte across runs.

## Evaluation

See [eval/README.md](eval/README.md) for full methodology. Three measured axes:

- **Grounding rate** — cited claims / total claims, target ≥ 0.95.
- **Retrieval precision@5** — held-out 10-query eval set, target ≥ 0.7.
- **Edit-loop effectiveness** — normalized edit distance v2 → reference shrinks vs v1 → reference, over ≥ 3 doc/edit pairs.
- **Draft-quality rubric** — 1–5 on clarity & structure, factual support, usefulness; target ≥ 3.5/5 averaged across 5 drafts.

Eval hygiene is non-negotiable: held-out queries do not inform chunking or prompt iteration.

## What could change after first review

- **Cross-encoder re-ranker** if P@5 lands below 0.7.
- **Hosted OCR fallback** (Azure Form Recognizer or AWS Textract) if Tesseract+TrOCR underperform on real customer scans.
- **Async ingestion queue** when corpus crosses ~10k documents.
- **Per-operator learning stores** if multiple operators come online.

None of these are required for v1; all are clean upgrades behind existing interfaces.
