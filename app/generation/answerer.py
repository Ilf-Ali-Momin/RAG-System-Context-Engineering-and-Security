from __future__ import annotations

import re

import httpx

from app.config.settings import settings


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def answer_from_context(prompt: str, context: str, query: str) -> str:
    ollama_answer = _generate_with_ollama(prompt)
    if ollama_answer:
        return ollama_answer.strip()

    if not settings.allow_model_fallback_answering:
        sentences = [s.strip() for s in SENTENCE_RE.split(context) if s.strip()]
        query_terms = {w for w in query.lower().split() if len(w) > 3}
        ranked = sorted(
            sentences,
            key=lambda s: sum(1 for w in query_terms if w in s.lower()),
            reverse=True,
        )
        if not ranked or all(score == 0 for score in [sum(1 for w in query_terms if w in r.lower()) for r in ranked[:1]]):
            return ""
        return " ".join(ranked[:2]).strip()
    return ""


def _generate_with_ollama(prompt: str) -> str:
    try:
        with httpx.Client(timeout=settings.ollama_request_timeout_seconds) as client:
            response = client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_chat_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return ""
    answer = payload.get("response", "")
    if not isinstance(answer, str):
        return ""
    return answer


def grounded_against_context(answer: str, context: str) -> bool:
    if not answer.strip():
        return False
    answer_words = {w.lower() for w in answer.split() if len(w) > 4}
    context_words = {w.lower() for w in context.split()}
    if not answer_words:
        return False
    coverage = sum(1 for w in answer_words if w in context_words) / len(answer_words)
    return coverage >= 0.55

