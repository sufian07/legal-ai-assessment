"""Document ingestion: route messy files to the right extractor.

Accepts ``.pdf``, ``.png``, ``.jpg``, ``.jpeg``, ``.tiff``, ``.tif``, ``.txt``.
Routes each file to the appropriate extractor:

- text-bearing PDF      -> pdfplumber
- image-based PDF       -> pdf2image + pytesseract (TrOCR fallback if confidence low)
- standalone image      -> pytesseract (TrOCR fallback if confidence low)
- handwritten / low-conf image -> microsoft/trocr-base-handwritten
- .txt                  -> passthrough

Emits, per document:

- ``processed/<doc_id>.text.md``       extracted text with page markers
- ``processed/<doc_id>.manifest.json``  per-page confidence + ocr engine + flags

Pages with very short extractions, high non-ASCII ratio, or OCR confidence below
``settings.ocr_confidence_floor`` are flagged in the manifest so retrieval can
downweight them.

Usage::

    python -m app.ingest samples/raw/
    python -m app.ingest --selftest
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.logging import get_logger
from app.schemas import DocumentManifest, PageManifest

logger = get_logger(__name__)

SUPPORTED_PDF_EXT = {".pdf"}
SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tiff", ".tif"}
SUPPORTED_TEXT_EXT = {".txt"}
SUPPORTED_EXT = SUPPORTED_PDF_EXT | SUPPORTED_IMAGE_EXT | SUPPORTED_TEXT_EXT

# Lazy module-level cache for TrOCR (loaded on first handwriting page).
_trocr_processor: Any = None
_trocr_model: Any = None


# --- Routing entry points ----------------------------------------------------


def ingest_path(path: Path) -> DocumentManifest:
    """Route a single file to the right ingester."""
    ext = path.suffix.lower()
    if ext in SUPPORTED_TEXT_EXT:
        return _ingest_text(path)
    if ext in SUPPORTED_PDF_EXT:
        return _ingest_pdf(path)
    if ext in SUPPORTED_IMAGE_EXT:
        return _ingest_image(path)
    raise ValueError(
        f"Unsupported file type: {path.name!r} (extension {ext!r}). "
        f"Supported extensions: {sorted(SUPPORTED_EXT)}."
    )


def ingest_directory(directory: Path) -> list[DocumentManifest]:
    """Ingest every supported file in a directory. Re-runs are idempotent."""
    if not directory.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")
    files = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXT
    )
    if not files:
        logger.warning("no supported files found", extra={"directory": str(directory)})
        return []

    manifests: list[DocumentManifest] = []
    for path in files:
        logger.info("ingesting", extra={"path": str(path)})
        manifest = ingest_path(path)
        manifests.append(manifest)
        logger.info(
            "ingested",
            extra={
                "doc_id": manifest.doc_id,
                "pages": len(manifest.pages),
                "overall_confidence": round(manifest.overall_confidence, 3),
                "flagged_pages": sum(1 for p in manifest.pages if p.flagged),
            },
        )
    return manifests


# --- Per-format ingesters ----------------------------------------------------


def _ingest_text(path: Path) -> DocumentManifest:
    text = path.read_text(encoding="utf-8", errors="replace")
    flagged, reason = _flag_page(text, 1.0)
    page = PageManifest(
        page=1,
        text_length=len(text),
        confidence=1.0,
        ocr_engine="passthrough",
        ocr_attempts=["passthrough"],
        flagged=flagged,
        flag_reason=reason,
    )
    manifest = DocumentManifest(
        doc_id=_doc_id(path),
        source_path=str(path),
        source_type="text",
        ingested_at=datetime.now(UTC),
        pages=[page],
        overall_confidence=1.0,
    )
    _write_outputs(manifest, [(1, text)])
    return manifest


def _ingest_pdf(path: Path) -> DocumentManifest:
    import pdfplumber

    pages_text: list[tuple[int, str]] = []
    page_manifests: list[PageManifest] = []
    warnings: list[str] = []
    floor = settings.ocr_confidence_floor / 100.0

    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            confidence = _text_confidence(text)
            engine: str = "pdfplumber"
            attempts: list[str] = ["pdfplumber"]

            if confidence < floor:
                try:
                    text, confidence, engine, attempts = _ocr_pdf_page(path, idx)
                except Exception as exc:  # noqa: BLE001  catch + record, don't crash
                    warnings.append(f"page {idx}: OCR fallback failed: {exc}")
                    text = text or ""

            flagged, reason = _flag_page(text, confidence)
            page_manifests.append(PageManifest(
                page=idx,
                text_length=len(text),
                confidence=confidence,
                ocr_engine=engine,
                ocr_attempts=attempts,
                flagged=flagged,
                flag_reason=reason,
            ))
            pages_text.append((idx, text))

    overall = (
        sum(p.confidence for p in page_manifests) / len(page_manifests)
        if page_manifests else 0.0
    )
    manifest = DocumentManifest(
        doc_id=_doc_id(path),
        source_path=str(path),
        source_type="pdf",
        ingested_at=datetime.now(UTC),
        pages=page_manifests,
        overall_confidence=overall,
        warnings=warnings,
    )
    _write_outputs(manifest, pages_text)
    return manifest


def _ingest_image(path: Path) -> DocumentManifest:
    from PIL import Image

    img = Image.open(path)
    text, confidence, engine, attempts = _ocr_image(img)
    flagged, reason = _flag_page(text, confidence)
    page = PageManifest(
        page=1,
        text_length=len(text),
        confidence=confidence,
        ocr_engine=engine,
        ocr_attempts=attempts,
        flagged=flagged,
        flag_reason=reason,
    )
    manifest = DocumentManifest(
        doc_id=_doc_id(path),
        source_path=str(path),
        source_type="image",
        ingested_at=datetime.now(UTC),
        pages=[page],
        overall_confidence=confidence,
    )
    _write_outputs(manifest, [(1, text)])
    return manifest


# --- OCR primitives ----------------------------------------------------------


def _ocr_image(img: Any) -> tuple[str, float, str, list[str]]:
    """OCR a PIL image. Tesseract first; TrOCR fallback if confidence is low."""
    import pytesseract

    floor = settings.ocr_confidence_floor / 100.0
    attempts: list[str] = ["tesseract"]

    data = pytesseract.image_to_data(
        img, lang=settings.ocr_lang, output_type=pytesseract.Output.DICT
    )
    text = " ".join(w for w in data["text"] if w.strip())
    confs = [int(c) for c in data["conf"] if int(c) >= 0]
    avg_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0

    if avg_conf >= floor:
        return text, avg_conf, "tesseract", attempts

    attempts.append("trocr")
    trocr_text, trocr_conf = _trocr_image(img)
    return trocr_text, trocr_conf, "trocr", attempts


def _ocr_pdf_page(pdf_path: Path, page_num: int) -> tuple[str, float, str, list[str]]:
    """Render a PDF page to image, then OCR via the image path."""
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
    if not images:
        return "", 0.0, "tesseract", ["tesseract"]
    return _ocr_image(images[0])


def _trocr_image(img: Any) -> tuple[str, float]:
    """Run TrOCR on a PIL image. Loads model lazily.

    TrOCR doesn't expose per-token confidence cheaply, so we assign a baseline
    of 0.55 — deliberately below the default ``ocr_confidence_floor`` of 0.60
    so handwriting pages get flagged for retrieval downweighting. TrOCR really
    is less reliable than Tesseract-on-print, and the manifest should say so.
    """
    processor = _get_trocr_processor()
    model = _get_trocr_model()
    pixel_values = processor(images=img.convert("RGB"), return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text, 0.55


def _get_trocr_processor() -> Any:
    global _trocr_processor
    if _trocr_processor is None:
        from transformers import TrOCRProcessor
        _trocr_processor = TrOCRProcessor.from_pretrained(
            "microsoft/trocr-base-handwritten",
            cache_dir=str(settings.models_dir),
        )
    return _trocr_processor


def _get_trocr_model() -> Any:
    global _trocr_model
    if _trocr_model is None:
        from transformers import VisionEncoderDecoderModel
        _trocr_model = VisionEncoderDecoderModel.from_pretrained(
            "microsoft/trocr-base-handwritten",
            cache_dir=str(settings.models_dir),
        )
    return _trocr_model


# --- Heuristics & helpers ----------------------------------------------------


def _doc_id(path: Path) -> str:
    """Stable doc_id derived from filename stem."""
    return path.stem


def _text_confidence(text: str) -> float:
    """Heuristic confidence for pdfplumber-extracted text."""
    if not text or len(text) < 20:
        return 0.0
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii / len(text) > 0.2:
        return 0.3
    return 0.95


def _flag_page(text: str, confidence: float) -> tuple[bool, str | None]:
    """Decide whether a page should be flagged for retrieval downweighting."""
    floor = settings.ocr_confidence_floor / 100.0
    if confidence < floor:
        return True, f"low confidence {confidence:.2f} (floor {floor:.2f})"
    if len(text) < 50:
        return True, f"very short extraction ({len(text)} chars)"
    if text:
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii / len(text) > 0.2:
            return True, f"high non-ASCII ratio {non_ascii / len(text):.0%}"
    return False, None


def _write_outputs(manifest: DocumentManifest, pages: list[tuple[int, str]]) -> None:
    """Write extracted text and manifest under settings.processed_dir."""
    out_dir = settings.processed_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    text_path = out_dir / f"{manifest.doc_id}.text.md"
    manifest_path = out_dir / f"{manifest.doc_id}.manifest.json"

    text_body = "\n\n".join(
        f"--- Page {p} ---\n\n{t.strip()}" for p, t in pages
    )
    text_path.write_text(text_body + "\n", encoding="utf-8")
    manifest_path.write_text(
        manifest.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )


# --- CLI ---------------------------------------------------------------------


def _selftest() -> int:
    """Smoke test: ingest a synthetic .txt and verify outputs round-trip."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        sample = tmp_path / "selftest.txt"
        sample.write_text("Hello from the selftest.\n" * 5, encoding="utf-8")

        original = settings.processed_dir
        try:
            settings.processed_dir = tmp_path / "processed"
            manifest = ingest_path(sample)
            text_path = settings.processed_dir / f"{manifest.doc_id}.text.md"
            manifest_path = settings.processed_dir / f"{manifest.doc_id}.manifest.json"

            assert text_path.exists(), "text output missing"
            assert manifest_path.exists(), "manifest output missing"
            assert "Hello from the selftest" in text_path.read_text(encoding="utf-8")
            assert manifest.pages[0].ocr_engine == "passthrough"
            assert manifest.overall_confidence == 1.0
        finally:
            settings.processed_dir = original

    print("selftest: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Document ingestion stage.")
    parser.add_argument("path", nargs="?", help="File or directory to ingest")
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a synthetic smoke test (no external deps).",
    )
    args = parser.parse_args()

    if args.selftest:
        return _selftest()

    if not args.path:
        parser.error("provide a path or use --selftest")

    target = Path(args.path)
    if target.is_dir():
        ingest_directory(target)
    elif target.is_file():
        ingest_path(target)
    else:
        print(f"not found: {target}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
