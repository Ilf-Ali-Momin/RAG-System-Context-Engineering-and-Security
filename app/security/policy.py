from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import settings


PROTECTED_REQUEST_PATTERNS = [
    "system prompt",
    "hidden instructions",
    "developer message",
    "internal chain of thought",
]


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str | None = None


def check_user_query_policy(query: str, injection_flags: list[str]) -> PolicyDecision:
    lower_query = query.lower()
    for marker in PROTECTED_REQUEST_PATTERNS:
        if marker in lower_query:
            return PolicyDecision(allowed=False, reason="request_for_protected_internals")
    if len(injection_flags) >= settings.blocked_pattern_score_threshold:
        return PolicyDecision(allowed=False, reason="prompt_injection_detected")
    return PolicyDecision(allowed=True)


def check_context_confidence(confidence: float) -> PolicyDecision:
    if confidence < settings.min_context_confidence:
        return PolicyDecision(allowed=False, reason="insufficient_reliable_context")
    return PolicyDecision(allowed=True)

