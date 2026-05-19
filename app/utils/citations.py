from __future__ import annotations

from app.models.schemas import Citation, RetrievedChunk


def build_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            source_id=chunk.chunk.source_id,
            title=chunk.chunk.title,
            chunk_id=chunk.chunk.chunk_id,
        )
        for chunk in chunks
    ]

