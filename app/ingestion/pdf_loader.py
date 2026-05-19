from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from app.security.sanitizer import sanitize_text


def extract_pdf_text(raw_bytes: bytes, max_chars: int) -> str:
    reader = PdfReader(BytesIO(raw_bytes))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return sanitize_text("\n".join(parts), max_chars=max_chars)

