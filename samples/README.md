# Sample Inputs & Outputs

This directory holds the synthetic sample documents and their pre-computed outputs. Samples land as TASK-001 / TASK-002 / TASK-004 progress.

## Layout

```
samples/
├── README.md                       this file
├── raw/                            source inputs (committed)
│   ├── 01_case_brief_clean.pdf            text-bearing PDF
│   ├── 02_title_search_scanned.pdf        image-based PDF (Tesseract path)
│   ├── 03_property_deed.png               standalone scanned image
│   └── 04_handwritten_notice.png          handwriting + partial illegibility (TrOCR path)
└── processed/                      pre-computed outputs (committed for review mode)
    ├── 01_case_brief_clean.text.md
    ├── 01_case_brief_clean.manifest.json
    ├── 01_case_brief_clean.fields.json
    ├── 02_title_search_scanned.text.md
    ├── 02_title_search_scanned.manifest.json
    ├── 02_title_search_scanned.fields.json
    └── …
```

## Why both `raw/` and `processed/` are committed

Reviewers may not have Tesseract, Poppler, the TrOCR weights, or an Anthropic API key. Committing the pre-computed outputs means:

- the dashboard launches against real data on a fresh clone with zero setup,
- a reviewer can read `processed/*.text.md` and `processed/*.fields.json` to judge ingest quality directly, and
- TASK-006 and TASK-007 dependencies (retrieval, drafting, eval) don't block on a working OCR install.

This is "review mode" — see [ASSUMPTIONS.md](../ASSUMPTIONS.md) § Assumptions.

## What each sample exercises

| File | Path | Purpose |
|------|------|---------|
| `01_case_brief_clean.pdf` | `pdfplumber` direct text | Baseline ingest quality, no OCR. |
| `02_title_search_scanned.pdf` | `pdf2image + pytesseract` | Image-based PDF; tests OCR-fallback path and per-page confidence emission. |
| `03_property_deed.png` | `PIL + pytesseract` | Standalone image; tests image-only ingest route. |
| `04_handwritten_notice.png` | `TrOCR` | Handwriting + a deliberately illegible region; tests the handwriting route and low-confidence flagging. |

## Generation

Samples are hand-crafted; generation scripts live under `scripts/generate_samples.py` (lands with TASK-001). Re-running the script reproduces every file byte-for-byte from seed inputs in `scripts/seeds/`.

## What's *not* in this folder

- Generated drafts → `outputs/`
- Captured operator edits → `edits/`
- Eval queries and results → `eval/`
