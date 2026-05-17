"""Centralized configuration loaded from environment.

All tunable knobs flow through here so callers can ``from app.config import
settings`` instead of sprinkling ``os.environ.get`` calls across the codebase.
The ``settings`` object is a singleton — instantiated once at import time.

Environment variables can be set in a ``.env`` file at the project root;
see ``.env.example`` for the canonical list.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project-wide settings loaded from environment + .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Anthropic
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-sonnet-4-6",
        description="Claude model for extraction, drafting, and classification",
    )

    # OCR
    ocr_confidence_floor: int = Field(
        default=60,
        ge=0,
        le=100,
        description="Tesseract pages below this confidence are retried with TrOCR",
    )
    ocr_lang: str = Field(default="eng", description="Tesseract language hint")

    # Embeddings & retrieval
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence-transformers model for chunk embeddings",
    )
    chroma_db_path: Path = Field(default=Path(".chroma"))
    retrieval_k: int = Field(default=8, ge=1)
    low_confidence_penalty: float = Field(
        default=0.7,
        gt=0.0,
        le=1.0,
        description="Score multiplier applied to chunks from low-confidence pages",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Paths
    samples_dir: Path = Field(default=Path("samples/raw"))
    processed_dir: Path = Field(default=Path("samples/processed"))
    outputs_dir: Path = Field(default=Path("outputs"))
    edits_dir: Path = Field(default=Path("edits"))
    usage_log: Path = Field(default=Path("usage_log.jsonl"))
    patterns_file: Path = Field(default=Path("app/learned_patterns.json"))
    models_dir: Path = Field(default=Path(".models"))


settings = Settings()
