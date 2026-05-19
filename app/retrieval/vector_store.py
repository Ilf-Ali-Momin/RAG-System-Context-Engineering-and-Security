from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import ChunkRecord
from app.retrieval.embeddings import cosine_similarity, embed_text


@dataclass
class StoredChunk:
    chunk: ChunkRecord
    embedding: object


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: dict[str, StoredChunk] = {}

    def add_chunks(self, chunks: list[ChunkRecord]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = StoredChunk(chunk=chunk, embedding=embed_text(chunk.text))

    def search(self, query: str, top_k: int) -> list[tuple[ChunkRecord, float]]:
        query_embedding = embed_text(query)
        scored = [
            (entry.chunk, cosine_similarity(query_embedding, entry.embedding))
            for entry in self._chunks.values()
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

