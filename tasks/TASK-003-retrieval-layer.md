# TASK-003 — Retrieval Layer

| Field | Value |
|-------|-------|
| **Story points** | 5 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-001 |

## User story

> As a draft generator, I want to ask "what does the corpus say about X?" and get back the most relevant passages with stable citation IDs, so that the draft I produce is anchored to real source material and a reviewer can trace every claim back to its evidence.

## Description

Stand up the retrieval layer over the processed documents.

- Chunk processed text into ~500-token windows with 80-token overlap, on sentence boundaries. Each chunk carries `{doc_id, page, chunk_id, char_offset}`.
- Embed chunks with `sentence-transformers/all-MiniLM-L6-v2` (CPU; no GPU requirement).
- Persist in a local ChromaDB collection under `./.chroma/`.
- Expose `retrieve(query: str, k: int = 8) -> list[Chunk]` returning chunks with their citation metadata.
- Provide an inspection CLI: `python -m app.retrieval inspect "<query>"` prints retrieved chunks with scores so a reviewer can sanity-check grounding offline.

## Acceptance criteria

- [ ] `python -m app.retrieval index processed/` indexes every processed document and is idempotent (re-running doesn't duplicate chunks).
- [ ] `retrieve("party names in the contract")` returns 8 chunks with `doc_id`, `page`, `chunk_id`, score, and the chunk text.
- [ ] Citation IDs are stable across re-indexing of the same source (same doc + same chunk boundaries → same `chunk_id`).
- [ ] Re-indexing a document evicts Chroma entries whose `chunk_id` is no longer present in the new chunk set for that `doc_id`. No orphan chunks left behind.
- [ ] Chunks inheriting low-confidence page metadata (from TASK-001 manifests) are downranked at retrieval time by a configurable penalty (default `0.7×`).
- [ ] Held-out 10-query eval set committed at `eval/queries.json` with a `hygiene_rule` header. Queries are not used during chunking parameter tuning or prompt iteration. Methodology in [`eval/README.md`](../eval/README.md).
- [ ] On the held-out query set, precision@5 is ≥ 0.7. Below that, the task isn't done — investigate chunking or add a cross-encoder re-ranker before closing.
- [ ] Inspection CLI shows scores and source snippets so retrieval quality can be debugged without running a full draft.

## Definition of Done

- [ ] Code merged in `app/retrieval.py` and `app/chunking.py`.
- [ ] `eval/queries.json` committed with 10 query/expected-doc pairs.
- [ ] `eval/retrieval_results.md` committed with measured precision@k and a short narrative on failures.
- [ ] `.chroma/` added to `.gitignore`.
- [ ] README has a "How retrieval works" subsection pointing at the citation-ID scheme.

## Technical notes

- Chunk IDs should be deterministic: `f"{doc_id}:p{page}:c{ordinal}"`. Don't use UUIDs — citations need to be human-debuggable.
- Sentence-boundary splitting via `nltk.sent_tokenize` is fine; pre-download the `punkt` data in the install step.
- Keep the embed function pure (no global state) so it's testable.
- If precision@5 lands below the bar, the cheapest upgrade is a `bge-reranker-base` cross-encoder pass on the top-20 — don't change the embedding model first.
