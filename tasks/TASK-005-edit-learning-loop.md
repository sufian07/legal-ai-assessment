# TASK-005 — Edit-Learning Loop

| Field | Value |
|-------|-------|
| **Story points** | 5 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | TASK-004 |

## User story

> As an operator, I want the system to learn from how I edit its drafts — terminology I prefer, sections I always add, citation styles I change — so that next time it drafts something similar, I edit less.

## Description

Close the loop. This is the highest-value task in the sprint and the part the rubric weights most heavily (25 pts).

1. **Capture** — operator saves their edited markdown next to the baseline as `outputs/draft_vN_edited.md`. `python -m app.edits capture <vN>` produces a unified diff and stores it under `edits/`.
2. **Classify** — the diff is sent to Claude with a classifier prompt that labels each hunk as one of: `terminology | structure | tone | citation_style | content_emphasis | omission`. Output is structured JSON per hunk: `{type, before, after, suggested_rule}`.
3. **Store** — patterns accumulate in `app/learned_patterns.json` keyed by `{type, rule}`. Repeats increment a `frequency` counter. Confidence promotes: ≥1 occurrence = `low`, ≥2 = `medium`, ≥3 = `high`.
4. **Apply** — next draft generation reads `learned_patterns.json`:
   - **high-confidence** patterns become explicit rules at the top of the system prompt,
   - **medium-confidence** patterns are injected as 2–3 before/after few-shot pairs,
   - **structural** patterns seed the output skeleton (e.g. "always include a 'Key Dates' section").

## Acceptance criteria

- [ ] On the sample corpus, the workflow `draft v1 → simulate operator edits → re-run draft v2` produces a v2 that visibly reflects ≥2 of the simulated edits (e.g. a renamed party, an added section, a citation-style change).
- [ ] `learned_patterns.json` grows monotonically as more edits land; identical patterns increment `frequency` instead of duplicating.
- [ ] Pattern confidence promotion is observable: after 3 identical edits across separate sessions, the pattern's `confidence` field reads `high` and it appears as a rule in the next prompt.
- [ ] `python -m app.edits show` prints the current learned ruleset in a reviewer-readable format.
- [ ] An eval script measures edit-distance between v1 and v2 against the same ground-truth edited draft; v2 should be measurably closer than v1 was.

## Definition of Done

- [ ] Code merged in `app/edits.py` (capture + classify) and `app/learning.py` (store + apply).
- [ ] `app/prompts/edit_classifier.md` and `app/prompts/draft_with_learned.md` committed.
- [ ] Sample artifacts committed under `outputs/`: `draft_v1.md`, `draft_v1_edited.md`, `draft_v2.md` showing the loop in action.
- [ ] `eval/edit_loop_results.md` documents the edit-distance improvement and which specific patterns transferred.
- [ ] README "How the system learns" section explains the loop end-to-end with a concrete example.

## Technical notes

- Don't try to learn from a single edit on a single doc. Require `frequency ≥ 2` before any pattern affects the prompt — otherwise the system overfits to one operator's typo fix.
- Cap the injected few-shot context: top 5 medium-confidence patterns + top 10 high-confidence rules. Beyond that, the prompt bloats and quality drops.
- Operator can manually demote / delete patterns via `python -m app.edits forget <pattern_id>` — needed for when a one-off edit gets misclassified as a pattern.
- Keep the classifier prompt resilient to small diffs: trivial whitespace / punctuation hunks should be filtered out before classification, not after.
