# Draft Quality Rubric

Three axes, each scored 1–5. Two reviewers grade independently; any disagreement of more than one point triggers a re-grade.

## Axis 1 — Clarity & structure

| Score | Description |
|:---:|---|
| 5 | Sections flow logically. Every paragraph has a clear purpose. No redundancy. |
| 4 | Mostly clear. One or two awkward transitions or a single redundant paragraph. |
| 3 | Readable but jumbled in places. Missing or overlong sections. |
| 2 | Hard to follow. Sections fight each other. |
| 1 | Incoherent. |

## Axis 2 — Factual support

| Score | Description |
|:---:|---|
| 5 | Every factual claim cites resolvable evidence. No unsupported assertions. Evidence section is complete. |
| 4 | One or two minor unsupported claims (e.g. boilerplate framing). All material claims grounded. |
| 3 | Some material claims lack citation. Reader has to take them on faith. |
| 2 | Many claims unsupported or citations point to weak evidence. |
| 1 | Confident-sounding text built on assumption. The exact failure mode the brief flags. |

## Axis 3 — Usefulness as a first pass

| Score | Description |
|:---:|---|
| 5 | An operator could send this with minor edits. |
| 4 | Operator edits a few sections, but the bones are right. |
| 3 | Operator rewrites significant portions, but the skeleton helps. |
| 2 | Operator throws most of it out. The structure was wrong from the start. |
| 1 | Not useful. Faster to start from a blank document. |

## Aggregation

- Average across the three axes per draft.
- Average across drafts for the system-level score.
- **Target: ≥ 3.5/5 averaged across five graded drafts.**

## Logging

Graders record scores in `eval/RESULTS.md` using this template, one row per draft × grader:

```
| Draft | Grader | Clarity | Support | Usefulness | Avg | Notes |
|-------|--------|--------:|--------:|-----------:|----:|-------|
| draft_v1_01 | A | 4 | 5 | 4 | 4.33 | "Background section is tight."  |
| draft_v1_01 | B | 4 | 4 | 4 | 4.00 | "Citation in §2 is shaky."     |
```

One-sentence justification per axis is required for any score ≤ 3.
