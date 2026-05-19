from __future__ import annotations

import hashlib
import math

import httpx
import numpy as np

from app.config.settings import settings


def _tokenize(text: str) -> list[str]:
    return [token for token in text.lower().split() if token]


def embed_text(text: str, dim: int = 256) -> np.ndarray:
    if settings.ollama_embeddings_enabled:
        ollama_vector = _embed_with_ollama(text)
        if ollama_vector is not None:
            return ollama_vector

    vector = np.zeros(dim, dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % dim
        vector[idx] += 1.0
    norm = math.sqrt(float((vector * vector).sum()))
    if norm > 0:
        vector /= norm
    return vector


def _embed_with_ollama(text: str) -> np.ndarray | None:
    try:
        with httpx.Client(timeout=settings.ollama_request_timeout_seconds) as client:
            response = client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": settings.ollama_embedding_model, "prompt": text},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return None

    embedding = payload.get("embedding")
    if not isinstance(embedding, list) or not embedding:
        return None
    vector = np.array(embedding, dtype=np.float32)
    norm = float(np.linalg.norm(vector))
    if norm > 0:
        vector /= norm
    return vector


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

