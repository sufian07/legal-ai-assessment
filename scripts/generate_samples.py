"""Generate the 4 synthetic sample documents committed under samples/raw/.

Each sample exercises one ingest route in app/ingest.py:

  01_case_brief_clean.pdf       text-bearing PDF      -> pdfplumber
  02_title_search_scanned.pdf   image-based PDF       -> pdf2image + pytesseract
  03_property_deed.png          standalone image      -> pytesseract
  04_handwritten_notice.png     handwriting / noisy   -> TrOCR fallback

Run from the project root::

    python scripts/generate_samples.py

The script is deterministic — re-running reproduces every file byte-for-byte
from the seeds below. The samples are committed; this script exists so
reviewers can regenerate or extend the set.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

RAW_DIR = Path("samples/raw")


# ----------------------------------------------------------------------------
# Seed texts (the "ground truth" — what the documents are *supposed* to say)
# ----------------------------------------------------------------------------

CASE_BRIEF_TEXT = """\
PEARSON SPECTER LITT LLP — CASE BRIEF

Case No.: 2026-CV-04812
Court:    Superior Court of New York County
Parties:  Harvey Specter, Plaintiff
          Charles Tannen, Defendant
Filed:    March 12, 2026

BACKGROUND

This action arises from a breach of contract claim filed by Harvey Specter
against Charles Tannen on March 12, 2026. The plaintiff alleges that the
defendant failed to perform under a written services agreement dated
January 8, 2025, resulting in damages of USD 2,400,000.

KEY DATES

- 2025-01-08: Services Agreement executed by both parties.
- 2025-11-30: Plaintiff demands performance in writing; defendant does not respond.
- 2026-02-14: Cure period expires.
- 2026-03-12: Complaint filed.

OUTSTANDING ISSUES

1. Whether the cure period was reasonable under the circumstances.
2. Whether the alleged damages of USD 2,400,000 can be substantiated by the
   plaintiff's accounting records.
3. Whether any affirmative defenses apply, including waiver and estoppel.

REQUESTED RELIEF

The plaintiff seeks compensatory damages, pre-judgment interest, and costs.
"""

TITLE_SEARCH_TEXT = """\
TITLE SEARCH REPORT

Property:    742 Evergreen Terrace, Springfield, NY 10001
Search Date: April 2, 2026
Search By:   Pearson Specter Litt LLP, Real Estate Division

CHAIN OF TITLE (most recent first)

1. Deed dated 2018-06-15, recorded 2018-06-22, Book 4421, Page 118.
   Grantor: First National Bank of Springfield
   Grantee: Charles Tannen
   Consideration: USD 1,150,000

2. Deed dated 2009-03-04, recorded 2009-03-11, Book 3102, Page 88.
   Grantor: Estate of Mona Simpson
   Grantee: First National Bank of Springfield (Trustee)

ENCUMBRANCES

- Mortgage in favor of First National Bank, recorded 2018-06-22,
  Book 4421, Page 119, original principal USD 920,000.
- Mechanic's lien recorded 2024-09-10 by Burns Roofing LLC, USD 18,500.

EFFECTIVE DATE OF TITLE TRANSFER: 2018-06-22.

EXCEPTIONS AND OUTSTANDING ITEMS

A. The 2024 mechanic's lien remains open and must be discharged at closing.
B. Survey on file dated 2017; a current survey is recommended.
"""

PROPERTY_DEED_TEXT = """\
WARRANTY DEED

THIS DEED, made this 15th day of June, 2018, between
First National Bank of Springfield (Grantor) and
Charles Tannen (Grantee), witnesseth:

The Grantor, in consideration of the sum of
One Million One Hundred Fifty Thousand Dollars (USD 1,150,000),
the receipt of which is hereby acknowledged, does hereby grant, sell, and
convey unto the Grantee, his heirs and assigns forever, the following
described real property:

ALL THAT CERTAIN parcel of land lying in the City of Springfield,
County of [redacted], State of New York, known as 742 Evergreen Terrace,
being more particularly described as Lot 14, Block 7, Evergreen Heights
Subdivision, as per plat thereof recorded in Plat Book 22, Page 41.

SUBJECT TO: covenants, restrictions, and easements of record;
real estate taxes for the year 2018 and subsequent years.

EFFECTIVE DATE: 2018-06-22.
"""

HANDWRITTEN_NOTICE_TEXT = """\
Notice of Termination

To: Charles Tannen
From: Harvey Specter

