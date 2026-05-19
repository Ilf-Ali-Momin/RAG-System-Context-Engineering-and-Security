from __future__ import annotations

from app.models.schemas import DocumentIn
from app.security.sanitizer import sanitize_text


def normalize_documents(documents: list[DocumentIn], max_chars: int) -> list[DocumentIn]:
    normalized: list[DocumentIn] = []
    for doc in documents:
        normalized.append(
            DocumentIn(
                source_id=doc.source_id.strip(),
                title=doc.title.strip(),
                content=sanitize_text(doc.content, max_chars=max_chars),
                trust_level=doc.trust_level,
                metadata=doc.metadata,
            )
        )
    return normalized

