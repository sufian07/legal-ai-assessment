# Reviewer Guide

> A 60-second tour. If you only have time for one doc, read this one and skip the rest.

## What this is

Take-home for the Pearson Specter Litt AI Engineer role. The system ingests messy legal documents (clean PDFs, scanned PDFs, images, handwriting), extracts structured facts, retrieves grounded evidence, generates cited **Case Fact Summary** drafts, and learns from operator edits so subsequent drafts need less editing.

## What to read, in order

| # | File | What you'll learn | Time |
|--:|------|-------------------|-----:|
| 1 | This file | The lay of the land | 2 min |
| 2 | [ARCHITECTURE.md](ARCHITECTURE.md) | How the pipeline works end-to-end | 5 min |
| 3 | [ASSUMPTIONS.md](ASSUMPTIONS.md) | Why every non-obvious decision | 5 min |
| 4 | [tasks/README.md § Coverage matrix](tasks/README.md#coverage-matrix--brief--task--doc) | How each rubric point is addressed | 2 min |
| 5 | [eval/README.md](eval/README.md) | How we know the system works | 3 min |
| 6 | `eval/RESULTS.md` (lands in TASK-007) | Whether it actually worked | 2 min |

Total: ~20 minutes to full context.

## Magic moments — what to look at if you have five minutes

1. **Grounding is real, not theater.** Open `outputs/draft_v1.md`. Every factual sentence carries a `[doc_id:chunk_id]` citation. Cross-reference to the **Evidence** section at the bottom — every citation resolves to a chunk that's listed verbatim. Open `app/citations.py` to see how unresolved citations get stripped and re-prompted at generation time. Empty retrieval doesn't fabricate — it says "No supporting evidence found in the provided documents."

2. **The improvement loop actually improves.** Open `outputs/draft_v1.md`, then `outputs/draft_v1_edited.md` (the operator's edit), then `outputs/draft_v2.md` (the regenerated draft after the loop saw those edits). The diff between v1 and v1_edited shows what the operator changed. The diff between v1 and v2 shows the same patterns transferring to a new generation without the operator touching v2 by hand. `eval/RESULTS.md` quantifies it as edit-distance reduction.

3. **Handwriting works.** `samples/raw/04_handwritten_notice.png` is genuine handwriting. `samples/processed/04_handwritten_notice.text.md` is what TrOCR pulled out. The manifest flags low-confidence pages, and retrieval downranks them by `0.7×` so the draft doesn't over-rely on shaky extractions.

## How to run it (with an Anthropic API key)

```bash
git clone https://github.com/sufian07/legal-ai-assessment
cd legal-ai-assessment
make install          # creates venv, installs deps, fetches TrOCR weights on first ingest
cp .env.example .env  # add your ANTHROPIC_API_KEY
make dashboard        # launches Streamlit on http://localhost:8501
```

## How to inspect it (review mode — no API key needed)

The repo ships pre-computed `samples/processed/`, `outputs/`, and `app/learned_patterns.json`. The dashboard renders against those artifacts. Run `make dashboard` and explore — no LLM calls happen until you click **Generate Draft** or **Save edits**.

## Rubric → code map

For each rubric item, the single best file to read to judge it:

| Rubric item (points) | Read this |
|----------------------|-----------|
| Document Processing (25) | `app/ingest.py` + `samples/processed/04_handwritten_notice.text.md` (TrOCR output + manifest) |
| Retrieval & Grounding (25) | `app/retrieval.py` (confidence-aware ranking) + `app/citations.py` (validator) + the **Evidence** section of `outputs/draft_v1.md` |
| Draft Quality (10) | `outputs/draft_v1.md` itself, graded in `eval/RESULTS.md` against `eval/draft_quality_rubric.md` |
| Improvement from Edits (25) | `app/learning.py` + `app/learned_patterns.json` + diff(`outputs/draft_v1.md`, `outputs/draft_v2.md`) |
| Code Quality & Design (10) | `ARCHITECTURE.md` § Scaling + any single file under `app/` |
| Documentation & Clarity (5) | This file + `ARCHITECTURE.md` + `ASSUMPTIONS.md` |

## What I'd ask if I were reviewing

1. **Does the system fabricate when retrieval is empty?** Search `outputs/` for "No supporting evidence found" — that's the explicit hedge path. The citation validator (`app/citations.py`) strips unresolved citations before the draft is finalized.
2. **Are patterns overfitting to one operator's typos?** Check the `frequency` field in `app/learned_patterns.json`. The `≥ 2` gate is enforced in `app/learning.py:_promote_confidence` — no pattern affects the next draft until it's been seen twice.
3. **Is grounding measured or just claimed?** `eval/grounding.py` computes cited-claims / total-claims; numbers in `eval/RESULTS.md`. Held-out eval queries are isolated in `eval/queries.json` with a hygiene-rule header.

## What's deliberately not here

- API endpoints, Docker — optional per brief, deferred to keep scope honest. See `ASSUMPTIONS.md` § Scope decisions.
- Fine-tuning the model — the improvement loop runs at the prompting layer. Reasoning in `ASSUMPTIONS.md` § Tradeoffs.
- A bigger embedding model — `MiniLM-L6-v2` runs on a 2 GB GPU and on CI. A cross-encoder re-ranker is a clean upgrade behind the same `retrieve()` interface if P@5 underperforms.

## Sprint plan

Eight Scrum task cards in [`tasks/`](tasks/). Each ≤ 5 story points. Total 32 SP. The coverage matrix in [`tasks/README.md`](tasks/README.md) maps every rubric item and every required deliverable to a concrete file or task — no rubric item is uncovered.

## Author

[Your name]. GitHub: [sufian07](https://github.com/sufian07). Reach out at [email].
