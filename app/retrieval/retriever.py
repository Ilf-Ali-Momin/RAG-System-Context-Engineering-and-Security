from __future__ import annotations

from app.config.settings import settings
from app.models.schemas import RetrievedChunk
from app.retrieval.vector_store import InMemoryVectorStore
from app.security.injection_detector import detect_prompt_injection


class Retriever:
    def __init__(self, store: InMemoryVectorStore) -> None:
        self.store = store

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        limit = top_k or settings.retrieval_top_k
        results = self.store.search(query=query, top_k=limit)
        chunks: list[RetrievedChunk] = []
        for chunk, similarity in results:
            flags = detect_prompt_injection(chunk.text)
            chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    similarity=similarity,
                    security_flags=flags,
                )
            )
        return chunks

