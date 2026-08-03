"""
Extracts plain text from uploaded files, based on file type. This runs
BEFORE chunking (Lesson 3 mistake #4: clean/extract first, chunk second).
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(file_path)
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        doc = DocxDocument(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if suffix in (".txt", ".md"):
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    if suffix in (".png", ".jpg", ".jpeg"):
        # OCR is a deliberately separate lesson/feature - not wired in yet.
        # Placeholder so uploads of images don't crash; we'll implement
        # this with pytesseract in the OCR milestone.
        raise NotImplementedError(
            "OCR for image uploads isn't implemented yet - coming in the next milestone."
        )

    raise ValueError(f"Unsupported file type: {suffix}")
