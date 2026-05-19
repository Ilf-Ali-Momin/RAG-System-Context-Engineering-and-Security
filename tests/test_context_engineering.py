from app.context.builder import build_structured_context
from app.context.selector import select_high_quality_context
from app.models.schemas import ChunkRecord, RetrievedChunk


def _mk(chunk_id: str, text: str, similarity: float, trust: int = 4) -> RetrievedChunk:
    return RetrievedChunk(
        chunk=ChunkRecord(
            chunk_id=chunk_id,
            source_id="doc-a",
            title="Doc A",
            text=text,
            trust_level=trust,
            metadata={},
        ),
        similarity=similarity,
        security_flags=[],
    )


def test_selector_removes_duplicates_and_low_similarity() -> None:
    selected = select_high_quality_context(
        [
            _mk("1", "secure rag context engineering principles", 0.8),
            _mk("2", "secure rag context engineering principles", 0.79),
            _mk("3", "totally unrelated", 0.01),
        ]
    )
    assert len(selected) == 1
    assert selected[0].chunk.chunk_id == "1"


def test_context_builder_produces_confidence_and_structure() -> None:
    selected = select_high_quality_context([_mk("1", "a b c d", 0.8), _mk("2", "e f g h", 0.75)])
    context, confidence = build_structured_context(selected)
    assert "[SOURCE]" in context
    assert confidence > 0

