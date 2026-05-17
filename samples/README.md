# Sample Inputs & Outputs

Synthetic sample documents covering the four ingest routes, plus their per-document processed outputs.

## Layout

```
samples/
├── README.md                              this file
├── raw/                                   source inputs (committed)
│   ├── 01_case_brief_clean.pdf            text-bearing PDF        -> pdfplumber
│   ├── 02_title_search_scanned.pdf        image-based PDF         -> pdf2image + pytesseract
│   ├── 03_property_deed.png               standalone scanned image -> pytesseract
│   └── 04_handwritten_notice.png          handwriting + smudge    -> TrOCR fallback
└── processed/                             pre-computed outputs (committed for review mode)
    ├── 01_case_brief_clean.text.md
    ├── 01_case_brief_clean.manifest.json
    ├── 02_title_search_scanned.text.md
    ├── 02_title_search_scanned.manifest.json
    ├── 03_property_deed.text.md
    ├── 03_property_deed.manifest.json
    ├── 04_handwritten_notice.text.md
    └── 04_handwritten_notice.manifest.json
```

## How these were produced

| # | File | Route | Produced by |
|---|------|-------|-------------|
| 01 | `01_case_brief_clean.pdf` | `pdfplumber` | **Real run** — `python -m app.ingest samples/raw/01_case_brief_clean.pdf`. Confidence 0.95. |
| 02 | `02_title_search_scanned.pdf` | `pdf2image + tesseract` | Hand-crafted to show what the pipeline produces with Tesseract+Poppler installed. The local dev machine that generated this sprint set didn't have those binaries, so the output reflects what a reviewer with `make install` + Tesseract + Poppler would see. Re-ingest at any time to overwrite. |
| 03 | `03_property_deed.png` | `tesseract` | Hand-crafted, same reason as 02. |
| 04 | `04_handwritten_notice.png` | `tesseract -> trocr` fallback | Hand-crafted to show the TrOCR fallback path. Confidence 0.55 (deliberately below the 0.60 floor — see `app/ingest.py:_trocr_image` docstring) so the page is flagged for retrieval downweighting. |

This is the **review mode** described in [`../ASSUMPTIONS.md`](../ASSUMPTIONS.md). A reviewer can inspect the full pipeline outputs without installing OCR binaries. To reproduce 02–04 from scratch:

```bash
# Install Tesseract + Poppler per README setup section, then:
python -m app.ingest samples/raw/
```

Re-ingesting is idempotent — same input, same chunk IDs, overwrites in place.

## Regenerating the raw inputs

The raw inputs are deterministic. Run:

```bash
python scripts/generate_samples.py
```

This rewrites `samples/raw/01_case_brief_clean.pdf`, `02_title_search_scanned.pdf`, `03_property_deed.png`, and `04_handwritten_notice.png` byte-for-byte from the seed text constants at the top of the script. Useful if you want to tweak the seed content or test a new ingest route.

## What's *not* in this folder

- Generated drafts → `../outputs/`
- Captured operator edits → `../edits/`
- Eval queries and results → `../eval/`
