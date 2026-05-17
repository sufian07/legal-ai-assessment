"""Shared Pydantic models used across the pipeline.

Centralising schemas here means ingest, extract, retrieval, draft, and the
dashboard all import from a single source — no drift between stages.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OCREngine = Literal["pdfplumber", "tesseract", "trocr", "passthrough"]
SourceType = Literal["pdf", "image", "text"]


class PageManifest(BaseModel):
    """Per-page extraction metadata."""

    page: int = Field(..., ge=1)
    text_length: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    ocr_engine: OCREngine
    ocr_attempts: list[OCREngine] = Field(default_factory=list)
    flagged: bool = False
    flag_reason: str | None = None


class DocumentManifest(BaseModel):
    """Per-document extraction manifest, written alongside the extracted text."""

    doc_id: str
    source_path: str
    source_type: SourceType
    ingested_at: datetime
    pages: list[PageManifest]
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
