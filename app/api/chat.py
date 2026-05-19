from __future__ import annotations

from fastapi import APIRouter

from app.context.builder import build_structured_context
from app.context.selector import select_high_quality_context
from app.generation.answerer import answer_from_context, grounded_against_context
from app.generation.prompting import build_context_only_prompt
from app.memory.session_memory import SessionTurn
from app.models.schemas import ChatRequest, ChatResponse
from app.security.injection_detector import detect_prompt_injection
from app.security.policy import check_context_confidence, check_user_query_policy
from app.security.sanitizer import sanitize_text
from app.services import memory_store, retriever
from app.utils.citations import build_citations

router = APIRouter(prefix="/chat", tags=["chat"])


def _refusal(reason: str) -> ChatResponse:
    return ChatResponse(
        status="refusal",
        answer="I can only answer using safe, reliable retrieved context and cannot fulfill that request.",
        reason=reason,
        citations=[],
    )


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    clean_query = sanitize_text(payload.query, max_chars=4000)
    injection_flags = detect_prompt_injection(clean_query)
    query_decision = check_user_query_policy(clean_query, injection_flags)
    if not query_decision.allowed:
        return _refusal(query_decision.reason or "policy_denied")

    retrieved = retriever.retrieve(query=clean_query, top_k=payload.top_k)
    selected = select_high_quality_context(retrieved)
    context, confidence = build_structured_context(selected)
    confidence_decision = check_context_confidence(confidence)
    if not confidence_decision.allowed or not context:
        return _refusal(confidence_decision.reason or "missing_context")

    session = memory_store.get(payload.session_id)
    memory = session.compact_verified_memory()
    prompt = build_context_only_prompt(clean_query, memory, context)
    answer = answer_from_context(prompt=prompt, context=context, query=clean_query)
    if not grounded_against_context(answer=answer, context=context):
        return _refusal("ungrounded_output")

    session.add_turn(SessionTurn(user_query=clean_query, assistant_answer=answer, verified=True))
    return ChatResponse(status="answer", answer=answer, citations=build_citations(selected))

