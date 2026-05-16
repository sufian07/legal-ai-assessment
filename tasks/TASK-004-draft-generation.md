# TASK-004 — Draft Generation

| Field | Value |
|-------|-------|
| **Story points** | 3 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-002, TASK-003 |

## User story

> As an operator, I want to run one command and get a first-pass Case Fact Summary with every factual claim citing its source passage, so that I can edit and ship it instead of writing it from scratch.

## Description

Generate a Case Fact Summary in markdown from the indexed corpus.

- Pull structured fields from `processed/*.fields.json` to seed the skeleton (parties, dates, document inventory).
- For each section that needs narrative ("Background", "Key Facts", "Outstanding Issues"), call `retrieve()` with a section-specific query, pass the top-k chunks to Claude, generate prose with inline `[doc_id:chunk_id]` citations.
- Append an **Evidence** section that lists every cited chunk verbatim with its source location.
- Validate citations post-generation: every `[doc_id:chunk_id]` must resolve to a real chunk; if any don't, strip them and re-prompt the model to rewrite the affected sentence with a valid citation or hedge. The citation format `[doc_id:chunk_id]` is canonical across README, ARCHITECTURE, prompts, and validator — no other forms accepted.
- If retrieval returns nothing relevant for a section, the draft says "No supporting evidence found in the provided documents" instead of fabricating.

## Acceptance criteria

- [ ] `python -m app.draft <corpus_id> --out outputs/draft_v1.md` produces a markdown memo with the structure: Header → Parties → Background → Key Facts → Outstanding Issues → Evidence.
- [ ] Every factual sentence has at least one `[doc_id:chunk_id]` citation.
- [ ] Every citation in the body resolves to a chunk listed in the Evidence section.
- [ ] When run against the sample corpus with no evidence on a topic, the relevant section explicitly says so.
- [ ] Output is reproducible: same corpus + same prompts → same draft (temperature 0 or pinned seed).

## Definition of Done

- [ ] Code merged in `app/draft.py`.
- [ ] Prompt template at `app/prompts/draft_case_fact_summary.md`.
- [ ] Citation validator in `app/citations.py` with unit tests covering: valid citation, missing chunk, malformed ID.
- [ ] Sample `outputs/draft_v1.md` committed.
- [ ] README "Generating a draft" section walks through the command.

## Technical notes

- Don't generate the full draft in one prompt — section-by-section keeps retrieval focused and citations clean.
- The Evidence section is what makes grounding inspectable per the rubric — render it as a numbered table with `doc_id`, page, and the chunk text.
- Citation validator runs on the assembled draft; failures trigger a single rewrite attempt per failing sentence, then a hard hedge ("source unclear") if it still fails. Don't loop unbounded.
