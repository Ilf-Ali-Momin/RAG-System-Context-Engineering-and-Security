from __future__ import annotations

from collections import defaultdict

from app.config.settings import settings
from app.models.schemas import RetrievedChunk
from app.security.sanitizer import redact_secrets


def build_structured_context(chunks: list[RetrievedChunk]) -> tuple[str, float]:
    grouped: dict[str, list[RetrievedChunk]] = defaultdict(list)
    for chunk in chunks:
        grouped[f"{chunk.chunk.source_id}::{chunk.chunk.title}"].append(chunk)

    budget_remaining = settings.max_context_chars
    blocks: list[str] = []
    scores: list[float] = []
    for source_key, source_chunks in grouped.items():
        source_header = f"[SOURCE] {source_key}"
        source_lines: list[str] = [source_header]
        for candidate in source_chunks:
            cleaned = redact_secrets(candidate.chunk.text)
            allowed = cleaned[: max(0, budget_remaining - len(source_header))]
            if not allowed:
                continue
            source_lines.append(f"- ({candidate.chunk.chunk_id}) {allowed}")
            budget_remaining -= len(allowed)
            scores.append(candidate.quality_score)
            if budget_remaining <= 0:
                break
        if len(source_lines) > 1:
            blocks.append("\n".join(source_lines))
        if budget_remaining <= 0:
            break

    context = "\n\n".join(blocks)
    confidence = (sum(scores) / len(scores)) if scores else 0.0
    return context, confidence

