"""Legal AI Assessment — internal workflow for processing legal documents.

Ingests messy legal-style documents (PDF, scanned, image, handwriting),
extracts structured fields, retrieves grounded evidence from a vector store,
generates cited Case Fact Summary drafts, and learns from operator edits to
improve subsequent drafts.

See ARCHITECTURE.md for the full pipeline and ASSUMPTIONS.md for tradeoffs.
"""

__version__ = "0.1.0"
