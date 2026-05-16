# TASK-001 — Document Ingestion

| Field | Value |
|-------|-------|
| **Story points** | 5 |
| **Sprint** | Sprint 1 |
| **Status** | To Do |
| **Owner** | — |
| **Depends on** | — |

## User story

> As an operator, I want to drop messy legal documents (clean PDFs, scanned PDFs, images, handwritten scans) into a single intake folder and get back clean extracted text plus a per-document confidence manifest, so that downstream retrieval and drafting stages don't have to re-handle file-format chaos.

## Description

Build the intake stage of the pipeline. Accept `.pdf`, `.png`, `.jpg`, `.tiff`, `.txt`. Route each file to the right extractor:

- text-bearing PDF → `pdfplumber`
- image-based PDF → `pdf2image` → `pytesseract`
- standalone image → `PIL` → `pytesseract`
- `.txt` → passthrough

Emit, per document:
- `processed/<doc_id>.text.md` — extracted text with page markers
- `processed/<doc_id>.manifest.json` — `{doc_id, source_path, pages, per_page_confidence, ocr_used, warnings}`

Pages where extraction looks unreliable (very short text, high non-ASCII ratio, OCR confidence below threshold) get flagged in the manifest so retrieval can downweight them.

## Acceptance criteria

- [ ] Running `python -m app.ingest samples/raw/` processes every supported file and writes paired `.text.md` + `.manifest.json` under `processed/`.
- [ ] At least one sample is a scanned PDF that triggers the OCR path and is correctly extracted.
- [ ] At least one sample is a partially illegible scan; affected pages are flagged in the manifest with a clear reason.
- [ ] Unknown file types fail loudly with an actionable error, not silently.
- [ ] Re-running on the same input is idempotent (no duplicate processing, no stale outputs).

## Definition of Done

- [ ] Code merged in `app/ingest.py` with module-level docstring.
- [ ] `requirements.txt` lists `pdfplumber`, `pytesseract`, `pdf2image`, `Pillow` with pinned versions.
- [ ] `README.md` setup section documents the Tesseract binary dependency on Windows + the install path.
- [ ] 4 sample raw inputs committed under `samples/raw/` covering: clean PDF, scanned PDF, image, partially illegible scan.
- [ ] Smoke test runs in CI or via `python -m app.ingest --selftest` and passes.

## Technical notes

- Don't rebuild Tesseract config on every page — initialize once per process.
- Confidence threshold for "flag this page" lives in `app/config.py` so it's tunable without code changes.
- Manifest schema goes in `app/schemas.py` (pydantic) so TASK-002 and TASK-003 can import the same model.
- Windows-specific gotcha: `pdf2image` needs `poppler` on PATH — document the install in the README, not in a comment.