I am writing to formally notify you that the
Services Agreement dated 8 January 2025 is
hereby terminated, effective 30 days from
the date of this notice.

[illegible — water damage]

Please contact our office to arrange the
return of all confidential materials.

Dated: 14 February 2026
"""


# ----------------------------------------------------------------------------
# Sample generators
# ----------------------------------------------------------------------------


def make_clean_pdf(out_path: Path) -> None:
    """01: text-bearing PDF via reportlab Paragraphs. pdfplumber extracts directly."""
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    story = []
    for para in CASE_BRIEF_TEXT.split("\n\n"):
        story.append(Paragraph(para.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)


def make_scanned_pdf(out_path: Path) -> None:
    """02: image-based PDF. Text rendered to a PNG, then embedded in a PDF page.
    pdfplumber extracts nothing -> ingest falls back to Tesseract via pdf2image."""
    img = _render_text_image(TITLE_SEARCH_TEXT, size=(1200, 1600))
    tmp_png = out_path.with_suffix(".tmp.png")
    img.save(tmp_png, format="PNG")
    try:
        c = canvas.Canvas(str(out_path), pagesize=letter)
        page_w, page_h = letter
        c.drawImage(str(tmp_png), 0, 0, width=page_w, height=page_h)
        c.showPage()
        c.save()
    finally:
        tmp_png.unlink(missing_ok=True)


def make_image_doc(out_path: Path) -> None:
    """03: standalone PNG with printed text. Tesseract path."""
    img = _render_text_image(PROPERTY_DEED_TEXT, size=(1200, 1600))
    img.save(out_path, format="PNG")


def make_handwritten_image(out_path: Path) -> None:
    """04: noisy image deliberately engineered to trip Tesseract confidence,
    so the route picker falls back to TrOCR.

    We don't have rights to a real handwriting font, so we render the text with
    a serif at varied baselines + add blur + speckle noise + a partial smudge
    region (the 'water damage' marker in the seed text). Tesseract returns low
    confidence on the smudged region, exercising the fallback route."""
    img = Image.new("L", (1200, 1600), color=245)
    draw = ImageDraw.Draw(img)
    font = _pick_font(size=42)

    y = 80
    rng = random.Random(42)  # deterministic
    for line in HANDWRITTEN_NOTICE_TEXT.split("\n"):
        x = 80 + rng.randint(-6, 6)
        # tiny baseline jitter so the result doesn't look like a printed doc
        offset = rng.randint(-2, 2)
        draw.text((x, y + offset), line, fill=20 + rng.randint(-10, 10), font=font)
        y += 64

    # Smudge a region (the "[illegible -- water damage]" line)
    smudge = Image.new("L", (1100, 90), color=200)
    smudge_draw = ImageDraw.Draw(smudge)
    for _ in range(2000):
        sx = rng.randint(0, 1099)
        sy = rng.randint(0, 89)
        smudge_draw.point((sx, sy), fill=rng.randint(100, 220))
    smudge = smudge.filter(ImageFilter.GaussianBlur(radius=4))
    img.paste(smudge, (50, 580), smudge)

    # Whole-image speckle + slight blur (simulates a scan)
    pixels = img.load()
    for _ in range(8000):
        px = rng.randint(0, 1199)
        py = rng.randint(0, 1599)
        if pixels is not None:
            pixels[px, py] = max(0, min(255, pixels[px, py] + rng.randint(-40, 40)))
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))

    img.save(out_path, format="PNG")


# ----------------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------------


def _render_text_image(text: str, size: tuple[int, int]) -> Image.Image:
    """Render multi-line text onto a white page as a PIL image."""
    img = Image.new("L", size, color=255)
    draw = ImageDraw.Draw(img)
    font = _pick_font(size=28)
    y = 60
    for line in text.split("\n"):
        draw.text((60, y), line, fill=20, font=font)
        y += 38
    return img


def _pick_font(size: int) -> ImageFont.ImageFont:
    """Try a few likely-installed TTFs; fall back to PIL's default if none found."""
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        (RAW_DIR / "01_case_brief_clean.pdf", make_clean_pdf),
        (RAW_DIR / "02_title_search_scanned.pdf", make_scanned_pdf),
        (RAW_DIR / "03_property_deed.png", make_image_doc),
        (RAW_DIR / "04_handwritten_notice.png", make_handwritten_image),
    ]
    for out_path, generator in targets:
        generator(out_path)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
