from __future__ import annotations

from app.models.schemas import ChunkRecord, DocumentIn


def chunk_document(document: DocumentIn, chunk_size: int = 700, overlap: int = 120) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    text = document.content
    start = 0
    index = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        snippet = text[start:end].strip()
        if snippet:
            chunk_id = f"{document.source_id}-{index}"
            chunks.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    source_id=document.source_id,
                    title=document.title,
                    text=snippet,
                    trust_level=document.trust_level,
                    metadata=document.metadata,
                )
            )
        if end == len(text):
            break
        start = max(0, end - overlap)
        index += 1
    return chunks

