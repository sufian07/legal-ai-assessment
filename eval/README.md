# Evaluation Approach

Methodology committed *before* any code lands, so metric-gaming is not a confounder. Numbers land in [`RESULTS.md`](RESULTS.md) as TASK-007 closes the sprint.

## What we measure

| Axis | Metric | Target | Implemented in |
|---|---|---|---|
| Grounding | cited claims / total claims | ≥ 0.95 | `eval/grounding.py` over 5 generated drafts |
| Retrieval relevance | precision@5 on held-out queries | ≥ 0.70 | `eval/retrieval.py` over `queries.json` |
| Edit-loop effectiveness | edit-distance reduction (v1→ref vs v2→ref) | strictly decreasing as patterns accumulate | `eval/edit_loop.py` over ≥ 3 doc/edit pairs |
| Draft quality | rubric score | ≥ 3.5 / 5 average | `eval/draft_quality_rubric.md` applied to 5 drafts |

## Files in this directory

- `README.md` — this file (approach)
- `queries.json` — 10 held-out retrieval queries with `expected_doc_ids` (TASK-003)
- `draft_quality_rubric.md` — 1–5 rubric on three axes for human grading of drafts
- `RESULTS.md` — measured numbers + narratives on failures (lands in TASK-007)

## Eval hygiene

**Held-out rule:** queries in `queries.json` are **not** used during chunking parameter tuning or prompt iteration. Anyone touching chunking or prompts must iterate against a scratch query set to avoid inflating P@5.

The rule is enforced socially (PR review) and documented in the header of `queries.json`.

## Methodology by axis

### Grounding rate

For each generated draft, count sentences that contain at least one factual claim. Of those, count how many have at least one `[doc_id:chunk_id]` citation that resolves to a real chunk in the corpus. Ratio is the grounding rate.

- Implemented in `eval/grounding.py`.
- Reusable as a CI gate on any commit that touches `app/draft.py` or `app/prompts/draft_*.md`.
- Target ≥ 0.95. Below 0.90 = blocker; investigate prompts and validator before shipping.

### Retrieval precision@5

Each query in `queries.json` lists `expected_doc_ids` (one or more correct sources). After retrieval, a result is relevant iff its `doc_id` is in the expected set **and** a human spot-check confirms the chunk text actually addresses the query. P@5 is the fraction of the top-5 results that are relevant, averaged over all 10 queries.

- Implemented in `eval/retrieval.py`.
- Target ≥ 0.70. Below that → add `bge-reranker-base` cross-encoder pass over top-20 before changing the embedding model.

### Edit-loop effectiveness

The critical metric for rubric § 4 (25 points).

For each of 3+ doc/edit pairs:

1. Generate baseline draft v1.
2. Apply a known set of operator edits → reference v1' (the "ground truth" edited draft).
3. Run the learning loop on (v1, v1').
4. Generate v2 from the same source with the loop's patterns applied.
5. Measure normalized Levenshtein distance from v2 → v1' and v1 → v1'.

Loop is doing its job iff `distance(v2, v1') < distance(v1, v1')` and the gap widens over repeated sessions (patterns gaining frequency).

- Implemented in `eval/edit_loop.py`.
- Failure mode to watch: patterns that fire on one doc and silently degrade quality on another. Mitigated by `frequency ≥ 2` gate and per-doc spot checks.

### Draft quality rubric

Three axes (1–5 each): clarity & structure, factual support, usefulness as a first pass. Two graders score independently; disagreements > 1 point trigger a re-grade. Documented in [`draft_quality_rubric.md`](draft_quality_rubric.md).

Target ≥ 3.5/5 average across 5 graded drafts.

## Reproducibility

All evals run with `temperature=0`, pinned embedding model version, deterministic chunk IDs. Numbers should be byte-identical across runs given the same corpus and the same `learned_patterns.json`.

## When to re-run

- Every commit that touches `app/draft.py`, `app/retrieval.py`, `app/learning.py`, or any `app/prompts/*` file → grounding + retrieval evals.
- Every sprint end → full eval suite + rubric grading + update `RESULTS.md`.
