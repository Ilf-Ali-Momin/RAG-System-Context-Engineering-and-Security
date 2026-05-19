from __future__ import annotations

from app.config.settings import settings
from app.models.schemas import RetrievedChunk
from app.retrieval.embeddings import cosine_similarity, embed_text


def _quality_score(item: RetrievedChunk) -> float:
    trust_component = item.chunk.trust_level / 5.0
    security_penalty = 0.35 if item.security_flags else 0.0
    return max(0.0, (0.7 * item.similarity) + (0.3 * trust_component) - security_penalty)


def select_high_quality_context(candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
    enriched: list[RetrievedChunk] = []
    for candidate in candidates:
        if candidate.similarity < settings.min_similarity:
            continue
        candidate.quality_score = _quality_score(candidate)
        if candidate.quality_score <= 0:
            continue
        enriched.append(candidate)

    enriched.sort(key=lambda c: c.quality_score, reverse=True)
    deduped: list[RetrievedChunk] = []
    dedupe_embeddings: list[object] = []
    for candidate in enriched:
        current_emb = embed_text(candidate.chunk.text)
        duplicate = False
        for existing_emb in dedupe_embeddings:
            if cosine_similarity(current_emb, existing_emb) >= settings.dedupe_similarity_threshold:
                duplicate = True
                break
        if not duplicate and not candidate.security_flags:
            deduped.append(candidate)
            dedupe_embeddings.append(current_emb)
        if len(deduped) >= settings.max_context_chunks:
            break
    return deduped

